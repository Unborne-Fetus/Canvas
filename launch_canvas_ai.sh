#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -x .venv-ai/bin/python ]]; then
  echo "Setting up local AI environment on this computer."
  bash ./setup_canvas_ai.sh
fi
if [[ -n "${1:-}" ]]; then
  .venv-ai/bin/python run_canvas_ai.py --source "$1"
else
  .venv-ai/bin/python run_canvas_ai.py
fi
