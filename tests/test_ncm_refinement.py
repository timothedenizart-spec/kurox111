from __future__ import annotations

import unittest
from pathlib import Path

from uca.config import load_config
from uca.factory import build_engine
from uca.model_adapters import ExternalNcmAdapter


class NcmRefinementTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root_dir = Path(__file__).resolve().parent.parent
        self.config = load_config(self.root_dir)
        self.engine = build_engine(self.root_dir, self.config)

    def test_ncm_refiner_invocation_contract(self) -> None:
        ncm_spec = self.config["models"]["ncm"]
        adapter = ExternalNcmAdapter(ncm_spec)
        self.assertTrue(adapter.capability().status.name, "FUNCTIONAL")

        reflection = {
            "metacognitive_state": {"uncertainty_ratio": 0.2, "unresolved": []},
            "coverage": {"exact_computation": True},
            "prediction_error_register": [],
            "working_memory": [],
            "conflict_register": [],
        }
        computations = [{
            "operation": "exact_algebra_and_equations",
            "data": {"variable": "x", "exact_value": "7", "steps": ["(4)*x - 8 = 20", "4*x = 28", "x = 7"]},
        }]

        result = adapter.refine_response(
            query="Résous 4*x - 8 = 20",
            reflection=reflection,
            computations=computations,
            analyses=[],
            documents=[],
            facts=[],
            proposals=[],
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.get("status"), "success")
        self.assertIn("refined_answer", result)
        self.assertIn("x = 7", result["refined_answer"])
        self.assertIn("Synthèse & Résolution Cognitive", result["refined_answer"])
        self.assertIn("Réflexion Métacognitive", result["refined_answer"])

    def test_engine_end_to_end_reflective_answer(self) -> None:
        res = self.engine.process("Résous 6*x + 12 = 48").to_dict(developer=True)
        answer = res.get("answer", "")
        self.assertIn("x = 6", answer)
        self.assertIn("Synthèse & Résolution Cognitive", answer)
        self.assertIn("Démonstration Déductive & Preuves Formelles", answer)
        self.assertIn("Réflexion Métacognitive & Contrôle Épistémique", answer)
        self.assertIn("Résonance Conceptuelle Neuronale", answer)
        self.assertFalse(answer.startswith("Réponse UCA — synthèse locale traçable."))

    def test_causal_reasoning_reflection_synthesis(self) -> None:
        res = self.engine.process("L'humidité provoque la moisissure. La moisissure entraîne des allergies.").to_dict(developer=True)
        answer = res.get("answer", "")
        self.assertIn("causale", answer.lower())
        self.assertIn("allergies", answer.lower())
        self.assertIn("Synthèse & Résolution Cognitive", answer)

    def test_out_of_domain_epistemic_honesty(self) -> None:
        res = self.engine.process("Quelle est la vitesse orbitale de Titan le 12 juillet 2042 ?").to_dict(developer=True)
        answer = res.get("answer", "")
        self.assertIn("corpus documentaire local", answer.lower())
        self.assertIn("honnêteté épistémique", answer.lower())


if __name__ == "__main__":
    unittest.main()
