# OpenCode Go + LiteLLM Gateway Setup Guide

## Getting started in 2 minutes

If you want the shortest path to a working local gateway, use this section first and come back to the rest of the guide only when you need the deeper explanation.

### What you need before starting

Download or verify these tools first:

- `Git` — required because the runtime is installed from the fork at <https://github.com/malafronte/litellm>
- `Python` 3.10+ — required to create the local runtime
- Windows only: PowerShell 7+ (`pwsh`) is recommended
- An `OPENCODE_GO_API_KEY` value from your OpenCode Go account

Quick checks:

```powershell
git --version
py --version
pwsh --version
```

```bash
git --version
python3 --version
```

### Which LiteLLM fork and ref to use

This repository is designed to install LiteLLM from the fork at:

- <https://github.com/malafronte/litellm>

The [helper scripts](../scripts/) are already prepared for the validated ref:

- `v1.83.11-nightly-opencode-go1`

If you use the provided install scripts, pass the fork explicitly so there is no ambiguity.

### Fastest path on Windows

1. Install the patched LiteLLM runtime from the fork:

```powershell
pwsh -File .\scripts\install-litellm-fork.ps1 -Repo "malafronte/litellm" -Ref "v1.83.11-nightly-opencode-go1"
```

2. Create your LiteLLM config from the repository template:

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\litellm" | Out-Null
Copy-Item .\config\opencode-go-config.template.yaml "$HOME\.claude\litellm\config.yaml" -Force
```

3. Export your OpenCode Go API key in the current terminal:

```powershell
$env:OPENCODE_GO_API_KEY = "<YOUR_OPENCODE_GO_API_KEY>"
```

4. Start the gateway:

```powershell
pwsh -File .\scripts\start-litellm-fork.ps1 -ConfigPath "$HOME\.claude\litellm\config.yaml"
```

5. Point your client to the local proxy:

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

At that point, the fastest next read is:

- [`examples/anthropic-client-presets/settings-kimi-k2.6.json`](../examples/anthropic-client-presets/settings-kimi-k2.6.json)
- [`config/opencode-go-config.template.yaml`](../config/opencode-go-config.template.yaml)

### Fastest path on Linux/macOS

1. Install the patched LiteLLM runtime from the fork:

```bash
./scripts/install-litellm-fork.sh "malafronte/litellm" "v1.83.11-nightly-opencode-go1"
```

2. Create your LiteLLM config from the repository template:

```bash
mkdir -p "$HOME/.claude/litellm"
cp ./config/opencode-go-config.template.yaml "$HOME/.claude/litellm/config.yaml"
```

3. Export your OpenCode Go API key:

```bash
export OPENCODE_GO_API_KEY="<YOUR_OPENCODE_GO_API_KEY>"
```

4. Start the gateway:

```bash
./scripts/start-litellm-fork.sh "$HOME/.claude/litellm-runtime" "$HOME/.claude/litellm/config.yaml"
```

5. Point your client to the local proxy with the same values shown in the Windows example above.

### What is happening in those 2 minutes

- the install script creates a dedicated local LiteLLM runtime;
- the runtime is installed from `malafronte/litellm` at ref `v1.83.11-nightly-opencode-go1`;
- the config template exposes ready-to-edit model aliases;
- the startup script launches the gateway on `http://127.0.0.1:4000`;
- your client only needs to target that local proxy.

### Immediate next steps

Once the proxy is up, use these sections next:

- section `7. Quick reference table` to switch models correctly;
- section `9. Practical example: how to switch from one model to another` for concrete alias changes;
- section `14. Essential troubleshooting` if the proxy starts but the client does not behave as expected.

## 1. Purpose

This guide explains how to expose OpenCode Go models through a local LiteLLM gateway when the client and the upstream provider do not speak the same API dialect.

The main operational goal is to document:

- which gateway parameters remain stable across models;
- which parameters change when you switch to a different upstream model;
- how to distinguish model families exposed through different endpoint styles;
- how to map a client-facing alias to the correct upstream provider configuration.

This document is intentionally broader than a single client integration. An Anthropic-style consumer such as `Claude Code` is just one example.

For a shorter operational summary, see `docs/model-routing-reference.md`.

### Compact rule: model selection in three steps

