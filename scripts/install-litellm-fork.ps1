param(
    [string]$Repo = "<github-user>/litellm",
    [string]$Ref = "v1.83.11-nightly-opencode-go1",
    [string]$RuntimeDir = "$HOME\.claude\litellm-runtime",
    [string]$SourceDir = "",
    [switch]$ForceReinstall
)

$ErrorActionPreference = 'Stop'

function Test-CommandExists {
    param([Parameter(Mandatory = $true)][string]$Name)

    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Invoke-NativeCommand {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$ArgumentList,
        [Parameter(Mandatory = $true)][string]$FailureMessage
    )

    & $FilePath @ArgumentList

    if ($LASTEXITCODE -ne 0) {
        throw $FailureMessage
    }
}

if (-not (Test-CommandExists -Name 'py')) {
    throw 'Python launcher `py` non trovato nel PATH.'
}

if (-not (Test-CommandExists -Name 'git')) {
    throw 'Git non trovato nel PATH. Serve per installare LiteLLM dalla fork GitHub.'
}

$pythonExe = Join-Path $RuntimeDir 'Scripts\python.exe'
$pipArgs = @('-m', 'pip')
$repoUrl = "https://github.com/$Repo.git"
$sourceDirProvided = -not [string]::IsNullOrWhiteSpace($SourceDir)

if ([string]::IsNullOrWhiteSpace($SourceDir)) {
    if ($env:SystemDrive) {
        $sourceId = [System.Guid]::NewGuid().ToString('N').Substring(0, 8)
        $SourceDir = Join-Path $env:SystemDrive "litellm-src-$sourceId"
    }
    else {
        $sourceId = [System.Guid]::NewGuid().ToString('N').Substring(0, 8)
        $SourceDir = Join-Path $HOME ".claude\litellm-src-$sourceId"
    }
}

if ($ForceReinstall -and (Test-Path $RuntimeDir)) {
    Remove-Item -Recurse -Force $RuntimeDir
}

if (-not (Test-Path $pythonExe)) {
    New-Item -ItemType Directory -Path $RuntimeDir -Force | Out-Null
    Invoke-NativeCommand -FilePath 'py' -ArgumentList @('-m', 'venv', $RuntimeDir) -FailureMessage "Creazione del virtual environment fallita in $RuntimeDir."
}

Invoke-NativeCommand -FilePath $pythonExe -ArgumentList ($pipArgs + @('install', '--upgrade', 'pip')) -FailureMessage 'Aggiornamento di pip fallito.'

if (Test-Path $SourceDir) {
    if (-not $sourceDirProvided) {
        $sourceId = [System.Guid]::NewGuid().ToString('N').Substring(0, 8)
        $sourceRoot = Split-Path -Parent $SourceDir
        $SourceDir = Join-Path $sourceRoot ("litellm-src-" + $sourceId)
    }
    else {
        Remove-Item -Recurse -Force $SourceDir
    }
}

Invoke-NativeCommand -FilePath 'git' -ArgumentList @('-c', 'core.longpaths=true', 'clone', '--branch', $Ref, '--depth', '1', $repoUrl, $SourceDir) -FailureMessage "Clone di $Repo@$Ref fallito in $SourceDir."

Push-Location $SourceDir
try {
    Invoke-NativeCommand -FilePath $pythonExe -ArgumentList ($pipArgs + @('install', '--upgrade', '.[proxy]')) -FailureMessage "Installazione di LiteLLM da $SourceDir fallita."
}
finally {
    Pop-Location
}

$metadata = [ordered]@{
    repo        = $Repo
    ref         = $Ref
    installedAt = (Get-Date).ToString('s')
    runtimeDir  = $RuntimeDir
    sourceDir   = $SourceDir
}

$metadataPath = Join-Path $RuntimeDir 'install-metadata.json'
$metadata | ConvertTo-Json | Set-Content -Path $metadataPath -Encoding UTF8

Write-Host "LiteLLM installato da $Repo@$Ref"
Write-Host "Runtime: $RuntimeDir"
Write-Host "Metadata: $metadataPath"