"""Local-only adapters for heterogeneous neural systems.

No adapter hands token IDs, embeddings, or tensors to a different model. The
shared medium is decoded text plus typed UCA artifacts.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import shlex
import subprocess

from .config import local_path
from .modules import Capability
from .types import ModuleStatus


def invoke_json_runner(command: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    """Run a local integration shim using one JSON object on stdin/stdout.

    This deliberately avoids `shell=True`. The executable is an operator-owned
    shim around an actual experimental model; UCA does not assume a checkpoint
    architecture it has not inspected.
    """
    if not command.strip():
        raise RuntimeError("No local runner command configured")
    completed = subprocess.run(
        shlex.split(command), input=json.dumps(payload), text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"Runner exited {completed.returncode}: {completed.stderr.strip()[:500]}")
    try:
        response = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"Runner did not return one JSON object: {error}") from error
    if not isinstance(response, dict):
        raise RuntimeError("Runner response must be a JSON object")
    return response


class LocalCausalGenerator:
    """Lazy local Transformers adapter used only for SmolLM2 causal models."""
    def __init__(self, config: dict[str, Any], root_config: dict[str, Any], label: str) -> None:
        self.config = config
        self.root_config = root_config
        self.label = label
        self._tokenizer: Any = None
        self._model: Any = None

    @property
    def path(self) -> Path | None:
        raw = str(self.config.get("path", "")).strip()
        return local_path(self.root_config, raw) if raw else None

    def capability(self) -> Capability:
        model_path = self.path
        if not model_path:
            return Capability(ModuleStatus.UNAVAILABLE, f"No local checkpoint path configured for {self.label}")
        if not model_path.exists():
            return Capability(ModuleStatus.UNAVAILABLE, f"Checkpoint path does not exist: {model_path}")
        try:
            import transformers  # noqa: F401 # type: ignore
            import torch  # noqa: F401 # type: ignore
        except ImportError:
            return Capability(ModuleStatus.UNAVAILABLE,
                              "Install optional local model dependencies: pip install -e '.[models]'")
        return Capability(ModuleStatus.FUNCTIONAL,
                          "Local checkpoint and Transformers runtime detected; lazy load pending")

    def _load(self) -> None:
        if self._model is not None:
            return
        from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore
        self._tokenizer = AutoTokenizer.from_pretrained(str(self.path), local_files_only=True)
        self._model = AutoModelForCausalLM.from_pretrained(str(self.path), local_files_only=True)
        self._model.eval()
        device = str(self.config.get("device", "auto"))
        if device not in ("", "auto"):
            self._model.to(device)

    def generate(self, prompt: str) -> str:
        check = self.capability()
        if check.status is not ModuleStatus.FUNCTIONAL:
            raise RuntimeError(check.reason)
        self._load()
        import torch  # type: ignore
        encoded = self._tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4096)
        try:
            device = next(self._model.parameters()).device
            encoded = {name: value.to(device) for name, value in encoded.items()}
        except StopIteration:
            pass
        pad_id = self._tokenizer.pad_token_id
        if pad_id is None:
            pad_id = self._tokenizer.eos_token_id
        with torch.inference_mode():
            output = self._model.generate(
                **encoded,
                max_new_tokens=int(self.config.get("max_new_tokens", 280)),
                do_sample=False,
                pad_token_id=pad_id,
            )
        input_count = int(encoded["input_ids"].shape[-1])
        generated = output[0][input_count:]
        return self._tokenizer.decode(generated, skip_special_tokens=True).strip()

    def unload(self) -> None:
        self._model = None
        self._tokenizer = None


class ExternalNcmAdapter:
    """Validated runner contract for the unknown NCM LM1B/VQ architecture."""
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    def capability(self) -> Capability:
        if not self.config.get("validated", False):
            return Capability(ModuleStatus.NON_VALIDATED,
                              "NCM runner/checkpoint interface has not been validated")
        if not str(self.config.get("runner_command", "")).strip():
            return Capability(ModuleStatus.UNAVAILABLE, "No local NCM runner configured")
        return Capability(ModuleStatus.FUNCTIONAL, "Validated local NCM runner configured")

    def concepts(self, query: str, context: dict[str, Any], timeout: float) -> list[dict[str, Any]]:
        result = invoke_json_runner(str(self.config["runner_command"]), {
            "operation": "concept_generation", "query": query, "context": context,
            "contract_version": 1,
        }, timeout)
        proposals = result.get("proposals", [])
        if not isinstance(proposals, list):
            raise RuntimeError("NCM runner field 'proposals' must be a list")
        clean: list[dict[str, Any]] = []
        for proposal in proposals[:12]:
            if isinstance(proposal, str) and proposal.strip():
                clean.append({"text": proposal.strip()})
            elif isinstance(proposal, dict) and isinstance(proposal.get("text"), str):
                clean.append({"text": proposal["text"].strip(), "runner_metadata": proposal.get("metadata", {})})
        return clean

    def refine_response(self, query: str, reflection: dict[str, Any],
                        computations: list[dict[str, Any]],
                        analyses: list[dict[str, Any]],
                        documents: list[dict[str, Any]],
                        facts: list[dict[str, Any]],
                        proposals: list[dict[str, Any]],
                        timeout: float = 45.0) -> dict[str, Any] | None:
        if self.capability().status != ModuleStatus.FUNCTIONAL:
            return None
        try:
            result = invoke_json_runner(str(self.config["runner_command"]), {
                "operation": "response_refinement",
                "query": query,
                "reflection": reflection,
                "computations": computations,
                "analyses": analyses,
                "documents": documents,
                "facts": facts,
                "proposals": proposals,
                "contract_version": 1,
            }, timeout)
            if isinstance(result, dict) and result.get("status") == "success":
                return result
        except Exception:
            return None
        return None


class MaskedNanoDiffAdapter:
    """Adapter for a masked denoiser, explicitly *not* a causal LM adapter.

    The expected local runner receives tokenizer-native IDs and a set of masked
    positions, then returns replacement IDs. It must never be called through
    `generate()` or interpreted as an autoregressive continuation.
    """
    def __init__(self, config: dict[str, Any], root_config: dict[str, Any]) -> None:
        self.config = config
        self.root_config = root_config
        self._tokenizer: Any = None

    def _base_capability(self, require_validated: bool) -> Capability:
        if require_validated and not self.config.get("validated", False):
            return Capability(ModuleStatus.NON_VALIDATED,
                              "nanoDiff is held until masked-denoiser calibration validates an improvement")
        if not str(self.config.get("runner_command", "")).strip():
            return Capability(ModuleStatus.UNAVAILABLE, "No nanoDiff masked-denoiser runner configured")
        raw = str(self.config.get("tokenizer_path") or self.config.get("path") or "").strip()
        if not raw:
            return Capability(ModuleStatus.UNAVAILABLE, "nanoDiff tokenizer path is required")
        tokenizer_path = local_path(self.root_config, raw)
        if not tokenizer_path.exists():
            return Capability(ModuleStatus.UNAVAILABLE, f"nanoDiff tokenizer path does not exist: {tokenizer_path}")
        if int(self.config.get("mask_token_id", -1)) < 0:
            return Capability(ModuleStatus.NON_VALIDATED,
                              "A concrete nanoDiff mask_token_id is required; GPT-2 has no implicit mask token")
        try:
            import transformers  # noqa: F401 # type: ignore
        except ImportError:
            return Capability(ModuleStatus.UNAVAILABLE, "Transformers is required only to use the local nanoDiff tokenizer")
        return Capability(ModuleStatus.FUNCTIONAL,
                          "Validated masked-denoiser contract configured" if require_validated else
                          "Masked-denoiser contract is available for calibration only")

    def capability(self) -> Capability:
        return self._base_capability(require_validated=True)

    def calibration_capability(self) -> Capability:
        """Checks whether an unvalidated adapter can be evaluated, not activated."""
        return self._base_capability(require_validated=False)

    def _tokenizer_for_nano(self) -> Any:
        if self._tokenizer is None:
            from transformers import AutoTokenizer  # type: ignore
            raw = str(self.config.get("tokenizer_path") or self.config.get("path"))
            self._tokenizer = AutoTokenizer.from_pretrained(
                str(local_path(self.root_config, raw)), local_files_only=True
            )
        return self._tokenizer

    @staticmethod
    def _mask_positions(ids: list[int], strategy: str) -> list[int]:
        if len(ids) < 5:
            return []
        stride = 7 if strategy == "single_pass" else 11
        # Preserve first/last tokens to keep an anchored denoising request.
        return list(range(2, max(2, len(ids) - 2), stride))[:64]

    def denoise(self, text: str, strategy: str, timeout: float, *, calibration: bool = False) -> dict[str, Any]:
        check = self.calibration_capability() if calibration else self.capability()
        if check.status is not ModuleStatus.FUNCTIONAL:
            raise RuntimeError(check.reason)
        tokenizer = self._tokenizer_for_nano()
        token_ids = list(tokenizer.encode(text, add_special_tokens=False))
        positions = self._mask_positions(token_ids, strategy)
        if not positions:
            return {"candidate_text": text, "changed": False, "strategy": strategy,
                    "reason": "Input too short for safe masked denoising"}
        masked = list(token_ids)
        mask_id = int(self.config["mask_token_id"])
        for position in positions:
            masked[position] = mask_id
        response = invoke_json_runner(str(self.config["runner_command"]), {
            "operation": "masked_denoise", "architecture": "nanodiff_masked_denoiser",
            "strategy": strategy, "token_ids": token_ids, "masked_token_ids": masked,
            "mask_positions": positions, "mask_token_id": mask_id, "contract_version": 1,
        }, timeout)
        candidate_ids = response.get("candidate_token_ids")
        if not isinstance(candidate_ids, list) or not all(isinstance(value, int) for value in candidate_ids):
            raise RuntimeError("nanoDiff runner must return integer candidate_token_ids")
        candidate = tokenizer.decode(candidate_ids, skip_special_tokens=True).strip()
        return {"candidate_text": candidate, "changed": candidate != text, "strategy": strategy,
                "runner_score": response.get("candidate_score"),
                "calibration_id": response.get("calibration_id")}

    def unload(self) -> None:
        self._tokenizer = None
