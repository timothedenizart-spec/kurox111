from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from uca.auxiliary import AuxiliaryRegistry
from uca.config import DEFAULT_CONFIG
from uca.training import BASE_MODEL_ID, TARGET, TRAINING_SCHEMA, training_preflight


class TrainingPreflightTests(unittest.TestCase):
    def valid_config(self, root: Path) -> dict:
        model = root / "models" / "smollm2-360"
        model.mkdir(parents=True)
        (model / "config.json").write_text("{}", encoding="utf-8")
        (model / "tokenizer_config.json").write_text("{}", encoding="utf-8")
        (model / "model.safetensors").write_bytes(b"test-weight-placeholder")
        dataset = root / "training" / "approved.jsonl"
        dataset.parent.mkdir()
        dataset.write_text(json.dumps({"id": "one", "text": "Texte SFT local approuvé.",
                                      "source": "curated-local", "license": "CC-BY-4.0"}) + "\n", encoding="utf-8")
        digest = sha256(dataset.read_bytes()).hexdigest()
        manifest = root / "training" / "manifest.json"
        manifest.write_text(json.dumps({
            "schema": TRAINING_SCHEMA, "target": TARGET, "base_model_id": BASE_MODEL_ID,
            "base_checkpoint_fingerprint": AuxiliaryRegistry.checkpoint_fingerprint(model),
            "dataset_sha256": digest, "distillation": False, "contains_user_memory": False,
            "data_rights_confirmed": True, "approved_by": "local-data-steward",
        }), encoding="utf-8")
        cfg = deepcopy(DEFAULT_CONFIG)
        cfg["_root"] = str(root)
        cfg["models"]["smollm2_360"]["path"] = "models/smollm2-360"
        cfg["training"].update({
            "enabled": True, "target": TARGET, "dataset_path": "training/approved.jsonl",
            "manifest_path": "training/manifest.json", "output_dir": "training-runs/adapter",
            "lora_target_modules": ["q_proj", "v_proj"],
        })
        return cfg

    def test_approved_local_assets_pass_preflight_without_loading_model(self) -> None:
        with TemporaryDirectory() as temp:
            report = training_preflight(self.valid_config(Path(temp)))
            self.assertTrue(report["can_train"], report["errors"])
            self.assertEqual(report["dataset"]["records"], 1)
            self.assertEqual(report["policy"]["distillation"], "forbidden")

    def test_preflight_rejects_checkpoint_without_weight_file(self) -> None:
        with TemporaryDirectory() as temp:
            root = Path(temp)
            cfg = self.valid_config(root)
            (root / "models" / "smollm2-360" / "model.safetensors").unlink()
            report = training_preflight(cfg)
            self.assertFalse(report["can_train"])
            self.assertTrue(any("no local weight file" in error for error in report["errors"]))

    def test_manifest_rejects_distillation_and_user_memory(self) -> None:
        with TemporaryDirectory() as temp:
            cfg = self.valid_config(Path(temp))
            manifest_path = Path(temp) / "training" / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["distillation"] = True
            manifest["contains_user_memory"] = True
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            report = training_preflight(cfg)
            self.assertFalse(report["can_train"])
            self.assertTrue(any("distillation" in error for error in report["errors"]))
            self.assertTrue(any("user_memory" in error for error in report["errors"]))

    def test_examples_marked_not_for_training_are_blocked(self) -> None:
        with TemporaryDirectory() as temp:
            cfg = self.valid_config(Path(temp))
            dataset_path = Path(temp) / "training" / "approved.jsonl"
            dataset_path.write_text(json.dumps({"id": "example", "text": "not usable", "source": "example",
                                                 "license": "NO_TRAINING_DATA"}) + "\n", encoding="utf-8")
            report = training_preflight(cfg)
            self.assertFalse(report["can_train"])
            self.assertTrue(any("explicitly marked not for training" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
