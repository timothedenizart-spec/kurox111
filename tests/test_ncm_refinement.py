from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sys
import unittest

from uca.benchmark import variant_config
from uca.config import DEFAULT_CONFIG
from uca.evaluation import evaluate_context
from uca.factory import build_engine
from uca.storage import import_documents, initialize_knowledge_db
from uca.types import ArtifactKind


class NcmReasoningRefinementTests(unittest.TestCase):
    @staticmethod
    def _runner(root: Path) -> str:
        script = root / "ncm_runner.py"
        script.write_text(
            "import json, sys\n"
            "payload = json.load(sys.stdin)\n"
            "if payload['operation'] == 'concept_generation':\n"
            "    print(json.dumps({'proposals': [{'text': 'Hypothèse NCM initiale, à vérifier.'}]}))\n"
            "elif payload['operation'] == 'reasoning_refinement':\n"
            "    print(json.dumps({'review_targets': ['La capitale administrative de la Bretagne est Rennes.'], "
            "'response_plan': 'PLAN_NCM_INTERNE_NE_PAS_AFFICHER', 'metadata': {'fixture': 'local-shim'}}))\n"
            "else:\n"
            "    raise SystemExit('unsupported operation')\n",
            encoding="utf-8",
        )
        return f"{sys.executable} {script}"

    @staticmethod
    def _config(root: Path, command: str, *, refinement_validated: bool = True) -> dict:
        cfg = deepcopy(DEFAULT_CONFIG)
        cfg["_root"] = str(root)
        cfg["stores"] = {"memory_path": "data/memory.json", "knowledge_db": "data/knowledge.sqlite",
                         "knowledge_table": "documents", "facts_path": "data/operator_facts.json"}
        cfg["models"]["ncm"].update({
            "enabled": True, "validated": True, "runner_command": command,
            "refinement_enabled": True, "refinement_validated": refinement_validated,
        })
        return cfg

    @staticmethod
    def _local_evidence(root: Path, *, conflicting_facts: bool = False) -> None:
        data = root / "data"
        data.mkdir()
        (data / "memory.json").write_text(json.dumps({"entries": []}), encoding="utf-8")
        initialize_knowledge_db(data / "knowledge.sqlite")
        import_documents(data / "knowledge.sqlite", [{
            "doc_id": "local-bretagne", "content": "La capitale administrative de la Bretagne est Rennes.",
            "provenance": "fixture-local", "metadata": {"revision": "test"},
        }])
        facts: list[dict[str, str]] = []
        if conflicting_facts:
            facts = [
                {"id": "f-rennes", "subject": "Bretagne", "predicate": "capitale", "object": "Rennes"},
                {"id": "f-nantes", "subject": "Bretagne", "predicate": "capitale", "object": "Nantes"},
            ]
        (data / "operator_facts.json").write_text(json.dumps({"facts": facts}), encoding="utf-8")

    def test_refinement_requires_a_separate_contract_validation_gate(self) -> None:
        with TemporaryDirectory() as temp:
            root = Path(temp)
            command = self._runner(root)
            self._local_evidence(root)
            engine = build_engine(config=self._config(root, command, refinement_validated=False))
            state = engine.status()["modules"]["ncm_reasoning_refinement"]
            self.assertEqual(state["status"], "non_validated")
            self.assertIn("reasoning-refinement contract", state["reason"])

    def test_refinement_never_runs_without_base_ncm_stage(self) -> None:
        with TemporaryDirectory() as temp:
            root = Path(temp)
            command = self._runner(root)
            self._local_evidence(root)
            cfg = self._config(root, command)
            cfg["models"]["ncm"]["enabled"] = False
            state = build_engine(config=cfg).status()["modules"]["ncm_reasoning_refinement"]
            self.assertEqual(state["status"], "disabled_voluntarily")
            self.assertIn("cannot run alone", state["reason"])

    def test_validated_local_shim_refines_verification_plan_without_becoming_fact(self) -> None:
        with TemporaryDirectory() as temp:
            root = Path(temp)
            command = self._runner(root)
            self._local_evidence(root)
            context = build_engine(config=self._config(root, command)).process(
                "Quelle est la capitale administrative de la Bretagne ?"
            )
            refinements = [item for item in context.artifacts_of(ArtifactKind.PROPOSAL)
                           if item.provenance.producer == "ncm_reasoning_refinement"]
            self.assertEqual(len(refinements), 1)
            refinement = refinements[0]
            self.assertEqual(refinement.content["status"], "NON_VERIFIE")
            self.assertTrue(refinement.content["must_not_be_promoted_to_fact"])
            self.assertTrue(refinement.content["must_not_replace_base_answer_automatically"])
            self.assertIn("global_workspace", {item.provenance.producer for item in context.artifacts})
            self.assertNotIn(refinement.id, {item["id"] for item in context.symbolic_facts})

            verification = context.artifacts_of(ArtifactKind.VERIFICATION)[-1].content
            target_checks = verification["ncm_refinement"]["review_target_checks"]
            self.assertEqual(len(target_checks), 1)
            self.assertEqual(target_checks[0]["status"], "review_target_has_local_anchor")
            self.assertIn("local-bretagne", target_checks[0]["document_ids"])
            self.assertIn("Affinement NCM", context.final_response or "")
            self.assertNotIn("PLAN_NCM_INTERNE_NE_PAS_AFFICHER", context.final_response or "")
            self.assertTrue(evaluate_context(context)["passed"])

    def test_bounded_correction_reexecutes_the_refinement_stage_once(self) -> None:
        with TemporaryDirectory() as temp:
            root = Path(temp)
            command = self._runner(root)
            self._local_evidence(root, conflicting_facts=True)
            context = build_engine(config=self._config(root, command)).process(
                "Quelle est la capitale de la Bretagne ?"
            )
            attempts = [record.attempt for record in context.execution_history
                        if record.module_id == "ncm_reasoning_refinement" and record.status.value == "completed"]
            verification_attempts = [record.attempt for record in context.execution_history
                                     if record.module_id == "final_verification" and record.status.value == "completed"]
            self.assertEqual(attempts, [1, 2])
            self.assertEqual(verification_attempts, [1, 2])

    def test_ncm_ablation_removes_both_concept_and_refinement_stages(self) -> None:
        cfg = variant_config(deepcopy(DEFAULT_CONFIG), "uca_without_ncm")
        self.assertIsNotNone(cfg)
        pipeline = cfg["pipeline"]["order"]
        self.assertNotIn("ncm_concept_generation", pipeline)
        self.assertNotIn("ncm_reasoning_refinement", pipeline)


if __name__ == "__main__":
    unittest.main()
