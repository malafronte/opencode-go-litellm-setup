param(
    [string]$RuntimeDir = "$HOME\.claude\litellm-runtime",
    [string]$ConfigPath = "$HOME\.claude\litellm\config.yaml",
    [string]$ListenHost = "127.0.0.1",
    [int]$Port = 4000,
    [switch]$DetailedDebug
)

$ErrorActionPreference = 'Stop'

$pythonExe = Join-Path $RuntimeDir 'Scripts\python.exe'
$litellmExe = Join-Path $RuntimeDir 'Scripts\litellm.exe'

if (-not (Test-Path $pythonExe)) {
    throw "Runtime LiteLLM non trovato in $RuntimeDir. Eseguire prima install-litellm-fork.ps1."
}

if (-not (Test-Path $litellmExe)) {
    throw "Entrypoint LiteLLM non trovato in $litellmExe."
}

if (-not (Test-Path $ConfigPath)) {
    throw "Config LiteLLM non trovata in $ConfigPath."
}

if (-not $env:OPENCODE_GO_API_KEY) {
    throw 'Variabile OPENCODE_GO_API_KEY non trovata nell''ambiente corrente.'
}

$args = @(
    '--config', $ConfigPath,
    '--host', $ListenHost,
    '--port', $Port
)

if ($DetailedDebug) {
    $args += '--detailed_debug'
}

& $litellmExe @args