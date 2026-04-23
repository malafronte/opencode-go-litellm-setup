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

Esempi attuali:

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

Esempi attuali:

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

## 6. Comandi consigliati

### 6.0 Comandi pronti per il config reale attuale

Al momento il `config.yaml` reale espone questi alias:

- `kimi-k2.6`
- `claude-haiku-4-5-20251001`
- `claude-sonnet-4-5-20250929`
- `claude-opus-4-1-20250805`

Nel setup corrente tutti e quattro gli alias puntano allo stesso upstream `openai/kimi-k2.6`.
Questo significa che la batteria, nello stato attuale, verifica soprattutto:

- corretto riconoscimento degli alias da parte del proxy;
- assenza di `ProxyModelNotFoundError` con i nomi Anthropic-style usati da `Claude Code`;
- stabilita del bridge multi-turn sul modello `kimi-k2.6` esposto con alias diversi.

Smoke test su tutti gli alias reali, Windows:

```powershell
py .\assets\litellm-fork\tests\run-opencode-go-battery.py --mode smoke --models kimi-k2.6 claude-haiku-4-5-20251001 claude-sonnet-4-5-20250929 claude-opus-4-1-20250805
```

Smoke test su tutti gli alias reali, Linux:

```bash
python3 ./assets/litellm-fork/tests/run-opencode-go-battery.py --mode smoke --models kimi-k2.6 claude-haiku-4-5-20251001 claude-sonnet-4-5-20250929 claude-opus-4-1-20250805
```

Tool-loop su tutti gli alias reali, Windows:

```powershell
py .\assets\litellm-fork\tests\run-opencode-go-battery.py --mode tool-loop --models kimi-k2.6 claude-haiku-4-5-20251001 claude-sonnet-4-5-20250929 claude-opus-4-1-20250805
```

Tool-loop su tutti gli alias reali, Linux:

```bash
python3 ./assets/litellm-fork/tests/run-opencode-go-battery.py --mode tool-loop --models kimi-k2.6 claude-haiku-4-5-20251001 claude-sonnet-4-5-20250929 claude-opus-4-1-20250805
```

Batteria completa su tutti gli alias reali, Windows:

```powershell
py .\assets\litellm-fork\tests\run-opencode-go-battery.py --mode all --models kimi-k2.6 claude-haiku-4-5-20251001 claude-sonnet-4-5-20250929 claude-opus-4-1-20250805
```

Finche il `config.yaml` reale non viene esteso con alias aggiuntivi verso altri upstream, `GO-04` resta non applicabile perche non c'e ancora un alias della famiglia `messages`.

### 6.1 Smoke test su una lista di modelli

Windows:

```powershell
py .\assets\litellm-fork\tests\run-opencode-go-battery.py --mode smoke --models kimi-k2.6 qwen3.5-plus minimax-m2.5
```

Linux:

```bash
python3 ./assets/litellm-fork/tests/run-opencode-go-battery.py --mode smoke --models kimi-k2.6 qwen3.5-plus minimax-m2.5
```

### 6.2 Tool-loop test sulla famiglia `chat/completions`

Windows:

```powershell
py .\assets\litellm-fork\tests\run-opencode-go-battery.py --mode tool-loop --models kimi-k2.6 glm-5 qwen3.6-plus
```

Linux:

```bash
python3 ./assets/litellm-fork/tests/run-opencode-go-battery.py --mode tool-loop --models kimi-k2.6 glm-5 qwen3.6-plus
```

### 6.3 Batteria completa su un set misto

```powershell
py .\assets\litellm-fork\tests\run-opencode-go-battery.py --mode all --models kimi-k2.6 qwen3.5-plus minimax-m2.5
```

### 6.4 Variante specifica per `minimax-m2.5`

Quando vuoi isolare il comportamento reale di `minimax-m2.5` sul tool-use, usa questo comando dedicato:

```powershell
py .\assets\litellm-fork\tests\run-opencode-go-battery.py --mode tool-loop --models minimax-m2.5
```

La batteria applica automaticamente la variante specifica del primo turno per questo alias.

## 7. Risultato atteso dello script

Lo script deve produrre righe come queste:

```text
[PASS] health http://127.0.0.1:4000
[PASS] smoke kimi-k2.6 -> ok
[PASS] tool-loop kimi-k2.6 -> tool-loop-ok
Summary: 2 passed, 0 failed
```

Interpretazione minima:

- se fallisce `health`, il proxy non e raggiungibile;
- se fallisce `smoke`, il problema e nel routing di base o nell'autenticazione;
- se fallisce `tool-loop`, il problema e tipicamente nel bridge multi-turn, nella gestione del tool-use o del reasoning.

## 8. Matrice dei test consigliati

