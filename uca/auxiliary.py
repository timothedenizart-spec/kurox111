"""Administration gates for experimental techniques not allowed to masquerade as active."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import hashlib
import json

from .modules import Capability
from .types import ModuleStatus


@dataclass(frozen=True)
class CompatibilityManifest:
    technique: str
    base_model_id: str
    base_model_fingerprint: str
    artifact_path: str
    validated: bool = False


class AuxiliaryRegistry:
    """Keeps optional techniques visible and guarded without simulating execution."""
    SMOL360_ID = "SmolLM2-360M-Instruct"

    def __init__(self, config: dict[str, Any], root: Path) -> None:
        self.config = config
        self.root = root
        self.manifests: dict[str, CompatibilityManifest] = {}

    def register_manifest(self, manifest_path: str | Path) -> CompatibilityManifest:
        path = Path(manifest_path)
        parsed = json.loads(path.read_text(encoding="utf-8"))
        manifest = CompatibilityManifest(
            technique=str(parsed["technique"]), base_model_id=str(parsed["base_model_id"]),
            base_model_fingerprint=str(parsed["base_model_fingerprint"]), artifact_path=str(parsed["artifact_path"]),
            validated=bool(parsed.get("validated", False)),
        )
        self.manifests[manifest.technique] = manifest
        return manifest

    @staticmethod
    def checkpoint_fingerprint(path: str | Path) -> str:
        """Cheap local fingerprint for an operator-supplied base checkpoint manifest."""
        candidate = Path(path)
        digest = hashlib.sha256()
        if candidate.is_file():
            digest.update(candidate.name.encode())
            digest.update(str(candidate.stat().st_size).encode())
            digest.update(str(candidate.stat().st_mtime_ns).encode())
        elif candidate.is_dir():
            for child in sorted(candidate.rglob("*")):
                if child.is_file():
                    digest.update(str(child.relative_to(candidate)).encode())
                    digest.update(str(child.stat().st_size).encode())
        else:
            raise FileNotFoundError(candidate)
        return digest.hexdigest()

    def capability(self, name: str) -> Capability:
        spec = self.config.get(name, {})
        if not spec.get("enabled", False):
            return Capability(ModuleStatus.DISABLED, "Disabled voluntarily by configuration")
        if name in {"lora", "ties", "dare"}:
            manifest = self.manifests.get(name)
            if not manifest:
                return Capability(ModuleStatus.NON_VALIDATED,
                                  "No compatibility manifest registered for SmolLM2-360M-Instruct")
            if manifest.base_model_id != self.SMOL360_ID or not manifest.validated:
                return Capability(ModuleStatus.NON_VALIDATED,
                                  "Adapter manifest does not validate the exact SmolLM2-360M base")
            artifact = Path(manifest.artifact_path)
            if not artifact.exists():
                return Capability(ModuleStatus.UNAVAILABLE, f"Adapter artifact missing: {artifact}")
            return Capability(ModuleStatus.NON_VALIDATED,
                              "Compatible manifest exists, but no safe weight-application backend is implemented")
        if name == "aoe":
            return Capability(ModuleStatus.NON_VALIDATED,
                              "AoE is gated pending a real set of shape-compatible MoE tensors")
        if name == "fla":
            return Capability(ModuleStatus.NON_VALIDATED,
                              "FLA integration awaits local dependency and checkpoint validation")
        if name == "e2e":
            return Capability(ModuleStatus.NON_VALIDATED,
                              "E2E/JAX scorer awaits dependency, checkpoint and scoring-contract validation")
        if name == "scallop":
            return Capability(ModuleStatus.UNAVAILABLE,
                              "Scallop has a future integration interface but is not bundled or assumed available")
        return Capability(ModuleStatus.UNAVAILABLE, "Unknown auxiliary module")

    def set_enabled(self, name: str, enabled: bool) -> None:
        if name not in self.config:
            raise KeyError(name)
        self.config[name]["enabled"] = bool(enabled)

    def status(self) -> dict[str, dict[str, Any]]:
        return {name: {"status": capability.status.value, "reason": capability.reason, "details": capability.details}
                for name in self.config for capability in (self.capability(name),)}


class AoeShapeGate:
    """Validates real MoE tensor metadata before any assembly is allowed."""
    @staticmethod
    def compatible(expert_specs: list[dict[str, Any]]) -> tuple[bool, str]:
        if len(expert_specs) < 2:
            return False, "At least two real experts are required"
        shapes = {tuple(item.get("shape", [])) for item in expert_specs}
        dtypes = {item.get("dtype") for item in expert_specs}
        architectures = {item.get("architecture") for item in expert_specs}
        if len(shapes) != 1 or len(dtypes) != 1 or len(architectures) != 1:
            return False, "Experts differ in tensor shape, dtype, or architecture"
        return True, "Metadata is compatible; actual assembly still requires a validated backend"
