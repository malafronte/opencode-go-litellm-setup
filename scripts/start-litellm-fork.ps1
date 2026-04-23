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
    throw "LiteLLM runtime not found in $RuntimeDir. Run install-litellm-fork.ps1 first."
}

if (-not (Test-Path $litellmExe)) {
    throw "LiteLLM entrypoint not found in $litellmExe."
}

if (-not (Test-Path $ConfigPath)) {
    throw "LiteLLM config not found in $ConfigPath."
}

if (-not $env:OPENCODE_GO_API_KEY) {
    throw 'OPENCODE_GO_API_KEY was not found in the current environment.'
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
