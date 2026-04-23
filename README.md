# OpenCode Go + LiteLLM Gateway Setup

This repository documents and packages a practical LiteLLM-based gateway for using OpenCode Go models through API-shape translation layers, while also carrying the fixes introduced in the upstream LiteLLM pull request for Anthropic message handling.

In practice, this setup allows a client that speaks Anthropic-style `v1/messages` to reach upstream providers that expose either:

- OpenAI-compatible `v1/chat/completions` endpoints, or
- Anthropic-compatible `v1/messages` endpoints.

The gateway is centered on LiteLLM, with a small but important patch set that improves fidelity when handling reasoning-bearing Anthropic responses.

## What this repository provides

- documentation for configuring LiteLLM in front of OpenCode Go;
- example client settings for Anthropic-style consumers;
- a regression patch for the Anthropic message transformation path;
- test scripts for validating proxy health, model routing, tool loops, and think-tag sanitization.

## Why the patch matters

The upstream LiteLLM pull request referenced by this repository addresses concrete issues in the Anthropic message bridge:

- preservation of reasoning content extracted from upstream thinking blocks;
- sanitization of leaked `</think>` markers before final text is returned to clients;
- more reliable behavior in multi-turn tool-use flows.

This makes the gateway more robust when an Anthropic-format client is routed to non-native upstream APIs through LiteLLM.

## Repository layout

- `docs/` — setup guides and reference documentation
- `docs/testing/` — validation procedure and test battery notes
- `config/` — configuration templates
- `examples/claude-code-settings/` — example client presets for Anthropic-style consumers
- `patches/` — patch files that capture the LiteLLM changes
- `scripts/` — helper scripts for install and startup workflows
- `tests/proxy-battery/` — direct proxy regression and routing checks

## Quick start

### 1. Install the patched LiteLLM runtime

- Windows: `./scripts/install-litellm-fork.ps1`
- Linux/macOS: `./scripts/install-litellm-fork.sh`

### 2. Configure LiteLLM

Copy `config/opencode-go-config.template.yaml` to your LiteLLM runtime location, then set `OPENCODE_GO_API_KEY` in the environment used by the proxy process.

### 3. Start the gateway

- Windows: `./scripts/start-litellm-fork.ps1`
- Linux/macOS: `./scripts/start-litellm-fork.sh`

### 4. Validate the bridge

Run the battery in `tests/proxy-battery/run-opencode-go-battery.py` against the local proxy.

## Documentation

- `docs/guida-claude-code-opencode-go-via-litellm.md` — full setup walkthrough
- `docs/cheat-sheet-claude-code-opencode-go-via-litellm.md` — quick model mapping reference
- `docs/testing/opencode-go-test-battery.md` — structured validation plan

## Example materials

- `examples/claude-code-settings/` contains ready-made example presets for Anthropic-style desktop clients.

These files are examples, not a hard product requirement. The main value of this repository is the general LiteLLM gateway pattern plus the Anthropic bridge fixes.

## Upstream reference

- LiteLLM PR: `BerriAI/litellm#26285`
