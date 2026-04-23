# Test Battery for OpenCode Go with LiteLLM Gateway

## 1. Scope

This document defines a practical validation battery for a local setup in which:

- an Anthropic-compatible client sends requests in `v1/messages` format;
- `LiteLLM` acts as the local gateway and translation layer;
- `OpenCode Go` provides the upstream models.

The battery intentionally separates three layers of validation:

1. local gateway health;
2. correct routing toward OpenCode Go model aliases;
3. real client behavior across tool-use and multi-turn exchanges.

## 2. Validation objective

The goal is not just to observe a simple reply, but to verify that the gateway behaves correctly across a broader class of scenarios:

- basic reply path;
- prompt-driven tool-use request;
- second turn with `tool_result`;
- real client-side workflows involving read, planning, and controlled edits.

## 3. Preconditions

Before running the battery, verify these assumptions:

- `LiteLLM` is running locally;
- the active LiteLLM configuration exposes the model aliases under test;
- `OPENCODE_GO_API_KEY` is available in the proxy environment;
- the client under test points to the local gateway base URL.

### 3.1 Example configuration block

The current local configuration can expose multiple aliases, including Anthropic-style aliases for client compatibility, while routing them to OpenCode Go upstream models.

If you want to preserve those aliases and add direct Family A and Family B model mappings, the base configuration can look like this:

