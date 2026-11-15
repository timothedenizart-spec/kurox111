"""Tests for the NCM-local response refiner (UCA-13) and the probe lab."""
from __future__ import annotations

from pathlib import Path
import json
import unittest

from uca.probes import run_all_probes
from uca.types import ArtifactKind
from uca.probes import _engine_with  # probe helper builds isolated engines


class ResponseRefinerTests(unittest.TestCase):
    def test_refinement_surfaces_open_conflict_and_stays_honest(self) -> None:
        engine = _engine_with({"facts": [
            {"id": "f1", "subject": "Bretagne", "predicate": "capitale", "object": "Rennes"},
            {"id": "f2", "subject": "Bretagne", "predicate": "capitale", "object": "Nantes"}]})
        context = engine.process("Quelle est la capitale de la Bretagne ?")
        refinements = context.artifacts_of(ArtifactKind.REFINEMENT)
        self.assertEqual(len(refinements), 1)
        plan = refinements[0].content
        self.assertTrue(plan["conflict_lines"], "le conflit structuré doit remonter dans le plan")
        self.assertIn("final_verification", plan["reflection_sources"])
        self.assertIn("global_workspace", plan["reflection_sources"])
        answer = context.final_response or ""
        self.assertIn("raffineur conceptuel", answer)               # rôle assumé
        self.assertIn("Conflits symboliques ouverts", answer)       # conflit visible
        self.assertIn("arbitrage humain requis", answer)            # jamais de vote
        self.assertTrue(refinements[0].uncertainty)                 # incertitude explicite
        # Jamais de promotion : les deux faits contradictoires restent des faits séparés,
        # la réponse affirme l'indétermination plutôt que choisir Rennes ou Nantes.
        self.assertEqual(len(context.symbolic_facts), 2)

    def test_refinement_empty_evidence_stays_honest(self) -> None:
        engine = _engine_with({})
        context = engine.process("Que sait-on du ptérodactyle ?")
        answer = context.final_response or ""
        self.assertIn("Aucune source documentaire", answer)
        refinements = context.artifacts_of(ArtifactKind.REFINEMENT)
        self.assertTrue(any("Aucune preuve locale" in line
                            for line in refinements[-1].content["limit_lines"]))
        self.assertEqual(context.module_states["ncm_response_refiner"]["status"], "functional")

    def test_refinement_reflects_grounding_gaps(self) -> None:
        # Consolidated associations with NO documentary corroboration shape →
        # grounding reference exists; check coverage counts ride the plan.
        engine = _engine_with({"documents": [
            {"doc_id": "d1", "content": "La Bretagne borde la Manche.", "provenance": "probe"}]})
        context = engine.process("Que borde la Bretagne ?")
        plan = context.artifacts_of(ArtifactKind.REFINEMENT)[-1].content
        self.assertEqual(plan["concept_counts"]["documents"], 1)
        self.assertTrue(plan["reflection_lines"][0].startswith("Couverture"))


class ProbeLabTests(unittest.TestCase):
    _report = None

    @classmethod
    def report(cls) -> dict:
        if cls._report is None:
            cls._report = run_all_probes()
        return cls._report

    def test_all_probes_run_and_report_verdicts(self) -> None:
        report = self.report()
        self.assertEqual(report["schema"], "uca.probe-lab.v1")
        names = {probe["name"] for probe in report["probes"]}
        self.assertEqual(len(names), len(report["probes"]))
        for probe in report["probes"]:
            self.assertIn(probe["verdict"], ("solide", "à améliorer"), probe["name"])
        json.dumps(report)  # fully serializable

    def test_core_resilience_probes_are_solid(self) -> None:
        by_name = {probe["name"]: probe for probe in self.report()["probes"]}
        for solid in ("timeout_isolation", "memory_optin_gate", "conflict_bounded_correction",
                      "absence_honesty_with_refiner", "arithmetic_extraction_robustness"):
            self.assertEqual(by_name[solid]["verdict"], "solide",
                             f"{solid}: {by_name[solid]['measurements']}")

    def test_parenthesized_expressions_survive_extraction(self) -> None:
        # Régression mesurée par la sonde : « calcule (2+3)×7 » perdait « ( ».
        engine = _engine_with({})
        context = engine.process("calcule (2+3)×7")
        computations = context.artifacts_of(ArtifactKind.COMPUTATION)
        self.assertTrue(computations)
        self.assertEqual(computations[0].content["exact_value"], "35")

    def test_vsa_scaling_finding_is_measured(self) -> None:
        vsa = {probe["name"]: probe for probe in self.report()["probes"]}["vsa_scaling_fidelity"]
        self.assertIn("dim_64", vsa["measurements"])
        self.assertIn("dim_2048", vsa["measurements"])
        # si une faiblesse est mesurée à petite dimension, une amélioration candidate existe
        if vsa["verdict"] == "à améliorer":
            self.assertTrue(vsa["candidate_improvement"])


if __name__ == "__main__":
    unittest.main()
