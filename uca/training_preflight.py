"""Local-only preflight checks for reproducible UCA fine-tuning runs.

The preflight intentionally does not download a checkpoint, start a trainer, or
claim a model was trained. It checks that an operator supplied enough local,
licensed and disjoint inputs to *permit* a subsequent training run.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping
import json
import os
import re
import subprocess


TRAINING_SCHEMA = "uca.training.v1"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_PLACEHOLDER = re.compile(r"(?:REPLACE_WITH|<[^>]+>)", re.IGNORECASE)


@dataclass(frozen=True)
class TrainingPreflightReport:
    """A transparent readiness report; ``ready`` never means training occurred."""
    ready: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    dataset_counts: dict[str, int]
    file_digests: dict[str, str]
    cuda_visible: bool


class TrainingManifestError(ValueError):
    """Raised when the manifest cannot be parsed as a local training contract."""


def sha256_file(path: str | Path) -> str:
    """Hash a local file without reading it all into memory."""
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def cuda_visible() -> bool:
    """Check visibility only; never initialize a heavyweight ML runtime."""
    try:
        result = subprocess.run(["nvidia-smi", "-L"], text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL, timeout=3, check=False)
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0 and bool(result.stdout.strip())


def _copy_json_object(manifest: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(manifest, Mapping):
        raise TrainingManifestError("Training manifest must be a JSON object")
    try:
        copied = json.loads(json.dumps(manifest, allow_nan=False))
    except (TypeError, ValueError) as error:
        raise TrainingManifestError("Training manifest must contain JSON values only") from error
    if not isinstance(copied, dict):
        raise TrainingManifestError("Training manifest must be a JSON object")
    return copied


def _text(value: Any, label: str, errors: list[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty string")
        return ""
    result = value.strip()
    if _PLACEHOLDER.search(result):
        errors.append(f"{label} still contains a placeholder")
    return result


def _digest(value: Any, label: str, errors: list[str]) -> str:
    rendered = _text(value, label, errors).lower()
    if rendered and not _SHA256.fullmatch(rendered):
        errors.append(f"{label} must be a 64-character SHA-256 hex digest")
    return rendered


def _local_path(root: Path, raw: str, label: str, errors: list[str]) -> Path | None:
    if not raw:
        return None
    if "://" in raw:
        errors.append(f"{label} must be a local path, not a URL")
        return None
    path = Path(raw).expanduser()
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _mapping(parent: Mapping[str, Any], key: str, errors: list[str]) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        errors.append(f"{key} must be an object")
        return {}
    return value


def _positive_number(value: Any, label: str, errors: list[str], *, integer: bool = False) -> float | int | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        errors.append(f"{label} must be positive")
        return None
    if integer and int(value) != value:
        errors.append(f"{label} must be an integer")
        return None
    return int(value) if integer else float(value)


def _load_ids(path: Path, split: str, errors: list[str]) -> set[str]:
    identifiers: set[str] = set()
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        errors.append(f"Cannot read {split} dataset: {error}")
        return identifiers
    if not lines:
        errors.append(f"{split} dataset is empty")
        return identifiers
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            errors.append(f"{split} dataset line {number} is not JSONL")
            continue
        identifier = record.get("id") if isinstance(record, dict) else None
        if not isinstance(identifier, (str, int)) or not str(identifier).strip():
            errors.append(f"{split} dataset line {number} has no non-empty id")
            continue
        normalized = str(identifier)
        if normalized in identifiers:
            errors.append(f"{split} dataset repeats id {normalized!r}")
        identifiers.add(normalized)
    if not identifiers and not errors:
        errors.append(f"{split} dataset has no records")
    return identifiers


def preflight_training(manifest: Mapping[str, Any], root: str | Path = ".") -> TrainingPreflightReport:
    """Inspect a proposed local run and return all blockers in one report.

    The function is deliberately side-effect free except for reading local
    metadata/files. It neither imports optional training libraries nor creates
    output directories, making it safe to invoke in CI or before GPU allocation.
    """
    errors: list[str] = []
    warnings: list[str] = []
    counts: dict[str, int] = {}
    digests: dict[str, str] = {}
    try:
        data = _copy_json_object(manifest)
    except TrainingManifestError as error:
        return TrainingPreflightReport(False, (str(error),), (), counts, digests, cuda_visible())
    root_path = Path(root).resolve()
    if data.get("schema") != TRAINING_SCHEMA:
        errors.append(f"schema must equal {TRAINING_SCHEMA!r}")
    _text(data.get("run_id"), "run_id", errors)
    model = _mapping(data, "base_model", errors)
    corpus = _mapping(data, "data", errors)
    method = _mapping(data, "method", errors)
    budget = _mapping(data, "budget", errors)
    output = _mapping(data, "output", errors)
    evaluation = _mapping(data, "evaluation", errors)

    model_path = _local_path(root_path, _text(model.get("path"), "base_model.path", errors), "base_model.path", errors)
    tokenizer_path = _local_path(root_path, _text(model.get("tokenizer_path"), "base_model.tokenizer_path", errors),
                                 "base_model.tokenizer_path", errors)
    _digest(model.get("sha256"), "base_model.sha256", errors)
    _text(model.get("architecture"), "base_model.architecture", errors)
    _text(model.get("license"), "base_model.license", errors)
    for label, path in (("base_model.path", model_path), ("base_model.tokenizer_path", tokenizer_path)):
        if path is not None and not path.exists():
            errors.append(f"{label} does not exist locally: {path}")

    _text(corpus.get("license"), "data.license", errors)
    review = _text(corpus.get("personal_data_review"), "data.personal_data_review", errors).lower()
    if review not in {"approved", "not_required", "not_applicable"}:
        errors.append("data.personal_data_review must be approved, not_required, or not_applicable")
    card_path = _local_path(root_path, _text(corpus.get("data_card"), "data.data_card", errors), "data.data_card", errors)
    if card_path is not None and not card_path.is_file():
        errors.append(f"data.data_card does not exist locally: {card_path}")

    declared_digests = corpus.get("sha256") if isinstance(corpus.get("sha256"), dict) else {}
    if not isinstance(corpus.get("sha256"), dict):
        errors.append("data.sha256 must be an object with train, validation, and holdout digests")
    split_ids: dict[str, set[str]] = {}
    for split in ("train", "validation", "holdout"):
        raw_path = _text(corpus.get(f"{split}_path"), f"data.{split}_path", errors)
        expected = _digest(declared_digests.get(split), f"data.sha256.{split}", errors)
        file_path = _local_path(root_path, raw_path, f"data.{split}_path", errors)
        if file_path is None or not file_path.is_file():
            if file_path is not None:
                errors.append(f"data.{split}_path does not exist locally: {file_path}")
            split_ids[split] = set()
            continue
        actual = sha256_file(file_path)
        digests[split] = actual
        if expected and actual != expected:
            errors.append(f"data.sha256.{split} does not match the local file")
        split_ids[split] = _load_ids(file_path, split, errors)
        counts[split] = len(split_ids[split])
    for left, right in (("train", "validation"), ("train", "holdout"), ("validation", "holdout")):
        overlap = split_ids.get(left, set()) & split_ids.get(right, set())
        if overlap:
            errors.append(f"Dataset leakage: {left} and {right} share id(s), e.g. {sorted(overlap)[0]!r}")

    kind = _text(method.get("kind"), "method.kind", errors).lower()
    if kind not in {"lora", "qlora", "full_finetune"}:
        errors.append("method.kind must be lora, qlora, or full_finetune")
    seed = method.get("seed")
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        errors.append("method.seed must be a non-negative integer")
    _positive_number(method.get("max_steps"), "method.max_steps", errors, integer=True)
    _positive_number(method.get("learning_rate"), "method.learning_rate", errors)
    _positive_number(method.get("max_sequence_length"), "method.max_sequence_length", errors, integer=True)
    _text(method.get("prompt_template_version"), "method.prompt_template_version", errors)

    device = _text(budget.get("device"), "budget.device", errors).lower()
    _positive_number(budget.get("max_wall_minutes"), "budget.max_wall_minutes", errors)
    _positive_number(budget.get("max_checkpoints"), "budget.max_checkpoints", errors, integer=True)
    has_cuda = cuda_visible()
    if device not in {"cpu", "cuda"}:
        errors.append("budget.device must be cpu or cuda")
    if device == "cuda":
        _positive_number(budget.get("max_gpu_memory_gib"), "budget.max_gpu_memory_gib", errors)
        if not has_cuda:
            errors.append("CUDA requested but no NVIDIA GPU is visible to this process")
    elif budget.get("max_gpu_memory_gib") not in (None, 0):
        warnings.append("max_gpu_memory_gib is ignored for a CPU run")

    destination = _local_path(root_path, _text(output.get("path"), "output.path", errors), "output.path", errors)
    if output.get("adapter_only") is not True:
        errors.append("output.adapter_only must be true for the first reversible training stage")
    if destination is not None and model_path is not None:
        try:
            destination.relative_to(model_path)
        except ValueError:
            pass
        else:
            errors.append("output.path must not be inside the immutable base-model directory")

    _text(evaluation.get("baseline"), "evaluation.baseline", errors)
    suite = _local_path(root_path, _text(evaluation.get("benchmark_suite"), "evaluation.benchmark_suite", errors),
                        "evaluation.benchmark_suite", errors)
    if suite is not None and not suite.is_file():
        errors.append(f"evaluation.benchmark_suite does not exist locally: {suite}")
    criteria = evaluation.get("acceptance_criteria")
    if not isinstance(criteria, list) or not criteria or not all(isinstance(item, str) and item.strip() for item in criteria):
        errors.append("evaluation.acceptance_criteria must be a non-empty list of strings")

    return TrainingPreflightReport(not errors, tuple(errors), tuple(warnings), counts, digests, has_cuda)
