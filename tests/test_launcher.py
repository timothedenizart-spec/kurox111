"""Tests for the single-file launcher (UCA-15): one file starts everything —
interface AND live chat."""
from __future__ import annotations

from pathlib import Path
import ast
import json
import sys
import unittest
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lancer_uca import ApplicationComplete, lancer


class LauncherTests(unittest.TestCase):
    def test_application_builds_engine_and_page_once(self) -> None:
        app = ApplicationComplete(".")
        summary = app.status_summary()
        self.assertEqual(summary["modules"], 15)
        self.assertEqual(summary["execution_mode"], "parallel_levels")
        self.assertIn("Interface autonome", app.page)
        self.assertIn("window.UCA_BOOT = ", app.page)

    def test_single_file_serves_page_and_live_chat(self) -> None:
        server, url = lancer(".", host="127.0.0.1", port=0, open_browser=False)
        try:
            import threading
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_address[1]}"
            # 1) La page autonome est servie
            with urllib.request.urlopen(base + "/", timeout=15) as reply:
                page = reply.read().decode("utf-8")
            self.assertIn("Interface autonome", page)
            self.assertNotIn("<script src", page)  # aucune ressource externe
            # 2) Le statut réel est exposé (la page activera le chat)
            with urllib.request.urlopen(base + "/api/status", timeout=15) as reply:
                status = json.loads(reply.read())
            self.assertIn("ncm_response_refiner", status["modules"])
            # 3) Le tchat est VIVANT : calcul exact réel via l'API
            body = json.dumps({"message": "calcule 22/7 + 3", "developer": False}).encode()
            request = urllib.request.Request(base + "/api/chat", data=body,
                                             headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(request, timeout=30) as reply:
                chat = json.loads(reply.read())
            self.assertIn("43/7", chat["answer"])
        finally:
            server.shutdown()
            server.server_close()

    def test_launcher_is_one_standalone_file(self) -> None:
        path = Path(__file__).resolve().parent.parent / "lancer_uca.py"
        self.assertTrue(path.exists())
        tree = ast.parse(path.read_text(encoding="utf-8"))
        external = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                external.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                external.add(node.module.split(".")[0])
        stdlib = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else set()
        self.assertEqual(external - stdlib - {"uca"}, set(),
                         "le lanceur ne doit dépendre que de la stdlib et du paquet uca local")


if __name__ == "__main__":
    unittest.main()
