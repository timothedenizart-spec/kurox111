from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import urlopen
import json
import unittest

from uca.launcher import _browser_url, initialize_local_stores, start_interface


class LauncherTests(unittest.TestCase):
    def test_initialization_creates_only_empty_local_stores(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = initialize_local_stores(root)
            self.assertTrue((root / "data" / "memory.json").is_file())
            self.assertTrue((root / "data" / "operator_facts.json").is_file())
            self.assertTrue((root / "data" / "knowledge.sqlite").is_file())
            self.assertEqual(json.loads((root / "data" / "memory.json").read_text(encoding="utf-8"))["entries"], [])
            self.assertEqual(config["_root"], str(root.resolve()))

    def test_start_interface_serves_preloaded_status_without_opening_browser(self) -> None:
        with TemporaryDirectory() as temporary:
            session = start_interface(temporary, port=0, open_browser=False)
            try:
                self.assertTrue(session.thread.is_alive())
                self.assertFalse(session.browser_opened)
                self.assertTrue(session.url.startswith("http://127.0.0.1:"))
                self.assertIn("modules", session.status)
                with urlopen(session.url + "api/status", timeout=3) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                self.assertIn("input_processing", payload["modules"])
                self.assertEqual(payload["modules"]["input_processing"]["status"], "functional")
            finally:
                session.close()

    def test_browser_url_translates_wildcard_bind_to_loopback(self) -> None:
        self.assertEqual(_browser_url("0.0.0.0", 8123), "http://127.0.0.1:8123/")
        self.assertEqual(_browser_url("localhost", 8123), "http://localhost:8123/")


if __name__ == "__main__":
    unittest.main()
