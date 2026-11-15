from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from uca.config import DEFAULT_CONFIG
from uca.factory import build_engine
from uca.storage import import_documents, initialize_knowledge_db
from uca.types import Artifact, ArtifactKind, CognitiveContext, Provenance


class EngineIntegrationTests(unittest.TestCase):
    def make_config(self, root: Path) -> dict:
        cfg = deepcopy(DEFAULT_CONFIG)
        cfg["_root"] = str(root)
        cfg["stores"] = {"memory_path": "data/memory.json", "knowledge_db": "data/knowledge.sqlite",
                         "knowledge_table": "documents", "facts_path": "data/operator_facts.json"}
        return cfg

    def test_degrades_honestly_and_preserves_explicit_local_evidence(self) -> None:
        with TemporaryDirectory() as temp:
            root = Path(temp); (root / "data").mkdir()
            (root / "data/memory.json").write_text(json.dumps({"entries": [
                {"id": "keep", "text": "Préférence explicitement enregistrée : Bretagne.", "explicit": True, "tags": ["Bretagne"]},
                {"id": "ignore", "text": "Ne jamais montrer", "explicit": False, "tags": ["Bretagne"]},
            ]}), encoding="utf-8")
            db = root / "data/knowledge.sqlite"
            initialize_knowledge_db(db)
            import_documents(db, [{"doc_id": "fr-shard-1", "content": "La Bretagne est une région française.",
                                   "provenance": "wikipedia-fr-local-shard", "metadata": {"shard": "test"}}])
            engine = build_engine(config=self.make_config(root))
            result = engine.process("Que contient le corpus local sur la Bretagne ?")
            self.assertTrue(result.final_response)
            self.assertIn("fr-shard-1", result.final_response or "")
            memory = result.artifacts_of(ArtifactKind.MEMORY)
            self.assertEqual(len(memory), 1)
            self.assertEqual(memory[0].content["memory_id"], "keep")
            self.assertFalse(any(item.content.get("memory_id") == "ignore" for item in memory))
            # Missing checkpoint does not prevent final provenance-preserving output.
            state = result.module_states["smollm2_135_analysis"]
            self.assertEqual(state["status"], "unavailable")
            self.assertEqual(result.module_states["final_response"]["execution"], "completed")
            self.assertGreaterEqual(len(result.execution_history), 11)

    def test_symbolic_fact_index_is_explicit_and_correction_is_bounded(self) -> None:
        with TemporaryDirectory() as temp:
            root = Path(temp); (root / "data").mkdir()
            initialize_knowledge_db(root / "data/knowledge.sqlite")
            (root / "data/memory.json").write_text('{"entries": []}', encoding="utf-8")
            # These deliberately conflicting structured records exercise the targeted review hook.
            (root / "data/operator_facts.json").write_text(json.dumps({"facts": [
                {"id": "f1", "subject": "Bretagne", "predicate": "capitale", "object": "Rennes"},
                {"id": "f2", "subject": "Bretagne", "predicate": "capitale", "object": "Nantes"},
            ]}), encoding="utf-8")
            result = build_engine(config=self.make_config(root)).process("Quelle est la capitale de la Bretagne ?")
            self.assertEqual(len(result.artifacts_of(ArtifactKind.SYMBOLIC_FACT)), 2)
            verification_attempts = [record for record in result.execution_history if record.module_id == "final_verification"]
            self.assertEqual(len(verification_attempts), 2)  # max_corrections=1, never a loop
            self.assertTrue(any(item.content.get("symbolic_conflicts")
                                for item in result.artifacts_of(ArtifactKind.VERIFICATION)))

    def test_proposals_never_enter_symbolic_facts(self) -> None:
        context = CognitiveContext(request_id="r", user_text="x")
        proposal = Artifact(ArtifactKind.PROPOSAL, {"text": "invented", "status": "NON_VERIFIE"},
                            Provenance("ncm"))
        context.add_artifact(proposal)
        self.assertEqual(len(context.propositions), 1)
        self.assertEqual(context.symbolic_facts, [])

    def test_pipeline_order_rejects_known_dependency_reversal(self) -> None:
        with TemporaryDirectory() as temp:
            root = Path(temp); (root / "data").mkdir(); initialize_knowledge_db(root / "data/knowledge.sqlite")
            (root / "data/memory.json").write_text('{"entries": []}', encoding="utf-8")
            engine = build_engine(config=self.make_config(root))
            order = list(engine.pipeline)
            order.remove("input_processing"); order.insert(3, "input_processing")
            with self.assertRaises(ValueError):
                engine.set_pipeline(order)


if __name__ == "__main__":
    unittest.main()
