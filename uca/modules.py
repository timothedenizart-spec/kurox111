"""Normalized module contract for the Unified Cognitive Engine."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Iterable

from .types import CognitiveContext, ModuleResult, ModuleStatus


@dataclass(frozen=True)
class Capability:
    status: ModuleStatus
    reason: str = ""
    details: dict[str, Any] = field(default_factory=dict)


class CognitiveModule(ABC):
    """All modules consume a snapshot and return append-only results.

    Implementations must not mutate the `CognitiveContext` received at engine
    construction or retain request-specific state. This permits the engine to
    preserve results when a model is unloaded or a later module fails.
    """
    module_id: str
    dependencies: tuple[str, ...] = ()
    timeout_seconds: float | None = None
    # Only pure read-only modules should set this. The engine still applies a
    # stage barrier and canonical merge order after concurrent execution.
    parallel_safe: bool = False

    def __init__(self, module_id: str, *, enabled: bool = True,
                 dependencies: Iterable[str] = (), timeout_seconds: float | None = None,
                 parallel_safe: bool = False) -> None:
        self.module_id = module_id
        self.enabled = enabled
        self.dependencies = tuple(dependencies)
        self.timeout_seconds = timeout_seconds
        self.parallel_safe = parallel_safe

    def capability(self) -> Capability:
        if not self.enabled:
            return Capability(ModuleStatus.DISABLED, "Disabled voluntarily by local configuration")
        return Capability(ModuleStatus.FUNCTIONAL, "Ready")

    def can_run(self, context: CognitiveContext) -> tuple[bool, str]:
        capability = self.capability()
        if capability.status is not ModuleStatus.FUNCTIONAL:
            return False, capability.reason
        return True, ""

    @abstractmethod
    def run(self, snapshot: dict[str, Any]) -> ModuleResult:
        raise NotImplementedError

    def unload(self) -> None:
        """Release optional model resources. Non-model modules are no-ops."""


class AuxiliaryModule(CognitiveModule):
    """Marker base for administrable but not pipeline-default experimental tools."""
