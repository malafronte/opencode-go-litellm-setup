# OpenCode Go + LiteLLM Gateway Setup

[![Windows](https://img.shields.io/badge/Windows-supported-0F7B0F?style=for-the-badge&logo=windows)](#copypaste-setup)
[![Linux/macOS](https://img.shields.io/badge/Linux%20%2F%20macOS-supported-1F6FEB?style=for-the-badge&logo=linux)](#copypaste-setup)
[![LiteLLM fork](https://img.shields.io/badge/LiteLLM-malafronte%2Flitellm-F97316?style=for-the-badge&logo=github)](https://github.com/malafronte/litellm)
[![OpenCode Go](https://img.shields.io/badge/OpenCode%20Go-upstream%20target-111827?style=for-the-badge)](#why-this-exists)

Use Anthropic-style clients with OpenCode Go models through a local LiteLLM gateway that can translate protocol shape, preserve reasoning content more reliably, and smooth out multi-turn tool flows.

> **What this repository enables**
>
> - Route **Anthropic-style clients** to both **OpenAI-style** and **Anthropic-style** upstreams
> - Keep a **single client-facing API shape** while swapping model families behind the proxy
> - Apply focused LiteLLM fixes for **reasoning preservation**, `</think>` cleanup, and **tool-loop stability**

| Start here | Go to |
| --- | --- |
| Full setup guide | [docs/gateway-setup-guide.md](docs/gateway-setup-guide.md) |
| Model routing reference | [docs/model-routing-reference.md](docs/model-routing-reference.md) |
| Proxy test battery | [docs/testing/opencode-go-test-battery.md](docs/testing/opencode-go-test-battery.md) |

**Jump to**

[Downloads](#downloads) · [Copy/paste setup](#copypaste-setup) · [Quick start](#quick-start) · [Repository layout](#repository-layout) · [Upstream references](#upstream-references)

## Downloads

| Tool | Download |
| --- | --- |
| Git | [git-scm.com/downloads](https://git-scm.com/downloads) |
| Python 3 | [python.org/downloads](https://www.python.org/downloads/) |
| PowerShell 7 | [github.com/PowerShell/PowerShell](https://github.com/PowerShell/PowerShell) |

## Copy/paste setup

### Windows

```powershell
pwsh -File .\scripts\install-litellm-fork.ps1 -Repo "malafronte/litellm" -Ref "v1.83.11-nightly-opencode-go1"
New-Item -ItemType Directory -Force -Path "$HOME\.claude\litellm" | Out-Null
Copy-Item .\config\opencode-go-config.template.yaml "$HOME\.claude\litellm\config.yaml" -Force
$env:OPENCODE_GO_API_KEY = "<YOUR_OPENCODE_GO_API_KEY>"
pwsh -File .\scripts\start-litellm-fork.ps1 -ConfigPath "$HOME\.claude\litellm\config.yaml"
```

### Linux/macOS

```bash
./scripts/install-litellm-fork.sh "malafronte/litellm" "v1.83.11-nightly-opencode-go1"
mkdir -p "$HOME/.claude/litellm"
cp ./config/opencode-go-config.template.yaml "$HOME/.claude/litellm/config.yaml"
export OPENCODE_GO_API_KEY="<YOUR_OPENCODE_GO_API_KEY>"
./scripts/start-litellm-fork.sh "$HOME/.claude/litellm-runtime" "$HOME/.claude/litellm/config.yaml"
```

Client values to keep aligned:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:4000",
    "ANTHROPIC_AUTH_TOKEN": "local-litellm-key",
    "ANTHROPIC_MODEL": "kimi-k2.6",
    "ANTHROPIC_CUSTOM_MODEL_OPTION": "kimi-k2.6"
  }
}
```

## At a glance

```text
Anthropic-style client
e.g. Claude Code
        |
        |  /v1/messages
        v
LiteLLM local gateway
route + translate + patch
    |                    |
    |                    |
    v                    v
OpenAI-style upstream    Anthropic-style upstream
/v1/chat/completions     /v1/messages
e.g. Kimi K2.6           e.g. MiniMax M2.7
```

## Why this exists

Some clients speak only the Anthropic Messages API, while upstream models behind OpenCode Go may expose different API families. This repository packages the gateway pattern that lets the client stay fixed while the backend routing changes.

In practical terms:

- a client such as `Claude Code` can keep sending Anthropic-style `v1/messages` requests;
- LiteLLM can route those requests to the correct OpenCode Go upstream family;
- responses are normalized back into an Anthropic-compatible shape before returning to the client.

That means one client contract, multiple upstream families, and fewer edge-case failures when reasoning or tool calls are involved.

## What the gateway is doing

| Step | Gateway action | Why it matters |
| --- | --- | --- |
| 1 | Accept an Anthropic `v1/messages` request | The client does not need provider-specific logic |
| 2 | Resolve the requested LiteLLM alias | Client-facing model names stay stable |
| 3 | Pick the correct OpenCode Go endpoint family | The proxy chooses the right transport automatically |
| 4 | Normalize the response back to Anthropic-compatible output | The client sees one consistent API contract |
| 5 | Apply bridge fixes for reasoning and `</think>` cleanup | Final output is cleaner and tool loops are more reliable |

## What this repository provides

| Area | Includes |
| --- | --- |
| Configuration | LiteLLM templates for OpenCode Go routing |
| Client examples | Anthropic-style preset examples |
| Patch set | Regression fix for the Anthropic message transformation path |
| Validation | Scripts and docs for proxy health, model routing, and tool-loop checks |

### Typical use case

```text
Anthropic-only client
        |
        | /v1/messages
        v
LiteLLM gateway
        |
        | translated /v1/chat/completions
        v
OpenCode Go -> Kimi K2.6
```

The key idea is simple: the client keeps speaking Anthropic Messages, while the upstream model can remain OpenAI-compatible.

## Why the patch matters

The referenced upstream LiteLLM work improves concrete failure points in the Anthropic bridge:

- preservation of reasoning content extracted from upstream thinking blocks;
- sanitization of leaked `</think>` markers before final text is returned;
- more reliable multi-turn behavior in tool-use flows.

Those fixes matter most when an Anthropic-format client is routed through LiteLLM to a non-native upstream API.

## Quick start

### 1. Install the patched LiteLLM runtime

- Windows: [`scripts/install-litellm-fork.ps1`](scripts/install-litellm-fork.ps1)
- Linux/macOS: [`scripts/install-litellm-fork.sh`](scripts/install-litellm-fork.sh)

### 2. Configure LiteLLM

Use [`config/opencode-go-config.template.yaml`](config/opencode-go-config.template.yaml) as the starting template, then set `OPENCODE_GO_API_KEY` in the environment used by the proxy process.

### 3. Start the gateway

- Windows: [`scripts/start-litellm-fork.ps1`](scripts/start-litellm-fork.ps1)
- Linux/macOS: [`scripts/start-litellm-fork.sh`](scripts/start-litellm-fork.sh)

### 4. Validate the bridge

Run [`tests/proxy-battery/run-opencode-go-battery.py`](tests/proxy-battery/run-opencode-go-battery.py) against the local proxy.

## Repository layout

| Path | Purpose |
| --- | --- |
| [`docs/`](docs/) | Setup guides and reference documentation |
| [`docs/testing/`](docs/testing/) | Validation procedure and battery notes |
| [`config/`](config/) | Configuration templates |
| [`examples/anthropic-client-presets/`](examples/anthropic-client-presets/) | Example presets for Anthropic-style consumers |
| [`patches/`](patches/) | Patch files capturing the LiteLLM changes |
| [`scripts/`](scripts/) | Install and startup helpers |
| [`tests/proxy-battery/`](tests/proxy-battery/) | Direct proxy regression and routing checks |

## Example materials

[`examples/anthropic-client-presets/`](examples/anthropic-client-presets/) contains ready-made presets for Anthropic-style clients.

These files are examples, not a hard product requirement. The main value of the repository is the LiteLLM gateway pattern plus the Anthropic bridge fixes.

## Upstream references

| Reference | Link |
| --- | --- |
| LiteLLM pull request | [BerriAI/litellm#26285](https://github.com/BerriAI/litellm/pull/26285) |
| Upstream repository | [BerriAI/litellm](https://github.com/BerriAI/litellm) |
| Fork used for patch work | [malafronte/litellm](https://github.com/malafronte/litellm) |
