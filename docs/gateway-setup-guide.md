# OpenCode Go + LiteLLM Gateway Setup Guide

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

- `model: openai/<nome-modello>`
- `api_base: https://opencode.ai/zen/go/v1`

### 4.2 Family B — upstream `messages`

These models should be configured as Anthropic-compatible upstream targets:

- `minimax-m2.5`
- `minimax-m2.7`

For these models, the gateway should use:

- `model: anthropic/<nome-modello>`
- `api_base: https://opencode.ai/zen/go`

Important note:

for Anthropic-compatible upstream models, do not append `/v1/messages` to `api_base`, because LiteLLM adds the protocol path when needed.

## 5. Cosa non cambia mai

Indipendentemente dal modello scelto, questi parametri restano stabili.

### 5.1 Parametri stabili in `settings.json`

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

Questi valori non dipendono dal modello:

- `ANTHROPIC_BASE_URL`
- `ANTHROPIC_AUTH_TOKEN`
- `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS`

### 5.2 Parametri stabili in `config.yaml`

```yaml
litellm_settings:
  drop_params: true
  modify_params: true
  use_chat_completions_url_for_anthropic_messages: true

general_settings:
  master_key: local-litellm-key
```

Questi valori devono restare coerenti con il bridge gia validato.

## 6. Cosa cambia quando si cambia modello

Per usare un modello OpenCode Go diverso, in pratica cambiano solo due aree.

### 6.1 In `settings.json`

Devi cambiare questi due campi, mettendo lo stesso alias in entrambi:

- `ANTHROPIC_MODEL`
- `ANTHROPIC_CUSTOM_MODEL_OPTION`

Facoltativamente puoi aggiornare anche:

- `ANTHROPIC_CUSTOM_MODEL_OPTION_NAME`
- `ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION`

### 6.2 In `config.yaml`

Devi avere un blocco `model_list` coerente con il modello scelto:

- `model_name`: alias esposto a `Claude Code`;
- `litellm_params.model`: upstream reale con provider corretto;
- `litellm_params.api_base`: endpoint corretto per la famiglia del modello.

## 7. Tabella rapida: cosa impostare per ogni modello attuale

La tabella seguente e il riferimento principale del documento.

| Modello OpenCode Go | Famiglia | `model_name` in `config.yaml` | `litellm_params.model` | `api_base` | Cosa mettere in `ANTHROPIC_MODEL` e `ANTHROPIC_CUSTOM_MODEL_OPTION` |
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

## 8. Configurazione pronta per tutti i modelli attuali

Se vuoi una base gia completa, puoi usare il template del repository:

- `assets/litellm-fork/opencode-go-config.template.yaml`

Questo template include gia i modelli attuali di entrambe le famiglie.

Una base completa equivalente e questa:

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

## 9. Esempio pratico: come passare da un modello all'altro

### 9.1 Per usare `glm-5`

In `config.yaml` deve esistere:

```yaml
- model_name: glm-5
  litellm_params:
    model: openai/glm-5
    api_base: https://opencode.ai/zen/go/v1
    api_key: os.environ/OPENCODE_GO_API_KEY
```

In `settings.json` devi mettere:

```json
{
  "env": {
    "ANTHROPIC_CUSTOM_MODEL_OPTION": "glm-5",
    "ANTHROPIC_MODEL": "glm-5"
  }
}
```

### 9.2 Per usare `minimax-m2.7`

In `config.yaml` deve esistere:

```yaml
- model_name: minimax-m2.7
  litellm_params:
    model: anthropic/minimax-m2.7
    api_base: https://opencode.ai/zen/go
    api_key: os.environ/OPENCODE_GO_API_KEY
```

In `settings.json` devi mettere:

```json
{
  "env": {
    "ANTHROPIC_CUSTOM_MODEL_OPTION": "minimax-m2.7",
    "ANTHROPIC_MODEL": "minimax-m2.7"
  }
}
```

## 10. Alias Claude-style: quando servono davvero

Gli alias come:

- `claude-haiku-4-5-20251001`
- `claude-sonnet-4-5-20250929`
- `claude-opus-4-1-20250805`

non sono modelli OpenCode Go distinti.
Sono alias di compatibilita utili quando `Claude Code` invia al proxy un nome modello Anthropic nativo invece dell'alias scelto dall'utente.

Questi alias servono soprattutto in due casi:

1. test manuali con preset dedicati;
2. riduzione di errori `ProxyModelNotFoundError` quando il client cambia nome modello in modo implicito.

Se vuoi usare davvero un modello OpenCode Go specifico, la regola consigliata resta:

- esporre nel proxy un alias uguale al nome reale del modello OpenCode Go;
- impostare `ANTHROPIC_MODEL` e `ANTHROPIC_CUSTOM_MODEL_OPTION` con quello stesso alias.

