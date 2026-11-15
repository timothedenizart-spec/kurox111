"""One-file local UCA launcher used by Lancer_UCA.py.

It starts the local UI, initializes the engine/configuration, waits until the
HTTP server is bound, then opens the user's default browser. It never downloads
or pretends to preload absent checkpoints/corpora.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import argparse
import json
import webbrowser

from .factory import build_engine
from .web import UcaWebApplication, serve


@dataclass(frozen=True)
class LaunchSession:
    server: Any
    url: str
    readiness: dict[str, Any]


def summarize_readiness(status: dict[str, Any]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for module in status.get("modules", {}).values():
        state = str(module.get("status", "unknown"))
        counts[state] = counts.get(state, 0) + 1
    return {
        "server_ready": True,
        "execution_topology": status.get("execution_topology", {}),
        "module_status_counts": counts,
        "note": ("The interface and local configuration are initialized. Model weights/corpora marked "
                 "unavailable or non_validated are not silently loaded or simulated."),
    }


def prepare_launch(root: str | Path = ".", host: str = "127.0.0.1", port: int = 0) -> LaunchSession:
    """Build UCA and bind a local server without entering its event loop.

    A port of zero asks the operating system for a free local port, so opening
    the launcher does not fail merely because 8080 is already occupied.
    """
    root_path = Path(root).resolve()
    engine = build_engine(root_path)
    application = UcaWebApplication(engine)
    server = serve(application, host=host, port=port)
    address = "127.0.0.1" if host in {"0.0.0.0", "::"} else host
    url = f"http://{address}:{server.server_port}/"
    return LaunchSession(server=server, url=url, readiness=summarize_readiness(engine.status()))


def launch(root: str | Path = ".", host: str = "127.0.0.1", port: int = 0,
           open_browser: bool = True) -> int:
    session = prepare_launch(root, host, port)
    # One flushed line makes the ready URL immediately visible to a terminal,
    # a file-manager-launched console, and local automation before the server
    # enters its long-running event loop.
    print(json.dumps({"event": "uca_launcher_ready", "url": session.url,
                      "readiness": session.readiness}, ensure_ascii=False), flush=True)
    if open_browser:
        opened = webbrowser.open(session.url, new=1, autoraise=True)
        if not opened:
            print(f"Browser could not be opened automatically. Open this URL manually: {session.url}")
    try:
        session.server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        session.server.server_close()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Launch the local Unified Cognitive Architecture interface")
    parser.add_argument("--root", default=".", help="UCA repository / local asset root")
    parser.add_argument("--host", default="127.0.0.1", help="Local bind host (default: 127.0.0.1)")
    parser.add_argument("--port", default=0, type=int, help="Port; 0 chooses a free local port")
    parser.add_argument("--no-browser", action="store_true", help="Start the UI without opening a browser")
    args = parser.parse_args(argv)
    return launch(args.root, args.host, args.port, open_browser=not args.no_browser)


if __name__ == "__main__":
    raise SystemExit(main())
