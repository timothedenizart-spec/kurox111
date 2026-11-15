"""Structural and epistemic invariant checks for UCA runs.

These checks assess architecture discipline, not answer intelligence, factual
truth, language quality, or model capability. They are useful before expensive
human/model benchmarks are available.
"""
from __future__ import annotations

from typing import Any

from .types import ArtifactKind, CognitiveContext


def _check(name: str, passed: bool, detail: str, *, critical: bool = True) -> dict[str, Any]:
    return {"name": name, "passed": passed, "critical": critical, "detail": detail}


def evaluate_context(context: CognitiveContext, expectations: dict[str, Any] | None = None) -> dict[str, Any]:
    """Inspect one completed run without changing it.

    `expectations` are task-local assertions, such as an exact arithmetic output
    or expected execution topology. They do not turn a task into a truth
    benchmark; they simply make structural regressions observable.
    """
    expectations = expectations or {}
    artifacts = context.artifacts
    serialized = [item.to_dict() for item in artifacts]
    ids = [item.id for item in artifacts]
    known_ids = set(ids)
    checks: list[dict[str, Any]] = []

    checks.append(_check("artifact_ids_unique", len(ids) == len(known_ids),
                         f"{len(ids)} artifacts, {len(known_ids)} unique IDs"))
    missing_producers = [item.id for item in artifacts if not item.provenance.producer]
    checks.append(_check("provenance_producer_present", not missing_producers,
                         "All artifacts identify a producer" if not missing_producers else
                         f"Missing producer for {len(missing_producers)} artifact(s)"))
    dangling_inputs = [(item.id, parent) for item in artifacts for parent in item.provenance.input_artifact_ids
                       if parent not in known_ids]
    checks.append(_check("provenance_inputs_resolve", not dangling_inputs,
                         "All declared artifact inputs resolve locally" if not dangling_inputs else
                         f"{len(dangling_inputs)} declared input reference(s) do not resolve"))

    proposition_ids = {item.id for item in artifacts if item.kind is ArtifactKind.PROPOSAL}
    symbolic_ids = {entry.get("id") for entry in context.symbolic_facts}
    overlap = proposition_ids & symbolic_ids
    checks.append(_check("facts_and_proposals_disjoint", not overlap,
                         "Generated proposals remain outside the symbolic-fact bin" if not overlap else
                         f"{len(overlap)} proposal(s) also appear as symbolic facts"))

    ncm_refinements = [item for item in artifacts if item.kind is ArtifactKind.PROPOSAL and
                       item.content.get("kind") == "ncm_reasoning_refinement"]
    malformed_ncm_refinements = [item.id for item in ncm_refinements if
                                 item.content.get("status") != "NON_VERIFIE" or
                                 item.content.get("must_not_be_promoted_to_fact") is not True or
                                 item.content.get("must_not_replace_base_answer_automatically") is not True]
    checks.append(_check("ncm_refinement_remains_unverified", not malformed_ncm_refinements,
                         "No NCM refinement ran" if not ncm_refinements else
                         "All NCM refinement artifacts remain explicit non-verified proposals" if not malformed_ncm_refinements else
                         f"{len(malformed_ncm_refinements)} NCM refinement artifact(s) lack a non-promotion guard"))
    ncm_completed = any(record.module_id == "ncm_reasoning_refinement" and record.status.value == "completed"
                        for record in context.execution_history)
    if ncm_completed:
        verified_ids = set()
        for item in artifacts:
            if item.kind is ArtifactKind.VERIFICATION:
                refinement = item.content.get("ncm_refinement", {})
                inspected = refinement.get("artifact_ids", []) if isinstance(refinement, dict) else []
                if isinstance(inspected, list):
                    verified_ids.update(str(value) for value in inspected)
        expected_ids = {item.id for item in ncm_refinements}
        reached_verifier = bool(expected_ids) and expected_ids.issubset(verified_ids)
        checks.append(_check("ncm_refinement_reaches_independent_verification", reached_verifier,
                             f"{len(expected_ids & verified_ids)}/{len(expected_ids)} completed NCM refinement artifact(s) reached verification"))

    malformed_documents = [item.id for item in artifacts if item.kind is ArtifactKind.DOCUMENT and
                           not all(item.content.get(key) for key in ("document_id", "content", "provenance"))]
    checks.append(_check("document_provenance_complete", not malformed_documents,
                         "All document artifacts retain ID, content and provenance" if not malformed_documents else
                         f"{len(malformed_documents)} document(s) lack mandatory provenance fields"))

    computations = [item for item in artifacts if item.kind is ArtifactKind.COMPUTATION]
    malformed_computations = [item.id for item in computations if
                              item.content.get("verification_status") != "exact_deterministic" or
                              not item.content.get("expression") or item.content.get("exact_value") is None]
    checks.append(_check("exact_computations_scoped", not malformed_computations,
                         "All computation artifacts expose exact scope/status" if not malformed_computations else
                         f"{len(malformed_computations)} computation(s) are missing exact-evaluation metadata"))

    final_count = sum(1 for item in artifacts if item.kind is ArtifactKind.FINAL)
    checks.append(_check("single_final_response", final_count == 1 and bool(context.final_response),
                         f"{final_count} final artifact(s); final response {'present' if context.final_response else 'absent'}"))

    topology = context.available_context.get("execution_topology", {})
    checks.append(_check("execution_topology_declared", isinstance(topology, dict) and bool(topology.get("mode")),
                         f"Topology: {topology.get('mode', 'missing')}"))
    fanout_events = [item for item in artifacts if item.kind is ArtifactKind.DIAGNOSTIC and
                     item.content.get("event") == "parallel_afferent_fanout"]
    if topology.get("mode") == "staged_parallel":
        checks.append(_check("parallel_fanout_traced", len(fanout_events) == 1,
                             f"{len(fanout_events)} staged-parallel fanout event(s)"))

    expected_exact = expectations.get("expected_exact_computation")
    if expected_exact is not None:
        actual = {str(item.content.get("exact_value")) for item in computations}
        checks.append(_check("expected_exact_computation", str(expected_exact) in actual,
                             f"Expected {expected_exact}; observed {sorted(actual)}"))
    expected_topology = expectations.get("expected_topology")
    if expected_topology is not None:
        checks.append(_check("expected_topology", topology.get("mode") == expected_topology,
                             f"Expected {expected_topology}; observed {topology.get('mode')}"))
    if expectations.get("require_parallel_fanout") is True:
        checks.append(_check("required_parallel_fanout", bool(fanout_events),
                             f"{len(fanout_events)} fanout event(s) observed"))
    if expectations.get("min_document_sources") is not None:
        required = int(expectations["min_document_sources"])
        checks.append(_check("minimum_document_sources", len(context.sources) >= required,
                             f"Expected at least {required}; observed {len(context.sources)}"))

    critical = [check for check in checks if check["critical"]]
    passed = all(check["passed"] for check in critical)
    return {
        "schema": "uca.structural-evaluation.v1",
        "passed": passed,
        "critical_passed": sum(1 for check in critical if check["passed"]),
        "critical_total": len(critical),
        "artifact_count": len(serialized),
        "checks": checks,
        "notice": "Structural pass/fail is not an answer-quality, factuality, reasoning or intelligence score.",
    }
