#!/usr/bin/env python3
"""Double-click friendly launcher for the complete local UCA interface."""
from pathlib import Path
import os

# Opening this file from a file manager must use the repository as its root,
# rather than the file manager's arbitrary working directory.
os.chdir(Path(__file__).resolve().parent)

from uca.launcher import main  # noqa: E402

raise SystemExit(main())
