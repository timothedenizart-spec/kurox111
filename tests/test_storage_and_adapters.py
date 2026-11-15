from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sys
import unittest

from uca.config import DEFAULT_CONFIG
from uca.model_adapters import ExternalNcmAdapter, MaskedNanoDiffAdapter
from uca.pipeline import NcmConceptModule
from uca.storage import FTSKnowledgeStore, import_documents, initialize_knowledge_db
from uca.types import ModuleStatus


class StorageAndAdapterTests(unittest.TestCase):
    def test_fts_escapes_user_grammar_and_keeps_provenance(self) -> None:
        with TemporaryDirectory() as temp:
            db = Path(temp) / "knowledge.sqlite"
            initialize_knowledge_db(db)
            import_documents(db, [{"doc_id": "doc-1", "content": "Les données locales restent limitées.",
                                   "provenance": "test-shard", "metadata": {"source": "unit"}}])
            store = FTSKnowledgeStore(db)
            result = store.search('données OR " injection')
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["provenance"], "test-shard")
            self.assertEqual(result[0]["metadata"]["source"], "unit")

    def test_ncm_external_contract_marks_proposal_unverified(self) -> None:
        with TemporaryDirectory() as temp:
            script = Path(temp) / "runner.py"
            script.write_text("import json,sys\np=json.load(sys.stdin)\nprint(json.dumps({'proposals':[{'text':'hypothèse'}]}))\n", encoding="utf-8")
            adapter = ExternalNcmAdapter({"validated": True, "runner_command": f"{sys.executable} {script}"})
            module = NcmConceptModule(adapter, enabled=True)
            result = module.run({"user_text": "test", "normalized_text": "test"})
            self.assertEqual(result.artifacts[0].content["status"], "NON_VERIFIE")
            self.assertTrue(result.artifacts[0].content["must_not_be_promoted_to_fact"])

    def test_nanodiff_is_held_when_not_validated(self) -> None:
        cfg = {"validated": False, "runner_command": "", "path": "", "tokenizer_path": "", "mask_token_id": -1}
        root = dict(DEFAULT_CONFIG); root["_root"] = "."
        adapter = MaskedNanoDiffAdapter(cfg, root)
        self.assertEqual(adapter.capability().status, ModuleStatus.NON_VALIDATED)


if __name__ == "__main__":
    unittest.main()