The practical rule is:

1. change `litellm_params.model` in `config.yaml`;
2. change `api_base` in `config.yaml` according to the model family;
3. set the same exposed alias in the client configuration.

| Model | `litellm_params.model` | `api_base` | Client-facing alias |
| --- | --- | --- | --- |
| `kimi-k2.5` | `openai/kimi-k2.5` | `https://opencode.ai/zen/go/v1` | `kimi-k2.5` |
| `kimi-k2.6` | `openai/kimi-k2.6` | `https://opencode.ai/zen/go/v1` | `kimi-k2.6` |
| `glm-5` | `openai/glm-5` | `https://opencode.ai/zen/go/v1` | `glm-5` |
| `glm-5.1` | `openai/glm-5.1` | `https://opencode.ai/zen/go/v1` | `glm-5.1` |
| `mimo-v2-pro` | `openai/mimo-v2-pro` | `https://opencode.ai/zen/go/v1` | `mimo-v2-pro` |
| `mimo-v2-omni` | `openai/mimo-v2-omni` | `https://opencode.ai/zen/go/v1` | `mimo-v2-omni` |
| `mimo-v2.5-pro` | `openai/mimo-v2.5-pro` | `https://opencode.ai/zen/go/v1` | `mimo-v2.5-pro` |
| `mimo-v2.5` | `openai/mimo-v2.5` | `https://opencode.ai/zen/go/v1` | `mimo-v2.5` |
| `qwen3.5-plus` | `openai/qwen3.5-plus` | `https://opencode.ai/zen/go/v1` | `qwen3.5-plus` |
| `qwen3.6-plus` | `openai/qwen3.6-plus` | `https://opencode.ai/zen/go/v1` | `qwen3.6-plus` |
| `minimax-m2.5` | `anthropic/minimax-m2.5` | `https://opencode.ai/zen/go` | `minimax-m2.5` |
| `minimax-m2.7` | `anthropic/minimax-m2.7` | `https://opencode.ai/zen/go` | `minimax-m2.7` |

## 2. Technical context

Many Anthropic-style clients only support the `v1/messages` API shape.

OpenCode Go does not expose every model through the same upstream interface:

- some models are available through OpenAI-compatible `v1/chat/completions`;
- others are available through Anthropic-compatible `v1/messages`.

Because of this, a direct client-to-provider configuration is not always possible.
LiteLLM fills that gap by:

1. receiving Anthropic-style requests from the client;
2. routing them to the correct upstream provider endpoint;
3. translating the protocol when the upstream model is OpenAI-compatible;
4. returning a response that matches the client-facing API contract.

## 3. Logical architecture

The general request path is:

```text
Anthropic-style client
  -> http://127.0.0.1:4000/v1/messages
Local LiteLLM gateway
  -> OpenCode Go endpoint selected for the alias
OpenCode Go
  -> target model
```

The main components are:

| Component | Role | Operational notes |
| --- | --- | --- |
| Anthropic-style client | local client | speaks `v1/messages` |
| `LiteLLM` | local gateway/proxy | routes and translates protocol shape |
| `OpenCode Go` | remote provider | requires a valid API key |
| target model | selected model | depends on the alias configured in LiteLLM |

## 4. Key point: not all models use the same endpoint shape

Current OpenCode Go models can be split into two families.

### 4.1 Family A — upstream `chat/completions`

These models should be configured as OpenAI-compatible upstream targets:

- `kimi-k2.5`
- `kimi-k2.6`
- `glm-5`
- `glm-5.1`
- `mimo-v2-pro`
- `mimo-v2-omni`
- `mimo-v2.5-pro`
- `mimo-v2.5`
- `qwen3.5-plus`
- `qwen3.6-plus`

For these models, the gateway should use:

- `model: openai/<model-name>`
- `api_base: https://opencode.ai/zen/go/v1`

### 4.2 Family B — upstream `messages`

These models should be configured as Anthropic-compatible upstream targets:

- `minimax-m2.5`
- `minimax-m2.7`

For these models, the gateway should use:

- `model: anthropic/<model-name>`
- `api_base: https://opencode.ai/zen/go`

Important note:

for Anthropic-compatible upstream models, do not append `/v1/messages` to `api_base`, because LiteLLM adds the protocol path when needed.

