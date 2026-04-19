# ═══════════════════════════════════════════════════════════════
#  Laguitos Docker — start.ps1
# ═══════════════════════════════════════════════════════════════
#  Levanta el stack con docker compose up -d.
#  Muestra estado y health despues de 5 segundos.
#
#  Uso:
#    .\scripts\docker\start.ps1           # arranca sin rebuild
#    .\scripts\docker\start.ps1 -Build    # fuerza --build
# ═══════════════════════════════════════════════════════════════

param(
    [switch]$Build
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $projectRoot

. "$PSScriptRoot\_common.ps1"

if (-not (Test-DockerRunning)) {
    Write-Host 'Error: Docker Desktop no esta corriendo.' -ForegroundColor Red
    exit 1
}

Write-Header 'Laguitos Docker Start'

if ($Build) {
    Write-Host 'Levantando stack con --build (puede tardar)...' -ForegroundColor Yellow
    docker compose up -d --build
} else {
    Write-Host 'Levantando stack (sin rebuild)...' -ForegroundColor Yellow
    docker compose up -d
}

if ($LASTEXITCODE -ne 0) {
    Write-Host 'Error: docker compose up fallo.' -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host 'Esperando 5s para que el backend arranque...' -ForegroundColor Gray
Start-Sleep -Seconds 5

Write-Host ''
Write-Host 'Estado actual:' -ForegroundColor Cyan
docker compose ps
Write-Host ''

if (Test-ContainerHealthy) {
    Write-Host 'Backend healthy. Disponible en http://localhost:8000' -ForegroundColor Green
} else {
    Write-Host 'Backend aun no esta healthy. Revisa logs con:' -ForegroundColor Yellow
    Write-Host '  .\scripts\docker\logs.ps1' -ForegroundColor White
}
Write-Host ''
