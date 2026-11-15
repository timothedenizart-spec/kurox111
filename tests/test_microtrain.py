"""Tests for UCA-09 local micro-training (masked-denoiser contract instance)."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json
import subprocess
import sys
import unittest

from uca.microtrain import (MaskedDenoiser, MicroTokenizer, load_corpus_sentences,
                          make_calibration_cases, normalize_text, split_train_holdout, train)

TINY_CORPUS = [
    "la bretagne est une région du nord ouest de la france",
    "rennes est la capitale de la bretagne",
    "la normandie est une région du nord de la france",
    "rouen est la capitale historique de la normandie",
    "la bretagne et la normandie partagent le mont saint michel",
    "le mont saint michel est une île commune française",
    "nantes est une ville de bretagne historique",
    "rennes et nantes sont deux villes bretonnes",
    "la france est un pays d europe occidentale",
    "l europe est un continent de l hémisphère nord",
    "la normandie borde la manche au nord",
    "la bretagne borde l océan atlantique à l ouest",
    "la manche sépare la france de l angleterre",
    "l atlantique est un océan à l ouest de l europe",
    "rennes compte de nombreux étudiants en france",
    "rouen compte un port important sur la seine",
    "la seine traverse rouen et paris en france",
    "paris est la capitale de la france entière",
    "la région bretagne compte quatre départements français",
    "la normandie compte cinq départements en france",
    "les départements bretons incluent le finistère et le morbihan",
    "le finistère est le département le plus ouest de france",
    "le morbihan borde le golfe du même nom en bretagne",
    "la bretagne possède une langue régionale celtique le breton",
]


class TokenizerTests(unittest.TestCase):
    def test_normalize_and_roundtrip(self) -> None:
        self.assertEqual(normalize_text("La Bretagne, Région!"), ["la", "bretagne", "région"])
        tokenizer = MicroTokenizer.build(TINY_CORPUS, min_freq=1)
        ids = tokenizer.encode("La Bretagne, Région !")
        self.assertEqual(tokenizer.decode(ids), "la bretagne région")
        self.assertEqual(tokenizer.encode(tokenizer.decode(ids)), ids)

    def test_vocab_is_deterministic(self) -> None:
        a = MicroTokenizer.build(TINY_CORPUS, min_freq=2)
        b = MicroTokenizer.build(TINY_CORPUS, min_freq=2)
        self.assertEqual(a.vocab, b.vocab)
        self.assertEqual(a.vocab[2], "[MASK]")


class TrainingTests(unittest.TestCase):
    def test_training_actually_learns_and_is_deterministic(self) -> None:
        first = train(TINY_CORPUS, dim=16, epochs=25, seed=7)
        second = train(TINY_CORPUS, dim=16, epochs=25, seed=7)
        metrics = first["metrics"]
        self.assertLess(metrics["loss_curve"]["final_epoch_mean_ce"],
                        metrics["loss_curve"]["first_epoch_mean_ce"])
        self.assertLess(metrics["holdout"]["model_perplexity"],
                        metrics["holdout"]["uniform_baseline_perplexity"])
        import numpy as np
        np.testing.assert_array_equal(first["model"].W, second["model"].W)
        np.testing.assert_array_equal(first["model"].E, second["model"].E)

    def test_split_is_deterministic_and_disjoint(self) -> None:
        train_a, hold_a = split_train_holdout(TINY_CORPUS)
        train_b, hold_b = split_train_holdout(TINY_CORPUS)
        self.assertEqual(train_a, train_b)
        self.assertEqual(hold_a, hold_b)
        self.assertFalse(set(train_a) & set(hold_a))

    def test_calibration_cases_are_corruptions_with_references(self) -> None:
        tokenizer = MicroTokenizer.build(TINY_CORPUS, min_freq=1)
        cases = make_calibration_cases(TINY_CORPUS, tokenizer, limit=6, seed=5)
        self.assertTrue(cases)
        for case in cases:
            self.assertNotEqual(case["text"], case["reference"])
            again = make_calibration_cases(TINY_CORPUS, tokenizer, limit=6, seed=5)
            self.assertEqual(cases, again)


class RunnerShimTests(unittest.TestCase):
    def test_contract_roundtrip(self) -> None:
        with TemporaryDirectory() as temp:
            result = train(TINY_CORPUS, dim=16, epochs=12, seed=3)
            result["model"].save(temp)
            result["tokenizer"].save(temp)
            payload = {"operation": "masked_denoise", "architecture": "nanodiff_masked_denoiser",
                       "strategy": "single_pass", "token_ids": result["tokenizer"].encode(TINY_CORPUS[0]),
                       "masked_token_ids": [1] * 8, "mask_positions": [2, 3],
                       "mask_token_id": result["tokenizer"].mask_token_id, "contract_version": 1}
            completed = subprocess.run(
                [sys.executable, "shims/nanodiff_micro_runner.py", temp],
                input=json.dumps(payload), text=True, capture_output=True, timeout=60)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            response = json.loads(completed.stdout)
            self.assertIn("candidate_token_ids", response)
            self.assertIn("candidate_score", response)
            self.assertIn("calibration_id", response)
            self.assertEqual(len(response["candidate_token_ids"]), len(payload["masked_token_ids"]))

    def test_adapter_capability_and_full_calibration_if_transformers(self) -> None:
        transformers = pytest_free_import("transformers")
        if not transformers:
            self.skipTest("transformers not installed in this environment")
        with TemporaryDirectory() as temp:
            result = train(TINY_CORPUS, dim=16, epochs=12, seed=11)
            result["model"].save(temp)
            result["tokenizer"].save(temp)
            result["tokenizer"].save_hf(Path(temp) / "tokenizer")
            from uca.model_adapters import MaskedNanoDiffAdapter
            from uca.nanodiff_validation import validate_masked_denoiser
            root = Path(temp)
            shim = root / "shim.py"
            shim.write_text(Path("shims/nanodiff_micro_runner.py").read_text(encoding="utf-8"))
            config = {"path": temp, "tokenizer_path": str(root / "tokenizer"),
                      "runner_command": f"{sys.executable} {shim} {temp}",
                      "mask_token_id": result["tokenizer"].mask_token_id, "validated": False,
                      "strategies": ["single_pass"]}
            adapter = MaskedNanoDiffAdapter(config, {"_root": temp})
            self.assertEqual(adapter.calibration_capability().status.value, "functional")
            # Deterministic hand-built cases: one controlled corruption per sentence.
            tokenizer = result["tokenizer"]
            cases = []
            for index, sentence in enumerate(TINY_CORPUS[:4]):
                ids = tokenizer.encode(sentence)
                ids[2] = tokenizer.token_to_id.get("france", 1)  # known in-vocab corruption
                cases.append({"id": f"t-{index}", "text": tokenizer.decode(ids), "reference": sentence})
            report = validate_masked_denoiser(adapter, cases, timeout=60)
            self.assertEqual(report["status"], "executed")
            self.assertIn("mean_delta", report)

    def test_empty_calibration_is_inconclusive_not_a_crash(self) -> None:
        with TemporaryDirectory() as temp:
            result = train(TINY_CORPUS, dim=16, epochs=6, seed=5)
            result["model"].save(temp)
            result["tokenizer"].save(temp)
            result["tokenizer"].save_hf(Path(temp) / "tokenizer")
            from uca.model_adapters import MaskedNanoDiffAdapter
            from uca.nanodiff_validation import validate_masked_denoiser
            root = Path(temp)
            shim = root / "shim.py"
            shim.write_text(Path("shims/nanodiff_micro_runner.py").read_text(encoding="utf-8"))
            config = {"path": temp, "tokenizer_path": str(root / "tokenizer"),
                      "runner_command": f"{sys.executable} {shim} {temp}",
                      "mask_token_id": result["tokenizer"].mask_token_id, "validated": False,
                      "strategies": ["single_pass"]}
            adapter = MaskedNanoDiffAdapter(config, {"_root": temp})
            # Guard contract: an empty case list must be an honest "not_executable",
            # never a ZeroDivisionError. (The CLI's load_cases already enforces ≥1 case.)
            report = validate_masked_denoiser(adapter, [], timeout=60)
            self.assertEqual(report["status"], "not_executable")
            self.assertFalse(report["validated_for_activation"])


def pytest_free_import(name: str) -> bool:
    try:
        __import__(name)
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    unittest.main()
