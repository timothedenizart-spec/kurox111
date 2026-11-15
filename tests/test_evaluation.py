from __future__ import annotations

import unittest

from uca.evaluation import evaluate_context
from uca.factory import build_engine
from uca.types import Artifact, ArtifactKind, CognitiveContext, Provenance


class StructuralEvaluationTests(unittest.TestCase):
    def test_math_run_satisfies_declared_structural_expectations(self) -> None:
        context = build_engine().process("Calcule 2*(3+4)/5")
        report = evaluate_context(context, {
            "expected_exact_computation": "14/5",
            "expected_topology": "staged_parallel",
            "require_parallel_fanout": True,
        })
        self.assertTrue(report["passed"])
        self.assertEqual(report["critical_passed"], report["critical_total"])

    def test_evaluator_detects_proposal_promoted_to_fact_bin(self) -> None:
        context = CognitiveContext(request_id="r", user_text="x", final_response="ok")
        proposal = Artifact(ArtifactKind.PROPOSAL, {"text": "unverified"}, Provenance("ncm"))
        final = Artifact(ArtifactKind.FINAL, {"answer": "ok"}, Provenance("composer"))
        context.add_artifact(proposal)
        context.add_artifact(final)
        # Simulate an invalid external mutation that UCA's normal append API does not do.
        context.symbolic_facts.append(proposal.to_dict())
        report = evaluate_context(context)
        check = next(item for item in report["checks"] if item["name"] == "facts_and_proposals_disjoint")
        self.assertFalse(check["passed"])
        self.assertFalse(report["passed"])


if __name__ == "__main__":
    unittest.main()
