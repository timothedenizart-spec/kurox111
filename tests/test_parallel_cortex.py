from __future__ import annotations

import unittest

from uca.factory import build_engine
from uca.parallel_cortex import HyperdimensionalMemory, Hypervector, ParallelCognitiveCortex
from uca.symbolic_math import (
    CausalReasoner,
    ExactAlgebraKernel,
    HornClauseEngine,
    MinimumDescriptionLength,
    PropositionalTruthTable,
)
from uca.types import ArtifactKind


class ParallelCortexAndSymbolicMathTests(unittest.TestCase):

    def test_exact_algebra_linear_solver(self) -> None:
        sol = ExactAlgebraKernel.solve_linear("Résous 5*x - 15 = 35")
        self.assertIsNotNone(sol)
        assert sol is not None
        self.assertEqual(sol.variable, "x")
        self.assertEqual(sol.exact_value, "10")
        self.assertEqual(sol.approximate_value, 10.0)
        self.assertGreater(len(sol.steps), 1)

    def test_exact_algebra_rational_fraction(self) -> None:
        sol = ExactAlgebraKernel.solve_linear("résous 3*y + 2 = 7")
        self.assertIsNotNone(sol)
        assert sol is not None
        self.assertEqual(sol.variable, "y")
        self.assertEqual(sol.exact_value, "5/3")

    def test_number_theory_factorization_and_gcd(self) -> None:
        factors = ExactAlgebraKernel.analyze_number("factorise 360")
        self.assertIsNotNone(factors)
        assert factors is not None
        self.assertEqual(factors.result["factors"], [(2, 3), (3, 2), (5, 1)])

        gcd = ExactAlgebraKernel.analyze_number("PGCD de 84 et 36")
        self.assertIsNotNone(gcd)
        assert gcd is not None
        self.assertEqual(gcd.result["gcd"], 12)

    def test_horn_clause_forward_deduction(self) -> None:
        engine = HornClauseEngine()
        engine.add_rule("R1", ["pluie", "vent"], "tempete")
        engine.add_rule("R2", ["tempete"], "alerte_orange")
        engine.add_fact("pluie")
        engine.add_fact("vent")

        steps = engine.deduce()
        derived = [s.conclusion for s in steps]
        self.assertIn("tempete", derived)
        self.assertIn("alerte_orange", derived)

    def test_propositional_truth_table_tautology_and_contradiction(self) -> None:
        taut = PropositionalTruthTable.evaluate("A or not A")
        self.assertIsNotNone(taut)
        assert taut is not None
        self.assertEqual(taut["classification"], "tautology")

        contra = PropositionalTruthTable.evaluate("A and not A")
        self.assertIsNotNone(contra)
        assert contra is not None
        self.assertEqual(contra["classification"], "contradiction")

        contingent = PropositionalTruthTable.evaluate("A or B")
        self.assertIsNotNone(contingent)
        assert contingent is not None
        self.assertEqual(contingent["classification"], "contingency")

    def test_causal_dag_and_pearl_intervention(self) -> None:
        text = "L'humidité provoque la moisissure. La moisissure entraîne des allergies."
        dag = CausalReasoner.extract_graph(text)
        self.assertIn("humidité", dag.nodes)
        self.assertIn("moisissure", dag.nodes)
        self.assertIn("allergies", dag.nodes)

        intervention = CausalReasoner.analyze_intervention(text, "moisissure")
        self.assertIsNotNone(intervention)
        assert intervention is not None
        self.assertEqual(intervention["target"], "moisissure")
        self.assertIn("interventional_validity", intervention)

    def test_minimum_description_length_metric(self) -> None:
        mdl = MinimumDescriptionLength.score("Gravité newtonienne F = G*m1*m2/r^2", "mouvement orbital des planètes")
        self.assertIn("total_mdl_score", mdl)
        self.assertIn("parsimony_assessment", mdl)

    def test_vsa_hypervector_binding_and_associative_cleanup(self) -> None:
        h_mem = HyperdimensionalMemory()
        v_paris = h_mem.get_or_create("paris")
        v_france = h_mem.get_or_create("france")
        self.assertEqual(v_paris.similarity(v_paris), 1.0)
        self.assertLess(abs(v_paris.similarity(v_france)), 0.25)

        relation_vector = h_mem.encode_relation("france", "capitale", "paris")
        self.assertEqual(len(relation_vector.values), Hypervector.DIMENSION)

        matches = h_mem.cleanup(v_paris, top_k=1)
        self.assertEqual(matches[0][0], "paris")

    def test_parallel_cortex_engine_integration_linear_equation(self) -> None:
        engine = build_engine()
        result = engine.process("Résous 4*x + 10 = 30")
        computations = result.artifacts_of(ArtifactKind.COMPUTATION)
        self.assertTrue(any("exact_algebra" in str(c.content) for c in computations))
        self.assertIn("x = 5", result.final_response or "")

    def test_parallel_cortex_engine_integration_logic_deduction(self) -> None:
        engine = build_engine()
        result = engine.process("Si soleil alors chaleur. Sachant que soleil.")
        computations = result.artifacts_of(ArtifactKind.COMPUTATION)
        self.assertTrue(any("chaleur" in str(c.content) for c in computations))
        self.assertIn("chaleur", result.final_response or "")


if __name__ == "__main__":
    unittest.main()
