#!/usr/bin/env bash
# One-time setup on a Runpod Pod with a network volume mounted at /workspace.
# Everything (venv, HF cache, outputs) lives on the volume, so a new Pod only needs `source runpod_env.sh`.
set -euo pipefail

cd "$(dirname "$0")"
source ./runpod_env.sh

if [ ! -x "$VENV/bin/python" ]; then
    python3 -m venv "$VENV"
fi
"$VENV/bin/pip" install --upgrade pip
"$VENV/bin/pip" install -r requirements.txt "huggingface_hub[cli]"

"$VENV/bin/hf" download "$MODEL"

"$VENV/bin/python" - <<'PY'
import torch, vllm
print("torch", torch.__version__, "| CUDA", torch.cuda.is_available(), torch.cuda.get_device_name(0))
print("vllm", vllm.__version__)
PY

[ -n "${S2_API_KEY:-}" ] || echo "Warning: S2_API_KEY is not set; Semantic Scholar will be heavily rate limited."
echo "Setup done. Smoke test: python inspiration_pred.py --limit 2 --output_dir /workspace/outputs/smoke"
