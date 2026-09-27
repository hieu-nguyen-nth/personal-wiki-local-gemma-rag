#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
PYTHON_BIN="/opt/homebrew/bin/python3.12"

if [[ ! -x "$PYTHON_BIN" ]]; then
  print -u2 "Python 3.12 is required. Install it with: brew install python@3.12"
  exit 1
fi

if [[ ! -x "$SCRIPT_DIR/.venv/bin/python" ]]; then
  "$PYTHON_BIN" -m venv "$SCRIPT_DIR/.venv"
fi
"$SCRIPT_DIR/.venv/bin/python" -m pip install --upgrade -r "$SCRIPT_DIR/requirements.txt"

MODEL_DIR="$SCRIPT_DIR/models/gemma4-e2b-it-local"
if [[ ! -f "$MODEL_DIR/config.json" ]]; then
  mkdir -p "$MODEL_DIR"
  print "Downloading the selected local Gemma checkpoint (about 2.5 GB)..."
  "$SCRIPT_DIR/.venv/bin/hf" download \
    mlx-community/Gemma4-E2B-IT-Text-int4 \
    --local-dir "$MODEL_DIR"
fi

print "Setup complete. Run: ./launch.command help"
