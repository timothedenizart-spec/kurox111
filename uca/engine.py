"""Central coordinator for the Unified Cognitive Architecture.

Two execution modes:

- ``sequential`` (historical): modules run one after another; each sees every
  earlier artifact.
- ``parallel_levels`` (default here): the declared dependency graph is cut into
  topological levels (Kahn's algorithm over the pipeline order). Independent
  modules inside a level run *concurrently* on one shared immutable snapshot,
  then their results are applied in canonical pipeline order. This keeps the
  append-only ledger deterministic — identical inputs produce identical
  artifact sequences — while real parallelism shortens wall time whenever
  heavyweight local models are present.

Correction passes and dependency validation are unchanged. Modules may only
rely on artifacts produced by their *declared* dependencies; the pipeline
declares them accordingly.
"""
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
from .types import CognitiveContext, ModuleReport, ModuleResult, ModuleStatus


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


EXECUTION_MODES = ("sequential", "parallel_levels")


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
                 cognitive_settings: dict[str, Any] | None = None,
                 execution_mode: str = "sequential") -> None:
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
        if execution_mode not in EXECUTION_MODES:
            raise ValueError(f"Unknown execution mode: {execution_mode}")
        self.execution_mode = execution_mode
        self.validate_pipeline(self.pipeline)
        self._levels = self._level_schedule(self.pipeline) if execution_mode == "parallel_levels" else []

    # ------------------------------------------------------------------ order
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
        if self.execution_mode == "parallel_levels":
            self._levels = self._level_schedule(self.pipeline)

    def _level_schedule(self, proposed: list[str]) -> list[list[str]]:
        """Greedy *contiguous* topological levels over the pipeline order.

        Modules accumulate into the current level while every declared
        dependency is already placed in an earlier level; the first module that
        is not ready closes the level. Flattening the result reproduces the
        pipeline order exactly, so parallel execution never changes the
        observable ledger order — it only shortens wall-clock time. This is a
        dataflow scheduler in the sense of Kahn, restricted to a document
        order: determinism is a hard invariant, not an aspiration.
        """
        levels: list[list[str]] = []
        placed: set[str] = set()
        current: list[str] = []
        for module_id in proposed:
            ready = all(dep in placed or dep not in self.modules
                        for dep in self.modules[module_id].dependencies)
            if ready:
                current.append(module_id)
            else:
                if current:
                    levels.append(current)
                    placed.update(current)
                current = [module_id]
        if current:
            levels.append(current)
        return levels

    @property
    def levels(self) -> list[list[str]]:
        if self.execution_mode != "parallel_levels":
            return [[module_id] for module_id in self.pipeline]
        return [list(level) for level in self._levels]

    # ----------------------------------------------------------------- states
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
            "execution_mode": self.execution_mode,
            "parallel_levels": [[*level] for level in self._levels] if self._levels else [],
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

    # ----------------------------------------------------------- single steps
    def _precheck(self, context: CognitiveContext, module_id: str,
                  started: str, clock: float, attempt: int) -> tuple[CognitiveModule, Any, bool, dict[str, Any] | None]:
        """Capability / dependency / gate checks shared by both modes.

        Returns the module, its capability, whether it may run, and — when it
        may not — a *deferred* refusal record. Recording is left to the caller
        so that parallel levels can apply every trace entry in strict canonical
        order. Never raises: degradation is data, not an exception.
        """
        module = self.modules[module_id]
        capability = module.capability()
        context.module_states[module_id] = self._state(capability.status, capability.reason, capability.details)
        if capability.status is not ModuleStatus.FUNCTIONAL:
            return module, capability, False, {"status": capability.status, "reason": capability.reason,
                                               "execution": "not_run", "details": capability.details}
        absent = [dep for dep in module.dependencies if dep not in self.modules]
        if absent:
            reason = f"Unknown dependency: {', '.join(absent)}"
            return module, capability, False, {"status": ModuleStatus.FAILED, "reason": reason,
                                               "execution": "skipped"}
        allowed, reason = module.can_run(context)
        if not allowed:
            return module, capability, False, {"status": ModuleStatus.SKIPPED, "reason": reason,
                                               "execution": "skipped"}
        return module, capability, True, None

    def _apply_precheck_refusal(self, context: CognitiveContext, module_id: str, refusal: dict[str, Any],
                                started: str, clock: float, attempt: int) -> None:
        status = refusal["status"]
        context.module_states[module_id] = self._state(status, refusal["reason"], refusal.get("details"),
                                                       execution=refusal["execution"])
        self._record(context, module_id, status, started, clock, refusal["reason"], attempt=attempt)

    def _apply_success(self, context: CognitiveContext, module: CognitiveModule, module_id: str,
                       capability: Any, result: ModuleResult, started: str, clock: float,
                       attempt: int) -> dict[str, Any]:
        """Append artifacts and recognised metadata; engine-only mutation."""
        for produced in result.artifacts:
            context.add_artifact(produced)
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
        return dict(result.metadata)

    def _apply_failure(self, context: CognitiveContext, module: CognitiveModule, module_id: str,
                       message: str, execution: str, started: str, clock: float, attempt: int,
                       trace_message: str | None = None) -> None:
        context.module_states[module_id] = self._state(ModuleStatus.FAILED, message, execution=execution)
        self._record(context, module_id, ModuleStatus.FAILED, started, clock,
                     trace_message or "Module execution failed", message, attempt=attempt)
        self.resource_policy.after_step(module)

    def _execute(self, context: CognitiveContext, module_id: str, attempt: int = 1) -> dict[str, Any]:
        """Sequential execution (historical mode), unchanged semantics."""
        started, clock = timestamp(), perf_counter()
        module, capability, runnable, refusal = self._precheck(context, module_id, started, clock, attempt)
        if not runnable:
            self._apply_precheck_refusal(context, module_id, refusal, started, clock, attempt)
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
            self._apply_failure(context, module, module_id, message, "timed_out", started, clock, attempt,
                                trace_message=message)
            return {"executed": False, "metadata": {}}
        except Exception as error:  # module error must not terminate the architecture
            worker.shutdown(wait=False, cancel_futures=True)
            message = f"{type(error).__name__}: {str(error)[:700]}"
            self._apply_failure(context, module, module_id, message, "failed", started, clock, attempt)
            return {"executed": False, "metadata": {}}
        worker.shutdown(wait=True, cancel_futures=False)
        metadata = self._apply_success(context, module, module_id, capability, result, started, clock, attempt)
        return {"executed": True, "metadata": metadata}

    # ----------------------------------------------------------- parallel step
    def _execute_level(self, context: CognitiveContext, level: list[str]) -> dict[str, dict[str, Any]]:
        """Run one topological level: members execute concurrently on one
        frozen snapshot; their results are merged in canonical pipeline order.

        Determinism invariants:
        - one shared snapshot per level (taken after all pre-checks);
        - artifacts are applied member by member in pipeline order, so the
          ledger order does not depend on thread-completion order;
        - per-module soft timeouts bound wall time; a late isolated result can
          never mutate central context.
        """
        checked: list[tuple[str, CognitiveModule, Any, bool, dict[str, Any] | None, str, float]] = []
        for module_id in level:  # phase 1: checks only, so all members see an identical context
            started, clock = timestamp(), perf_counter()
            module, capability, runnable, refusal = self._precheck(context, module_id, started, clock, 1)
            checked.append((module_id, module, capability, runnable, refusal, started, clock))
        outcomes: dict[str, dict[str, Any]] = {}
        frozen = context.snapshot()
        runnable_entries = [entry for entry in checked if entry[3]]
        workers = ThreadPoolExecutor(max_workers=max(1, len(runnable_entries)),
                                     thread_name_prefix="uca-level")
        futures = {entry[0]: workers.submit(entry[1].run, frozen) for entry in runnable_entries}
        try:
            for module_id, module, capability, runnable, refusal, started, clock in checked:
                # phase 2: every trace entry applied in strict canonical order
                if not runnable:
                    self._apply_precheck_refusal(context, module_id, refusal, started, clock, 1)
                    outcomes[module_id] = {"executed": False, "metadata": {}}
                    continue
                timeout = module.timeout_seconds or self.default_timeout
                try:
                    result = futures[module_id].result(timeout=timeout)
                except FutureTimeout:
                    futures[module_id].cancel()
                    message = f"Soft timeout after {timeout}s inside parallel level; result isolated and ignored"
                    self._apply_failure(context, module, module_id, message, "timed_out", started, clock, 1,
                                        trace_message=message)
                    outcomes[module_id] = {"executed": False, "metadata": {}}
                    continue
                except Exception as error:
                    message = f"{type(error).__name__}: {str(error)[:700]}"
                    self._apply_failure(context, module, module_id, message, "failed", started, clock, 1)
                    outcomes[module_id] = {"executed": False, "metadata": {}}
                    continue
                metadata = self._apply_success(context, module, module_id, capability, result, started, clock, 1)
                outcomes[module_id] = {"executed": True, "metadata": metadata}
        finally:
            workers.shutdown(wait=True, cancel_futures=False)
        for module_id in level:
            outcomes.setdefault(module_id, {"executed": False, "metadata": {}})
        return outcomes

    # -------------------------------------------------------------- correction
    def _maybe_correction(self, context: CognitiveContext, metadata: dict[str, Any],
                          corrections: int) -> int:
        """At most one targeted review pass, inserted after verification. It
        preserves prior outputs and can never loop indefinitely."""
        if (metadata.get("correction_required") is True and corrections < self.max_corrections
                and "smollm2_360_review" in self.modules):
            corrections += 1
            self._execute(context, "smollm2_360_review", attempt=2)
            if "global_workspace" in self.modules:
                self._execute(context, "global_workspace", attempt=2)
            self._execute(context, "final_verification", attempt=2)
        return corrections

    # ----------------------------------------------------------------- process
    def process(self, user_text: str) -> CognitiveContext:
        if not isinstance(user_text, str) or not user_text.strip():
            raise ValueError("A non-empty user message is required")
        context = CognitiveContext(request_id=str(uuid4()), user_text=user_text)
        corrections = 0
        if self.execution_mode == "parallel_levels":
            for level in self._levels:
                outcomes = self._execute_level(context, level)
                if "final_verification" in outcomes:
                    corrections = self._maybe_correction(
                        context, outcomes["final_verification"]["metadata"], corrections)
        else:
            for module_id in self.pipeline:
                execution = self._execute(context, module_id)
                if module_id == "final_verification":
                    corrections = self._maybe_correction(context, execution["metadata"], corrections)
        if not context.final_response:
            context.final_response = ("UCA could not run its final response module. Consult the execution trace for "
                                      "module availability and failure details.")
        self.run_store.put(context.request_id, context.to_dict(developer=True))
        return context