## 11. Struttura dei file coinvolti

Il setup usa i seguenti file nella home dell'utente:

```text
~/.claude/
  settings.json
  litellm/
    config.yaml
    set-opencode-go-key.ps1
    start-litellm.ps1
    test-litellm.ps1
```

Nel repository sono presenti anche questi file di supporto:

```text
assets/
  litellm-fork/
    opencode-go-config.template.yaml
    settings-presets/
    tests/
```

## 12. Procedura operativa su Windows

### 12.1 Salvare la API key nell'ambiente utente

```powershell
pwsh -File "$HOME\.claude\litellm\set-opencode-go-key.ps1" -ApiKey "<CHIAVE_OPENCODE_GO>"
```

### 12.2 Aprire un nuovo terminale

Questo passaggio e importante, perche lo script di avvio del proxy controlla la variabile nell'ambiente della sessione corrente.

### 12.3 Scegliere il modello nel `config.yaml`

Se il modello e gia nel file, non devi aggiungere altro.
Se il modello non e presente, usa la tabella del capitolo 7 per aggiungere la riga corretta.

### 12.4 Impostare il modello in `settings.json`

Imposta:

- `ANTHROPIC_MODEL`
- `ANTHROPIC_CUSTOM_MODEL_OPTION`

con l'alias del modello che vuoi usare.

### 12.5 Avviare il gateway locale

```powershell
pwsh -File "$HOME\.claude\litellm\start-litellm.ps1"
```

Se la sessione non ha ereditato la variabile ambiente, conviene aprire un nuovo terminale oppure esportarla esplicitamente prima dell'avvio.

### 12.6 Testare il bridge prima di aprire Claude Code

```powershell
pwsh -File "$HOME\.claude\litellm\test-litellm.ps1"
```

### 12.7 Aprire una nuova sessione di Claude Code

Dopo la modifica del modello o del proxy, conviene sempre aprire una nuova sessione del client.

## 13. Procedura equivalente su Linux

### 13.1 Esportare la chiave API

```bash
export OPENCODE_GO_API_KEY="<CHIAVE_OPENCODE_GO>"
```

### 13.2 Usare un `config.yaml` coerente con la famiglia del modello

Il principio e identico a Windows:

- famiglia A -> `openai/<modello>` e `https://opencode.ai/zen/go/v1`;
- famiglia B -> `anthropic/<modello>` e `https://opencode.ai/zen/go`.

### 13.3 Avviare LiteLLM

```bash
uvx --from 'litellm[proxy]==1.83.11' litellm \
  --config "$HOME/.claude/litellm/config.yaml" \
  --host 127.0.0.1 \
  --port 4000
```

### 13.4 Verificare il bridge con `curl`

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

## 14. Troubleshooting essenziale

### 14.1 `Missing OPENCODE_GO_API_KEY`

Cause probabili:

- la chiave non e stata salvata;
- il terminale non e stato riaperto;
- la chiave esiste nell'ambiente utente ma non nella sessione corrente.

### 14.2 `Invalid model name passed`

Questo errore indica che `ANTHROPIC_MODEL` non corrisponde a un `model_name` esposto nel `config.yaml`.

Correzione:

1. verificare l'alias scelto in `settings.json`;
2. verificare che esista in `model_list`;
3. riavviare il proxy.

### 14.3 Routing verso `v1/responses`

Se il proxy usa il percorso sbagliato per i modelli della famiglia A, verificare:

```yaml
litellm_settings:
  use_chat_completions_url_for_anthropic_messages: true
```

### 14.4 Errori su `reasoning_content`

Per i turni multi-turn con tool-use, mantenere:

```yaml
litellm_settings:
  modify_params: true
```

### 14.5 Caso speciale `minimax-m2.5`

Nel test automatico e stato osservato un caso specifico: il primo turno di tool-use puo fermarsi con `max_tokens` e con il marker `<minimax:tool_call>` al posto del blocco `tool_use` strutturato.

La batteria del repository gestisce gia questo caso con una variante dedicata.

## 15. Verifica consigliata dopo ogni cambio modello

La sequenza minima consigliata e questa:

1. aggiornare `settings.json` con l'alias del modello scelto;
2. verificare che `config.yaml` esponga quel modello con provider e `api_base` corretti;
3. riavviare `LiteLLM`;
4. eseguire il test locale del proxy;
5. solo dopo aprire una nuova sessione di `Claude Code`.

Per una verifica piu ampia si vedano anche:

- `docs/opencode-go-test-battery.md`
- `docs/litellm-fork-distribution.md`

## 16. Checklist rapida: cosa cambiare per usare un modello diverso

Quando vuoi usare un modello diverso, chiediti solo queste quattro cose:

