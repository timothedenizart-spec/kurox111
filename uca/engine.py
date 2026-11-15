"""Central sequential coordinator for the Unified Cognitive Architecture."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Iterable
from uuid import uuid4

from .auxiliary import AuxiliaryRegistry
from .modules import CognitiveModule
from .resource import ResourcePolicy
from .storage import RunStore
from .types import CognitiveContext, ModuleReport, ModuleStatus


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


class UnifiedCognitiveEngine:
    """One owner of request context, module ordering, results, and degradation.

    Modules get snapshots and return `ModuleResult`; only this class mutates the
    central context. This is the key coordination boundary that prevents an
    unavailable module from corrupting or replacing previous evidence.
    """
    def __init__(self, modules: Iterable[CognitiveModule], pipeline: list[str], *,
                 resource_mode: str = "sequential_unload", default_timeout: float = 45,
                 max_corrections: int = 1, run_history_limit: int = 30,
                 auxiliary: AuxiliaryRegistry | None = None,
                 cognitive_settings: dict[str, Any] | None = None) -> None:
        module_list = list(modules)
        self.modules = {module.module_id: module for module in module_list}
        if len(self.modules) != len(module_list):
            raise ValueError("Module IDs must be unique")
        self.pipeline = list(pipeline)
        self.default_timeout = default_timeout
        self.max_corrections = max(0, max_corrections)
        self.resource_policy = ResourcePolicy(resource_mode)
        self.run_store = RunStore(run_history_limit)
        self.auxiliary = auxiliary
        self.cognitive_settings = dict(cognitive_settings or {})
        self.validate_pipeline(self.pipeline)

    def validate_pipeline(self, proposed: list[str]) -> None:
        if len(proposed) != len(set(proposed)):
            raise ValueError("Pipeline cannot contain a module more than once")
        missing = [module_id for module_id in proposed if module_id not in self.modules]
        if missing:
            raise ValueError(f"Pipeline names unknown module(s): {', '.join(missing)}")
        positions = {module_id: index for index, module_id in enumerate(proposed)}
        for module_id in proposed:
            for dependency in self.modules[module_id].dependencies:
                if dependency in positions and positions[dependency] > positions[module_id]:
                    raise ValueError(f"{module_id} cannot precede dependency {dependency}")

    def set_pipeline(self, proposed: list[str]) -> None:
        self.validate_pipeline(proposed)
        self.pipeline = list(proposed)

    def set_module_enabled(self, module_id: str, enabled: bool) -> None:
        if module_id not in self.modules:
            raise KeyError(module_id)
        self.modules[module_id].enabled = bool(enabled)

    def set_auxiliary_enabled(self, module_id: str, enabled: bool) -> None:
        if not self.auxiliary:
            raise KeyError(module_id)
        self.auxiliary.set_enabled(module_id, enabled)

    @staticmethod
    def _state(capability_status: ModuleStatus, reason: str, details: dict[str, Any] | None = None,
               execution: str = "not_run") -> dict[str, Any]:
        return {"status": capability_status.value, "reason": reason, "details": details or {},
                "execution": execution}

    def status(self) -> dict[str, Any]:
        module_status = {}
        for module_id, module in self.modules.items():
            capability = module.capability()
            module_status[module_id] = self._state(capability.status, capability.reason, capability.details)
        return {
            "pipeline": self.pipeline,
            "resource_mode": self.resource_policy.mode,
            "resource_notes": self.resource_policy.notes(),
            "cognitive_control": {"status": "functional", "settings": self.cognitive_settings,
                                  "scope": "bounded attention, evidence graph, metacognitive coverage, and exact arithmetic"},
            "modules": module_status,
            "auxiliary": self.auxiliary.status() if self.auxiliary else {},
        }

    def _record(self, context: CognitiveContext, module_id: str, status: ModuleStatus,
                started: str, started_clock: float, message: str = "", error: str | None = None,
                outputs: tuple[str, ...] = (), attempt: int = 1) -> None:
        ended = timestamp()
        duration = (perf_counter() - started_clock) * 1000
        context.execution_history.append(ModuleReport(module_id, status, started, ended, duration,
                                                      message, error, outputs, attempt))

    def _execute(self, context: CognitiveContext, module_id: str, attempt: int = 1) -> dict[str, Any]:
        module = self.modules[module_id]
        started, clock = timestamp(), perf_counter()
        capability = module.capability()
        context.module_states[module_id] = self._state(capability.status, capability.reason, capability.details)
        if capability.status is not ModuleStatus.FUNCTIONAL:
            self._record(context, module_id, capability.status, started, clock, capability.reason, attempt=attempt)
            context.module_states[module_id]["execution"] = "not_run"
            return {"executed": False, "metadata": {}}
        absent = [dep for dep in module.dependencies if dep not in self.modules]
        if absent:
            reason = f"Unknown dependency: {', '.join(absent)}"
            context.module_states[module_id] = self._state(ModuleStatus.FAILED, reason, execution="skipped")
            self._record(context, module_id, ModuleStatus.FAILED, started, clock, reason, attempt=attempt)
            return {"executed": False, "metadata": {}}
        allowed, reason = module.can_run(context)
        if not allowed:
            context.module_states[module_id] = self._state(ModuleStatus.SKIPPED, reason, execution="skipped")
            self._record(context, module_id, ModuleStatus.SKIPPED, started, clock, reason, attempt=attempt)
            return {"executed": False, "metadata": {}}
        timeout = module.timeout_seconds or self.default_timeout
        worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix=f"uca-{module_id}")
        future = worker.submit(module.run, context.snapshot())
        try:
            result = future.result(timeout=timeout)
        except FutureTimeout:
            # Python cannot safely kill a running arbitrary thread. It has only a snapshot,
            # so a late result cannot mutate central context; record a bounded soft timeout.
            future.cancel()
            worker.shutdown(wait=False, cancel_futures=True)
            message = f"Soft timeout after {timeout}s; module result was isolated and ignored"
            context.module_states[module_id] = self._state(ModuleStatus.FAILED, message, execution="timed_out")
            self._record(context, module_id, ModuleStatus.FAILED, started, clock, message, message, attempt=attempt)
            return {"executed": False, "metadata": {}}
        except Exception as error:  # module error must not terminate the architecture
            worker.shutdown(wait=False, cancel_futures=True)
            message = f"{type(error).__name__}: {str(error)[:700]}"
            context.module_states[module_id] = self._state(ModuleStatus.FAILED, message, execution="failed")
            self._record(context, module_id, ModuleStatus.FAILED, started, clock, "Module execution failed", message, attempt=attempt)
            return {"executed": False, "metadata": {}}
        else:
            worker.shutdown(wait=True, cancel_futures=False)
        for produced in result.artifacts:
            context.add_artifact(produced)
        # Central engine alone applies recognized contextual metadata.
        normalized = result.metadata.get("normalized_text")
        if isinstance(normalized, str):
            context.normalized_text = normalized
        query_type = result.metadata.get("query_type")
        if isinstance(query_type, str):
            context.query_type = query_type
        context.module_states[module_id] = self._state(ModuleStatus.FUNCTIONAL, capability.reason,
                                                        capability.details, execution="completed")
        output_ids = tuple(item.id for item in result.artifacts)
        note = result.message + (" Warnings: " + " | ".join(result.warnings) if result.warnings else "")
        self._record(context, module_id, ModuleStatus.COMPLETED, started, clock, note, outputs=output_ids, attempt=attempt)
        self.resource_policy.after_step(module)
        return {"executed": True, "metadata": dict(result.metadata)}

    def process(self, user_text: str) -> CognitiveContext:
        if not isinstance(user_text, str) or not user_text.strip():
            raise ValueError("A non-empty user message is required")
        context = CognitiveContext(request_id=str(uuid4()), user_text=user_text)
        corrections = 0
        for module_id in self.pipeline:
            execution = self._execute(context, module_id)
            # A correction is inserted immediately after verification, before final
            # composition. The limit prevents verifier/model feedback loops.
            if (module_id == "final_verification" and execution["metadata"].get("correction_required") is True
                    and corrections < self.max_corrections and "smollm2_360_review" in self.modules):
                corrections += 1
                self._execute(context, "smollm2_360_review", attempt=2)
                if "global_workspace" in self.modules:
                    self._execute(context, "global_workspace", attempt=2)
                self._execute(context, "final_verification", attempt=2)
        if not context.final_response:
            context.final_response = ("UCA could not run its final response module. Consult the execution trace for "
                                      "module availability and failure details.")
        self.run_store.put(context.request_id, context.to_dict(developer=True))
        return context