## 5. Stable settings

Regardless of the selected model, some values remain stable.

### 5.1 Stable values in Anthropic-style client settings

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "env": {
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:4000",
    "ANTHROPIC_AUTH_TOKEN": "local-litellm-key",
    "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": "1"
  }
}
```

These values do not depend on the selected model:

- `ANTHROPIC_BASE_URL`
- `ANTHROPIC_AUTH_TOKEN`
- `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS`

### 5.2 Stable values in `config.yaml`

```yaml
litellm_settings:
  drop_params: true
  modify_params: true
  use_chat_completions_url_for_anthropic_messages: true

general_settings:
  master_key: local-litellm-key
```

These values should remain aligned with the validated bridge behavior.

## 6. What changes when you switch models

When switching to a different OpenCode Go model, only two areas normally change.

### 6.1 In client settings

Update these two fields with the same exposed alias:

- `ANTHROPIC_MODEL`
- `ANTHROPIC_CUSTOM_MODEL_OPTION`

Optionally, you can also update:

- `ANTHROPIC_CUSTOM_MODEL_OPTION_NAME`
- `ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION`

### 6.2 In `config.yaml`

You need a `model_list` entry that matches the chosen model:

- `model_name`: alias exposed to the client;
- `litellm_params.model`: real upstream model with the correct provider prefix;
- `litellm_params.api_base`: correct endpoint for the model family.

## 7. Quick reference table

The following table is the main operational reference in this guide.

| OpenCode Go model | Family | `model_name` in `config.yaml` | `litellm_params.model` | `api_base` | Client alias |
| --- | --- | --- | --- | --- | --- |
| `kimi-k2.5` | A | `kimi-k2.5` | `openai/kimi-k2.5` | `https://opencode.ai/zen/go/v1` | `kimi-k2.5` |
| `kimi-k2.6` | A | `kimi-k2.6` | `openai/kimi-k2.6` | `https://opencode.ai/zen/go/v1` | `kimi-k2.6` |
| `glm-5` | A | `glm-5` | `openai/glm-5` | `https://opencode.ai/zen/go/v1` | `glm-5` |
| `glm-5.1` | A | `glm-5.1` | `openai/glm-5.1` | `https://opencode.ai/zen/go/v1` | `glm-5.1` |
| `mimo-v2-pro` | A | `mimo-v2-pro` | `openai/mimo-v2-pro` | `https://opencode.ai/zen/go/v1` | `mimo-v2-pro` |
| `mimo-v2-omni` | A | `mimo-v2-omni` | `openai/mimo-v2-omni` | `https://opencode.ai/zen/go/v1` | `mimo-v2-omni` |
| `mimo-v2.5-pro` | A | `mimo-v2.5-pro` | `openai/mimo-v2.5-pro` | `https://opencode.ai/zen/go/v1` | `mimo-v2.5-pro` |
| `mimo-v2.5` | A | `mimo-v2.5` | `openai/mimo-v2.5` | `https://opencode.ai/zen/go/v1` | `mimo-v2.5` |
| `qwen3.5-plus` | A | `qwen3.5-plus` | `openai/qwen3.5-plus` | `https://opencode.ai/zen/go/v1` | `qwen3.5-plus` |
| `qwen3.6-plus` | A | `qwen3.6-plus` | `openai/qwen3.6-plus` | `https://opencode.ai/zen/go/v1` | `qwen3.6-plus` |
| `minimax-m2.5` | B | `minimax-m2.5` | `anthropic/minimax-m2.5` | `https://opencode.ai/zen/go` | `minimax-m2.5` |
| `minimax-m2.7` | B | `minimax-m2.7` | `anthropic/minimax-m2.7` | `https://opencode.ai/zen/go` | `minimax-m2.7` |

## 8. Ready-to-use configuration baseline

If you want a broader starting point, you can use the repository template:

- `config/opencode-go-config.template.yaml`

This template can include current models from both upstream families.

An equivalent expanded baseline is:

