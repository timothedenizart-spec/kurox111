#!/usr/bin/env sh
# Double-click / terminal launcher for Linux and macOS.
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
exec "${PYTHON:-python3}" Lancer_UCA.py "$@"
