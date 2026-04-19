# ═══════════════════════════════════════════════════════════════
#  Laguitos Docker — shell.ps1
# ═══════════════════════════════════════════════════════════════
#  Abre una shell bash interactiva dentro del container backend.
#
#  Uso:
#    .\scripts\docker\shell.ps1
# ═══════════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $projectRoot

. "$PSScriptRoot\_common.ps1"

if (-not (Test-DockerRunning)) {
    Write-Host 'Error: Docker Desktop no esta corriendo.' -ForegroundColor Red
    exit 1
}

if (-not (Test-ContainerHealthy)) {
    Write-Host 'Aviso: el container no esta healthy. Igual intento abrir shell.' -ForegroundColor Yellow
}

Write-Header 'Laguitos Docker Shell'

Write-Host 'Abriendo bash en el container backend...' -ForegroundColor Gray
Write-Host 'Salida: escribe "exit" o Ctrl+D' -ForegroundColor Gray
Write-Host ''

docker compose exec backend bash
