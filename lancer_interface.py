#!/usr/bin/env python3
"""Lanceur Python tout-en-un pour l'interface UCA.

Démarre le serveur UCA avec tous les modules pré-chargés et ouvre automatiquement
le navigateur Web sur http://localhost:8080.
"""
from __future__ import annotations

import os
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Se positionner à la racine du projet
ROOT_DIR = Path(__file__).resolve().parent
os.chdir(ROOT_DIR)
sys.path.insert(0, str(ROOT_DIR))

from uca.config import load_config
from uca.factory import build_engine
from uca.web import UcaWebApplication, serve


def open_browser_delayed(url: str, delay_seconds: float = 0.8) -> None:
    def _open() -> None:
        time.sleep(delay_seconds)
        try:
            webbrowser.open(url)
        except Exception:
            pass
    threading.Thread(target=_open, daemon=True).start()


def main() -> int:
    print("======================================================================")
    print("  🚀 Initialisation de l'Interface Web UCA avec Tous Composants Chargés")
    print("======================================================================")

    # 1. Chargement et validation du moteur complet
    cfg = load_config(ROOT_DIR)
    engine = build_engine(ROOT_DIR, cfg)
    app = UcaWebApplication(engine)
    status = app.status()

    # 2. Rapport d'activation des composants
    modules = status.get("modules", {})
    functional_count = sum(1 for m in modules.values() if m.get("status") == "functional")
    print(f"  ✓ Modules fonctionnels : {functional_count}/{len(modules)}")
    print(f"  ✓ FTS5 Knowledge Store : {modules.get('knowledge_retrieval', {}).get('details', {}).get('passage_count', 0)} passages certifiés")
    print(f"  ✓ Passerelle MeTTa : {modules.get('symbolic_processing', {}).get('reason', 'Prête')}")
    print(f"  ✓ Cortex Parallèle : {modules.get('parallel_cortex', {}).get('reason', 'Prêt')}")
    print(f"  ✓ Modèle Neuronal NCM : {modules.get('ncm_concept_generation', {}).get('reason', 'Prêt')}")

    host = "0.0.0.0"
    port = 8080
    url = f"http://localhost:{port}"

    print("======================================================================")
    print(f"  🌐 Serveur UCA en écoute sur : http://{host}:{port}")
    print(f"  ⚡ Accès direct navigateur   : {url}")
    print("======================================================================")

    # 3. Ouverture automatique du navigateur
    open_browser_delayed(url)

    # 4. Lancement du serveur
    server = serve(app, host=host, port=port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur UCA.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
