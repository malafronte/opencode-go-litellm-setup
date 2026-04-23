#!/usr/bin/env bash
set -euo pipefail

REPO="${1:-<github-user>/litellm}"
REF="${2:-v1.83.11-nightly-opencode-go1}"
RUNTIME_DIR="${3:-$HOME/.claude/litellm-runtime}"
FORCE_REINSTALL="${FORCE_REINSTALL:-0}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found in PATH." >&2
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git not found in PATH. It is required to install LiteLLM from the GitHub fork." >&2
  exit 1
fi

PYTHON_EXE="$RUNTIME_DIR/bin/python"
PACKAGE_SPEC="litellm[proxy] @ git+https://github.com/$REPO.git@$REF"

if [[ "$FORCE_REINSTALL" == "1" && -d "$RUNTIME_DIR" ]]; then
  rm -rf "$RUNTIME_DIR"
fi

if [[ ! -x "$PYTHON_EXE" ]]; then
  mkdir -p "$RUNTIME_DIR"
  python3 -m venv "$RUNTIME_DIR"
fi

"$PYTHON_EXE" -m pip install --upgrade pip
"$PYTHON_EXE" -m pip install --upgrade "$PACKAGE_SPEC"

METADATA_PATH="$RUNTIME_DIR/install-metadata.json"
cat > "$METADATA_PATH" <<EOF
{
  "repo": "$REPO",
  "ref": "$REF",
  "runtimeDir": "$RUNTIME_DIR"
}
EOF

echo "LiteLLM installed from $REPO@$REF"
echo "Runtime: $RUNTIME_DIR"
echo "Metadata: $METADATA_PATH"