| ID | Test | Target | Esecuzione | Esito atteso |
| --- | --- | --- | --- | --- |
| GO-01 | Health del proxy | Tutti | automatico | `HEAD /` risponde senza errori critici |
| GO-02 | Smoke test su ogni alias configurato | Tutti | automatico | testo finale `ok` |
| GO-03 | Tool-loop su modelli `chat/completions` | Famiglia A | automatico | testo finale `tool-loop-ok` |
| GO-04 | Smoke test su modelli `messages` | Famiglia B | automatico | testo finale `ok` |
| GO-05 | Claude Code: lettura file e sintesi | 1 modello per famiglia | manuale | nessun errore proxy, nessuna perdita di contesto |
| GO-06 | Claude Code: file edit su piu turni | almeno 1 modello Famiglia A | manuale | nessun errore su `reasoning_content` |
| GO-07 | Claude Code: cambio modello alias | set di modelli del tuo abbonamento | manuale | nessun `ProxyModelNotFoundError` |

## 9. Test manuali dentro Claude Code

### 9.0 Checklist manuale allineata ai 4 alias correnti

Alias da verificare:

- `kimi-k2.6`
- `claude-haiku-4-5-20251001`
- `claude-sonnet-4-5-20250929`
- `claude-opus-4-1-20250805`

Per ogni alias:

1. Impostare in `~/.claude/settings.json` sia `ANTHROPIC_MODEL` sia `ANTHROPIC_CUSTOM_MODEL_OPTION` con lo stesso alias.
2. Riavviare la sessione di `Claude Code` o aprire una nuova sessione pulita.
3. Eseguire il prompt GO-05 di sola lettura.
4. Eseguire in sequenza i 3 prompt GO-06 di creazione, modifica e cancellazione file.
5. Registrare per l'alias: esito `PASS` o `FAIL`, eventuale `ProxyModelNotFoundError`, eventuale errore `reasoning_content missing`, e tempo percepito di risposta.

Checklist sintetica:

- `kimi-k2.6`: GO-05 [ ], GO-06 [ ], `ProxyModelNotFoundError` [ ], `reasoning_content missing` [ ], note [ ]
- `claude-haiku-4-5-20251001`: GO-05 [ ], GO-06 [ ], `ProxyModelNotFoundError` [ ], `reasoning_content missing` [ ], note [ ]
- `claude-sonnet-4-5-20250929`: GO-05 [ ], GO-06 [ ], `ProxyModelNotFoundError` [ ], `reasoning_content missing` [ ], note [ ]
- `claude-opus-4-1-20250805`: GO-05 [ ], GO-06 [ ], `ProxyModelNotFoundError` [ ], `reasoning_content missing` [ ], note [ ]

### 9.1 Sequenza pronta di 4 test manuali Claude Code

Test 1 - alias `kimi-k2.6`

Impostazioni da usare in `~/.claude/settings.json`:

- `ANTHROPIC_MODEL = kimi-k2.6`
- `ANTHROPIC_CUSTOM_MODEL_OPTION = kimi-k2.6`

Prompt da eseguire in ordine:

```text
Leggi docs/spec.md e riassumi in 5 punti gli obiettivi del progetto. Non modificare alcun file.
```

```text
Crea un file temporaneo docs/_proxy_battery_test_kimi.md con titolo, data di oggi e una breve nota di test.
```

```text
Riapri il file docs/_proxy_battery_test_kimi.md e aggiungi una riga finale con scritto: test multi-turn completato.
```

```text
Elimina il file temporaneo docs/_proxy_battery_test_kimi.md.
```

Test 2 - alias `claude-haiku-4-5-20251001`

Impostazioni da usare in `~/.claude/settings.json`:

- `ANTHROPIC_MODEL = claude-haiku-4-5-20251001`
- `ANTHROPIC_CUSTOM_MODEL_OPTION = claude-haiku-4-5-20251001`

Prompt da eseguire in ordine:

```text
Leggi docs/plan.md e dimmi in 4 punti quale iterazione viene prima e quale dopo. Non modificare file.
```

```text
Crea un file temporaneo docs/_proxy_battery_test_haiku.md con una checklist di tre righe.
```

```text
Aggiorna docs/_proxy_battery_test_haiku.md marcando la prima voce come completata.
```

```text
Elimina il file temporaneo docs/_proxy_battery_test_haiku.md.
```

Test 3 - alias `claude-sonnet-4-5-20250929`

Impostazioni da usare in `~/.claude/settings.json`:

- `ANTHROPIC_MODEL = claude-sonnet-4-5-20250929`
- `ANTHROPIC_CUSTOM_MODEL_OPTION = claude-sonnet-4-5-20250929`

Prompt da eseguire in ordine:

```text
Leggi docs/test-matrix.md e riassumi i gruppi di test in 5 punti. Non modificare file.
```

```text
Crea un file temporaneo docs/_proxy_battery_test_sonnet.md con una tabella markdown di due colonne e due righe.
```