1. il modello appartiene alla famiglia A o alla famiglia B?
2. nel `config.yaml` c'e una riga con `model_name` uguale al nome del modello?
3. il valore di `litellm_params.model` usa `openai/` o `anthropic/` correttamente?
4. `ANTHROPIC_MODEL` e `ANTHROPIC_CUSTOM_MODEL_OPTION` puntano allo stesso alias?

Se queste quattro condizioni sono vere, il resto del setup non cambia.

## 17. Conclusione

Il workaround con `LiteLLM` non va piu letto come una soluzione specifica per `Kimi K2.6`, ma come una guida generale per usare i modelli attuali di `OpenCode Go` dietro `Claude Code`.

Il punto decisivo non e il nome del modello in se, ma la famiglia di endpoint a cui appartiene:

- famiglia A -> upstream OpenAI-compatible;
- famiglia B -> upstream Anthropic-compatible.

Una volta chiarita questa distinzione, per usare un modello diverso l'utente deve cambiare soltanto:

- l'entry corrispondente in `config.yaml`;
- l'alias impostato in `ANTHROPIC_MODEL` e `ANTHROPIC_CUSTOM_MODEL_OPTION`.

Il resto del bridge locale puo restare invariato.

| Elemento | Deve coincidere con | Motivo |
| --- | --- | --- |
| `ANTHROPIC_AUTH_TOKEN` | `general_settings.master_key` | il client deve autenticarsi sul proxy locale |
| `ANTHROPIC_MODEL` | `model_list[].model_name` | il client deve chiedere un alias esposto dal gateway |
| `api_key: os.environ/OPENCODE_GO_API_KEY` | variabile ambiente reale `OPENCODE_GO_API_KEY` | LiteLLM legge la chiave dall'ambiente |
| `ANTHROPIC_BASE_URL` | host e porta di LiteLLM | il client deve colpire il proxy e non il provider remoto |

## 10. Problemi noti e troubleshooting

### 10.1 Errore: `Missing OPENCODE_GO_API_KEY`

Cause probabili:

- la chiave non e stata salvata;
- e stata salvata ma il terminale non e stato riaperto;
- la variabile e presente in un altro profilo utente.

Correzione:

1. rieseguire lo script di salvataggio della chiave;
2. aprire un nuovo terminale;
3. verificare con il comando adatto alla shell in uso.

### 10.2 Errore: `uvx is not available on PATH`

Cause probabili:

- `uv` non e installato;
- l'installazione esiste ma il `PATH` non e aggiornato.

Correzione:

1. installare `uv`;
2. riaprire il terminale;
3. verificare `uvx --version`.

### 10.3 Errore iniziale: `No module named 'websockets'`

Questo problema emerge quando si tenta di avviare `LiteLLM` senza l'extra `proxy`.

La forma corretta e:

```text
litellm[proxy]==1.83.11
```

Non basta usare il pacchetto base `litellm`.

### 10.4 Errore iniziale: richiesta inoltrata a `v1/responses`

Nel setup oggetto di questa documentazione, `LiteLLM` ha inizialmente provato a inoltrare il traffico verso:

```text
https://opencode.ai/zen/go/v1/responses
```

Questo ha prodotto un `404`, perche il provider testato per `Kimi K2.6` doveva essere raggiunto tramite:

```text
https://opencode.ai/zen/go/v1/chat/completions
```

La correzione applicata e stata:

```yaml
litellm_settings:
  use_chat_completions_url_for_anthropic_messages: true
```

### 10.5 Il test funziona, ma Claude Code non risponde come previsto

Se il test diretto del proxy ha successo ma `Claude Code` continua a non usare il gateway, conviene verificare:

1. che `settings.json` sia quello effettivamente letto dal client;
2. che sia stata aperta una nuova sessione del client dopo la modifica;
3. che `ANTHROPIC_BASE_URL` punti ancora a `127.0.0.1:4000`;
4. che il proxy sia realmente in esecuzione.

### 10.6 Errore: `Invalid model name passed in model=claude-haiku-4-5-20251001`

Questo errore indica che il proxy ha ricevuto da `Claude Code` un nome modello Anthropic nativo, ma quel nome non era presente negli alias esposti dal `model_list` di `LiteLLM`.

Correzione consigliata:

1. aggiungere nel `config.yaml` un alias con lo stesso `model_name` ricevuto nel log;
2. farlo puntare allo stesso upstream reale usato per `kimi-k2.6`;
3. riavviare il proxy.

Esempio:

```yaml
- model_name: claude-haiku-4-5-20251001
  litellm_params:
    model: openai/kimi-k2.6
    api_base: https://opencode.ai/zen/go/v1
    api_key: os.environ/OPENCODE_GO_API_KEY
```

### 10.7 Errore: `thinking is enabled but reasoning_content is missing in assistant tool call message`

