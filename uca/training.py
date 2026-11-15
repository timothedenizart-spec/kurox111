"""Guarded local LoRA-SFT preparation and execution for UCA.

This module trains an adapter for an *existing* local SmolLM2-360M checkpoint.
It never distils another model, merges model weights, downloads an asset, or
uses chat/user memory as a dataset. A preflight manifest must explicitly attest
to the local dataset's rights and provenance before any tensor is loaded.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any
import json
import random

from .auxiliary import AuxiliaryRegistry
from .config import local_path


TRAINING_SCHEMA = "uca.training-manifest.v1"
TARGET = "smollm2_360_lora"
BASE_MODEL_ID = "SmolLM2-360M-Instruct"
CONFIRMATION_PHRASE = "I_CONFIRM_LOCAL_TRAINING"


class TrainingBlockedError(RuntimeError):
    """Raised when the explicit local training contract is incomplete."""


def _hash_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _training_spec(config: dict[str, Any]) -> dict[str, Any]:
    value = config.get("training", {})
    return value if isinstance(value, dict) else {}


def _dataset_scan(path: Path) -> dict[str, Any]:
    """Validate a small, explicit JSONL SFT contract without retaining data."""
    records = 0
    invalid = 0
    missing_source = 0
    missing_license = 0
    forbidden_training_marker = 0
    duplicate_ids = 0
    seen_ids: set[str] = set()
    max_characters = 0
    reasons: list[str] = []
    try:
        handle = path.open(encoding="utf-8")
    except OSError as error:
        return {"records": 0, "errors": [f"Dataset cannot be opened: {error}"], "sha256": None}
    with handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                invalid += 1
                reasons.append(f"line {line_number}: invalid JSON")
                continue
            if not isinstance(item, dict) or not isinstance(item.get("text"), str) or not item["text"].strip():
                invalid += 1
                reasons.append(f"line {line_number}: require non-empty string field 'text'")
                continue
            records += 1
            max_characters = max(max_characters, len(item["text"]))
            identifier = item.get("id")
            if identifier is not None:
                value = str(identifier)
                if value in seen_ids:
                    duplicate_ids += 1
                seen_ids.add(value)
            source = item.get("source")
            if not source:
                missing_source += 1
            license_value = item.get("license")
            if isinstance(source, dict):
                license_value = license_value or source.get("license")
            if not license_value:
                missing_license += 1
            elif str(license_value).strip().upper() in {"NO_TRAINING_DATA", "DO_NOT_TRAIN", "EXAMPLE_ONLY"}:
                forbidden_training_marker += 1
    errors = list(reasons[:12])
    if records == 0:
        errors.append("Dataset contains no valid training records")
    if invalid:
        errors.append(f"Dataset has {invalid} invalid record(s)")
    if duplicate_ids:
        errors.append(f"Dataset has {duplicate_ids} duplicate explicit ID(s)")
    if missing_source:
        errors.append(f"Dataset has {missing_source} record(s) without source provenance")
    if missing_license:
        errors.append(f"Dataset has {missing_license} record(s) without license/rights label")
    if forbidden_training_marker:
        errors.append(f"Dataset has {forbidden_training_marker} record(s) explicitly marked not for training")
    return {"records": records, "invalid_records": invalid, "duplicate_ids": duplicate_ids,
            "missing_source": missing_source, "missing_license": missing_license,
            "forbidden_training_marker": forbidden_training_marker,
            "max_characters": max_characters, "errors": errors, "sha256": _hash_file(path)}


def training_preflight(config: dict[str, Any]) -> dict[str, Any]:
    """Return a machine-readable gate; does not import ML libraries or write files."""
    spec = _training_spec(config)
    errors: list[str] = []
    warnings: list[str] = []
    enabled = bool(spec.get("enabled", False))
    target = str(spec.get("target", TARGET))
    if target != TARGET:
        errors.append(f"Only guarded target '{TARGET}' is supported; got '{target}'")
    if not enabled:
        warnings.append("Training is disabled by configuration; preflight is advisory only.")

    base_raw = str(config.get("models", {}).get("smollm2_360", {}).get("path", "")).strip()
    base_path = local_path(config, base_raw) if base_raw else None
    if not base_path:
        errors.append("models.smollm2_360.path is required for adapter training")
    elif not base_path.is_dir():
        errors.append(f"Base checkpoint directory does not exist: {base_path}")
    else:
        if not (base_path / "config.json").is_file():
            errors.append("Base checkpoint lacks config.json")
        if not any((base_path / name).is_file() for name in ("tokenizer.json", "tokenizer_config.json")):
            errors.append("Base checkpoint lacks tokenizer.json or tokenizer_config.json")
        if not any(any(base_path.glob(pattern)) for pattern in ("*.safetensors", "*.bin", "*.pt", "*.pth")):
            errors.append("Base checkpoint has no local weight file (*.safetensors, *.bin, *.pt or *.pth)")

    dataset_raw = str(spec.get("dataset_path", "")).strip()
    dataset_path = local_path(config, dataset_raw) if dataset_raw else None
    scan: dict[str, Any] = {"records": 0, "errors": ["No dataset_path configured"], "sha256": None}
    if dataset_path and dataset_path.is_file():
        scan = _dataset_scan(dataset_path)
        errors.extend(scan["errors"])
    elif dataset_path:
        errors.append(f"Training dataset does not exist: {dataset_path}")
    else:
        errors.append("training.dataset_path is required")

    manifest_raw = str(spec.get("manifest_path", "")).strip()
    manifest_path = local_path(config, manifest_raw) if manifest_raw else None
    manifest = _read_json(manifest_path) if manifest_path else None
    if manifest is None:
        errors.append("A valid training manifest_path is required")
    else:
        if manifest.get("schema") != TRAINING_SCHEMA:
            errors.append(f"Training manifest schema must be '{TRAINING_SCHEMA}'")
        if manifest.get("target") != TARGET:
            errors.append(f"Training manifest target must be '{TARGET}'")
        if manifest.get("base_model_id") != BASE_MODEL_ID:
            errors.append(f"Training manifest base_model_id must be '{BASE_MODEL_ID}'")
        if manifest.get("distillation") is not False:
            errors.append("Training manifest must explicitly set distillation to false")
        if manifest.get("contains_user_memory") is not False:
            errors.append("Training manifest must explicitly set contains_user_memory to false")
        if manifest.get("data_rights_confirmed") is not True:
            errors.append("Training manifest must explicitly set data_rights_confirmed to true")
        if not isinstance(manifest.get("approved_by"), str) or not manifest["approved_by"].strip():
            errors.append("Training manifest requires non-empty approved_by")
        if scan.get("sha256") and manifest.get("dataset_sha256") != scan["sha256"]:
            errors.append("Training manifest dataset_sha256 does not match local dataset")

    target_modules = spec.get("lora_target_modules", [])
    if not isinstance(target_modules, list) or not target_modules or not all(isinstance(item, str) and item for item in target_modules):
        errors.append("training.lora_target_modules must be a non-empty explicit list; UCA will not guess architecture modules")
    output_raw = str(spec.get("output_dir", "")).strip()
    output_path = local_path(config, output_raw) if output_raw else None
    if not output_path:
        errors.append("training.output_dir is required")
    elif base_path and output_path.resolve() == base_path.resolve():
        errors.append("Adapter output_dir must not be the base checkpoint directory")
    elif output_path and output_path.exists() and not output_path.is_dir():
        errors.append(f"Adapter output_dir exists but is not a directory: {output_path}")
    elif output_path and output_path.exists() and any(output_path.iterdir()):
        errors.append(f"Adapter output_dir must be empty or absent: {output_path}")

    if int(spec.get("epochs", 1)) < 1 or int(spec.get("epochs", 1)) > 100:
        errors.append("training.epochs must be in [1, 100]")
    if int(spec.get("max_length", 512)) < 8 or int(spec.get("max_length", 512)) > 8192:
        errors.append("training.max_length must be in [8, 8192]")
    if int(spec.get("batch_size", 1)) < 1 or int(spec.get("batch_size", 1)) > 128:
        errors.append("training.batch_size must be in [1, 128]")

    checkpoint_fingerprint = None
    if base_path and base_path.is_dir():
        try:
            checkpoint_fingerprint = AuxiliaryRegistry.checkpoint_fingerprint(base_path)
        except OSError as error:
            warnings.append(f"Could not fingerprint checkpoint: {error}")
    if manifest is not None and checkpoint_fingerprint:
        if manifest.get("base_checkpoint_fingerprint") != checkpoint_fingerprint:
            errors.append("Training manifest base_checkpoint_fingerprint does not match local checkpoint")
    return {
        "schema": "uca.training-preflight.v1", "target": target, "enabled": enabled,
        "can_train": enabled and not errors, "errors": errors, "warnings": warnings,
        "base_checkpoint": str(base_path) if base_path else None,
        "base_checkpoint_fingerprint": checkpoint_fingerprint,
        "dataset": {"path": str(dataset_path) if dataset_path else None, **scan},
        "manifest_path": str(manifest_path) if manifest_path else None,
        "output_dir": str(output_path) if output_path else None,
        "policy": {"distillation": "forbidden", "base_weight_merge": "forbidden", "user_memory_dataset": "forbidden",
                   "download": "forbidden", "adapter": "LoRA only; remains separate from the base checkpoint"},
    }


def _load_texts(path: Path) -> list[str]:
    texts: list[str] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                item = json.loads(line)
                texts.append(item["text"])
    return texts


def train_lora_adapter(config: dict[str, Any], confirmation: str) -> dict[str, Any]:
    """Train and save a standalone LoRA adapter after all preflight gates pass.

    This function is intentionally never called by the UCA chat pipeline. It is
    an explicit operator action and does not merge adapter weights into the base.
    """
    report = training_preflight(config)
    if not report["can_train"]:
        raise TrainingBlockedError("Training preflight blocked: " + " | ".join(report["errors"]))
    if confirmation != CONFIRMATION_PHRASE:
        raise TrainingBlockedError(f"Confirmation phrase required: {CONFIRMATION_PHRASE}")
    try:
        import torch  # type: ignore
        from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore
    except ImportError as error:
        raise TrainingBlockedError("Local training environment requires torch and transformers; UCA will not install or download them") from error

    spec = _training_spec(config)
    base_path = Path(str(report["base_checkpoint"]))
    dataset_path = Path(str(report["dataset"]["path"]))
    output_dir = Path(str(report["output_dir"]))
    texts = _load_texts(dataset_path)
    if not texts:
        raise TrainingBlockedError("No texts available after preflight")
    seed = int(spec.get("seed", 17))
    random.seed(seed)
    torch.manual_seed(seed)
    tokenizer = AutoTokenizer.from_pretrained(str(base_path), local_files_only=True)
    if tokenizer.pad_token_id is None:
        if tokenizer.eos_token_id is None:
            raise TrainingBlockedError("Tokenizer has neither pad token nor EOS token for safe padding")
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(str(base_path), local_files_only=True)
    model.config.use_cache = False
    device_setting = str(spec.get("device", "auto"))
    device = "cuda" if device_setting == "auto" and torch.cuda.is_available() else ("cpu" if device_setting == "auto" else device_setting)
    model.to(device)
    # Freeze every base parameter before inserting lightweight local LoRA layers.
    # This implementation deliberately avoids a dependency on another adapter
    # project: its output format is explicit and remains disabled in UCA until a
    # separate loader/compatibility validation is supplied.
    for parameter in model.parameters():
        parameter.requires_grad_(False)

    class _LocalLoRALinear(torch.nn.Module):
        def __init__(self, base_layer: Any, rank: int, alpha: int, dropout: float) -> None:
            super().__init__()
            self.base_layer = base_layer
            self.rank = rank
            self.scale = alpha / rank
            self.dropout = torch.nn.Dropout(dropout)
            for parameter in self.base_layer.parameters():
                parameter.requires_grad_(False)
            kwargs = {"device": self.base_layer.weight.device, "dtype": self.base_layer.weight.dtype}
            self.lora_A = torch.nn.Parameter(torch.empty((rank, self.base_layer.in_features), **kwargs))
            self.lora_B = torch.nn.Parameter(torch.zeros((self.base_layer.out_features, rank), **kwargs))
            torch.nn.init.kaiming_uniform_(self.lora_A, a=5 ** 0.5)

        def forward(self, inputs: Any) -> Any:
            base = self.base_layer(inputs)
            low_rank = torch.nn.functional.linear(self.dropout(inputs), self.lora_A)
            update = torch.nn.functional.linear(low_rank, self.lora_B)
            return base + update * self.scale

    rank, alpha, dropout = int(spec.get("lora_rank", 16)), int(spec.get("lora_alpha", 32)), float(spec.get("lora_dropout", 0.05))
    targets = set(spec["lora_target_modules"])
    candidates = [(name, layer) for name, layer in model.named_modules()
                  if name and isinstance(layer, torch.nn.Linear) and name.rsplit(".", 1)[-1] in targets]
    if not candidates:
        raise TrainingBlockedError("No torch.nn.Linear module matched training.lora_target_modules; inspect the local checkpoint architecture")
    matched_modules = [name for name, _ in candidates]
    for name, layer in candidates:
        parent_path, attribute = name.rsplit(".", 1) if "." in name else ("", name)
        parent = model.get_submodule(parent_path) if parent_path else model
        setattr(parent, attribute, _LocalLoRALinear(layer, rank, alpha, dropout))
    trainable = [parameter for parameter in model.parameters() if parameter.requires_grad]
    if not trainable:
        raise TrainingBlockedError("Local LoRA attachment yielded no trainable parameters")
    optimizer = torch.optim.AdamW(trainable, lr=float(spec.get("learning_rate", 2e-4)))
    batch_size, max_length, epochs = int(spec.get("batch_size", 1)), int(spec.get("max_length", 512)), int(spec.get("epochs", 1))
    losses: list[float] = []
    model.train()
    for _epoch in range(epochs):
        order = list(range(len(texts)))
        random.shuffle(order)
        for offset in range(0, len(order), batch_size):
            batch = [texts[index] for index in order[offset:offset + batch_size]]
            encoded = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=max_length)
            input_ids = encoded["input_ids"].to(device)
            attention_mask = encoded["attention_mask"].to(device)
            labels = input_ids.clone()
            labels[attention_mask == 0] = -100
            optimizer.zero_grad(set_to_none=True)
            result = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            result.loss.backward()
            torch.nn.utils.clip_grad_norm_(trainable, max_norm=float(spec.get("max_grad_norm", 1.0)))
            optimizer.step()
            losses.append(float(result.loss.detach().cpu()))
    output_dir.mkdir(parents=True, exist_ok=False)
    adapter_tensors = {name: parameter.detach().cpu() for name, parameter in model.named_parameters()
                       if ".lora_A" in name or ".lora_B" in name}
    if not adapter_tensors:
        raise TrainingBlockedError("No local LoRA tensors found after training")
    adapter_path = output_dir / "adapter_lora.pt"
    torch.save({"schema": "uca.local-lora.v1", "tensors": adapter_tensors}, adapter_path)
    tokenizer.save_pretrained(str(output_dir / "tokenizer_reference"))
    final = {
        "schema": "uca.lora-training-report.v1", "created_at": datetime.now(timezone.utc).isoformat(),
        "target": TARGET, "base_model_id": BASE_MODEL_ID,
        "base_checkpoint_fingerprint": report["base_checkpoint_fingerprint"],
        "dataset_sha256": report["dataset"]["sha256"], "records": len(texts), "epochs": epochs,
        "steps": len(losses), "loss_first": losses[0] if losses else None, "loss_last": losses[-1] if losses else None,
        "device": device, "adapter_only": True, "base_weights_merged": False,
        "adapter_format": "uca.local-lora.v1", "adapter_path": str(adapter_path),
        "matched_modules": matched_modules, "trainable_parameter_count": sum(parameter.numel() for parameter in trainable),
        "manifest_path": report["manifest_path"],
    }
    (output_dir / "uca_training_report.json").write_text(json.dumps(final, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    compatibility = {
        "technique": "lora", "base_model_id": BASE_MODEL_ID,
        "base_model_fingerprint": report["base_checkpoint_fingerprint"],
        "artifact_path": str(adapter_path), "validated": False,
        "adapter_format": "uca.local-lora.v1", "matched_modules": matched_modules,
        "note": "Training completed but runtime application remains disabled until compatibility/evaluation validation.",
    }
    (output_dir / "adapter_manifest.json").write_text(json.dumps(compatibility, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return final
