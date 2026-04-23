# OpenCode Go Model Routing Reference

## Purpose

This reference summarizes how to map OpenCode Go models to the correct LiteLLM upstream configuration.

Use it when you need to answer three practical questions quickly:

1. Which upstream provider prefix should be used?
2. Which `api_base` should be used?
3. Which client-facing alias should be exposed through LiteLLM?

For a full explanation of the gateway architecture, see `docs/gateway-setup-guide.md`.

## Stable gateway settings

These LiteLLM settings stay stable across model choices:

```yaml
litellm_settings:
  drop_params: true
  modify_params: true
  use_chat_completions_url_for_anthropic_messages: true

general_settings:
  master_key: local-litellm-key
```

## Model families

### Family A — OpenAI-compatible upstream

Use:

- `litellm_params.model = openai/<model>`
- `api_base = https://opencode.ai/zen/go/v1`

Models:

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

### Family B — Anthropic-compatible upstream

Use:

- `litellm_params.model = anthropic/<model>`
- `api_base = https://opencode.ai/zen/go`

Models:

- `minimax-m2.5`
- `minimax-m2.7`

Do not append `/v1/messages` to `api_base`; LiteLLM adds the request path when needed.

## Quick reference table

| Model | Upstream family | `litellm_params.model` | `api_base` | Suggested alias |
| --- | --- | --- | --- | --- |
| `kimi-k2.5` | Family A | `openai/kimi-k2.5` | `https://opencode.ai/zen/go/v1` | `kimi-k2.5` |
| `kimi-k2.6` | Family A | `openai/kimi-k2.6` | `https://opencode.ai/zen/go/v1` | `kimi-k2.6` |
| `glm-5` | Family A | `openai/glm-5` | `https://opencode.ai/zen/go/v1` | `glm-5` |
| `glm-5.1` | Family A | `openai/glm-5.1` | `https://opencode.ai/zen/go/v1` | `glm-5.1` |
| `mimo-v2-pro` | Family A | `openai/mimo-v2-pro` | `https://opencode.ai/zen/go/v1` | `mimo-v2-pro` |
| `mimo-v2-omni` | Family A | `openai/mimo-v2-omni` | `https://opencode.ai/zen/go/v1` | `mimo-v2-omni` |
| `mimo-v2.5-pro` | Family A | `openai/mimo-v2.5-pro` | `https://opencode.ai/zen/go/v1` | `mimo-v2.5-pro` |
| `mimo-v2.5` | Family A | `openai/mimo-v2.5` | `https://opencode.ai/zen/go/v1` | `mimo-v2.5` |
| `qwen3.5-plus` | Family A | `openai/qwen3.5-plus` | `https://opencode.ai/zen/go/v1` | `qwen3.5-plus` |
| `qwen3.6-plus` | Family A | `openai/qwen3.6-plus` | `https://opencode.ai/zen/go/v1` | `qwen3.6-plus` |
| `minimax-m2.5` | Family B | `anthropic/minimax-m2.5` | `https://opencode.ai/zen/go` | `minimax-m2.5` |
| `minimax-m2.7` | Family B | `anthropic/minimax-m2.7` | `https://opencode.ai/zen/go` | `minimax-m2.7` |

## Minimal operating procedure

1. Verify that the desired model alias exists in the active LiteLLM `config.yaml`.
2. Confirm that `litellm_params.model` and `api_base` match the correct upstream family.
3. Point the client to the LiteLLM gateway and select the same exposed alias.
4. Restart the gateway if the configuration changed.
5. Run the proxy battery before relying on the new routing path.

## Client-specific examples

If you need example settings for Anthropic-style desktop clients, see:

- `examples/claude-code-settings/`

These presets are optional examples, not a requirement for the gateway design.
