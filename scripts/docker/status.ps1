# ═══════════════════════════════════════════════════════════════
#  Laguitos Docker — status.ps1
# ═══════════════════════════════════════════════════════════════
#  Muestra estado del stack, salud del backend y uptime.
#
#  Uso:
#    .\scripts\docker\status.ps1
# ═══════════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $projectRoot

. "$PSScriptRoot\_common.ps1"

if (-not (Test-DockerRunning)) {
    Write-Host 'Error: Docker Desktop no esta corriendo.' -ForegroundColor Red
    exit 1
}

Write-Header 'Laguitos Docker Status'

Write-Host 'Servicios (docker compose ps):' -ForegroundColor Cyan
docker compose ps
Write-Host ''

Write-Host 'Health endpoint (GET /api/health):' -ForegroundColor Cyan
try {
    $resp = Invoke-WebRequest -Uri 'http://localhost:8000/api/health' -UseBasicParsing -TimeoutSec 5
    Write-Host ('  HTTP {0}' -f $resp.StatusCode) -ForegroundColor Green
    Write-Host ('  Body: {0}' -f $resp.Content.Trim()) -ForegroundColor Gray
} catch {
    Write-Host '  No responde (container no healthy o no esta levantado).' -ForegroundColor Yellow
    Write-Host ('  Detalle: {0}' -f $_.Exception.Message) -ForegroundColor Gray
}
Write-Host ''

Write-Host 'Container:' -ForegroundColor Cyan
if (Test-ContainerHealthy) {
    $uptime = Get-ContainerUptime
    Write-Host ('  Estado : healthy') -ForegroundColor Green
    Write-Host ('  Uptime : {0}' -f $uptime) -ForegroundColor Gray
} else {
    Write-Host '  Estado : NO healthy (o container no existe)' -ForegroundColor Yellow
}
Write-Host ''