```yaml
model_list:
  - model_name: kimi-k2.6
    litellm_params:
      model: openai/kimi-k2.6
      api_base: https://opencode.ai/zen/go/v1
      api_key: os.environ/OPENCODE_GO_API_KEY

  - model_name: kimi-k2.5
    litellm_params:
      model: openai/kimi-k2.5
      api_base: https://opencode.ai/zen/go/v1
      api_key: os.environ/OPENCODE_GO_API_KEY

  - model_name: glm-5
    litellm_params:
      model: openai/glm-5
      api_base: https://opencode.ai/zen/go/v1
      api_key: os.environ/OPENCODE_GO_API_KEY

  - model_name: glm-5.1
    litellm_params:
      model: openai/glm-5.1
      api_base: https://opencode.ai/zen/go/v1
      api_key: os.environ/OPENCODE_GO_API_KEY

  - model_name: mimo-v2-pro
    litellm_params:
      model: openai/mimo-v2-pro
      api_base: https://opencode.ai/zen/go/v1
      api_key: os.environ/OPENCODE_GO_API_KEY

  - model_name: mimo-v2-omni
    litellm_params:
      model: openai/mimo-v2-omni
      api_base: https://opencode.ai/zen/go/v1
      api_key: os.environ/OPENCODE_GO_API_KEY

  - model_name: mimo-v2.5-pro
    litellm_params:
      model: openai/mimo-v2.5-pro
      api_base: https://opencode.ai/zen/go/v1
      api_key: os.environ/OPENCODE_GO_API_KEY

  - model_name: mimo-v2.5
    litellm_params:
      model: openai/mimo-v2.5
      api_base: https://opencode.ai/zen/go/v1
      api_key: os.environ/OPENCODE_GO_API_KEY

  - model_name: qwen3.5-plus
    litellm_params:
      model: openai/qwen3.5-plus
      api_base: https://opencode.ai/zen/go/v1
      api_key: os.environ/OPENCODE_GO_API_KEY

  - model_name: qwen3.6-plus
    litellm_params:
      model: openai/qwen3.6-plus
      api_base: https://opencode.ai/zen/go/v1
      api_key: os.environ/OPENCODE_GO_API_KEY

  - model_name: minimax-m2.5
    litellm_params:
      model: anthropic/minimax-m2.5
      api_base: https://opencode.ai/zen/go
      api_key: os.environ/OPENCODE_GO_API_KEY

  - model_name: minimax-m2.7
    litellm_params:
      model: anthropic/minimax-m2.7
      api_base: https://opencode.ai/zen/go
      api_key: os.environ/OPENCODE_GO_API_KEY

litellm_settings:
  drop_params: true
  modify_params: true
  use_chat_completions_url_for_anthropic_messages: true

general_settings:
  master_key: local-litellm-key
```

## 9. Practical example: how to switch from one model to another

### 9.1 To use `glm-5`

This entry must exist in `config.yaml`:

```yaml
- model_name: glm-5
  litellm_params:
    model: openai/glm-5
    api_base: https://opencode.ai/zen/go/v1
    api_key: os.environ/OPENCODE_GO_API_KEY
```

Set this in `settings.json`:

```json
{
  "env": {
    "ANTHROPIC_CUSTOM_MODEL_OPTION": "glm-5",
    "ANTHROPIC_MODEL": "glm-5"
  }
}
```

### 9.2 To use `minimax-m2.7`

This entry must exist in `config.yaml`:

```yaml
- model_name: minimax-m2.7
  litellm_params:
    model: anthropic/minimax-m2.7
    api_base: https://opencode.ai/zen/go
    api_key: os.environ/OPENCODE_GO_API_KEY
```

Set this in `settings.json`:

```json
{
  "env": {
    "ANTHROPIC_CUSTOM_MODEL_OPTION": "minimax-m2.7",
    "ANTHROPIC_MODEL": "minimax-m2.7"
  }
}
```

## 10. Claude-style aliases: when they are actually needed

Aliases such as:

- `claude-haiku-4-5-20251001`
- `claude-sonnet-4-5-20250929`
- `claude-opus-4-1-20250805`

are not distinct OpenCode Go models.
They are compatibility aliases that are useful when `Claude Code` sends the proxy a native Anthropic model name instead of the alias chosen by the user.

These aliases are mainly useful in two cases:

1. manual tests with dedicated presets;
2. reducing `ProxyModelNotFoundError` errors when the client changes the model name implicitly.

