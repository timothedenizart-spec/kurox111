#!/usr/bin/env python3
"""UCA — UN SEUL FICHIER QUI LANCE TOUT : interface + tchat réel.

Double-cliquez sur ce fichier, ou :

    python lancer_uca.py

Cela démarre le moteur complet (15 modules, contrôle cognitif, raffineur
NCM-local relié à la réflexion, arithmétique exacte…), sert l'interface
autonome préchargée ET l'API locale — puis ouvre automatiquement votre
navigateur avec le tchat **actif** contre le vrai moteur Python.

Départements du fichier : moteur (uca/), page préchargée (uca/interface_page.html),
API (uca/web.py). Ce script n'ajoute que le lancement : aucune ressource externe,
aucun téléchargement, tout reste local sur votre machine.

Options : --root REP (stockage, défaut : répertoire du script) · --port N
(défaut 8080, port libre de repli sinon) · --no-open (sans ouverture auto,
utile sans écran) · --config FICHIER.  Arrêt : Ctrl+C.
"""
from __future__ import annotations

from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any
import argparse
import json
import socket
import sys
import threading
import webbrowser

sys.path.insert(0, str(Path(__file__).resolve().parent))  # le fichier se lance de n'importe où

from uca.config import load_config
from uca.factory import build_engine
from uca.interface import collect_boot_payload, render_page
from uca.web import UcaWebApplication, _Handler


class ApplicationComplete:
    """Everything the single file launches: engine + API + preloaded page."""

    def __init__(self, root: str | Path, config_path: str | Path | None = None) -> None:
        cfg = load_config(root, config_path)
        self.engine = build_engine(root, cfg)
        self.api = UcaWebApplication(self.engine)
        payload = collect_boot_payload(root, config_path)
        payload["generated_at"] = datetime.now(timezone.utc).isoformat()
        self.page = render_page(payload)

    def status_summary(self) -> dict[str, Any]:
        status = self.engine.status()
        functional = sum(1 for item in status["modules"].values() if item["status"] == "functional")
        return {"modules": len(status["modules"]), "functional": functional,
                "execution_mode": status["execution_mode"]}


class ToutEnUnHandler(_Handler):
    """Existing API + the single preloaded page (so the chat is genuinely live)."""

    page_html: str = ""

    def _page(self) -> None:
        data = self.page_html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        from urllib.parse import urlparse
        if urlparse(self.path).path in ("/", "/index.html", "/uca.html"):
            self._page()
            return
        super().do_GET()  # /api/status, /api/runs… — real engine answers


def _port_libre(preferred: int, host: str) -> int:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind((host, preferred))
            return preferred
    except OSError:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind((host, 0))
            return probe.getsockname()[1]


def lancer(root: str | Path | None = None, *, host: str = "0.0.0.0", port: int = 8080,
           open_browser: bool = True, config_path: str | Path | None = None):
    """Builds everything and returns (server, url). Caller runs serve_forever()."""
    root = Path(root) if root else Path(__file__).resolve().parent
    app = ApplicationComplete(root, config_path)
    port = _port_libre(port, host)

    class Handler(ToutEnUnHandler):
        application = app.api
        page_html = app.page

    server = ThreadingHTTPServer((host, port), Handler)
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    summary = app.status_summary()
    print("╔══ UCA — tout est lancé depuis UN seul fichier ══╗")
    print(f"  Moteur : {summary['modules']} modules ({summary['functional']} fonctionnels), "
          f"mode {summary['execution_mode']}")
    print(f"  Interface + tchat actif : {url}")
    print("  Arrêt : Ctrl+C — tout reste local, rien n'est téléchargé.")
    if open_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    return server, url


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lance TOUT : moteur + interface + tchat actif.")
    parser.add_argument("--root", help="Répertoire de stockage (défaut : répertoire de ce fichier)")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--config", help="Fichier de configuration")
    parser.add_argument("--no-open", action="store_true", help="Ne pas ouvrir le navigateur")
    args = parser.parse_args(argv)
    server, url = lancer(args.root, host=args.host, port=args.port,
                         open_browser=not args.no_open, config_path=args.config)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt propre — à bientôt.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
