"""Tests for the single-file auto-opening interface (UCA-12)."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json
import re
import unittest

from uca.interface import build_interface, collect_boot_payload, render_page


class InterfaceBuilderTests(unittest.TestCase):
    def test_payload_is_real_engine_data(self) -> None:
        payload = collect_boot_payload(".", demo_prompts=("calcule 22/7 + 3",))
        self.assertEqual(len(payload["status"]["modules"]), 14)
        self.assertEqual(payload["status"]["execution_mode"], "parallel_levels")
        self.assertIn("43/7", payload["demo_answers"][0]["answer"])
        self.assertTrue(payload["status"]["parallel_levels"])

    def test_render_injects_valid_json_and_no_external_resources(self) -> None:
        payload = {"generated_at": "t", "status": {"modules": {}, "pipeline": [], "execution_mode": "x"},
                   "demo_answers": [], "model_metrics": None, "cognitive_eval": None}
        html = render_page(payload)
        self.assertNotIn("window.UCA_BOOT = null;", html)  # marker replaced
        raw = re.search(r"window\.UCA_BOOT = (\{[^\n]*\});", html, re.S)
        self.assertIsNotNone(raw)
        self.assertEqual(json.loads(raw.group(1)), payload)
        self.assertNotIn("<script src", html)   # single self-contained file
        self.assertNotIn("<link", html)         # no external stylesheet
        self.assertNotIn("https://", html)      # no CDN / remote call in markup

    def test_build_writes_file_and_embeds_reality(self) -> None:
        with TemporaryDirectory() as temp:
            out = Path(temp) / "uca.html"
            result = build_interface(".", out, open_browser=False)
            self.assertEqual(result["output"], str(out))
            self.assertFalse(result["opened_in_browser"])
            html = out.read_text(encoding="utf-8")
            boot = json.loads(re.search(r"window\.UCA_BOOT = (\{[^\n]*\});", html, re.S).group(1))
            self.assertEqual(len(boot["demo_answers"]), 2)
            self.assertIn("43/7", boot["demo_answers"][0]["answer"])

    def test_missing_template_marker_fails_loudly(self) -> None:
        import uca.interface as module
        original = module.TEMPLATE
        try:
            module.TEMPLATE = Path("/dev/null")  # empty file → no marker
            with self.assertRaises(RuntimeError):
                render_page({})
        finally:
            module.TEMPLATE = original


if __name__ == "__main__":
    unittest.main()
