"""Tests for the deterministic cognitive-behavior evaluation harness (UCA-05b)."""
from __future__ import annotations

from pathlib import Path
import json
import unittest

from uca.eval_cognition import EVAL_SCHEMA, load_eval_cases, run_evaluation


EXAMPLE = Path(__file__).resolve().parent.parent / "benchmarks" / "cognitive_checks.example.jsonl"


class CognitiveEvaluationTests(unittest.TestCase):
    def test_bundled_contract_cases_all_pass(self) -> None:
        report = run_evaluation(load_eval_cases(EXAMPLE))
        self.assertEqual(report["schema"], EVAL_SCHEMA)
        self.assertGreaterEqual(report["summary"]["total"], 6)
        failed = [case["id"] for case in report["cases"] if not case["passed"]]
        self.assertEqual(failed, [], f"contract cases failing: {failed}")
        ids = {case["id"] for case in report["cases"]}
        for expected in ("arithmetique-exacte", "absence-honnete", "memoire-optin-uniquement",
                         "conflit-symbolique-borne", "analogies-jamais-promues",
                         "consolidation-absente-declaree", "consolidation-active-provenant"):
            self.assertIn(expected, ids)

    def test_a_violated_contract_fails_loudly_without_crashing(self) -> None:
        case = {"id": "doit-echouer", "prompt": "calcule 1+1",
                "fixtures": {}, "checks": [{"type": "response_contains", "value": "reponse-impossible-xyz"},
                                           {"type": "check_inconnu_volontairement"},
                                           {"type": "computation_exact", "exact": "2"}]}
        report = run_evaluation([case])
        result = report["cases"][0]
        self.assertFalse(result["passed"])
        ok_flags = [item["ok"] for item in result["checks"]]
        self.assertEqual(ok_flags, [False, False, True])  # fail, fail, pass
        self.assertEqual(report["summary"]["failed"], 1)

    def test_report_datatypes_and_notice(self) -> None:
        case = {"id": "minimal", "prompt": "Bonjour",
                "fixtures": {}, "checks": [{"type": "module_status", "module": "final_response", "status": "functional"}]}
        report = run_evaluation([case])
        json.dumps(report)  # fully JSON-serializable
        self.assertIn("No quality", report["notice"])
        self.assertEqual(report["summary"]["passed"], 1)


if __name__ == "__main__":
    unittest.main()
