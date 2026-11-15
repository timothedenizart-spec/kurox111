from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import math
import unittest

from uca.experiment_registry import (ExperimentRegistry, ManifestValidationError, canonical_json,
                                     compare_metric, manifest_digest, normalize_manifest)


_DIGEST = "a" * 64
_ASSET_DIGEST = "b" * 64


def manifest(**overrides: object) -> dict[str, object]:
    record: dict[str, object] = {
        "experiment_id": "dag-parallel-v1",
        "code_revision": "b1b49f4",
        "config_digest": _DIGEST,
        "baseline": "uca-sequential-v1",
        "intervention": "dag-parallel-v1",
        "task_split": "holdout-v1",
        "assets": [{"id": "local-corpus-v1", "digest": _ASSET_DIGEST, "license": "operator-controlled"}],
        "metrics": {"exact_match": 0.75, "factual_accuracy": None, "p95_latency_ms": 25},
        "ablations": ["no-retrieval"],
        "failures": [],
        "review": {"status": "pending"},
    }
    record.update(overrides)
    return record


class ExperimentRegistryTests(unittest.TestCase):
    def test_canonical_digest_is_stable_and_schema_is_added(self) -> None:
        first = manifest()
        second = {key: first[key] for key in reversed(list(first))}
        normalized = normalize_manifest(first)
        self.assertEqual(normalized["schema"], "uca.experiment.v1")
        self.assertEqual(canonical_json(first), canonical_json(second))
        self.assertEqual(manifest_digest(first), manifest_digest(second))

    def test_manifest_rejects_non_reproducible_or_non_finite_values(self) -> None:
        invalid_records = [
            manifest(experiment_id="Not a valid id"),
            manifest(config_digest="short"),
            manifest(assets=[{"id": "x", "digest": "0" * 63, "license": "test"}]),
            manifest(metrics={"p95": math.nan}),
            manifest(metrics={"p95": True}),
            manifest(ablations=["", "valid"]),
        ]
        for record in invalid_records:
            with self.subTest(record=record):
                with self.assertRaises(ManifestValidationError):
                    normalize_manifest(record)

    def test_registry_writes_content_addressed_record_and_round_trips(self) -> None:
        with TemporaryDirectory() as temporary:
            registry = ExperimentRegistry(Path(temporary) / "experiments")
            saved = registry.record(manifest())
            self.assertTrue(saved.path.exists())
            self.assertIn(saved.digest[:16], saved.path.name)
            self.assertEqual(saved.manifest["metrics"]["factual_accuracy"], None)
            duplicate = registry.record(manifest())
            self.assertEqual(duplicate.path, saved.path)
            loaded = registry.load(saved.path)
            self.assertEqual(loaded.digest, saved.digest)
            self.assertEqual(loaded.manifest, saved.manifest)

    def test_metric_comparison_never_interprets_null_as_an_improvement(self) -> None:
        baseline = manifest(metrics={"quality": 0.4, "human_score": None})
        candidate = manifest(intervention="candidate", metrics={"quality": 0.6, "human_score": None})
        measured = compare_metric(baseline, candidate, "quality")
        self.assertEqual(measured["status"], "measured")
        self.assertEqual(measured["direction"], "improved")
        self.assertAlmostEqual(measured["delta"], 0.2)
        unavailable = compare_metric(baseline, candidate, "human_score")
        self.assertEqual(unavailable["status"], "unavailable")
        self.assertEqual(unavailable["direction"], "unknown")

    def test_metric_direction_handles_lower_cost_as_better(self) -> None:
        baseline = manifest(metrics={"p95_latency_ms": 25})
        candidate = manifest(intervention="faster", metrics={"p95_latency_ms": 20})
        comparison = compare_metric(baseline, candidate, "p95_latency_ms", higher_is_better=False)
        self.assertEqual(comparison["direction"], "improved")


if __name__ == "__main__":
    unittest.main()
