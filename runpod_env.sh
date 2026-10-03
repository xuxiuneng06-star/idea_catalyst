# Source this in every new shell on the Pod: `source runpod_env.sh`
export VENV=/workspace/venv
export HF_HOME=/workspace/hf-cache
export MODEL="${MODEL:-Qwen/Qwen3-14B}"
[ -f /workspace/secrets.sh ] && source /workspace/secrets.sh   # put `export S2_API_KEY=...` here
[ -x "$VENV/bin/python" ] && source "$VENV/bin/activate"
