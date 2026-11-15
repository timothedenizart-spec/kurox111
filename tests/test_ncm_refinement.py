from __future__ import annotations

from unittest.mock import patch
import unittest

from uca.model_adapters import ExternalNcmAdapter
from uca.pipeline import FinalResponseModule, NcmResponseRefinementModule
from uca.types import Artifact, ArtifactKind, ModuleStatus, Provenance


def serialized(kind: ArtifactKind, producer: str, content: dict) -> dict:
    return Artifact(kind, content, Provenance(producer)).to_dict()


class StubRefiner:
    def __init__(self):
        self.received = None

    def refine_response(self, query, draft, reasoning, allowed_ids, timeout):
        self.received = {"query": query, "draft": draft, "reasoning": reasoning,
                         "allowed_ids": allowed_ids, "timeout": timeout}
        return {"refined_text": "Réponse claire, mais à vérifier.",
                "evidence_artifact_ids": [next(iter(allowed_ids))],
                "change_summary": "Simplification stylistique"}


class NcmRefinementTests(unittest.TestCase):
    def test_refiner_receives_global_workspace_verification_and_evidence(self):
        doc = serialized(ArtifactKind.DOCUMENT, "retrieval", {"document_id": "d1", "content": "Source locale"})
        analysis = serialized(ArtifactKind.ANALYSIS, "smollm", {"model": "local", "text": "Analyse à vérifier"})
        workspace = serialized(ArtifactKind.SYNTHESIS, "global_workspace", {"selection_rule": "evidence first"})
        verification = serialized(ArtifactKind.VERIFICATION, "final_verification", {"checks": [], "negative_evidence_policy": "inconclusive"})
        snapshot = {"user_text": "Question ?", "normalized_text": "Question ?", "artifacts": [doc, analysis, workspace, verification]}
        adapter = StubRefiner()
        result = NcmResponseRefinementModule(adapter, enabled=True).run(snapshot)
        proposal = result.artifacts[0]
        self.assertEqual(proposal.kind, ArtifactKind.PROPOSAL)
        self.assertEqual(proposal.content["proposal_type"], "ncm_final_response_refinement")
        self.assertTrue(proposal.content["requires_independent_verification"])
        self.assertEqual(proposal.provenance.references, tuple(proposal.content["evidence_artifact_ids"]))
        self.assertEqual(adapter.received["reasoning"]["workspace_dossiers"][0]["artifact_id"], workspace["id"])
        self.assertEqual(adapter.received["reasoning"]["verification"][0]["artifact_id"], verification["id"])

    def test_final_response_keeps_baseline_when_shadow_candidate_exists(self):
        candidate = serialized(ArtifactKind.PROPOSAL, "ncm_response_refinement", {
            "proposal_type": "ncm_final_response_refinement", "text": "Candidate answer",
            "evidence_artifact_ids": [], "status": "NON_VERIFIE"})
        analysis = serialized(ArtifactKind.ANALYSIS, "local_model", {"model": "baseline", "text": "Baseline answer"})
        snapshot = {"sources": [], "symbolic_facts": [], "artifacts": [analysis, candidate]}
        result = FinalResponseModule().run(snapshot)
        answer = result.artifacts[0].content["answer"]
        self.assertIn("Baseline answer", answer)
        self.assertIn("mode shadow", answer)
        self.assertNotIn("Candidate answer", answer)
        self.assertTrue(result.artifacts[0].uncertainty)

    def test_adapter_rejects_untrusted_or_unknown_evidence_references(self):
        adapter = ExternalNcmAdapter({"validated": True, "response_refinement_validated": True,
                                      "runner_command": "local-runner"})
        with patch("uca.model_adapters.invoke_json_runner", return_value={
            "refined_text": "candidate", "evidence_artifact_ids": ["invented"]
        }):
            with self.assertRaisesRegex(RuntimeError, "unknown evidence"):
                adapter.refine_response("q", "draft", {}, {"known"}, 1)

    def test_adapter_requires_validated_ncm(self):
        capability = ExternalNcmAdapter({"validated": False, "runner_command": "local-runner"}).capability()
        self.assertEqual(capability.status, ModuleStatus.NON_VALIDATED)

    def test_response_refinement_has_a_separate_validation_gate(self):
        adapter = ExternalNcmAdapter({"validated": True, "runner_command": "local-runner",
                                      "response_refinement_validated": False})
        module = NcmResponseRefinementModule(adapter, enabled=True)
        self.assertEqual(module.capability().status, ModuleStatus.NON_VALIDATED)


if __name__ == "__main__":
    unittest.main()