```text
Aggiungi in fondo a docs/_proxy_battery_test_sonnet.md una nota finale con scritto: verifica sonnet completata.
```

```text
Elimina il file temporaneo docs/_proxy_battery_test_sonnet.md.
```

Test 4 - alias `claude-opus-4-1-20250805`

Impostazioni da usare in `~/.claude/settings.json`:

- `ANTHROPIC_MODEL = claude-opus-4-1-20250805`
- `ANTHROPIC_CUSTOM_MODEL_OPTION = claude-opus-4-1-20250805`

Prompt da eseguire in ordine:

```text
Leggi README.md e descrivi in 5 punti il contenuto del repository. Non modificare file.
```

```text
Crea un file temporaneo docs/_proxy_battery_test_opus.md con titolo, breve descrizione e un elenco puntato di due elementi.
```

```text
Aggiorna docs/_proxy_battery_test_opus.md aggiungendo una sezione finale chiamata Esito con valore PASS.
```

```text
Elimina il file temporaneo docs/_proxy_battery_test_opus.md.
```

### 9.2 Blocchi `settings.json` pronti da incollare

Per scambiare piu facilmente i preset durante i test manuali, il repository include anche questi 4 file separati:

- `assets/litellm-fork/settings-presets/settings-kimi-k2.6.json`
- `assets/litellm-fork/settings-presets/settings-claude-haiku-4-5-20251001.json`
- `assets/litellm-fork/settings-presets/settings-claude-sonnet-4-5-20250929.json`
- `assets/litellm-fork/settings-presets/settings-claude-opus-4-1-20250805.json`

### 9.3 Comandi PowerShell rapidi per sostituire `settings.json`

Eseguire questi comandi dalla root del repository per sostituire rapidamente `C:\Users\genna\.claude\settings.json` durante i test manuali.
Dopo ogni sostituzione conviene aprire una nuova sessione di `Claude Code`.

Preset `kimi-k2.6`:

```powershell
Copy-Item .\assets\litellm-fork\settings-presets\settings-kimi-k2.6.json "$HOME\.claude\settings.json" -Force
```

Preset `claude-haiku-4-5-20251001`:

```powershell
Copy-Item .\assets\litellm-fork\settings-presets\settings-claude-haiku-4-5-20251001.json "$HOME\.claude\settings.json" -Force
```

Preset `claude-sonnet-4-5-20250929`:

```powershell
Copy-Item .\assets\litellm-fork\settings-presets\settings-claude-sonnet-4-5-20250929.json "$HOME\.claude\settings.json" -Force
```

Preset `claude-opus-4-1-20250805`:

```powershell
Copy-Item .\assets\litellm-fork\settings-presets\settings-claude-opus-4-1-20250805.json "$HOME\.claude\settings.json" -Force
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

### GO-05 - Lettura e sintesi

Prompt suggerito:

```text
Leggi docs/spec.md e riassumi in 5 punti gli obiettivi del progetto. Non modificare alcun file.
```

Esito atteso:

- risposta coerente;
- nessun errore LiteLLM;
- nessun errore di modello non trovato.

### GO-06 - Multi-turn con modifica reale

Prompt 1:

```text
Crea un file temporaneo docs/_proxy_battery_test.md con titolo, data di oggi e una breve nota di test.
```

Prompt 2:

```text
Riapri il file appena creato e aggiungi una riga finale con scritto: test multi-turn completato.
```

Prompt 3:

```text
Elimina il file temporaneo docs/_proxy_battery_test.md.
```

Esito atteso:

- tutte le operazioni riescono;
- nessun `400` del proxy;
- nessun errore su `reasoning_content missing`.

### GO-07 - Cambio modello

Ripetere almeno GO-05 e GO-06 con:

- un modello della famiglia `chat/completions`;
- un secondo modello della stessa famiglia;
- almeno un modello della famiglia `messages`, se configurato nel proxy.

## 10. Ordine di esecuzione raccomandato

1. Eseguire `GO-01` e `GO-02` su tutti gli alias esposti.
2. Eseguire `GO-03` su almeno due modelli della famiglia `chat/completions`.
3. Eseguire `GO-04` sui modelli della famiglia `messages`.
4. Solo dopo passare a `GO-05`, `GO-06` e `GO-07` in `Claude Code`.

## 11. Uso della batteria come criterio di accettazione

Il setup puo essere considerato accettabile se:

1. tutti gli smoke test passano sugli alias configurati;
2. almeno un modello `chat/completions` supera il `tool-loop`;
3. `Claude Code` completa almeno un flusso multi-turn reale senza errori del proxy.

## 12. Limiti della batteria

- Un test positivo non dimostra che tutti i modelli supportino tool-use nello stesso modo.
- I modelli della famiglia `messages` potrebbero richiedere test aggiuntivi specifici in base alle loro capacita reali.
- La batteria e pensata per convalidare il bridge locale, non per benchmarkare la qualita dei modelli.
