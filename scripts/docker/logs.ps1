# ═══════════════════════════════════════════════════════════════
#  Laguitos Docker — logs.ps1
# ═══════════════════════════════════════════════════════════════
#  Stream de logs del backend (docker compose logs -f).
#  Por defecto muestra las ultimas 50 lineas y luego sigue.
#
#  Uso:
#    .\scripts\docker\logs.ps1              # -Tail 50, follow
#    .\scripts\docker\logs.ps1 -Tail 200    # mas historia
#    .\scripts\docker\logs.ps1 -Tail 0      # solo nuevas lineas
# ═══════════════════════════════════════════════════════════════

param(
    [int]$Tail = 50
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $projectRoot

. "$PSScriptRoot\_common.ps1"

if (-not (Test-DockerRunning)) {
    Write-Host 'Error: Docker Desktop no esta corriendo.' -ForegroundColor Red
    exit 1
}

Write-Header 'Laguitos Docker Logs (Ctrl+C para salir)'

Write-Host ('Tail: {0} lineas, follow activo' -f $Tail) -ForegroundColor Gray
Write-Host ''

docker compose logs -f --tail $Tail backend
