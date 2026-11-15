"""Central staged coordinator for the Unified Cognitive Architecture."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from dataclasses import dataclass
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Iterable
from uuid import uuid4

from .auxiliary import AuxiliaryRegistry
from .modules import CognitiveModule
from .resource import ResourcePolicy
from .storage import RunStore
from .types import (Artifact, ArtifactKind, CognitiveContext, ModuleReport, ModuleResult,
                    ModuleStatus, Provenance)


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class _PreparedExecution:
    module_id: str
    module: CognitiveModule
    capability_reason: str
    capability_details: dict[str, Any]
    snapshot: dict[str, Any]
    timeout: float
    started_at: str
    started_clock: float
    attempt: int


@dataclass(frozen=True)
class _Invocation:
    result: ModuleResult | None = None
    failure_status: ModuleStatus | None = None
    message: str = ""


class UnifiedCognitiveEngine:
    """One owner of request context, ordering, stage barriers, and degradation.

    The engine supports a fully sequential topology. ``staged_parallel`` adds a bounded
    *afferent evidence field*: explicit-memory lookup, FTS retrieval and
    symbolic lookup consume the same post-input snapshot concurrently, then the
    engine merges their immutable results in canonical pipeline order. Every
    later deliberative/model stage remains ordered. This gives safe parallelism
    without tensor/tokenizer sharing or non-deterministic context mutation.
    """
    _PARALLEL_AFFERENT_IDS = frozenset({"user_memory", "knowledge_retrieval", "symbolic_processing"})
    _SCHEDULING_MODES = frozenset({"sequential", "staged_parallel"})

    def __init__(self, modules: Iterable[CognitiveModule], pipeline: list[str], *,
                 resource_mode: str = "sequential_unload", default_timeout: float = 45,
                 max_corrections: int = 1, run_history_limit: int = 30,
                 auxiliary: AuxiliaryRegistry | None = None,
                 cognitive_settings: dict[str, Any] | None = None,
                 scheduling_mode: str = "sequential", parallel_max_workers: int = 3) -> None:
        module_list = list(modules)
        self.modules = {module.module_id: module for module in module_list}
        if len(self.modules) != len(module_list):
            raise ValueError("Module IDs must be unique")
        if scheduling_mode not in self._SCHEDULING_MODES:
            raise ValueError(f"Unknown scheduling mode: {scheduling_mode}")
        self.pipeline = list(pipeline)
        self.default_timeout = default_timeout
        self.max_corrections = max(0, max_corrections)
        self.resource_policy = ResourcePolicy(resource_mode)
        self.run_store = RunStore(run_history_limit)
        self.auxiliary = auxiliary
        self.cognitive_settings = dict(cognitive_settings or {})
        self.scheduling_mode = scheduling_mode
        self.parallel_max_workers = max(1, min(int(parallel_max_workers), 8))
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
            "execution_topology": {
                "mode": self.scheduling_mode,
                "parallel_max_workers": self.parallel_max_workers,
                "parallel_stage": [module_id for module_id in self.pipeline
                                   if module_id in self._PARALLEL_AFFERENT_IDS and self.modules[module_id].parallel_safe],
                "guarantee": "Parallel results are merged in canonical pipeline order at a stage barrier.",
            },
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

    def _prepare(self, context: CognitiveContext, module_id: str, attempt: int,
                 snapshot: dict[str, Any] | None = None) -> _PreparedExecution | None:
        """Validate one execution on the coordinator thread before it can fan out."""
        module = self.modules[module_id]
        started, clock = timestamp(), perf_counter()
        capability = module.capability()
        context.module_states[module_id] = self._state(capability.status, capability.reason, capability.details)
        if capability.status is not ModuleStatus.FUNCTIONAL:
            self._record(context, module_id, capability.status, started, clock, capability.reason, attempt=attempt)
            context.module_states[module_id]["execution"] = "not_run"
            return None
        absent = [dep for dep in module.dependencies if dep not in self.modules]
        if absent:
            reason = f"Unknown dependency: {', '.join(absent)}"
            context.module_states[module_id] = self._state(ModuleStatus.FAILED, reason, execution="skipped")
            self._record(context, module_id, ModuleStatus.FAILED, started, clock, reason, attempt=attempt)
            return None
        allowed, reason = module.can_run(context)
        if not allowed:
            context.module_states[module_id] = self._state(ModuleStatus.SKIPPED, reason, execution="skipped")
            self._record(context, module_id, ModuleStatus.SKIPPED, started, clock, reason, attempt=attempt)
            return None
        context.module_states[module_id]["execution"] = "running"
        return _PreparedExecution(
            module_id=module_id, module=module, capability_reason=capability.reason,
            capability_details=capability.details, snapshot=snapshot if snapshot is not None else context.snapshot(),
            timeout=module.timeout_seconds or self.default_timeout, started_at=started,
            started_clock=clock, attempt=attempt,
        )

    @staticmethod
    def _invoke(prepared: _PreparedExecution) -> _Invocation:
        """Run pure module code in isolation; it has no mutable central context."""
        worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix=f"uca-{prepared.module_id}")
        future = worker.submit(prepared.module.run, prepared.snapshot)
        try:
            result = future.result(timeout=prepared.timeout)
        except FutureTimeout:
            # Arbitrary Python threads cannot safely be killed. Late results hold an
            # immutable snapshot and are discarded, so they cannot contaminate UCA.
            future.cancel()
            worker.shutdown(wait=False, cancel_futures=True)
            return _Invocation(failure_status=ModuleStatus.FAILED,
                               message=f"Soft timeout after {prepared.timeout}s; isolated result ignored")
        except Exception as error:  # one specialist must not stop the architecture
            worker.shutdown(wait=False, cancel_futures=True)
            return _Invocation(failure_status=ModuleStatus.FAILED,
                               message=f"{type(error).__name__}: {str(error)[:700]}")
        else:
            worker.shutdown(wait=True, cancel_futures=False)
            return _Invocation(result=result)

    def _finish(self, context: CognitiveContext, prepared: _PreparedExecution, invocation: _Invocation) -> dict[str, Any]:
        """Merge an isolated outcome. This is always executed by the coordinator."""
        if invocation.failure_status is not None or invocation.result is None:
            message = invocation.message or "Module execution failed"
            context.module_states[prepared.module_id] = self._state(ModuleStatus.FAILED, message, execution="failed")
            self._record(context, prepared.module_id, ModuleStatus.FAILED, prepared.started_at,
                         prepared.started_clock, "Module execution failed", message, attempt=prepared.attempt)
            return {"executed": False, "metadata": {}}
        result = invocation.result
        for produced in result.artifacts:
            context.add_artifact(produced)
        # Central engine alone applies recognized contextual metadata.
        normalized = result.metadata.get("normalized_text")
        if isinstance(normalized, str):
            context.normalized_text = normalized
        query_type = result.metadata.get("query_type")
        if isinstance(query_type, str):
            context.query_type = query_type
        context.module_states[prepared.module_id] = self._state(ModuleStatus.FUNCTIONAL, prepared.capability_reason,
                                                                 prepared.capability_details, execution="completed")
        output_ids = tuple(item.id for item in result.artifacts)
        note = result.message + (" Warnings: " + " | ".join(result.warnings) if result.warnings else "")
        self._record(context, prepared.module_id, ModuleStatus.COMPLETED, prepared.started_at,
                     prepared.started_clock, note, outputs=output_ids, attempt=prepared.attempt)
        self.resource_policy.after_step(prepared.module)
        return {"executed": True, "metadata": dict(result.metadata)}

    def _execute(self, context: CognitiveContext, module_id: str, attempt: int = 1) -> dict[str, Any]:
        prepared = self._prepare(context, module_id, attempt)
        if prepared is None:
            return {"executed": False, "metadata": {}}
        return self._finish(context, prepared, self._invoke(prepared))

    def _execute_parallel(self, context: CognitiveContext, module_ids: list[str], attempt: int = 1) -> dict[str, dict[str, Any]]:
        """Execute independent afferent modules from one snapshot, then merge stably."""
        shared_snapshot = context.snapshot()
        prepared = [item for module_id in module_ids
                    if (item := self._prepare(context, module_id, attempt, shared_snapshot)) is not None]
        outcomes: dict[str, _Invocation] = {}
        if len(prepared) > 1:
            with ThreadPoolExecutor(max_workers=min(self.parallel_max_workers, len(prepared)),
                                    thread_name_prefix="uca-afferent") as pool:
                futures = {item.module_id: pool.submit(self._invoke, item) for item in prepared}
                # Await and merge in configured order, never completion order.
                for item in prepared:
                    outcomes[item.module_id] = futures[item.module_id].result()
        elif prepared:
            outcomes[prepared[0].module_id] = self._invoke(prepared[0])
        merged: dict[str, dict[str, Any]] = {}
        for item in prepared:
            merged[item.module_id] = self._finish(context, item, outcomes[item.module_id])
        # The trace states exactly which stage shared a snapshot and how results
        # were ordered. It carries no substantive evidence.
        context.add_artifact(Artifact(
            kind=ArtifactKind.DIAGNOSTIC,
            content={"event": "parallel_afferent_fanout", "modules": module_ids,
                     "executed_modules": [item.module_id for item in prepared],
                     "merge_order": [item.module_id for item in prepared],
                     "snapshot_boundary": "post_input_pre_evidence",
                     "invariant": "Concurrent modules did not observe one another's output; the coordinator merged immutable results canonically."},
            provenance=Provenance(producer="unified_cognitive_engine",
                                  implementation="bounded staged-parallel scheduler"),
            uncertainty=("Parallel scheduling reduces latency only; it does not increase evidential authority.",),
        ))
        return merged

    def _parallel_group_at(self, start: int) -> list[str]:
        if self.scheduling_mode != "staged_parallel":
            return []
        group: list[str] = []
        for module_id in self.pipeline[start:]:
            module = self.modules[module_id]
            if module_id not in self._PARALLEL_AFFERENT_IDS or not module.parallel_safe:
                break
            group.append(module_id)
        return group if len(group) > 1 else []

    def process(self, user_text: str) -> CognitiveContext:
        if not isinstance(user_text, str) or not user_text.strip():
            raise ValueError("A non-empty user message is required")
        context = CognitiveContext(request_id=str(uuid4()), user_text=user_text)
        context.available_context["execution_topology"] = {
            "mode": self.scheduling_mode, "parallel_max_workers": self.parallel_max_workers,
            "parallelism_scope": "independent afferent evidence only; deliberative/model stages remain ordered",
        }
        corrections = 0
        index = 0
        while index < len(self.pipeline):
            group = self._parallel_group_at(index)
            if group:
                executions = self._execute_parallel(context, group)
                index += len(group)
            else:
                module_id = self.pipeline[index]
                executions = {module_id: self._execute(context, module_id)}
                index += 1
            # A correction is inserted immediately after verification, before final
            # composition. The limit prevents verifier/model feedback loops.
            verification = executions.get("final_verification")
            if (verification and verification["metadata"].get("correction_required") is True
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
