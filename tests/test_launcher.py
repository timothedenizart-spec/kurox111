from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from unittest.mock import patch
from urllib.request import urlopen
import json
import unittest

from uca import launcher


class LauncherTests(unittest.TestCase):
    def test_prepare_launch_binds_a_free_port_and_serves_honest_status(self) -> None:
        """A launch preparation is usable without a browser or model assets."""
        with TemporaryDirectory() as temp:
            root = Path(temp)
            session = launcher.prepare_launch(root=root, host="127.0.0.1", port=0)
            worker = Thread(target=session.server.serve_forever, daemon=True)
            worker.start()
            try:
                self.assertTrue(session.url.startswith("http://127.0.0.1:"))
                self.assertNotIn(":0/", session.url)
                self.assertTrue(session.readiness["server_ready"])
                self.assertEqual(session.readiness["execution_topology"]["mode"], "staged_parallel")
                # No assets were created or synthesized by preparing the UI.
                self.assertFalse((root / "data").exists())
                self.assertGreaterEqual(session.readiness["module_status_counts"].get("unavailable", 0), 2)

                with urlopen(session.url + "api/status", timeout=3) as response:
                    status = json.loads(response.read().decode("utf-8"))
                self.assertIn("input_processing", status["modules"])
                self.assertEqual(status["modules"]["smollm2_135_analysis"]["status"], "unavailable")
                self.assertEqual(status["modules"]["ncm_reasoning_refinement"]["status"], "disabled_voluntarily")
            finally:
                session.server.shutdown()
                worker.join(timeout=3)
                session.server.server_close()

    def test_main_forwards_no_browser_option_to_launch(self) -> None:
        with patch("uca.launcher.launch", return_value=0) as launch:
            code = launcher.main(["--root", "assets", "--host", "127.0.0.1", "--port", "4567", "--no-browser"])
        self.assertEqual(code, 0)
        launch.assert_called_once_with("assets", "127.0.0.1", 4567, open_browser=False)

    def test_launch_opens_default_browser_after_preparation(self) -> None:
        class Server:
            closed = False

            def serve_forever(self) -> None:
                raise KeyboardInterrupt

            def server_close(self) -> None:
                self.closed = True

        server = Server()
        session = launcher.LaunchSession(server=server, url="http://127.0.0.1:4567/", readiness={})
        with patch("uca.launcher.prepare_launch", return_value=session), \
             patch("uca.launcher.webbrowser.open", return_value=True) as open_browser, \
             patch("builtins.print"):
            self.assertEqual(launcher.launch(open_browser=True), 0)
        open_browser.assert_called_once_with(session.url, new=1, autoraise=True)
        self.assertTrue(server.closed)


if __name__ == "__main__":
    unittest.main()
