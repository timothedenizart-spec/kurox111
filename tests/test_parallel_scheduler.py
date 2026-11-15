from __future__ import annotations

import time
import unittest

from uca.engine import UnifiedCognitiveEngine
from uca.modules import CognitiveModule
from uca.types import Artifact, ArtifactKind, ModuleResult, Provenance


class _ReadOnlyEvidenceModule(CognitiveModule):
    def __init__(self, module_id: str, delay_seconds: float = 0.12) -> None:
        super().__init__(module_id, parallel_safe=True)
        self.delay_seconds = delay_seconds

    def run(self, snapshot: dict) -> ModuleResult:
        observed = len(snapshot["artifacts"])
        time.sleep(self.delay_seconds)
        return ModuleResult(artifacts=(Artifact(
            ArtifactKind.DIAGNOSTIC,
            {"module": self.module_id, "observed_artifact_count": observed},
            Provenance(self.module_id, implementation="test read-only evidence module"),
        ),), message="read-only evidence completed")


class ParallelSchedulerTests(unittest.TestCase):
    def test_afferent_fanout_uses_one_snapshot_and_canonical_merge_order(self) -> None:
        order = ["user_memory", "knowledge_retrieval", "symbolic_processing"]
        engine = UnifiedCognitiveEngine(
            [_ReadOnlyEvidenceModule(module_id) for module_id in order], order,
            scheduling_mode="staged_parallel", parallel_max_workers=3,
        )
        started = time.perf_counter()
        context = engine.process("test parallel field")
        elapsed = time.perf_counter() - started
        # Three 120 ms modules should share a bounded parallel stage, not a 360 ms serial chain.
        self.assertLess(elapsed, 0.30)
        reports = [record.module_id for record in context.execution_history]
        self.assertEqual(reports, order)
        produced = [artifact for artifact in context.artifacts if artifact.provenance.producer in order]
        self.assertEqual([artifact.provenance.producer for artifact in produced], order)
        self.assertEqual([artifact.content["observed_artifact_count"] for artifact in produced], [0, 0, 0])
        fanout = [artifact for artifact in context.artifacts
                  if artifact.content.get("event") == "parallel_afferent_fanout"]
        self.assertEqual(len(fanout), 1)
        self.assertEqual(fanout[0].content["merge_order"], order)

    def test_sequential_mode_does_not_enter_parallel_fanout(self) -> None:
        order = ["user_memory", "knowledge_retrieval", "symbolic_processing"]
        engine = UnifiedCognitiveEngine(
            [_ReadOnlyEvidenceModule(module_id, delay_seconds=0) for module_id in order], order,
            scheduling_mode="sequential",
        )
        context = engine.process("test sequential field")
        self.assertFalse(any(artifact.content.get("event") == "parallel_afferent_fanout"
                             for artifact in context.artifacts))
        produced = [artifact for artifact in context.artifacts if artifact.provenance.producer in order]
        self.assertEqual([artifact.content["observed_artifact_count"] for artifact in produced], [0, 1, 2])


if __name__ == "__main__":
    unittest.main()
