#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
if [[ ! -x .venv-ai/bin/python ]]; then
  "$PYTHON" -m venv .venv-ai
fi
.venv-ai/bin/python -m pip install --upgrade pip
# On macOS PyTorch may use Apple MPS; on Linux supported CUDA devices
# follow the installed PyTorch wheel. CPU mode remains available by opt-in.
.venv-ai/bin/python -m pip install torch
.venv-ai/bin/python -m pip install -r ai/requirements-local.txt
.venv-ai/bin/python -c "import torch,diffusers; print('PyTorch',torch.__version__,'CUDA',torch.cuda.is_available(),'MPS',hasattr(torch.backends,'mps') and torch.backends.mps.is_available())"
echo "Canvas AI setup finished for this computer."