If you really want to use a specific OpenCode Go model, the recommended rule is still:

- expose an alias in the proxy that matches the real OpenCode Go model name;
- set `ANTHROPIC_MODEL` and `ANTHROPIC_CUSTOM_MODEL_OPTION` to that same alias.

## 11. File structure involved

The setup uses the following files in the user's home directory:

```text
~/.claude/
  settings.json
  litellm/
    config.yaml
    set-opencode-go-key.ps1
    start-litellm.ps1
    test-litellm.ps1
```

The repository also includes these support files:

```text
config/
  opencode-go-config.template.yaml
examples/
  anthropic-client-presets/
patches/
  litellm-anthropic-reasoning-content.diff
scripts/
  install-litellm-fork.ps1
  install-litellm-fork.sh
  start-litellm-fork.ps1
  start-litellm-fork.sh
tests/
  proxy-battery/
  run-opencode-go-battery.py
```

## 12. Operational procedure on Windows

### 12.1 Save the API key in the user environment

```powershell
pwsh -File "$HOME\.claude\litellm\set-opencode-go-key.ps1" -ApiKey "<OPENCODE_GO_API_KEY>"
```

### 12.2 Open a new terminal

This step is important because the proxy startup script checks the variable in the current session environment.

### 12.3 Choose the model in `config.yaml`

If the model is already in the file, you do not need to add anything else.
If the model is not present, use the table in chapter 7 to add the correct entry.

### 12.4 Set the model in `settings.json`

Set:

- `ANTHROPIC_MODEL`
- `ANTHROPIC_CUSTOM_MODEL_OPTION`

to the alias of the model you want to use.

### 12.5 Start the local gateway

```powershell
pwsh -File "$HOME\.claude\litellm\start-litellm.ps1"
```

If the session did not inherit the environment variable, it is best to open a new terminal or export it explicitly before startup.

### 12.6 Test the bridge before opening Claude Code

```powershell
pwsh -File "$HOME\.claude\litellm\test-litellm.ps1"
```

### 12.7 Open a new Claude Code session

After changing the model or proxy, it is always best to open a new client session.

## 13. Equivalent procedure on Linux

### 13.1 Export the API key

```bash
export OPENCODE_GO_API_KEY="<OPENCODE_GO_API_KEY>"
```

### 13.2 Use a `config.yaml` consistent with the model family

The principle is identical to Windows:

- family A -> `openai/<model>` and `https://opencode.ai/zen/go/v1`;
- family B -> `anthropic/<model>` and `https://opencode.ai/zen/go`.

### 13.3 Start LiteLLM

```bash
uvx --from 'litellm[proxy]==1.83.11' litellm \
  --config "$HOME/.claude/litellm/config.yaml" \
  --host 127.0.0.1 \
  --port 4000
```

### 13.4 Verify the bridge with `curl`

```bash
curl http://127.0.0.1:4000/v1/messages \
  -H 'Authorization: Bearer local-litellm-key' \
  -H 'anthropic-version: 2023-06-01' \
  -H 'content-type: application/json' \
  -d '{
    "model": "kimi-k2.6",
    "max_tokens": 64,
    "messages": [
      {
        "role": "user",
        "content": "Reply with exactly: ok"
      }
    ]
  }'
```

## 14. Essential troubleshooting

### 14.1 `Missing OPENCODE_GO_API_KEY`

Likely causes:

- the key was not saved;
- the terminal was not reopened;
- the key exists in the user environment but not in the current session.

### 14.2 `Invalid model name passed`

This error means that `ANTHROPIC_MODEL` does not match a `model_name` exposed in `config.yaml`.

Fix:

1. verify the chosen alias in `settings.json`;
2. verify that it exists in `model_list`;
3. restart the proxy.

### 14.3 Routing to `v1/responses`

If the proxy uses the wrong path for Family A models, verify:

```yaml
litellm_settings:
  use_chat_completions_url_for_anthropic_messages: true
```

### 14.4 `reasoning_content` errors

For multi-turn tool-use turns, keep:

```yaml
litellm_settings:
  modify_params: true
```

### 14.5 Special case `minimax-m2.5`

In automated testing, a specific case was observed: the first tool-use turn can stop at `max_tokens` and with the `<minimax:tool_call>` marker instead of a structured `tool_use` block.

