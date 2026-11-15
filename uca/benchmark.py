"""Reproducible benchmark harness; it records unavailable runs instead of inventing scores."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import os
import platform
import resource
import subprocess
import sys
import time

from .evaluation import evaluate_context
from .factory import build_engine


def _git_commit(root: str | Path) -> str | None:
    try:
        return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _gpu_memory() -> int | None:
    try:
        import torch  # type: ignore
        return int(torch.cuda.max_memory_allocated()) if torch.cuda.is_available() else None
    except ImportError:
        return None


def _normal(text: str) -> str:
    return " ".join(text.lower().split())


def _automatic_reference_metrics(answer: str | None, task: dict[str, Any]) -> dict[str, float | None]:
    """Only objective labels supplied in a task are scored automatically.

    Factual correctness, linguistic coherence, and hallucination judgment remain
    null unless an operator supplies a validated evaluator or human annotations.
    """
    if not answer:
        return {"exact_match": 0.0 if task.get("expected_answer") else None,
                "required_keyword_recall": None, "factual_accuracy": None,
                "reasoning": None, "math": None, "linguistic_coherence": None, "hallucination_rate": None}
    expected = task.get("expected_answer")
    exact = float(_normal(answer) == _normal(str(expected))) if expected is not None else None
    keywords = [str(item).lower() for item in task.get("required_keywords", [])]
    recall = (sum(1 for word in keywords if word in answer.lower()) / len(keywords)) if keywords else None
    return {"exact_match": exact, "required_keyword_recall": recall, "factual_accuracy": None,
            "reasoning": None, "math": None, "linguistic_coherence": None, "hallucination_rate": None}


def load_tasks(path: str | Path) -> list[dict[str, Any]]:
    result = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            item = json.loads(line)
            if not isinstance(item, dict) or not isinstance(item.get("prompt"), str):
                raise ValueError(f"Task {line_number} must be an object containing a string prompt")
            item.setdefault("id", f"task-{line_number}")
            result.append(item)
    return result


def variant_config(base: dict[str, Any], variant: str) -> dict[str, Any] | None:
    cfg = deepcopy(base)
    full = cfg["pipeline"]["order"]
    if variant == "uca_full":
        return cfg
    if variant == "uca_full_sequential":
        cfg["engine"]["scheduling_mode"] = "sequential"
        return cfg
    if variant == "uca_full_staged_parallel":
        cfg["engine"]["scheduling_mode"] = "staged_parallel"
        return cfg
    if variant == "smollm2_135_alone":
        cfg["pipeline"]["order"] = ["input_processing", "smollm2_135_analysis", "final_response"]
        return cfg
    if variant == "smollm2_360_alone":
        cfg["pipeline"]["order"] = ["input_processing", "smollm2_360_review", "final_response"]
        return cfg
    if variant == "nanodiff_compatible_only":
        cfg["pipeline"]["order"] = ["input_processing", "nanodiff_specialist", "final_response"]
        return cfg
    if variant.startswith("uca_without_"):
        target = variant.removeprefix("uca_without_")
        mapping = {"memory": {"user_memory"}, "retrieval": {"knowledge_retrieval"},
                   "symbolic": {"symbolic_processing"},
                   "ncm": {"ncm_concept_generation", "ncm_reasoning_refinement"},
                   "nanodiff": {"nanodiff_specialist"}}
        modules = mapping.get(target)
        if modules:
            cfg["pipeline"]["order"] = [item for item in full if item not in modules]
            return cfg
    return None


def run_benchmark(base_config: dict[str, Any], tasks: list[dict[str, Any]], variants: list[str]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for variant in variants:
        if variant == "legacy_current_project":
            results.append({"variant": variant, "status": "not_executable",
                            "reason": "The audited starting commit had no executable architecture to benchmark.", "runs": []})
            continue
        cfg = variant_config(base_config, variant)
        if cfg is None:
            results.append({"variant": variant, "status": "invalid_variant", "runs": []})
            continue
        runs: list[dict[str, Any]] = []
        for task in tasks:
            if variant == "nanodiff_compatible_only" and not task.get("nanodiff_compatible", False):
                runs.append({"task_id": task["id"], "status": "skipped", "reason": "Task not marked nanodiff_compatible"})
                continue
            engine = build_engine(config=cfg)
            before_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            before_gpu = _gpu_memory()
            started = time.perf_counter()
            context = engine.process(task["prompt"])
            elapsed = time.perf_counter() - started
            after_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            after_gpu = _gpu_memory()
            reports = context.execution_history
            unavailable = [record.module_id for record in reports if record.status.value in ("unavailable", "non_validated")]
            failed = [record.module_id for record in reports if record.status.value == "failed_execution"]
            structural = evaluate_context(context, task.get("expectations") if isinstance(task.get("expectations"), dict) else {})
            run_status = "completed_with_degradation" if unavailable or failed else "completed"
            if not structural["passed"]:
                run_status = "completed_with_structural_violations"
            runs.append({
                "task_id": task["id"], "status": run_status,
                "unavailable_modules": unavailable, "failed_modules": failed,
                "metrics": _automatic_reference_metrics(context.final_response, task),
                "structural_evaluation": structural,
                "performance": {"wall_seconds": elapsed, "max_rss_delta_kib": max(0, after_rss - before_rss),
                                "cuda_peak_bytes_before": before_gpu, "cuda_peak_bytes_after": after_gpu,
                                "computational_cost_proxy": "local wall time + peak process memory only; no monetary-cost claim"},
                "execution_topology": engine.status()["execution_topology"],
                "request_id": context.request_id,
            })
        results.append({"variant": variant, "status": "executed", "runs": runs})
    return {"schema": "uca.benchmark.v1", "created_at": datetime.now(timezone.utc).isoformat(),
            "environment": {"python": sys.version, "platform": platform.platform(), "pid": os.getpid(),
                            "git_commit": _git_commit(base_config.get("_root", "."))},
            "scoring_notice": "Null quality metrics require human annotation or a separately validated evaluator; no result is inferred.",
            "results": results}
