"""Configuration loading with explicit defaults; paths remain local to project root."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any
import tomllib

DEFAULT_CONFIG: dict[str, Any] = {
    "engine": {"mode": "sequential_unload", "default_timeout_seconds": 45,
               "max_corrections": 1, "cache_enabled": False, "run_history_limit": 30,
               "scheduling_mode": "staged_parallel", "parallel_max_workers": 3},
    "stores": {"memory_path": "data/memory.json", "knowledge_db": "data/knowledge.sqlite",
               "knowledge_table": "documents", "facts_path": "data/operator_facts.json"},
    "cognitive": {"working_memory_capacity": 12, "max_evidence_nodes": 48, "max_evidence_edges": 160,
                  "diversity_bonus": 0.08},
    "training": {
        "enabled": False, "target": "smollm2_360_lora", "dataset_path": "", "manifest_path": "",
        "output_dir": "training-runs/smollm2_360_lora", "lora_target_modules": [],
        "lora_rank": 16, "lora_alpha": 32, "lora_dropout": 0.05,
        "epochs": 1, "batch_size": 1, "max_length": 512, "learning_rate": 0.0002,
        "max_grad_norm": 1.0, "seed": 17, "device": "auto",
    },
    "models": {
        "smollm2_135": {"enabled": True, "path": "", "max_new_tokens": 280, "device": "auto"},
        "smollm2_360": {"enabled": True, "path": "", "max_new_tokens": 360, "device": "auto"},
        "ncm": {"enabled": False, "runner_command": "", "validated": False,
                "refinement_enabled": False, "refinement_validated": False},
        "nanodiff": {"enabled": False, "path": "", "tokenizer_path": "", "runner_command": "",
                     "mask_token_id": -1, "validated": False,
                     "strategies": ["single_pass", "iterative_low_mask"]},
    },
    "metta": {"enabled": True, "runner_command": ""},
    "auxiliary": {name: {"enabled": False} for name in
                  ("lora", "ties", "dare", "aoe", "fla", "e2e", "scallop")},
    "pipeline": {"order": [
        "input_processing", "user_memory", "knowledge_retrieval", "symbolic_processing",
        "ncm_concept_generation", "smollm2_135_analysis", "smollm2_360_review",
        "nanodiff_specialist", "global_workspace", "ncm_reasoning_refinement",
        "final_verification", "final_response"]},
}


def _merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _merge(base[key], value)
        else:
            base[key] = value
    return base


def load_config(root: str | Path = ".", config_path: str | Path | None = None) -> dict[str, Any]:
    root_path = Path(root).resolve()
    file_path = Path(config_path) if config_path else root_path / "config" / "uca.toml"
    config = deepcopy(DEFAULT_CONFIG)
    if file_path.exists():
        with file_path.open("rb") as handle:
            _merge(config, tomllib.load(handle))
    config["_root"] = str(root_path)
    return config


def local_path(config: dict[str, Any], configured_path: str) -> Path:
    """Resolve a configured path without permitting accidental remote URIs."""
    if "://" in configured_path:
        raise ValueError("UCA accepts local asset paths only; remote URLs are not supported")
    candidate = Path(configured_path)
    return candidate if candidate.is_absolute() else Path(config["_root"]) / candidate
