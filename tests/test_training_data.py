from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.validate_training_data import validate


def example(identifier: str, split: str, user: str | None = None) -> dict:
    return {"id": identifier, "split": split, "source": "curated-local-v1", "license": "CC-BY-4.0",
            "messages": [{"role": "user", "content": user or f"Question {identifier}"},
                         {"role": "assistant", "content": f"Answer {identifier}"}]}


class TrainingDataValidationTests(unittest.TestCase):
    def write_rows(self, path: Path, rows: list[dict]) -> None:
        path.write_text("".join(json.dumps(item) + "\n" for item in rows), encoding="utf-8")

    def test_accepts_clean_license_attributed_three_way_splits(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "data.jsonl"
            self.write_rows(path, [example("a", "train"), example("b", "validation"), example("c", "test")])
            result = validate(path)
            self.assertTrue(result["valid"], result["errors"])
            self.assertEqual(result["counts"], {"test": 1, "train": 1, "validation": 1})

    def test_rejects_unknown_license_and_exact_cross_split_leakage(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "data.jsonl"
            first = example("a", "train", "What is two plus two?")
            second = example("b", "test", "What is two plus two?")
            second["messages"] = first["messages"]
            second["license"] = "unknown"
            self.write_rows(path, [first, second, example("c", "validation")])
            result = validate(path)
            self.assertFalse(result["valid"])
            self.assertTrue(any("duplicate" in error for error in result["errors"]))
            self.assertTrue(any("license" in error for error in result["errors"]))

    def test_rejects_malformed_json_lines(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "data.jsonl"
            path.write_text('{"ok":true}\nnot-json\n', encoding="utf-8")
            result = validate(path, require_all_splits=False)
            self.assertFalse(result["valid"])
            self.assertTrue(any("invalid JSON" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
