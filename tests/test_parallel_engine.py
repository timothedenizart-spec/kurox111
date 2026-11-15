from __future__ import annotations

from threading import Barrier
import time
import unittest

from uca.engine import UnifiedCognitiveEngine
from uca.modules import CognitiveModule
from uca.types import Artifact, ArtifactKind, ModuleResult, Provenance


class ParallelEngineTests(unittest.TestCase):
    def test_parallel_peers_share_one_snapshot_and_merge_in_pipeline_order(self) -> None:
        rendezvous = Barrier(2)

        class Peer(CognitiveModule):
            def run(self, snapshot):
                snapshot["artifacts"].append({"private_to": self.module_id})
                rendezvous.wait(timeout=2)
                if self.module_id == "slow":
                    time.sleep(0.04)
                return ModuleResult(artifacts=(Artifact(
                    ArtifactKind.DIAGNOSTIC,
                    {"module": self.module_id, "private_snapshot_size": len(snapshot["artifacts"])},
                    Provenance(self.module_id),
                ),))

        engine = UnifiedCognitiveEngine(
            [Peer("slow"), Peer("fast")], ["slow", "fast"],
            parallel_groups=[["slow", "fast"]], max_parallel_workers=2,
        )
        result = engine.process("parallel test")
        artifacts = result.artifacts_of(ArtifactKind.DIAGNOSTIC)
        self.assertEqual([item.content["module"] for item in artifacts], ["slow", "fast"])
        self.assertEqual([item.content["private_snapshot_size"] for item in artifacts], [1, 1])
        self.assertEqual([item.module_id for item in result.execution_history], ["slow", "fast"])
        self.assertTrue(all(result.module_states[name]["execution"] == "completed" for name in ("slow", "fast")))

    def test_parallel_groups_reject_dependency_edges(self) -> None:
        class Peer(CognitiveModule):
            def run(self, snapshot):
                return ModuleResult()

        with self.assertRaisesRegex(ValueError, "dependency edge"):
            UnifiedCognitiveEngine(
                [Peer("first"), Peer("second", dependencies=("first",))],
                ["first", "second"], parallel_groups=[["first", "second"]],
            )


if __name__ == "__main__":
    unittest.main()
