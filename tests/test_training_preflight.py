from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from uca.training_preflight import TRAINING_SCHEMA, preflight_training, sha256_file


def write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def make_manifest(root: Path, *, device: str = "cpu") -> dict:
    model = root / "models" / "tiny-model"; model.mkdir(parents=True)
    write(model / "config.json", "{}\n")
    card = write(root / "training-data" / "approved" / "DATA_CARD.md", "# approved\n")
    train = write(root / "training-data" / "approved" / "train.jsonl", '{"id":"train-1","text":"un"}\n')
    validation = write(root / "training-data" / "approved" / "validation.jsonl", '{"id":"val-1","text":"deux"}\n')
    holdout = write(root / "training-data" / "approved" / "holdout.jsonl", '{"id":"holdout-1","text":"trois"}\n')
    suite = write(root / "benchmarks" / "holdout.jsonl", '{"id":"bench-1","prompt":"test"}\n')
    return {
        "schema": TRAINING_SCHEMA,
        "run_id": "tiny-lora-smoke-v1",
        "objective": "continued_pretraining",
        "base_model": {"path": str(model.relative_to(root)), "sha256": "a" * 64,
                       "architecture": "causal_lm", "tokenizer_path": str(model.relative_to(root)), "license": "MIT"},
        "data": {"train_path": str(train.relative_to(root)), "validation_path": str(validation.relative_to(root)),
                 "holdout_path": str(holdout.relative_to(root)),
                 "sha256": {"train": digest(train), "validation": digest(validation), "holdout": digest(holdout)},
                 "license": "CC-BY-4.0", "data_card": str(card.relative_to(root)),
                 "personal_data_review": "approved"},
        "method": {"kind": "lora", "seed": 7, "max_steps": 2, "learning_rate": 0.0001,
                   "max_sequence_length": 64, "prompt_template_version": "v1"},
        "budget": {"device": device, "max_wall_minutes": 5, "max_gpu_memory_gib": None, "max_checkpoints": 1},
        "output": {"path": "runs/tiny-lora-smoke-v1", "adapter_only": True},
        "evaluation": {"baseline": str(model.relative_to(root)), "benchmark_suite": str(suite.relative_to(root)),
                       "acceptance_criteria": ["no leakage", "no regression"]},
    }


class TrainingPreflightTests(unittest.TestCase):
    def test_cpu_manifest_with_local_disjoint_data_is_ready(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            report = preflight_training(make_manifest(root), root)
            self.assertTrue(report.ready, report.errors)
            self.assertEqual(report.dataset_counts, {"train": 1, "validation": 1, "holdout": 1})
            self.assertFalse(report.cuda_visible)
            self.assertEqual(len(report.file_digests["train"]), 64)

    def test_detects_data_leakage_and_digest_tampering(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary); manifest = make_manifest(root)
            validation = root / manifest["data"]["validation_path"]
            validation.write_text('{"id":"train-1","text":"duplication"}\n', encoding="utf-8")
            report = preflight_training(manifest, root)
            self.assertFalse(report.ready)
            self.assertTrue(any("does not match" in error for error in report.errors))
            self.assertTrue(any("Dataset leakage" in error for error in report.errors))

    def test_placeholder_and_missing_cuda_are_hard_blockers(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary); manifest = make_manifest(root, device="cuda")
            manifest["base_model"]["path"] = "models/REPLACE_WITH_LOCAL_CHECKPOINT"
            report = preflight_training(manifest, root)
            self.assertFalse(report.ready)
            self.assertTrue(any("placeholder" in error for error in report.errors))
            self.assertTrue(any("CUDA requested" in error for error in report.errors))

    def test_missing_or_unknown_objective_is_a_blocker(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary); manifest = make_manifest(root)
            manifest.pop("objective")
            report = preflight_training(manifest, root)
            self.assertFalse(report.ready)
            self.assertTrue(any("objective" in error for error in report.errors))

    def test_sha256_file_is_streaming_equivalent(self) -> None:
        with TemporaryDirectory() as temporary:
            sample = write(Path(temporary) / "sample.bin", "abc" * 100000)
            self.assertEqual(sha256_file(sample), sha256(sample.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