The repository battery already handles this case with a dedicated variant.

## 15. Recommended verification after each model change

The minimum recommended sequence is:

1. update `settings.json` with the alias of the chosen model;
2. verify that `config.yaml` exposes that model with the correct provider and `api_base`;
3. restart `LiteLLM`;
4. run the local proxy test;
5. only then open a new `Claude Code` session.

For broader verification, see also:

- `docs/testing/opencode-go-test-battery.md`
- `docs/litellm-fork-distribution.md`

## 16. Quick checklist: what to change to use a different model

When you want to use a different model, ask only these four questions:

1. does the model belong to Family A or Family B?
2. in `config.yaml`, is there an entry with `model_name` equal to the model name?
3. does the value of `litellm_params.model` use `openai/` or `anthropic/` correctly?
4. do `ANTHROPIC_MODEL` and `ANTHROPIC_CUSTOM_MODEL_OPTION` point to the same alias?

If all four conditions are true, the rest of the setup does not change.

## 17. Conclusion

The `LiteLLM` workaround should no longer be read as a solution specific to `Kimi K2.6`, but as a general guide for using the current `OpenCode Go` models behind `Claude Code`.

The decisive point is not the model name itself, but the endpoint family it belongs to:

- family A -> OpenAI-compatible upstream;
- family B -> Anthropic-compatible upstream.

Once this distinction is clear, to use a different model the user only needs to change:

- the corresponding entry in `config.yaml`;
- the alias set in `ANTHROPIC_MODEL` and `ANTHROPIC_CUSTOM_MODEL_OPTION`.

The rest of the local bridge can stay unchanged.

| Element | Must match | Reason |
| --- | --- | --- |
| `ANTHROPIC_AUTH_TOKEN` | `general_settings.master_key` | the client must authenticate against the local proxy |
| `ANTHROPIC_MODEL` | `model_list[].model_name` | the client must request an alias exposed by the gateway |
| `api_key: os.environ/OPENCODE_GO_API_KEY` | the real `OPENCODE_GO_API_KEY` environment variable | LiteLLM reads the key from the environment |
| `ANTHROPIC_BASE_URL` | LiteLLM host and port | the client must hit the proxy and not the remote provider |

## 10. Known issues and troubleshooting

### 10.1 Error: `Missing OPENCODE_GO_API_KEY`

Likely causes:

- the key was not saved;
- it was saved but the terminal was not reopened;
- the variable is present in a different user profile.

Fix:

1. rerun the key-saving script;
2. open a new terminal;
3. verify it with the command appropriate for the current shell.

### 10.2 Error: `uvx is not available on PATH`

Likely causes:

- `uv` is not installed;
- the installation exists but `PATH` is not updated.

Fix:

1. install `uv`;
2. reopen the terminal;
3. verify `uvx --version`.

### 10.3 Initial error: `No module named 'websockets'`

This problem appears when you try to start `LiteLLM` without the `proxy` extra.

The correct form is:

```text
litellm[proxy]==1.83.11
```

Using the base `litellm` package alone is not enough.

### 10.4 Initial error: request forwarded to `v1/responses`

In the setup covered by this documentation, `LiteLLM` initially tried to forward traffic to:

```text
https://opencode.ai/zen/go/v1/responses
```

This produced a `404` because the provider tested for `Kimi K2.6` had to be reached via:

```text
https://opencode.ai/zen/go/v1/chat/completions
```

The applied fix was:

```yaml
litellm_settings:
  use_chat_completions_url_for_anthropic_messages: true
```

### 10.5 The test works, but Claude Code does not respond as expected

If the direct proxy test succeeds but `Claude Code` still does not use the gateway, it is worth verifying:

1. that `settings.json` is the one actually read by the client;
2. that a new client session was opened after the change;
3. that `ANTHROPIC_BASE_URL` still points to `127.0.0.1:4000`;
4. that the proxy is actually running.

### 10.6 Error: `Invalid model name passed in model=claude-haiku-4-5-20251001`

This error means that the proxy received a native Anthropic model name from `Claude Code`, but that name was not present among the aliases exposed by LiteLLM's `model_list`.

Recommended fix:

