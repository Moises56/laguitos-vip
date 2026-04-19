# ═══════════════════════════════════════════════════════════════
#  Laguitos Docker — restart.ps1
# ═══════════════════════════════════════════════════════════════
#  Reinicia unicamente el servicio backend (sin detener volumenes).
#
#  Uso:
#    .\scripts\docker\restart.ps1
# ═══════════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $projectRoot

. "$PSScriptRoot\_common.ps1"

if (-not (Test-DockerRunning)) {
    Write-Host 'Error: Docker Desktop no esta corriendo.' -ForegroundColor Red
    exit 1
}

Write-Header 'Laguitos Docker Restart'

Write-Host 'Ejecutando: docker compose restart backend' -ForegroundColor Yellow
docker compose restart backend

if ($LASTEXITCODE -ne 0) {
    Write-Host 'Error: restart fallo.' -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host 'Esperando 3s...' -ForegroundColor Gray
Start-Sleep -Seconds 3

if (Test-ContainerHealthy) {
    $uptime = Get-ContainerUptime
    Write-Host ('Backend healthy (uptime: {0}).' -f $uptime) -ForegroundColor Green
} else {
    Write-Host 'Backend no esta healthy todavia. Revisa logs:' -ForegroundColor Yellow
    Write-Host '  .\scripts\docker\logs.ps1' -ForegroundColor White
}
Write-Host ''
