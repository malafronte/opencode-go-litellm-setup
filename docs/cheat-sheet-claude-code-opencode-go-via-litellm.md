# Cheat Sheet - Claude Code con OpenCode Go tramite LiteLLM

## 1. Scopo

Questa cheat sheet serve a capire rapidamente cosa cambiare per usare un modello `OpenCode Go` specifico dietro `Claude Code` tramite proxy locale `LiteLLM`.

Per la guida completa si veda `docs/guida-claude-code-opencode-go-via-litellm.md`.

## 2. Cosa non cambia

In `settings.json` restano stabili:

- `ANTHROPIC_BASE_URL = http://127.0.0.1:4000`
- `ANTHROPIC_AUTH_TOKEN = local-litellm-key`
- `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS = 1`

In `config.yaml` restano stabili:

```yaml
litellm_settings:
  drop_params: true
  modify_params: true
  use_chat_completions_url_for_anthropic_messages: true

general_settings:
  master_key: local-litellm-key
```

## 3. Famiglie di modelli

Famiglia A:

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

Per questi modelli usa:

- `litellm_params.model = openai/<modello>`
- `api_base = https://opencode.ai/zen/go/v1`

Famiglia B:

- `minimax-m2.5`
- `minimax-m2.7`

Per questi modelli usa:

- `litellm_params.model = anthropic/<modello>`
- `api_base = https://opencode.ai/zen/go`

## 4. Tabella rapidissima

| Modello | `litellm_params.model` | `api_base` | Alias da mettere in `settings.json` |
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

## 5. Procedura minima

1. Verifica che il modello scelto esista in `~/.claude/litellm/config.yaml` con `litellm_params.model` e `api_base` corretti.
2. Imposta in `~/.claude/settings.json` lo stesso alias in `ANTHROPIC_MODEL` e `ANTHROPIC_CUSTOM_MODEL_OPTION`.
3. Riavvia `LiteLLM`.
4. Apri una nuova sessione di `Claude Code`.

## 6. Comandi utili

Avvio proxy Windows:

```powershell
pwsh -File "$HOME\.claude\litellm\start-litellm.ps1"
```

Test rapido del bridge Windows:

```powershell
pwsh -File "$HOME\.claude\litellm\test-litellm.ps1"
```

Batteria automatica del repository:

```powershell
py .\assets\litellm-fork\tests\run-opencode-go-battery.py --mode all --models kimi-k2.6 glm-5 qwen3.5-plus minimax-m2.7
```

## 7. Nota pratica sugli alias Claude-style

Alias come:

- `claude-haiku-4-5-20251001`
- `claude-sonnet-4-5-20250929`
- `claude-opus-4-1-20250805`

non sono modelli OpenCode Go aggiuntivi. Servono solo come alias di compatibilita quando `Claude Code` non usa l'alias scelto dall'utente.
