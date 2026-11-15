"""Local conceptual-response refiner ("NCM-local") wired into the reflection system (UCA-13).

Honesty boundary first: this is **not** the external NCM LM1B/VQ runner (that
contract slot is unchanged and still requires a validated operator shim). It is
a deterministic, auditable implementation of the *role* the pipeline reserves
for concept-level refinement of the final answer.

The refiner is deliberately "connected to the reflection system": its only
inputs are the *reflection artifacts* produced upstream —

- the GlobalWorkspace dossier (coverage, grounding-gap register, conflict
  register, bounded working memory),
- the FinalVerification artifact (structured symbolic conflicts, checks),
- the SurprisalMonitor diagnostics (novelty flags over local evidence),

plus the evidence bins (documents, facts, computations, consolidated
associations). It emits one `REFINEMENT` artifact: an explicit composition
plan with reflection lines, open-conflict annotations and active-limit lines.
`final_response` consumes it when present and composes the single user-facing
answer accordingly. No rule ever promotes generated text to fact, deletes an
uncertainty, or selects a conflicting claim — the plan can only *surface* and
*order* what the evidence ledger already contains.
"""
from __future__ import annotations

from typing import Any

from .modules import CognitiveModule
from .types import Artifact, ArtifactKind, ModuleResult, Provenance


def _latest(snapshot: dict[str, Any], kind: str, producer: str | None = None) -> dict[str, Any] | None:
    found = None
    for item in snapshot.get("artifacts", []):
        if item.get("kind") != kind:
            continue
        if producer and item.get("provenance", {}).get("producer") != producer:
            continue
        found = item
    return found


class NcmResponseRefinerModule(CognitiveModule):
    """Deterministic concept-level refinement of the final answer."""

    MODULE_ID = "ncm_response_refiner"

    def __init__(self, enabled: bool = True) -> None:
        super().__init__(self.MODULE_ID, enabled=enabled, dependencies=("final_verification",))

    def run(self, snapshot: dict[str, Any]) -> ModuleResult:
        docs = snapshot.get("sources", [])
        facts = snapshot.get("symbolic_facts", [])
        computations = snapshot.get("computations", [])
        proposals = snapshot.get("propositions", [])
        memories = [item for item in snapshot.get("artifacts", [])
                    if item.get("kind") == ArtifactKind.MEMORY.value]
        workspace = _latest(snapshot, ArtifactKind.SYNTHESIS.value, "global_workspace")
        verification = _latest(snapshot, ArtifactKind.VERIFICATION.value, "final_verification")
        surprisal = _latest(snapshot, ArtifactKind.DIAGNOSTIC.value, "surprisal_monitor")

        control = (workspace or {}).get("content", {}).get("cognitive_control", {})
        coverage = control.get("coverage", {})
        grounding_gaps = control.get("prediction_error_register", [])
        unresolved = control.get("metacognitive_state", {}).get("unresolved", [])
        verification_content = (verification or {}).get("content", {})
        conflicts = verification_content.get("symbolic_conflicts", [])
        checks = verification_content.get("checks", [])
        unverified_claims = sum(1 for check in checks
                                if check.get("status") != "supported_by_available_excerpt")
        flagged_surprisal = ((surprisal or {}).get("content", {}).get("flagged_count", 0))

        concept_counts = {"facts": len(facts), "documents": len(docs),
                          "computations": len(computations), "proposals": len(proposals),
                          "memories": len(memories)}
        covered = sum(1 for present in coverage.values() if present)

        # --- reflection lines: what the system's own metacognition reports ----
        reflection: list[str] = []
        reflection.append(f"Couverture des preuves : {covered}/5 substrats disponibles.")
        if grounding_gaps:
            reflection.append(f"{len(grounding_gaps)} artefact(s) généré(s) à faible ancrage lexical : à vérifier avant usage.")
        if unverified_claims:
            reflection.append(f"{unverified_claims} affirmation(s) analysée(s) non corroborées par les ressources locales.")
        if flagged_surprisal:
            reflection.append(f"{flagged_surprisal} analyse(s) très surprenante(s) relativement au corpus local.")
        if not reflection or all(line.startswith("Couverture") for line in reflection):
            reflection.append("Aucun signal de réflexion actif : limites standard seules.")

        # --- open conflicts: surfaced, never arbitrated by vote ---------------
        conflict_lines = []
        for conflict in conflicts[:4]:
            objects = ", ".join(conflict.get("objects", []))
            conflict_lines.append(f"{conflict.get('subject', '?')} · {conflict.get('predicate', '?')} : "
                                  f"valeurs en conflit ({objects}) — arbitrage humain requis.")

        # --- active limits (from upstream uncertainties, never invented) ------
        limit_lines: list[str] = list(unresolved[:4])
        if not docs:
            limit_lines.append("Aucun passage documentaire local disponible pour étayer la réponse.")
        if not facts and not computations:
            limit_lines.append("Aucun fait symbolique ni calcul exact disponible.")
        if proposals:
            limit_lines.append(f"{len(proposals)} proposition(s) restent à l'état NON_VERIFIE et ne sont pas des faits.")
        if not (docs or facts or computations or proposals):
            limit_lines.insert(0, "Aucune preuve locale (document, fait, calcul) disponible pour cette demande.")

        plan = {
            "composition_order": ["reflection", "documents", "computations", "symbolic_facts",
                                  "analysis", "open_conflicts", "active_limits"],
            "concept_counts": concept_counts,
            "coverage_hits": covered,
            "reflection_lines": reflection,
            "conflict_lines": conflict_lines,
            "limit_lines": limit_lines[:6],
            "reflection_sources": [name for name, present in
                                   (("global_workspace", bool(workspace)), ("final_verification", bool(verification)),
                                    ("surprisal_monitor", bool(surprisal))) if present],
        }
        return ModuleResult(artifacts=(Artifact(
                                kind=ArtifactKind.REFINEMENT,
                                content=plan,
                                provenance=Provenance(producer=self.module_id,
                                                      implementation="deterministic concept-level refinement over reflection artifacts"),
                                confidence=None,
                                uncertainty=("The refinement only surfaces and orders existing evidence; it adds no fact and opts no winner.",)),),
                            message=(f"Refinement plan: {covered}/5 substrata covered, "
                                     f"{len(conflict_lines)} open conflict(s), {len(limit_lines[:6])} active limit(s)"))
