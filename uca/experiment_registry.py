"""Versioned, local experiment records for evidence-based UCA changes.

This module deliberately records *what was measured* without inferring an
improvement. A result is comparable only when it names its code, configuration,
assets, task split, and baseline. Quality metrics may stay ``None`` when no
validated evaluator or human annotation is available.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
from math import isfinite
from pathlib import Path
from typing import Any, Mapping
import json
import os
import re
import tempfile


SCHEMA = "uca.experiment.v1"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_EXPERIMENT_ID = re.compile(r"^[a-z][a-z0-9_.-]{2,127}$")
_REQUIRED_TEXT = ("experiment_id", "code_revision", "config_digest", "baseline", "intervention", "task_split")


class ManifestValidationError(ValueError):
    """Raised when an experiment record is not reproducible enough to retain."""


@dataclass(frozen=True)
class StoredExperiment:
    """A normalized manifest and its content-addressed local storage location."""
    manifest: dict[str, Any]
    digest: str
    path: Path


def _json_copy(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ManifestValidationError("Experiment manifest must be a JSON object")
    try:
        rendered = json.dumps(value, ensure_ascii=False, allow_nan=False)
        decoded = json.loads(rendered)
    except (TypeError, ValueError) as error:
        raise ManifestValidationError("Experiment manifest must contain JSON values only") from error
    if not isinstance(decoded, dict):  # defensive; json object normally remains a dict
        raise ManifestValidationError("Experiment manifest must be a JSON object")
    return decoded


def _require_text(manifest: Mapping[str, Any], field: str) -> str:
    value = manifest.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ManifestValidationError(f"{field} must be a non-empty string")
    return value.strip()


def _validate_metrics(metrics: Any) -> dict[str, float | None]:
    if not isinstance(metrics, dict):
        raise ManifestValidationError("metrics must be an object of finite numeric values or null")
    normalized: dict[str, float | None] = {}
    for name, value in metrics.items():
        if not isinstance(name, str) or not name.strip():
            raise ManifestValidationError("Metric names must be non-empty strings")
        if value is None:
            normalized[name] = None
        elif isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(float(value)):
            raise ManifestValidationError(f"Metric {name!r} must be finite numeric or null")
        else:
            normalized[name] = float(value)
    return normalized


def _validate_assets(assets: Any) -> list[dict[str, str]]:
    if not isinstance(assets, list):
        raise ManifestValidationError("assets must be a list")
    normalized: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            raise ManifestValidationError(f"assets[{index}] must be an object")
        asset_id = _require_text(asset, "id")
        digest = _require_text(asset, "digest").lower()
        license_name = _require_text(asset, "license")
        if not _SHA256.fullmatch(digest):
            raise ManifestValidationError(f"assets[{index}].digest must be a SHA-256 hex digest")
        if asset_id in seen:
            raise ManifestValidationError(f"Duplicate asset id: {asset_id}")
        seen.add(asset_id)
        normalized.append({"id": asset_id, "digest": digest, "license": license_name})
    return normalized


def _validate_string_list(manifest: Mapping[str, Any], field: str) -> list[str]:
    values = manifest.get(field, [])
    if not isinstance(values, list) or not all(isinstance(value, str) and value.strip() for value in values):
        raise ManifestValidationError(f"{field} must be a list of non-empty strings")
    return [value.strip() for value in values]


def normalize_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and normalize the portable experiment-record contract.

    Unknown JSON fields are preserved deliberately so that a research team can
    add domain-specific metadata. The reproducibility-critical fields are
    validated here, and a missing schema is upgraded to the current local
    schema for backwards compatibility with early planning documents.
    """
    normalized = _json_copy(manifest)
    schema = normalized.get("schema", SCHEMA)
    if schema != SCHEMA:
        raise ManifestValidationError(f"Unsupported experiment schema: {schema!r}")
    normalized["schema"] = SCHEMA
    for field in _REQUIRED_TEXT:
        normalized[field] = _require_text(normalized, field)
    if not _EXPERIMENT_ID.fullmatch(normalized["experiment_id"]):
        raise ManifestValidationError("experiment_id must use lowercase letters, digits, dot, underscore, or hyphen")
    if not _SHA256.fullmatch(normalized["config_digest"].lower()):
        raise ManifestValidationError("config_digest must be a SHA-256 hex digest")
    normalized["config_digest"] = normalized["config_digest"].lower()
    normalized["assets"] = _validate_assets(normalized.get("assets"))
    normalized["metrics"] = _validate_metrics(normalized.get("metrics"))
    normalized["ablations"] = _validate_string_list(normalized, "ablations")
    normalized["failures"] = _validate_string_list(normalized, "failures")
    review = normalized.get("review", {})
    if not isinstance(review, dict) or not isinstance(review.get("status", "pending"), str):
        raise ManifestValidationError("review must be an object with a string status")
    normalized["review"] = deepcopy(review)
    normalized["review"].setdefault("status", "pending")
    return normalized


def canonical_json(manifest: Mapping[str, Any]) -> str:
    """Return canonical JSON for a normalized reproducibility record."""
    normalized = normalize_manifest(manifest)
    return json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def manifest_digest(manifest: Mapping[str, Any]) -> str:
    """Digest the canonical record; formatting and key order never affect it."""
    return sha256(canonical_json(manifest).encode("utf-8")).hexdigest()


def compare_metric(baseline: Mapping[str, Any], candidate: Mapping[str, Any], metric: str,
                   *, higher_is_better: bool = True) -> dict[str, Any]:
    """Compare one finite metric without inventing a conclusion for null data."""
    if not isinstance(metric, str) or not metric.strip():
        raise ValueError("A non-empty metric name is required")
    before = normalize_manifest(baseline)["metrics"].get(metric)
    after = normalize_manifest(candidate)["metrics"].get(metric)
    if before is None or after is None:
        return {"metric": metric, "status": "unavailable", "baseline": before, "candidate": after,
                "delta": None, "direction": "unknown"}
    delta = after - before
    direction = "improved" if (delta > 0 if higher_is_better else delta < 0) else "regressed" if delta else "unchanged"
    return {"metric": metric, "status": "measured", "baseline": before, "candidate": after,
            "delta": delta, "direction": direction}


class ExperimentRegistry:
    """Content-addressed local experiment storage with atomic writes.

    It accepts no remote URL and executes no model. The registry only records
    validated JSON evidence that an external benchmark produced.
    """
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def record(self, manifest: Mapping[str, Any]) -> StoredExperiment:
        normalized = normalize_manifest(manifest)
        digest = manifest_digest(normalized)
        destination = self.root / f"{normalized['experiment_id']}-{digest[:16]}.json"
        self.root.mkdir(parents=True, exist_ok=True)
        payload = canonical_json(normalized) + "\n"
        if destination.exists():
            existing = self.load(destination)
            if existing.digest != digest:
                raise ManifestValidationError(f"Existing record has a mismatched digest: {destination}")
            return existing
        descriptor, temporary = tempfile.mkstemp(prefix=".uca-experiment-", suffix=".tmp", dir=self.root)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, destination)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        return StoredExperiment(normalized, digest, destination)

    def load(self, path: str | Path) -> StoredExperiment:
        location = Path(path)
        try:
            parsed = json.loads(location.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ManifestValidationError(f"Cannot read experiment manifest: {location}") from error
        normalized = normalize_manifest(parsed)
        return StoredExperiment(normalized, manifest_digest(normalized), location)
