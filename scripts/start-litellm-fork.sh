#!/usr/bin/env bash
set -euo pipefail

RUNTIME_DIR="${1:-$HOME/.claude/litellm-runtime}"
CONFIG_PATH="${2:-$HOME/.claude/litellm/config.yaml}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-4000}"
DETAILED_DEBUG="${DETAILED_DEBUG:-0}"

PYTHON_EXE="$RUNTIME_DIR/bin/python"
LITELLM_EXE="$RUNTIME_DIR/bin/litellm"

if [[ ! -x "$PYTHON_EXE" ]]; then
  echo "Runtime LiteLLM non trovato in $RUNTIME_DIR. Eseguire prima install-litellm-fork.sh." >&2
  exit 1
fi

if [[ ! -x "$LITELLM_EXE" ]]; then
  echo "Entrypoint LiteLLM non trovato in $LITELLM_EXE." >&2
  exit 1
fi

if [[ ! -f "$CONFIG_PATH" ]]; then
  echo "Config LiteLLM non trovata in $CONFIG_PATH." >&2
  exit 1
fi

if [[ -z "${OPENCODE_GO_API_KEY:-}" ]]; then
  echo "Variabile OPENCODE_GO_API_KEY non trovata nell'ambiente corrente." >&2
  exit 1
fi

ARGS=( --config "$CONFIG_PATH" --host "$HOST" --port "$PORT" )

if [[ "$DETAILED_DEBUG" == "1" ]]; then
  ARGS+=( --detailed_debug )
fi

exec "$LITELLM_EXE" "${ARGS[@]}"