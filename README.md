# OpenCode Go + LiteLLM Gateway Setup

This repository documents and packages a practical LiteLLM-based gateway for using OpenCode Go models through API-shape translation layers, while also carrying the fixes introduced in the upstream LiteLLM pull request for Anthropic message handling.

> **What this repository enables**
>
> - Route **Anthropic-style clients** to **OpenAI-style upstream models**
> - Keep a **single client-facing API shape** while changing upstream model families
> - Preserve **reasoning content**, sanitize leaked `</think>` markers, and improve tool-loop fidelity

## Visual overview

### Protocol translation at a glance

```text
┌──────────────────────────┐
│ Anthropic-style client   │
│ e.g. Claude Code         │
│ sends /v1/messages       │
└────────────┬─────────────┘
	     │
	     ▼
┌──────────────────────────┐
│ LiteLLM local gateway    │
│ route + translate + fix  │
└───────┬──────────┬───────┘
	│          │
	│          └──────────────────────────────┐
	▼                                         ▼
┌──────────────────────────┐         ┌──────────────────────────┐
│ OpenAI-style upstream    │         │ Anthropic-style upstream │
│ /v1/chat/completions     │         │ /v1/messages             │
│ e.g. Kimi K2.6           │         │ e.g. MiniMax M2.7        │
└──────────────────────────┘         └──────────────────────────┘
```

### What the gateway is doing

| Step | Function | Result |
| --- | --- | --- |
| 1 | Accept a client request in Anthropic `v1/messages` format | Client does not need to support multiple provider APIs |
| 2 | Resolve the selected LiteLLM alias | A stable client-facing model name is preserved |
| 3 | Route to the correct OpenCode Go upstream endpoint | The gateway chooses OpenAI-style or Anthropic-style transport |
| 4 | Normalize the response back to Anthropic-compatible output | The client sees one consistent API contract |
| 5 | Apply PR fixes for reasoning and `</think>` sanitation | Cleaner final text and more reliable tool loops |

In practice, this setup allows a client that speaks Anthropic-style `v1/messages` to reach upstream providers that expose either:

- OpenAI-compatible `v1/chat/completions` endpoints, or
- Anthropic-compatible `v1/messages` endpoints.

For example:

- a client such as `Claude Code`, which only speaks the Anthropic Messages API, can send `v1/messages` requests to LiteLLM;
- LiteLLM can then translate those requests into OpenAI-style `v1/chat/completions` calls for an upstream model such as `Kimi K2.6` served through OpenCode Go;
- the response is translated back into Anthropic-compatible output before being returned to the client.

The same gateway can also forward Anthropic-style requests to upstream models that already expose native `v1/messages` semantics, such as Anthropic-compatible providers, without requiring the client to change its protocol.

The gateway is centered on LiteLLM, with a small but important patch set that improves fidelity when handling reasoning-bearing Anthropic responses.

## What this repository provides

- documentation for configuring LiteLLM in front of OpenCode Go;
- example client settings for Anthropic-style consumers;
- a regression patch for the Anthropic message transformation path;
- test scripts for validating proxy health, model routing, tool loops, and think-tag sanitization.

### Typical use case

```text
Anthropic-only client
	│
	│ /v1/messages
	▼
LiteLLM gateway
	│
	│ translated /v1/chat/completions
	▼
OpenCode Go -> Kimi K2.6
```

This is the key capability: the client continues to speak Anthropic Messages, while the upstream model can remain OpenAI-compatible.

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
- `examples/anthropic-client-presets/` — example client presets for Anthropic-style consumers
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

- `docs/gateway-setup-guide.md` — full setup and configuration guide
- `docs/model-routing-reference.md` — compact model mapping reference
- `docs/testing/opencode-go-test-battery.md` — structured validation plan

## Example materials

- `examples/anthropic-client-presets/` contains ready-made presets for Anthropic-style clients.

These files are examples, not a hard product requirement. The main value of this repository is the general LiteLLM gateway pattern plus the Anthropic bridge fixes.

## Upstream reference

- LiteLLM PR: `BerriAI/litellm#26285`
- Upstream repository: `https://github.com/BerriAI/litellm`
- Fork used for the patch work: `https://github.com/malafronte/litellm`
