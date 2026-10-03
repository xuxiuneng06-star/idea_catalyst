# Source this in every new shell on the Pod: `source runpod_env.sh`
export VENV=/workspace/venv
export HF_HOME=/workspace/hf-cache
export MODEL="${MODEL:-Qwen/Qwen3-14B}"
# Put `export S2_API_KEY=...` in /workspace/secrets.sh (kept out of git).
if [ -f /workspace/secrets.sh ]; then source /workspace/secrets.sh; fi
if [ -x "$VENV/bin/python" ]; then source "$VENV/bin/activate"; fi