```yaml
model_list:
	- model_name: kimi-k2.6
		litellm_params:
			model: openai/kimi-k2.6
			api_base: https://opencode.ai/zen/go/v1
			api_key: os.environ/OPENCODE_GO_API_KEY

	- model_name: claude-haiku-4-5-20251001
		litellm_params:
			model: openai/kimi-k2.6
			api_base: https://opencode.ai/zen/go/v1
			api_key: os.environ/OPENCODE_GO_API_KEY

	- model_name: claude-sonnet-4-5-20250929
		litellm_params:
			model: openai/kimi-k2.6
			api_base: https://opencode.ai/zen/go/v1
			api_key: os.environ/OPENCODE_GO_API_KEY

	- model_name: claude-opus-4-1-20250805
		litellm_params:
			model: openai/kimi-k2.6
			api_base: https://opencode.ai/zen/go/v1
			api_key: os.environ/OPENCODE_GO_API_KEY

	- model_name: glm-5
		litellm_params:
			model: openai/glm-5
			api_base: https://opencode.ai/zen/go/v1
			api_key: os.environ/OPENCODE_GO_API_KEY

	- model_name: qwen3.5-plus
		litellm_params:
			model: openai/qwen3.5-plus
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

This block preserves compatibility with Anthropic-style client settings while adding direct aliases for realistic Family A and Family B verification.

## 4. Model families to test

For OpenCode Go, it is useful to distinguish two upstream families.

### 4.1 Family A — upstream `chat/completions`

Current examples:

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

This family is the most important one for validating the Anthropic-to-OpenAI-compatible bridge.

### 4.2 Family B — upstream `messages`

Current examples:

- `minimax-m2.5`
- `minimax-m2.7`

This family verifies that the gateway also handles Anthropic-compatible upstream models without forcing OpenAI translation.

## 5. Automated battery script

The repository includes a parameterized Python script:

`tests/proxy-battery/run-opencode-go-battery.py`

The script runs two main checks:

- `smoke`: a simple prompt with an exact expected final reply;
- `tool-loop`: a first turn that explicitly requests tool use, followed by a second turn with `tool_result`.

To reduce false negatives observed with some OpenCode Go aliases, the `smoke` check includes a minimal retry when the model returns empty text.
For `minimax-m2.5`, the `tool-loop` applies a specific fallback: if the first turn stops with `stop_reason = max_tokens` and returns the textual marker `<minimax:tool_call>`, the battery retries that first turn with `max_tokens = 768` to obtain a structured `tool_use` block.

## 6. Recommended commands

### 6.0 Commands for the current local configuration

At the moment, the active local `config.yaml` exposes these aliases:

- `kimi-k2.6`
- `claude-haiku-4-5-20251001`
- `claude-sonnet-4-5-20250929`
- `claude-opus-4-1-20250805`

In the current setup, all four aliases point to the same upstream target: `openai/kimi-k2.6`.
This means the battery currently validates mostly:

- correct alias resolution by the proxy;
- absence of `ProxyModelNotFoundError` for Anthropic-style alias names used by the client;
- stability of the multi-turn bridge when the same upstream model is exposed through different aliases.

Smoke test on all currently configured aliases, Windows:

```powershell
py .\tests\proxy-battery\run-opencode-go-battery.py --mode smoke --models kimi-k2.6 claude-haiku-4-5-20251001 claude-sonnet-4-5-20250929 claude-opus-4-1-20250805
```

Smoke test on all currently configured aliases, Linux:

```bash
python3 ./tests/proxy-battery/run-opencode-go-battery.py --mode smoke --models kimi-k2.6 claude-haiku-4-5-20251001 claude-sonnet-4-5-20250929 claude-opus-4-1-20250805
```

Tool-loop on all currently configured aliases, Windows:

```powershell
py .\tests\proxy-battery\run-opencode-go-battery.py --mode tool-loop --models kimi-k2.6 claude-haiku-4-5-20251001 claude-sonnet-4-5-20250929 claude-opus-4-1-20250805
```

Tool-loop on all currently configured aliases, Linux:

```bash
python3 ./tests/proxy-battery/run-opencode-go-battery.py --mode tool-loop --models kimi-k2.6 claude-haiku-4-5-20251001 claude-sonnet-4-5-20250929 claude-opus-4-1-20250805
```

Full battery on all currently configured aliases, Windows:

```powershell
py .\tests\proxy-battery\run-opencode-go-battery.py --mode all --models kimi-k2.6 claude-haiku-4-5-20251001 claude-sonnet-4-5-20250929 claude-opus-4-1-20250805
```

Until the active `config.yaml` is extended with additional aliases targeting other upstream models, `GO-04` remains not applicable because there is still no alias mapped to the `messages` family.

### 6.1 Smoke test on a mixed model list

Windows:

```powershell
py .\tests\proxy-battery\run-opencode-go-battery.py --mode smoke --models kimi-k2.6 qwen3.5-plus minimax-m2.5
```

Linux:

```bash
python3 ./tests/proxy-battery/run-opencode-go-battery.py --mode smoke --models kimi-k2.6 qwen3.5-plus minimax-m2.5
```

### 6.2 Tool-loop test for the `chat/completions` family

Windows:

```powershell
py .\tests\proxy-battery\run-opencode-go-battery.py --mode tool-loop --models kimi-k2.6 glm-5 qwen3.6-plus
```

Linux:

```bash
python3 ./tests/proxy-battery/run-opencode-go-battery.py --mode tool-loop --models kimi-k2.6 glm-5 qwen3.6-plus
```

### 6.3 Full battery on a mixed set

```powershell
py .\tests\proxy-battery\run-opencode-go-battery.py --mode all --models kimi-k2.6 qwen3.5-plus minimax-m2.5
```

### 6.4 Dedicated variant for `minimax-m2.5`

When you want to isolate the real tool-use behavior of `minimax-m2.5`, use this dedicated command:

```powershell
py .\tests\proxy-battery\run-opencode-go-battery.py --mode tool-loop --models minimax-m2.5
```

The battery automatically applies the first-turn fallback variant for this alias.

## 7. Expected script output

The script should produce lines such as:

```text
[PASS] health http://127.0.0.1:4000
[PASS] smoke kimi-k2.6 -> ok
[PASS] tool-loop kimi-k2.6 -> tool-loop-ok
Summary: 2 passed, 0 failed
```

Minimal interpretation:

- if `health` fails, the proxy is not reachable;
- if `smoke` fails, the issue is usually basic routing or authentication;
- if `tool-loop` fails, the issue is typically in the multi-turn bridge, tool-use handling, or reasoning handling.

## 8. Recommended test matrix

| ID | Test | Target | Execution | Expected outcome |
| --- | --- | --- | --- | --- |
| GO-01 | Proxy health | All | automatic | `HEAD /` returns without critical errors |
| GO-02 | Smoke test for each configured alias | All | automatic | final text is `ok` |
| GO-03 | Tool-loop on `chat/completions` models | Family A | automatic | final text is `tool-loop-ok` |
| GO-04 | Smoke test on `messages` models | Family B | automatic | final text is `ok` |
| GO-05 | Client read-and-summarize flow | 1 model per family | manual | no proxy errors, no context loss |
| GO-06 | Client file-edit multi-turn flow | at least 1 Family A model | manual | no `reasoning_content` errors |
| GO-07 | Client alias switching | models available in your plan | manual | no `ProxyModelNotFoundError` |

## 9. Manual client tests

### 9.0 Manual checklist aligned with the current four aliases

Aliases to verify:

- `kimi-k2.6`
- `claude-haiku-4-5-20251001`
- `claude-sonnet-4-5-20250929`
- `claude-opus-4-1-20250805`

For each alias:

1. Set both `ANTHROPIC_MODEL` and `ANTHROPIC_CUSTOM_MODEL_OPTION` to the same alias in the client settings file.
2. Restart the client session or open a new clean session.
3. Run the GO-05 read-only prompt.
4. Run the three GO-06 prompts in sequence for file creation, update, and deletion.
5. Record for each alias: `PASS` or `FAIL`, any `ProxyModelNotFoundError`, any `reasoning_content missing` error, and perceived response time.

Compact checklist:

- `kimi-k2.6`: GO-05 [ ], GO-06 [ ], `ProxyModelNotFoundError` [ ], `reasoning_content missing` [ ], notes [ ]
- `claude-haiku-4-5-20251001`: GO-05 [ ], GO-06 [ ], `ProxyModelNotFoundError` [ ], `reasoning_content missing` [ ], notes [ ]
- `claude-sonnet-4-5-20250929`: GO-05 [ ], GO-06 [ ], `ProxyModelNotFoundError` [ ], `reasoning_content missing` [ ], notes [ ]
- `claude-opus-4-1-20250805`: GO-05 [ ], GO-06 [ ], `ProxyModelNotFoundError` [ ], `reasoning_content missing` [ ], notes [ ]

### 9.1 Ready-made sequence of four manual client tests

Test 1 — alias `kimi-k2.6`

Settings to use in the client configuration:

- `ANTHROPIC_MODEL = kimi-k2.6`
- `ANTHROPIC_CUSTOM_MODEL_OPTION = kimi-k2.6`

Prompts to run in order:

```text
Read `docs/spec.md` and summarize the project objectives in 5 bullet points. Do not modify any file.
```

```text
Create a temporary file `docs/_proxy_battery_test_kimi.md` with a title, today's date, and a short test note.
```

```text
Reopen `docs/_proxy_battery_test_kimi.md` and append a final line that says: `multi-turn test completed`.
```

```text
Delete the temporary file `docs/_proxy_battery_test_kimi.md`.
```

Test 2 — alias `claude-haiku-4-5-20251001`

Settings to use in the client configuration:

- `ANTHROPIC_MODEL = claude-haiku-4-5-20251001`
- `ANTHROPIC_CUSTOM_MODEL_OPTION = claude-haiku-4-5-20251001`

Prompts to run in order:

```text
Read `docs/plan.md` and explain in 4 bullet points which iteration comes first and which comes after. Do not modify files.
```

```text
Create a temporary file `docs/_proxy_battery_test_haiku.md` with a three-line checklist.
```

```text
Update `docs/_proxy_battery_test_haiku.md` by marking the first checklist item as completed.
```

```text
Delete the temporary file `docs/_proxy_battery_test_haiku.md`.
```

Test 3 — alias `claude-sonnet-4-5-20250929`

Settings to use in the client configuration:

- `ANTHROPIC_MODEL = claude-sonnet-4-5-20250929`
- `ANTHROPIC_CUSTOM_MODEL_OPTION = claude-sonnet-4-5-20250929`

Prompts to run in order:

```text
Read `docs/test-matrix.md` and summarize the test groups in 5 bullet points. Do not modify files.
```

```text
Create a temporary file `docs/_proxy_battery_test_sonnet.md` with a two-column, two-row Markdown table.
```

```text
Append a final note to `docs/_proxy_battery_test_sonnet.md` that says: `sonnet verification completed`.
```

```text
Delete the temporary file `docs/_proxy_battery_test_sonnet.md`.
```

Test 4 — alias `claude-opus-4-1-20250805`

Settings to use in the client configuration:

- `ANTHROPIC_MODEL = claude-opus-4-1-20250805`
- `ANTHROPIC_CUSTOM_MODEL_OPTION = claude-opus-4-1-20250805`

Prompts to run in order:

```text
Read `README.md` and describe the repository contents in 5 bullet points. Do not modify files.
```

```text
Create a temporary file `docs/_proxy_battery_test_opus.md` with a title, a short description, and a two-item bullet list.
```

```text
Update `docs/_proxy_battery_test_opus.md` by adding a final section named `Outcome` with value `PASS`.
```

```text
Delete the temporary file `docs/_proxy_battery_test_opus.md`.
```

### 9.2 Ready-to-use settings blocks

To swap presets more easily during manual tests, the repository also includes these four separate files:

- `examples/anthropic-client-presets/settings-kimi-k2.6.json`
- `examples/anthropic-client-presets/settings-claude-haiku-4-5-20251001.json`
- `examples/anthropic-client-presets/settings-claude-sonnet-4-5-20250929.json`
- `examples/anthropic-client-presets/settings-claude-opus-4-1-20250805.json`

### 9.3 Quick PowerShell commands to replace `settings.json`

Run these commands from the repository root to quickly replace `C:\Users\genna\.claude\settings.json` during manual tests.
After each replacement, it is recommended to open a new clean client session.

Preset `kimi-k2.6`:

```powershell
Copy-Item .\examples\anthropic-client-presets\settings-kimi-k2.6.json "$HOME\.claude\settings.json" -Force
```

Preset `claude-haiku-4-5-20251001`:

```powershell
Copy-Item .\examples\anthropic-client-presets\settings-claude-haiku-4-5-20251001.json "$HOME\.claude\settings.json" -Force
```

Preset `claude-sonnet-4-5-20250929`:

```powershell
Copy-Item .\examples\anthropic-client-presets\settings-claude-sonnet-4-5-20250929.json "$HOME\.claude\settings.json" -Force
```

Preset `claude-opus-4-1-20250805`:

```powershell
Copy-Item .\examples\anthropic-client-presets\settings-claude-opus-4-1-20250805.json "$HOME\.claude\settings.json" -Force
```

Blocco completo per `kimi-k2.6`:

```json
{
	"$schema": "https://json.schemastore.org/claude-code-settings.json",
	"env": {
		"ANTHROPIC_BASE_URL": "http://127.0.0.1:4000",
		"ANTHROPIC_AUTH_TOKEN": "local-litellm-key",
		"ANTHROPIC_CUSTOM_MODEL_OPTION": "kimi-k2.6",
		"ANTHROPIC_CUSTOM_MODEL_OPTION_NAME": "Kimi K2.6 via Gateway",
		"ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION": "Kimi K2.6 routed through a local LiteLLM gateway",
		"ANTHROPIC_MODEL": "kimi-k2.6",
		"CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": "1"
	},
	"permissions": {
		"deny": [
			"Read(.env)",
			"Read(.env.*)",
			"Read(secrets/**)",
			"Read(**/secrets/**)",
			"Edit(.env)",
			"Edit(.env.*)",
			"Write(.env)",
			"Write(.env.*)"
		]
	},
	"enabledPlugins": {},
	"effortLevel": "xhigh",
	"autoUpdatesChannel": "latest"
}
```

Blocco completo per `claude-haiku-4-5-20251001`:

```json
{
	"$schema": "https://json.schemastore.org/claude-code-settings.json",
	"env": {
		"ANTHROPIC_BASE_URL": "http://127.0.0.1:4000",
		"ANTHROPIC_AUTH_TOKEN": "local-litellm-key",
		"ANTHROPIC_CUSTOM_MODEL_OPTION": "claude-haiku-4-5-20251001",
		"ANTHROPIC_CUSTOM_MODEL_OPTION_NAME": "Claude Haiku 4.5 alias via Gateway",
		"ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION": "Claude Haiku 4.5 alias routed through the local LiteLLM gateway",
		"ANTHROPIC_MODEL": "claude-haiku-4-5-20251001",
		"CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": "1"
	},
	"permissions": {
		"deny": [
			"Read(.env)",
			"Read(.env.*)",
			"Read(secrets/**)",
			"Read(**/secrets/**)",
			"Edit(.env)",
			"Edit(.env.*)",
			"Write(.env)",
			"Write(.env.*)"
		]
	},
	"enabledPlugins": {},
	"effortLevel": "xhigh",
	"autoUpdatesChannel": "latest"
}
```

Blocco completo per `claude-sonnet-4-5-20250929`:

```json
{
	"$schema": "https://json.schemastore.org/claude-code-settings.json",
	"env": {
		"ANTHROPIC_BASE_URL": "http://127.0.0.1:4000",
		"ANTHROPIC_AUTH_TOKEN": "local-litellm-key",
		"ANTHROPIC_CUSTOM_MODEL_OPTION": "claude-sonnet-4-5-20250929",
		"ANTHROPIC_CUSTOM_MODEL_OPTION_NAME": "Claude Sonnet 4.5 alias via Gateway",
		"ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION": "Claude Sonnet 4.5 alias routed through the local LiteLLM gateway",
		"ANTHROPIC_MODEL": "claude-sonnet-4-5-20250929",
		"CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": "1"
	},
	"permissions": {
		"deny": [
			"Read(.env)",
			"Read(.env.*)",
			"Read(secrets/**)",
			"Read(**/secrets/**)",
			"Edit(.env)",
			"Edit(.env.*)",
			"Write(.env)",
			"Write(.env.*)"
		]
	},
	"enabledPlugins": {},
	"effortLevel": "xhigh",
	"autoUpdatesChannel": "latest"
}
```

Blocco completo per `claude-opus-4-1-20250805`:

```json
{
	"$schema": "https://json.schemastore.org/claude-code-settings.json",
	"env": {
		"ANTHROPIC_BASE_URL": "http://127.0.0.1:4000",
		"ANTHROPIC_AUTH_TOKEN": "local-litellm-key",
		"ANTHROPIC_CUSTOM_MODEL_OPTION": "claude-opus-4-1-20250805",
		"ANTHROPIC_CUSTOM_MODEL_OPTION_NAME": "Claude Opus 4.1 alias via Gateway",
		"ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION": "Claude Opus 4.1 alias routed through the local LiteLLM gateway",
		"ANTHROPIC_MODEL": "claude-opus-4-1-20250805",
		"CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": "1"
	},
	"permissions": {
		"deny": [
			"Read(.env)",
			"Read(.env.*)",
			"Read(secrets/**)",
			"Read(**/secrets/**)",
			"Edit(.env)",
			"Edit(.env.*)",
			"Write(.env)",
			"Write(.env.*)"
		]
	},
	"enabledPlugins": {},
	"effortLevel": "xhigh",
	"autoUpdatesChannel": "latest"
}
```

### GO-05 - Reading and summary

Suggested prompt:

```text
Read docs/spec.md and summarize the project objectives in 5 bullet points. Do not modify any file.
```

Expected outcome:

- coherent response;
- no LiteLLM errors;
- no model-not-found errors.

### GO-06 - Multi-turn with real edit

Prompt 1:

```text
Create a temporary file docs/_proxy_battery_test.md with a title, today's date, and a short test note.
```

Prompt 2:

```text
Reopen the file you just created and add a final line that says: multi-turn test completed.
```

Prompt 3:

```text
Delete the temporary file docs/_proxy_battery_test.md.
```

Expected outcome:

- all operations succeed;
- no proxy `400`;
- no `reasoning_content missing` errors.

### GO-07 - Model switch

Repeat at least GO-05 and GO-06 with:

- one model from the `chat/completions` family;
- a second model from the same family;
- at least one model from the `messages` family, if configured in the proxy.

## 10. Recommended execution order

1. Run `GO-01` and `GO-02` on all exposed aliases.
2. Run `GO-03` on at least two models from the `chat/completions` family.
3. Run `GO-04` on the models from the `messages` family.
4. Only then move to `GO-05`, `GO-06`, and `GO-07` in `Claude Code`.

## 11. Using the battery as an acceptance criterion

The setup can be considered acceptable if:

1. all smoke tests pass on the configured aliases;
2. at least one `chat/completions` model passes the `tool-loop`;
3. `Claude Code` completes at least one real multi-turn flow without proxy errors.

## 12. Limits of the battery

- A positive test does not prove that all models support tool use in the same way.
- Models in the `messages` family may require additional model-specific tests based on their actual capabilities.
- The battery is intended to validate the local bridge, not to benchmark model quality.
