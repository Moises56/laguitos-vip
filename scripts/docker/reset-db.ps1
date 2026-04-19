# ═══════════════════════════════════════════════════════════════
#  Laguitos Docker — reset-db.ps1
# ═══════════════════════════════════════════════════════════════
#  ATENCION: operacion destructiva.
#  Detiene el stack, borra data/laguitos.db y lo vuelve a levantar.
#  El backend re-seedea usuarios automaticamente al arrancar.
#
#  Requiere DOBLE confirmacion:
#    1. Y/N
#    2. Escribir literalmente: RESET
#
#  Uso:
#    .\scripts\docker\reset-db.ps1
# ═══════════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $projectRoot

. "$PSScriptRoot\_common.ps1"

if (-not (Test-DockerRunning)) {
    Write-Host 'Error: Docker Desktop no esta corriendo.' -ForegroundColor Red
    exit 1
}

Write-Header 'Laguitos Docker Reset DB'

Write-Host 'Esto va a:' -ForegroundColor Yellow
Write-Host '  1. Detener el stack (docker compose down)' -ForegroundColor Yellow
Write-Host '  2. Borrar data/laguitos.db (TODOS los usuarios/historial)' -ForegroundColor Red
Write-Host '  3. Levantar el stack (re-seed automatico)' -ForegroundColor Yellow
Write-Host ''
Write-Host 'NO afecta data/downloads/.' -ForegroundColor Gray
Write-Host ''

# ─── Confirmacion 1: Y/N ─────────────────────────────────────
$answer1 = Read-Host 'Estas seguro? (Y/N)'
if ($answer1 -notmatch '^(Y|y)$') {
    Write-Host 'Cancelado.' -ForegroundColor Yellow
    exit 0
}

# ─── Confirmacion 2: escribir RESET ──────────────────────────
Write-Host ''
Write-Host 'Ultima oportunidad: escribi literalmente RESET para continuar.' -ForegroundColor Red
$answer2 = Read-Host 'Confirmacion'
if ($answer2 -cne 'RESET') {
    Write-Host 'No escribiste RESET. Cancelado.' -ForegroundColor Yellow
    exit 0
}

Write-Host ''
Write-Host 'Bajando stack...' -ForegroundColor Yellow
docker compose down
if ($LASTEXITCODE -ne 0) {
    Write-Host 'Error: docker compose down fallo.' -ForegroundColor Red
    exit 1
}

$dbPath = Join-Path 'data' 'laguitos.db'
if (Test-Path $dbPath) {
    Remove-Item $dbPath -Force
    Write-Host ('  OK: {0} borrado.' -f $dbPath) -ForegroundColor Green
} else {
    Write-Host ('  AVISO: {0} no existia.' -f $dbPath) -ForegroundColor Yellow
}

Write-Host ''
Write-Host 'Levantando stack (el backend va a re-seedear)...' -ForegroundColor Yellow
docker compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host 'Error: docker compose up fallo.' -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host 'Esperando 5s para health check...' -ForegroundColor Gray
Start-Sleep -Seconds 5

if (Test-ContainerHealthy) {
    Write-Host 'Reset completo. Backend healthy.' -ForegroundColor Green
    Write-Host 'Los usuarios SEED estan disponibles con las credenciales de .env.' -ForegroundColor Gray
} else {
    Write-Host 'Backend no healthy todavia. Revisa logs con:' -ForegroundColor Yellow
    Write-Host '  .\scripts\docker\logs.ps1' -ForegroundColor White
}
Write-Host ''
