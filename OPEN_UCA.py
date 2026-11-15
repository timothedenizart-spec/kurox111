"""Double-click-friendly UCA launcher.

Run this file with Python (or double-click it on systems associated with Python)
to initialize local UCA stores, start the interface, and open a browser tab.
"""
from __future__ import annotations

from pathlib import Path

from uca.launcher import main


if __name__ == "__main__":
    raise SystemExit(main(["--root", str(Path(__file__).resolve().parent)]))