1. add an alias to `config.yaml` with the same `model_name` received in the log;
2. point it to the same real upstream used for `kimi-k2.6`;
3. restart the proxy.

Example:

```yaml
- model_name: claude-haiku-4-5-20251001
  litellm_params:
    model: openai/kimi-k2.6
    api_base: https://opencode.ai/zen/go/v1
    api_key: os.environ/OPENCODE_GO_API_KEY
```

### 10.7 Error: `thinking is enabled but reasoning_content is missing in assistant tool call message`

This error means that a conversation with tool-use and reasoning blocks was converted into a form that the upstream provider does not accept for that specific turn.

In the documented setup, the recommended remedy is to enable LiteLLM's native workaround:

```yaml
litellm_settings:
  modify_params: true
```

After the change, the proxy must be restarted.

### 10.8 Port `4000` is already in use

In this case you can:

1. free the port in use;
2. choose a different port;
3. update both `start-litellm.ps1` and `ANTHROPIC_BASE_URL` consistently.

## 11. Security considerations and best practices

It is recommended not to save the real API key in project files or shared repositories.

Minimum best practices:

- keep `OPENCODE_GO_API_KEY` outside the repository;
- do not publish screenshots or logs that reveal secrets;
- use a local proxy token different from the upstream key, as in the case of `local-litellm-key`;
- limit proxy binding to `127.0.0.1` when there is no explicit local-network need.

## 12. Recommended procedure for explaining the workaround to colleagues or students

For a teaching context, it is best to present the flow in four phases:

### 12.1 Phase 1 - initial problem

Show that `Claude Code` and `OpenCode Go` do not natively speak the same protocol for this model.

### 12.2 Phase 2 - introducing the gateway

Explain that `LiteLLM` does not change the model, but translates the access interface between the client and the remote provider.

### 12.3 Phase 3 - independent bridge verification

Run `test-litellm.ps1` first, to show that the gateway works even without opening the final client.

### 12.4 Phase 4 - real use in the client

Only after verifying the bridge do you move to `Claude Code`, so infrastructure issues remain clearly separated from client issues.

## 13. Quick installation checklist

1. Install or verify `Python`, `uv`, and `uvx`.
2. Create `~/.claude/settings.json` with the gateway's local base URL.
3. Create `~/.claude/litellm/config.yaml` with the model mapping.
4. Save `OPENCODE_GO_API_KEY` in the user environment.
5. Start `LiteLLM` with `litellm[proxy]==1.83.11`.
6. Test `http://127.0.0.1:4000/v1/messages`.
7. Open a new `Claude Code` session.

## 14. Outcome of the documented setup

In the setup covered by this documentation, the final positive verification was the following behavior:

- the local proxy test returned a valid Anthropic-style payload;
- the model reported in the response was `kimi-k2.6`;
- the expected final content `ok` was returned correctly.

This provides practical evidence that the workaround is operational.

## 15. Conclusion

The link between `Claude Code` and `Kimi K2.6` through `OpenCode Go` is not a direct integration, but a controlled protocol adaptation via `LiteLLM`.

The critical point is not only authentication, but also compatibility of the API path used by the gateway. For this reason, proxy configuration, environment variable management, and independent bridge testing must be considered essential parts of the setup, not secondary details.

If the procedure is followed consistently, the workaround is repeatable on both Windows and Linux.

## 16. Stable distribution of the workaround

The procedure described in this tutorial uses a locally validated solution and may be sufficient for a single machine.

If the workaround must be shared with colleagues or students, the recommended solution is not to modify the `uvx` cache on every computer, but to maintain a GitHub fork of `LiteLLM` with an explicit tag containing the fix.

The repository already includes:

- a reappliable patch in `patches/`;
- Windows and Linux installation scripts in `scripts/`;
- a dedicated guide in `docs/litellm-fork-distribution.md`.

The patch to the `LiteLLM` code should not be understood as a patch only for `Kimi K2.6`: the fix can be treated as a general correction to the Anthropic -> OpenAI-compatible bridge on turns that include `thinking` and `tool_calls`.

To support multiple `OpenCode Go` models, the correct step is to distinguish endpoint families in `config.yaml`, not to duplicate a patch for each model.

This strategy makes the workaround:

- repeatable;
- verifiable;
- better suited to teaching or team contexts.
