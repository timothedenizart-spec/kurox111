from __future__ import annotations

import unittest

from uca.ncm_refinement import build_reflection_packet, gate_refinement_response, select_final_answer


class NcmRefinementTests(unittest.TestCase):
    def snapshot(self) -> dict:
        return {
            "user_text": "Quelle est la capitale administrative de la Bretagne ?",
            "normalized_text": "Quelle est la capitale administrative de la Bretagne ?",
            "uncertainties": [{"message": "Le corpus local peut être incomplet."}],
            "artifacts": [
                {"id": "d1", "kind": "document", "content": {
                    "content": "La capitale administrative régionale de la Bretagne est Rennes."}},
                {"id": "f1", "kind": "symbolic_fact", "content": {
                    "statement": "Bretagne capitale administrative Rennes",
                    "relation": {"subject": "Bretagne", "predicate": "capitale administrative", "object": "Rennes"}}},
                {"id": "c1", "kind": "computation", "content": {
                    "expression": "1/3 + 1/6", "exact_value": "1/2"}},
                {"id": "m1", "kind": "memory", "content": {"text": "mémoire explicite privée"}},
                {"id": "p1", "kind": "proposal", "content": {"text": "proposition à exclure"}},
            ],
        }

    def test_reflection_packet_excludes_memory_and_generated_proposals(self) -> None:
        packet = build_reflection_packet(self.snapshot(), "Rennes est la capitale administrative.")
        identifiers = {item["artifact_id"] for item in packet["evidence"]}
        self.assertEqual(identifiers, {"d1", "f1", "c1"})
        self.assertNotIn("mémoire explicite privée", str(packet))
        self.assertNotIn("proposition à exclure", str(packet))
        self.assertEqual(packet["contract_version"], 1)

    def test_supported_ncm_proposal_is_shadow_only(self) -> None:
        packet = build_reflection_packet(self.snapshot(), "Réponse baseline : Rennes.")
        response = {
            "candidate_answer": "D’après le document local, Rennes est la capitale administrative de la Bretagne.",
            "change_intents": ["clarity", "cite_evidence"],
            "claims": [{"text": "Rennes est la capitale administrative de la Bretagne.", "source_artifact_ids": ["d1", "f1"]}],
            "uncertainties": ["Le corpus local peut être incomplet."],
            "runner_metadata": {"model_id": "local-ncm"},
        }
        decision = gate_refinement_response(response, packet)
        self.assertEqual(decision.status, "accepted_for_shadow_review")
        self.assertFalse(decision.auto_apply)
        selected = select_final_answer("Réponse baseline : Rennes.", decision, mode="shadow")
        self.assertEqual(selected.answer, "Réponse baseline : Rennes.")
        self.assertFalse(selected.applied_ncm)
        self.assertIn("shadow", selected.reason)

    def test_unknown_or_unsupported_claim_is_rejected(self) -> None:
        packet = build_reflection_packet(self.snapshot(), "Réponse baseline : Rennes.")
        unknown = gate_refinement_response({
            "candidate_answer": "Nantes est la capitale.", "change_intents": ["correct_supported_claim"],
            "claims": [{"text": "Nantes est la capitale.", "source_artifact_ids": ["does-not-exist"]}],
            "uncertainties": [],
        }, packet)
        self.assertEqual(unknown.status, "rejected")
        self.assertTrue(any("unavailable evidence" in item for item in unknown.errors))
        unsupported = gate_refinement_response({
            "candidate_answer": "La Bretagne a dix millions d'habitants.", "change_intents": ["clarity"],
            "claims": [{"text": "La Bretagne a dix millions d'habitants.", "source_artifact_ids": ["d1"]}],
            "uncertainties": [],
        }, packet)
        self.assertEqual(unsupported.status, "rejected")
        self.assertTrue(any("lacks lexical support" in item for item in unsupported.errors))

    def test_malformed_runner_response_falls_back_to_baseline(self) -> None:
        packet = build_reflection_packet(self.snapshot(), "Réponse baseline : Rennes.")
        decision = gate_refinement_response({"candidate_answer": "x", "claims": "not-a-list"}, packet)
        self.assertEqual(decision.status, "rejected")
        selected = select_final_answer("Réponse baseline : Rennes.", decision, mode="gated")
        self.assertEqual(selected.answer, "Réponse baseline : Rennes.")
        self.assertIn("baseline retained", selected.reason)


if __name__ == "__main__":
    unittest.main()
