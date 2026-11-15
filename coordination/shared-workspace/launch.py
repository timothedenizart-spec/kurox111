#!/usr/bin/env python3
"""Start the workspace server, wait until ready, and open its dashboard."""
from __future__ import annotations

from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen
import os
import subprocess
import sys
import time
import webbrowser

HERE = Path(__file__).resolve().parent
HOST = os.environ.get("WORKSPACE_HOST", "0.0.0.0")
PORT = int(os.environ.get("WORKSPACE_PORT", "8765"))
URL = f"http://127.0.0.1:{PORT}/"


def ready() -> bool:
    try:
        with urlopen(f"http://127.0.0.1:{PORT}/api/status", timeout=0.5) as response:
            return response.status == 200
    except (OSError, URLError):
        return False


def main() -> int:
    process = None
    if not ready():
        env = os.environ.copy()
        process = subprocess.Popen([sys.executable, str(HERE / "server.py")], cwd=HERE, env=env)
        for _ in range(100):
            if ready():
                break
            if process.poll() is not None:
                print("Le serveur n'a pas pu démarrer. Vérifiez le port WORKSPACE_PORT et Python.", file=sys.stderr)
                return int(process.returncode or 1)
            time.sleep(0.1)
        else:
            process.terminate()
            print("Délai dépassé en attendant le serveur.", file=sys.stderr)
            return 1
    print(f"Espace prêt : {URL}")
    print("Le tableau de bord affichera les fichiers déjà déposés dans inbox/.")
    webbrowser.open(URL)
    if process is None:
        return 0
    try:
        return process.wait()
    except KeyboardInterrupt:
        process.terminate()
        try:
            return process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            return process.wait()


if __name__ == "__main__":
    raise SystemExit(main())
