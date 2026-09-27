#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
LOCAL_PYTHON="$SCRIPT_DIR/.venv/bin/python"

if [[ -x "$LOCAL_PYTHON" ]]; then
  PYTHON_BIN="$LOCAL_PYTHON"
else
  print -u2 "No compatible runtime found. Run ./setup.sh once while online."
  exit 1
fi

cd "$SCRIPT_DIR"
exec "$PYTHON_BIN" wiki.py "$@"
