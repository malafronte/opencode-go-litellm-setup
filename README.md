# OpenCode Go + LiteLLM Setup

Use OpenCode Go models (Kimi, GLM, MiMo, Qwen, MiniMax) behind Claude Code via a patched LiteLLM proxy.

## Quick Start

1) Install fork
- Windows: .\\scripts\\install-litellm-fork.ps1
- Linux/macOS: ./scripts/install-litellm-fork.sh

2) Configure
- Copy config/opencode-go-config.template.yaml to ~/.claude/litellm/config.yaml
- Set OPENCODE_GO_API_KEY

3) Settings
- ANTHROPIC_BASE_URL = http://127.0.0.1:4000
- ANTHROPIC_AUTH_TOKEN = local-litellm-key

4) Start proxy
- Windows: .\\scripts\\start-litellm-fork.ps1
- Linux/macOS: ./scripts/start-litellm-fork.sh

## Docs
- docs/guida-claude-code-opencode-go-via-litellm.md
- docs/cheat-sheet-claude-code-opencode-go-via-litellm.md

## Related
- https://github.com/BerriAI/litellm/pull/26285
