"""One-click local launcher for the UCA web interface.

The launcher initializes only empty local stores and reads capability status before
opening the interface. It never downloads weights or data, and it never reports
an unavailable model as loaded.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import argparse
import json
import threading
import webbrowser

from .config import load_config, local_path
from .factory import build_engine
from .storage import initialize_knowledge_db
from .web import UcaWebApplication, serve


@dataclass
class InterfaceSession:
    """A running UCA interface and the readiness snapshot shown on startup."""
    server: Any
    thread: threading.Thread
    url: str
    status: dict[str, Any]
    browser_opened: bool

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


def initialize_local_stores(root: str | Path = ".") -> dict[str, Any]:
    """Create empty consent-aware stores without fetching a model or a corpus."""
    config = load_config(root)
    stores = config["stores"]
    memory = local_path(config, stores["memory_path"])
    memory.parent.mkdir(parents=True, exist_ok=True)
    if not memory.exists():
        memory.write_text(json.dumps({"schema": "uca.explicit-memory.v1", "entries": []}, indent=2) + "\n",
                          encoding="utf-8")
    facts = local_path(config, stores["facts_path"])
    facts.parent.mkdir(parents=True, exist_ok=True)
    if not facts.exists():
        facts.write_text(json.dumps({"schema": "uca.operator-facts.v1", "facts": [],
                                     "note": "Empty by design: import only actual operator facts."}, indent=2) + "\n",
                         encoding="utf-8")
    initialize_knowledge_db(local_path(config, stores["knowledge_db"]), stores.get("knowledge_table", "documents"))
    return config


def _browser_url(host: str, port: int) -> str:
    # 0.0.0.0 is needed to accept preview/local-network connections, but is not
    # a browser destination. A local launch therefore opens the loopback URL.
    browser_host = "127.0.0.1" if host in {"0.0.0.0", "::"} else host
    return f"http://{browser_host}:{port}/"


def start_interface(root: str | Path = ".", *, host: str = "0.0.0.0", port: int = 8080,
                    open_browser: bool = True) -> InterfaceSession:
    """Initialize UCA, start its server, and optionally request a browser tab.

    ``port=0`` asks the operating system for an available port, which is useful
    for tests and local parallel development. The resulting URL is always
    returned even when the environment cannot open a graphical browser.
    """
    config = initialize_local_stores(root)
    engine = build_engine(root, config=config)
    readiness = engine.status()  # Read module availability before exposing the UI.
    server = serve(UcaWebApplication(engine), host=host, port=port)
    actual_port = int(server.server_address[1])
    url = _browser_url(host, actual_port)
    thread = threading.Thread(target=server.serve_forever, name="uca-interface", daemon=True)
    thread.start()
    opened = bool(webbrowser.open(url, new=2)) if open_browser else False
    return InterfaceSession(server=server, thread=thread, url=url, status=readiness, browser_opened=opened)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Open the local UCA interface with initialized stores")
    parser.add_argument("--root", default=".", help="Repository / local asset root")
    parser.add_argument("--host", default="0.0.0.0", help="Listening host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Listening port (0 chooses a free port)")
    parser.add_argument("--no-browser", action="store_true", help="Start the interface without opening a browser tab")
    args = parser.parse_args(argv)
    session = start_interface(args.root, host=args.host, port=args.port, open_browser=not args.no_browser)
    print(f"UCA interface ready at {session.url}")
    print("Availability was loaded. Unavailable models remain visible as unavailable; no assets were downloaded.")
    try:
        session.thread.join()
    except KeyboardInterrupt:
        pass
    finally:
        session.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