Questo errore indica che una conversazione con tool-use e blocchi di reasoning e stata convertita in una forma che il provider upstream non accetta per quel turno specifico.

Nel setup documentato, il rimedio consigliato e attivare il workaround nativo di `LiteLLM`:

```yaml
litellm_settings:
  modify_params: true
```

Dopo la modifica e necessario riavviare il proxy.

### 10.8 La porta `4000` e gia occupata

In questo caso si puo:

1. liberare la porta in uso;
2. scegliere una porta diversa;
3. aggiornare in modo coerente sia `start-litellm.ps1` sia `ANTHROPIC_BASE_URL`.

## 11. Aspetti di sicurezza e buone pratiche

Si raccomanda di non salvare la vera API key nei file di progetto o in repository condivisi.

Buone pratiche minime:

- tenere `OPENCODE_GO_API_KEY` fuori dal repository;
- non pubblicare screenshot o log che mostrano segreti;
- usare un token locale del proxy diverso dalla chiave upstream, come nel caso di `local-litellm-key`;
- limitare l'ascolto del proxy a `127.0.0.1` quando non esiste un'esigenza esplicita di rete locale.

## 12. Procedura consigliata per spiegare il workaround a colleghi o studenti

Per un contesto didattico conviene presentare il flusso in quattro fasi:

### 12.1 Fase 1 - problema iniziale

Si mostra che `Claude Code` e `OpenCode Go` non parlano nativamente lo stesso protocollo per questo modello.

### 12.2 Fase 2 - introduzione del gateway

Si spiega che `LiteLLM` non cambia il modello, ma traduce l'interfaccia di accesso tra il client e il provider remoto.

### 12.3 Fase 3 - verifica indipendente del bridge

Si esegue prima `test-litellm.ps1`, cosi da dimostrare che il gateway funziona anche senza aprire il client finale.

### 12.4 Fase 4 - uso reale nel client

Solo dopo la verifica del bridge si passa a `Claude Code`, in modo da distinguere chiaramente i problemi di infrastruttura dai problemi del client.

## 13. Checklist rapida di installazione

1. Installare o verificare `Python`, `uv` e `uvx`.
2. Creare `~/.claude/settings.json` con il base URL locale del gateway.
3. Creare `~/.claude/litellm/config.yaml` con il mapping del modello.
4. Salvare `OPENCODE_GO_API_KEY` nell'ambiente utente.
5. Avviare `LiteLLM` con `litellm[proxy]==1.83.11`.
6. Testare `http://127.0.0.1:4000/v1/messages`.
7. Aprire una nuova sessione di `Claude Code`.

## 14. Esito del setup documentato

Nel setup oggetto di questa documentazione, la verifica finale positiva e stata il seguente comportamento:

- il test locale del proxy ha restituito un payload Anthropic-style valido;
- il modello riportato nella risposta era `kimi-k2.6`;
- il contenuto finale atteso `ok` e stato restituito correttamente.

Questo costituisce evidenza pratica che il workaround e operativo.

## 15. Conclusione

Il collegamento tra `Claude Code` e `Kimi K2.6` tramite `OpenCode Go` non e un'integrazione diretta, ma un adattamento controllato di protocollo tramite `LiteLLM`.

Il punto critico non e soltanto l'autenticazione, ma la compatibilita del percorso API usato dal gateway. Per questo motivo la configurazione del proxy, la gestione delle variabili d'ambiente e il test indipendente del bridge devono essere considerati parti essenziali del setup, non dettagli secondari.

Se la procedura viene seguita in modo coerente, il workaround risulta ripetibile sia su Windows sia su Linux.

## 16. Distribuzione stabile del workaround

La procedura descritta in questo tutorial usa una soluzione validata localmente e puo essere sufficiente per una singola macchina.

Se il workaround deve essere condiviso con colleghi o studenti, la soluzione consigliata non e modificare la cache di `uvx` su ogni computer, ma mantenere una fork GitHub di `LiteLLM` con una tag esplicita contenente il fix.

Il repository include gia:

- una patch riapplicabile in `assets/litellm-fork/patches/`;
- script di installazione Windows e Linux in `assets/litellm-fork/`;
- una guida dedicata in `docs/litellm-fork-distribution.md`.

La patch sul codice di `LiteLLM` non va intesa come una patch solo per `Kimi K2.6`: il fix puo essere trattato come una correzione generale del bridge Anthropic -> OpenAI-compatible sui turni con `thinking` e `tool_calls`.

Per supportare piu modelli di `OpenCode Go`, il passaggio corretto e distinguere nel `config.yaml` le famiglie di endpoint, non duplicare una patch per ogni modello.

Questa strategia rende il workaround:

- ripetibile;
- verificabile;
- piu adatto a contesti didattici o di team.
