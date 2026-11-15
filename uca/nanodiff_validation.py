"""Calibration harness for nanoDiff masked denoising before pipeline activation."""
from __future__ import annotations

from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any
import hashlib
import json

from .model_adapters import MaskedNanoDiffAdapter
from .types import ModuleStatus


def load_cases(path: str | Path) -> list[dict[str, str]]:
    """Load JSONL records containing operator-curated `text` and `reference`."""
    cases: list[dict[str, str]] = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            item = json.loads(line)
            if not isinstance(item, dict) or not isinstance(item.get("text"), str) or not isinstance(item.get("reference"), str):
                raise ValueError(f"Case {line_number} must contain string text and reference fields")
            cases.append({"id": str(item.get("id", f"case-{line_number}")), "text": item["text"], "reference": item["reference"]})
    if not cases:
        raise ValueError("At least one curated calibration case is required")
    return cases


def similarity(text: str, reference: str) -> float:
    """Transparent string proxy; not a factuality or safety evaluator."""
    return SequenceMatcher(a=" ".join(text.lower().split()), b=" ".join(reference.lower().split())).ratio()


def validate_masked_denoiser(adapter: MaskedNanoDiffAdapter, cases: list[dict[str, str]], *,
                              timeout: float = 45.0, min_mean_delta: float = 0.01) -> dict[str, Any]:
    capability = adapter.calibration_capability()
    if capability.status is not ModuleStatus.FUNCTIONAL:
        return {"schema": "uca.nanodiff-calibration.v1", "status": "not_executable", "reason": capability.reason,
                "validated_for_activation": False, "strategies": {}}
    strategies = [str(item) for item in adapter.config.get("strategies", [])] or ["single_pass"]
    reports: dict[str, Any] = {}
    all_deltas: list[float] = []
    for strategy in strategies:
        records: list[dict[str, Any]] = []
        for case in cases:
            output = adapter.denoise(case["text"], strategy, timeout, calibration=True)
            baseline = similarity(case["text"], case["reference"])
            candidate = similarity(str(output["candidate_text"]), case["reference"])
            delta = candidate - baseline
            all_deltas.append(delta)
            records.append({"case_id": case["id"], "baseline_similarity": baseline,
                            "candidate_similarity": candidate, "delta": delta,
                            "changed": output.get("changed", False), "runner_score": output.get("runner_score")})
        reports[strategy] = {"records": records,
                              "mean_delta": sum(item["delta"] for item in records) / len(records)}
    mean_delta = sum(all_deltas) / len(all_deltas) if all_deltas else 0.0
    # This merely gates deployment using references supplied by the operator. It
    # cannot prove factuality, so human review remains mandatory.
    canonical = json.dumps({"strategies": reports, "mean_delta": mean_delta}, sort_keys=True).encode()
    return {"schema": "uca.nanodiff-calibration.v1", "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "executed", "strategies": reports, "mean_delta": mean_delta,
            "min_mean_delta": min_mean_delta,
            "validated_for_activation": mean_delta >= min_mean_delta,
            "calibration_id": hashlib.sha256(canonical).hexdigest()[:16],
            "limitations": ["Similarity to operator references is a narrow denoising proxy, not factual verification.",
                            "Review per-case outputs and factual/coherence labels before setting models.nanodiff.validated=true."],}
