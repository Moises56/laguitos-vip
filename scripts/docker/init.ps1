# ═══════════════════════════════════════════════════════════════
#  Laguitos Docker — init.ps1
# ═══════════════════════════════════════════════════════════════
#  Script de inicialización para Windows (PowerShell).
#
#  Prepara el workspace local antes del primer `docker compose up`:
#    1. Crea cookies.txt placeholder si no existe
#    2. Copia docker/.env.example a .env si no existe
#    3. Crea directorios data/, logs/, data/downloads/
#
#  Uso:
#    .\scripts\docker\init.ps1
#
#  Idempotente: se puede correr las veces que haga falta.
# ═══════════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"

# Resolver raíz del repo (scripts/docker/init.ps1 → ../../ = raíz)
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $projectRoot

Write-Host ""
Write-Host "=== Laguitos Docker Init ===" -ForegroundColor Cyan
Write-Host "Repo root: $projectRoot"
Write-Host ""

# ─── 1. cookies.txt placeholder ──────────────────────────────
if (-not (Test-Path "cookies.txt")) {
    Write-Host "Creating empty cookies.txt placeholder..." -ForegroundColor Yellow
    "# Placeholder cookies file for yt-dlp" | Out-File -FilePath "cookies.txt" -Encoding utf8
    Write-Host "  OK: cookies.txt created (empty placeholder)" -ForegroundColor Green
    Write-Host "  Nota: si querés cookies reales de YouTube, usá la extensión" -ForegroundColor DarkGray
    Write-Host "        'Get cookies.txt LOCALLY' y reemplazá el contenido." -ForegroundColor DarkGray
} else {
    $size = (Get-Item cookies.txt).Length
    Write-Host "  OK: cookies.txt exists ($size bytes)" -ForegroundColor Green
}

# ─── 2. .env desde template ──────────────────────────────────
if (-not (Test-Path ".env")) {
    if (Test-Path "docker/.env.example") {
        Write-Host "Creating .env from docker/.env.example..." -ForegroundColor Yellow
        Copy-Item "docker/.env.example" ".env"
        Write-Host "  OK: .env created" -ForegroundColor Green
        Write-Host ""
        Write-Host "  IMPORTANTE: editá .env antes del primer docker compose up:" -ForegroundColor Red
        Write-Host '    - SECRET_KEY       (generar con: python -c "import secrets; print(secrets.token_urlsafe(64))")' -ForegroundColor Yellow
        Write-Host "    - SEED_USER_1_PASSWORD / SEED_USER_2_PASSWORD" -ForegroundColor Yellow
    } else {
        Write-Host "  WARNING: no .env ni docker/.env.example — revisá el repo" -ForegroundColor Red
    }
} else {
    Write-Host "  OK: .env exists" -ForegroundColor Green
}

# ─── 3. Directorios runtime ──────────────────────────────────
foreach ($dir in @("data", "logs", "data/downloads")) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  OK: created $dir/" -ForegroundColor Green
    } else {
        Write-Host "  OK: $dir/ exists" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Setup complete." -ForegroundColor Cyan
Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor White
Write-Host "  1. Revisá/editá .env (especialmente SECRET_KEY y passwords)" -ForegroundColor Gray
Write-Host "  2. Asegurate que Docker Desktop esté corriendo" -ForegroundColor Gray
Write-Host "  3. Levantá el container:" -ForegroundColor Gray
Write-Host "       docker compose up -d --build" -ForegroundColor White
Write-Host "  4. Verificá salud:" -ForegroundColor Gray
Write-Host "       curl http://localhost:8000/api/health" -ForegroundColor White
Write-Host ""
