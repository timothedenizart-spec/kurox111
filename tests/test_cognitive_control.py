from __future__ import annotations

import unittest

from uca.cognitive import CognitiveControlLayer, ExactArithmeticKernel
from uca.factory import build_engine
from uca.types import ArtifactKind


class CognitiveControlTests(unittest.TestCase):
    def test_exact_rational_kernel_evaluates_without_float_drift(self) -> None:
        expression = ExactArithmeticKernel.extract("Calcule 2 * (3 + 4) / 5")
        self.assertEqual(expression, "2 * (3 + 4) / 5")
        outcome = ExactArithmeticKernel.evaluate(expression or "")
        self.assertEqual(outcome.exact_value, "14/5")
        self.assertEqual(outcome.operation_count, 3)
        self.assertEqual(ExactArithmeticKernel.evaluate(ExactArithmeticKernel.extract("Calcule 13*(9-2)") or "").exact_value, "91")

    def test_kernel_rejects_code_and_does_not_misread_year_range(self) -> None:
        with self.assertRaises(ValueError):
            ExactArithmeticKernel.evaluate("__import__('os').system('false')")
        self.assertIsNone(ExactArithmeticKernel.extract("En 2020-2021, le corpus a changé."))

    def test_input_stage_publishes_verified_calculation_separately(self) -> None:
        context = build_engine().process("Calcule 2*(3+4)/5")
        computations = context.artifacts_of(ArtifactKind.COMPUTATION)
        self.assertEqual(len(computations), 1)
        self.assertEqual(computations[0].content["exact_value"], "14/5")
        self.assertEqual(computations[0].confidence, 1.0)
        self.assertEqual(context.symbolic_facts, [])
        self.assertIn("2*(3+4)/5 = 14/5", context.final_response or "")

    def test_bounded_workspace_keeps_attention_and_conflict_distinct_from_truth(self) -> None:
        controller = CognitiveControlLayer({"working_memory_capacity": 3, "max_evidence_nodes": 8, "max_evidence_edges": 20})
        snapshot = {
            "user_text": "Quelle capitale pour la Bretagne ?", "normalized_text": "Quelle capitale pour la Bretagne ?",
            "artifacts": [
                {"id": "d1", "kind": "document", "content": {"content": "La Bretagne possède une capitale administrative."},
                 "provenance": {"producer": "fts", "references": ["d1"], "input_artifact_ids": []}, "uncertainty": []},
                {"id": "f1", "kind": "symbolic_fact", "content": {"statement": "Bretagne capitale Rennes",
                 "relation": {"subject": "Bretagne", "predicate": "capitale", "object": "Rennes"}},
                 "provenance": {"producer": "metta", "implementation": "external MeTTa runner", "references": ["f1"], "input_artifact_ids": []}, "uncertainty": []},
                {"id": "f2", "kind": "symbolic_fact", "content": {"statement": "Bretagne capitale Nantes",
                 "relation": {"subject": "Bretagne", "predicate": "capitale", "object": "Nantes"}},
                 "provenance": {"producer": "metta", "implementation": "external MeTTa runner", "references": ["f2"], "input_artifact_ids": []}, "uncertainty": []},
                {"id": "p1", "kind": "proposal", "content": {"text": "Une idée non vérifiée sur la capitale Bretagne"},
                 "provenance": {"producer": "ncm", "references": [], "input_artifact_ids": []}, "uncertainty": ["unverified"]},
            ],
        }
        dossier = controller.workspace(snapshot)
        self.assertEqual(len(dossier["working_memory"]), 3)
        self.assertEqual(len(dossier["conflict_register"]), 1)
        self.assertIn("prediction_error_register", dossier)
        self.assertGreater(dossier["information_geometry"]["modality_entropy_bits"], 0)
        self.assertEqual(dossier["information_geometry"]["modality_counts"]["symbolic_fact"], 2)
        self.assertIn("not a truth confidence", dossier["attention_disclaimer"])
        self.assertTrue(dossier["coverage"]["generated_proposals"])


if __name__ == "__main__":
    unittest.main()
