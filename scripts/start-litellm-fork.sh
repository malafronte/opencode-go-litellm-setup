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
  echo "LiteLLM runtime not found in $RUNTIME_DIR. Run install-litellm-fork.sh first." >&2
  exit 1
fi

if [[ ! -x "$LITELLM_EXE" ]]; then
  echo "LiteLLM entrypoint not found in $LITELLM_EXE." >&2
  exit 1
fi

if [[ ! -f "$CONFIG_PATH" ]]; then
  echo "LiteLLM config not found in $CONFIG_PATH." >&2
  exit 1
fi

if [[ -z "${OPENCODE_GO_API_KEY:-}" ]]; then
  echo "OPENCODE_GO_API_KEY was not found in the current environment." >&2
  exit 1
fi

ARGS=( --config "$CONFIG_PATH" --host "$HOST" --port "$PORT" )

if [[ "$DETAILED_DEBUG" == "1" ]]; then
  ARGS+=( --detailed_debug )
fi

exec "$LITELLM_EXE" "${ARGS[@]}"
