from __future__ import annotations

import os
import unittest
from pathlib import Path

from uca.config import load_config
from uca.factory import build_engine
from uca.web import UcaWebApplication, INDEX_HTML


class WebApplicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root_dir = Path(__file__).resolve().parent.parent
        self.config = load_config(self.root_dir)
        self.engine = build_engine(self.root_dir, self.config)
        self.app = UcaWebApplication(self.engine)

    def test_index_html_has_dashboard_tabs_and_presets(self) -> None:
        self.assertIn("Cortex Parallèle", INDEX_HTML)
        self.assertIn("Pipeline & Modules", INDEX_HTML)
        self.assertIn("Collectif Multi-Agents", INDEX_HTML)
        self.assertIn("Résous 7*x - 14 = 28", INDEX_HTML)
        self.assertIn("thalamo-cortical", INDEX_HTML)

    def test_status_endpoint_returns_expected_modules(self) -> None:
        status = self.app.status()
        self.assertIn("pipeline", status)
        modules = status.get("modules", {})
        self.assertIn("knowledge_retrieval", modules)
        self.assertIn("symbolic_processing", modules)
        self.assertIn("parallel_cortex", modules)
        self.assertIn("ncm_concept_generation", modules)
        self.assertEqual(modules["parallel_cortex"]["status"], "functional")

    def test_chat_endpoint_executes_reasoning(self) -> None:
        result = self.app.chat("3*x + 7 = 22", developer=True)
        self.assertIn("answer", result)
        self.assertIn("computations", result)
        self.assertIn("x = 5", result["answer"])
        computations = result.get("computations", [])
        self.assertTrue(any(c.get("content", {}).get("operation") == "exact_algebra_and_equations" for c in computations))

    def test_launchers_exist_and_executable(self) -> None:
        sh_launcher = self.root_dir / "lancer_interface.sh"
        py_launcher = self.root_dir / "lancer_interface.py"
        self.assertTrue(sh_launcher.exists())
        self.assertTrue(py_launcher.exists())
        self.assertTrue(os.access(str(sh_launcher), os.X_OK))
        self.assertTrue(os.access(str(py_launcher), os.X_OK))


if __name__ == "__main__":
    unittest.main()
