# ═══════════════════════════════════════════════════════════════
#  Laguitos Docker — stop.ps1
# ═══════════════════════════════════════════════════════════════
#  Detiene el stack (docker compose down).
#  Con -Volumes elimina tambien los volumenes (pide confirmacion).
#
#  Uso:
#    .\scripts\docker\stop.ps1             # solo down
#    .\scripts\docker\stop.ps1 -Volumes    # down + borra volumenes
# ═══════════════════════════════════════════════════════════════

param(
    [switch]$Volumes
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $projectRoot

. "$PSScriptRoot\_common.ps1"

if (-not (Test-DockerRunning)) {
    Write-Host 'Error: Docker Desktop no esta corriendo.' -ForegroundColor Red
    exit 1
}

Write-Header 'Laguitos Docker Stop'

if ($Volumes) {
    Write-Host 'ATENCION: -Volumes eliminara los volumenes asociados.' -ForegroundColor Red
    Write-Host 'Esto NO borra data/ (que esta bind-mounted), pero si volumenes nombrados.' -ForegroundColor Yellow
    $answer = Read-Host 'Confirmas? (Y/N)'
    if ($answer -notmatch '^(Y|y)$') {
        Write-Host 'Cancelado.' -ForegroundColor Yellow
        exit 0
    }
    Write-Host 'Ejecutando: docker compose down -v' -ForegroundColor Yellow
    docker compose down -v
} else {
    Write-Host 'Ejecutando: docker compose down' -ForegroundColor Yellow
    docker compose down
}

if ($LASTEXITCODE -ne 0) {
    Write-Host 'Error: docker compose down fallo.' -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host 'Stack detenido.' -ForegroundColor Green
Write-Host ''
