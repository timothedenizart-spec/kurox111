"""Tests for the advanced cognitive extensions: VSA memory, Hopfield attractors,
surprisal monitoring, offline consolidation, and the parallel-levels engine."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from uca.associative import HopfieldNetwork, bipolar_code, corrupt
from uca.config import DEFAULT_CONFIG
from uca.consolidation import consolidate
from uca.factory import build_engine
from uca.predictive import LocalSurprisalModel, corpus_background, novelty_report
from uca.storage import import_documents, initialize_knowledge_db
from uca.types import ArtifactKind
from uca.vsa import HyperMemory, bind, bundle, similarity


class VectorSymbolicMemoryTests(unittest.TestCase):
    FACTS = [
        {"subject": "Bretagne", "predicate": "capitale", "object": "Rennes"},
        {"subject": "Normandie", "predicate": "capitale", "object": "Rouen"},
        {"subject": "Normandie", "predicate": "langue", "object": "français"},
        {"subject": "Bretagne", "predicate": "langue", "object": "français"},
    ]

    def make_memory(self) -> HyperMemory:
        memory = HyperMemory()
        for fact in self.FACTS:
            memory.encode_fact(fact["subject"], fact["predicate"], fact["object"],
                               fact_id=f"f-{fact['subject']}")
        return memory

    def test_binding_is_an_involution(self) -> None:
        memory = HyperMemory()
        left, right = memory.vector("alpha"), memory.vector("beta")
        self.assertEqual(bind(bind(left, right), right), left)

    def test_holographic_completion_recovers_the_encoded_object(self) -> None:
        memory = self.make_memory()
        completion = memory.complete("Bretagne", "capitale")
        self.assertTrue(completion)
        # Deterministic holographic recall: the encoded filler must rank first
        # with a clearly positive margin over noise-floor candidates.
        self.assertEqual(completion[0]["object"], "Rennes")
        self.assertGreater(completion[0]["score"], 0.15)

    def test_reconstruction_probe_is_perfect_for_small_fact_sets(self) -> None:
        fidelity = self.make_memory().reconstruct_check()
        self.assertEqual(fidelity["facts"], 4)
        self.assertEqual(fidelity["top1_accuracy"], 1.0)

    def test_structural_profiles_make_role_sharing_entities_similar(self) -> None:
        memory = self.make_memory()
        bretagne = memory.entity_profile("Bretagne", self.FACTS)
        normandie = memory.entity_profile("Normandie", self.FACTS)
        independent = memory.vector("entité-sans-lien")
        shared = similarity(bretagne, normandie)
        self.assertGreater(shared, similarity(bretagne, independent))

    def test_analogical_transfer_is_emitted_as_weighted_hypothesis(self) -> None:
        memory = self.make_memory()
        # Bretagne has both predicates; Normandie is missing a region predicate here.
        facts = self.FACTS + [{"subject": "Bretagne", "predicate": "region", "object": "France"}]
        memory.encode_fact("Bretagne", "region", "France", fact_id="f-extra")
        transfers = memory.analogical_transfer("Normandie", "region",
                                               sources=["Bretagne", "Normandie"], facts=facts)
        self.assertTrue(transfers)
        self.assertEqual(transfers[0]["object"], "France")
        self.assertGreater(transfers[0]["analogy_weight"], 0)


class HopfieldAttractorTests(unittest.TestCase):
    def test_completion_recovers_corrupted_stored_pattern(self) -> None:
        patterns = [bipolar_code(key) for key in ("bretagne", "rennes", "normandie")]
        network = HopfieldNetwork()
        network.store_all(patterns)
        cue = corrupt(patterns[0], flips=8, seed=7)
        result = network.recall(cue)
        self.assertTrue(result["converged"])
        self.assertEqual(result["state"], patterns[0])  # exact denoising at this tiny load
        index, overlap = network.nearest_stored(result["state"])
        self.assertEqual((index, overlap), (0, 1.0))

    def test_capacity_limit_is_an_honest_refusal(self) -> None:
        network = HopfieldNetwork(size=64)  # capacity: int(64*0.15) = 9
        for number in range(9):
            network.store(bipolar_code(f"pattern-{number}", size=64))
        with self.assertRaises(ValueError):
            network.store(bipolar_code("pattern-de-trop", size=64))

    def test_recall_requires_stored_patterns(self) -> None:
        network = HopfieldNetwork(size=64)
        with self.assertRaises(ValueError):
            network.recall([1] * 64)


class SurprisalMonitorTests(unittest.TestCase):
    CORPUS = ["La Bretagne est une région française.", "Rennes est la capitale de la Bretagne."]

    def test_novel_token_is_more_surprising_than_in_corpus_text(self) -> None:
        model = LocalSurprisalModel()
        model.train(self.CORPUS)
        known = model.sentence_profile("La Bretagne est une région française.")
        novel = model.sentence_profile("La Bretagne est une région ptérodactyle.")
        self.assertLess(known["mean_surprisal"], novel["mean_surprisal"])
        self.assertIn("ptérodactyle", {item["token"] for item in novel["surprising_tokens"]})

    def test_novelty_flag_uses_corpus_background(self) -> None:
        model = LocalSurprisalModel()
        model.train(self.CORPUS)
        background = corpus_background(model, self.CORPUS)["background_mean"]
        calm = novelty_report(model, self.CORPUS[0], background_mean=background)
        wild = novelty_report(model, "zyzzyva quasimodo bretagne xylophone", background_mean=background)
        self.assertFalse(calm["flagged"])
        self.assertTrue(wild["flagged"])

    def test_empty_model_is_inconclusive_not_negative(self) -> None:
        model = LocalSurprisalModel()
        report = novelty_report(model, "texte", background_mean=None)
        self.assertEqual(report["reason"], "inconclusive")
        self.assertFalse(report["flagged"])


class ConsolidationTests(unittest.TestCase):
    def make_root(self, root: Path) -> Path:
        (root / "data").mkdir(parents=True)
        (root / "data/memory.json").write_text('{"entries": []}', encoding="utf-8")
        (root / "data/operator_facts.json").write_text(json.dumps({"facts": [
            {"id": "f1", "subject": "Bretagne", "predicate": "capitale", "object": "Rennes"},
            {"id": "f2", "subject": "Bretagne", "predicate": "pays", "object": "France"},
        ]}), encoding="utf-8")
        db = root / "data/knowledge.sqlite"
        initialize_knowledge_db(db)
        import_documents(db, [
            {"doc_id": "d1", "content": "La Bretagne et Rennes sont liées administrativement.", "provenance": "test"},
            {"doc_id": "d2", "content": "Rennes est en Bretagne, région de France.", "provenance": "test"},
            {"doc_id": "d3", "content": "Aucun rapport ici.", "provenance": "test"},
        ])
        return root

    def test_consolidation_replay_is_deterministic_and_provenanced(self) -> None:
        with TemporaryDirectory() as temp:
            root = self.make_root(Path(temp))
            first = consolidate(root / "data/operator_facts.json", root / "data/knowledge.sqlite",
                                "documents", root / "data/associations.json")
            edges_first = first["edges"]
            second = consolidate(root / "data/operator_facts.json", root / "data/knowledge.sqlite",
                                 "documents", root / "data/associations.json")
            self.assertEqual(edges_first, second["edges"])  # deterministic replay
            pair = {edge["a"] for edge in edges_first}, {edge["b"] for edge in edges_first}
            self.assertTrue(any(edge["a"] == "Bretagne" and edge["b"] == "Rennes" for edge in edges_first))
            edge = next(edge for edge in edges_first if edge["a"] == "Bretagne" and edge["b"] == "Rennes")
            self.assertEqual(edge["supporting_document_ids"], ["d1", "d2"])
            self.assertGreater(edge["strength"], 0)

    def test_pipeline_module_reports_absent_store_then_surfaces_proposals(self) -> None:
        with TemporaryDirectory() as temp:
            root = self.make_root(Path(temp))
            config = deepcopy(DEFAULT_CONFIG)
            config["_root"] = str(root)
            before = build_engine(config=config).process("Où est Rennes ?")
            self.assertEqual(before.module_states["associative_consolidation"]["status"], "unavailable")
            self.assertEqual(before.artifacts_of(ArtifactKind.PROPOSAL), [])
            consolidate(root / "data/operator_facts.json", root / "data/knowledge.sqlite",
                        "documents", root / "data/associations.json")
            after = build_engine(config=config).process("Où est Rennes ?")
            self.assertEqual(after.module_states["associative_consolidation"]["status"], "functional")
            proposals = after.artifacts_of(ArtifactKind.PROPOSAL)
            self.assertTrue(any("co-occurrences" in item.content.get("text", "") for item in proposals))
            for item in proposals:  # invariant: associations never reach the fact bin
                self.assertEqual(item.content.get("status"), "NON_VERIFIE")
            self.assertFalse(any("Association" in str(fact) for fact in after.symbolic_facts))


class ParallelLevelsEngineTests(unittest.TestCase):
    def make_config(self, root: Path) -> dict:
        config = deepcopy(DEFAULT_CONFIG)
        config["_root"] = str(root)
        return config

    def make_root(self, root: Path) -> Path:
        (root / "data").mkdir(parents=True)
        (root / "data/memory.json").write_text(json.dumps({"entries": [
            {"id": "keep", "text": "Préférence explicitement enregistrée : Bretagne.", "explicit": True,
             "tags": ["Bretagne"]},
            {"id": "ignore", "text": "Ne jamais montrer", "explicit": False, "tags": ["Bretagne"]},
        ]}), encoding="utf-8")
        initialize_knowledge_db(root / "data/knowledge.sqlite")
        import_documents(root / "data/knowledge.sqlite", [
            {"doc_id": "fr-shard-1", "content": "La Bretagne est une région française.",
             "provenance": "wikipedia-fr-local-shard", "metadata": {"shard": "test"}},
        ])
        return root

    def test_levels_respect_declared_dependencies(self) -> None:
        with TemporaryDirectory() as temp:
            engine = build_engine(config=self.make_config(self.make_root(Path(temp))))
            levels = engine.levels
            position = {module_id: index for index, level in enumerate(levels) for module_id in level}
            for module_id, module in engine.modules.items():
                for dependency in module.dependencies:
                    if dependency in position and module_id in position:
                        self.assertLess(position[dependency], position[module_id],
                                        f"{module_id} must run after {dependency}")
            joined = [module_id for level in levels for module_id in level]
            self.assertEqual(joined, engine.pipeline)  # canonical order preserved

    def test_parallel_levels_match_sequential_outputs_for_local_assets(self) -> None:
        with TemporaryDirectory() as temp:
            root = self.make_root(Path(temp))
            sequential_config = self.make_config(root)
            sequential_config["engine"]["execution_mode"] = "sequential"
            parallel_config = self.make_config(root)
            parallel_config["engine"]["execution_mode"] = "parallel_levels"
            sequential = build_engine(config=sequential_config).process(
                "Que contient le corpus local sur la Bretagne ?")
            parallel = build_engine(config=parallel_config).process(
                "Que contient le corpus local sur la Bretagne ?")
            self.assertEqual(parallel.final_response, sequential.final_response)
            seq_states = {mid: state["status"] for mid, state in sequential.module_states.items()}
            par_states = {mid: state["status"] for mid, state in parallel.module_states.items()}
            self.assertEqual(par_states, seq_states)
            seq_order = [record.module_id for record in sequential.execution_history]
            par_order = [record.module_id for record in parallel.execution_history]
            self.assertEqual(par_order, seq_order)  # deterministic canonical application
            seq_kinds = [item.kind.value for item in sequential.artifacts]
            par_kinds = [item.kind.value for item in parallel.artifacts]
            self.assertEqual(par_kinds, seq_kinds)

    def test_arithmetic_exactness_survives_parallel_scheduling(self) -> None:
        with TemporaryDirectory() as temp:
            root = self.make_root(Path(temp))
            engine = build_engine(config=self.make_config(root))
            context = engine.process("calcule 22/7 + 3")
            computations = context.artifacts_of(ArtifactKind.COMPUTATION)
            self.assertEqual(computations[0].content["exact_value"], "43/7")
            self.assertIn("43/7", context.final_response or "")


if __name__ == "__main__":
    unittest.main()
