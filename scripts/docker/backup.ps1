# ═══════════════════════════════════════════════════════════════
#  Laguitos Docker — backup.ps1
# ═══════════════════════════════════════════════════════════════
#  Genera un backup local del estado runtime del backend:
#    - Copia data/laguitos.db
#    - Comprime data/downloads/ a un zip
#  Destino: backups/YYYY-MM-DD-HHMMSS/
#
#  Uso:
#    .\scripts\docker\backup.ps1
# ═══════════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $projectRoot

. "$PSScriptRoot\_common.ps1"

Write-Header 'Laguitos Docker Backup'

# ─── Preparar destino ────────────────────────────────────────
$stamp  = Get-Date -Format 'yyyy-MM-dd-HHmmss'
$dest   = Join-Path 'backups' $stamp
if (-not (Test-Path 'backups')) {
    New-Item -ItemType Directory -Path 'backups' -Force | Out-Null
}
New-Item -ItemType Directory -Path $dest -Force | Out-Null
Write-Host ('Destino: {0}' -f $dest) -ForegroundColor Cyan
Write-Host ''

# ─── 1. Copiar SQLite db ─────────────────────────────────────
$dbSrc = Join-Path 'data' 'laguitos.db'
if (Test-Path $dbSrc) {
    $dbDst = Join-Path $dest 'laguitos.db'
    Copy-Item $dbSrc $dbDst
    $dbSize = (Get-Item $dbDst).Length
    Write-Host ('  OK: laguitos.db copiada ({0:N0} bytes)' -f $dbSize) -ForegroundColor Green
} else {
    Write-Host '  AVISO: data/laguitos.db no existe, se omite.' -ForegroundColor Yellow
}

# ─── 2. Comprimir downloads/ ─────────────────────────────────
$dlSrc = Join-Path 'data' 'downloads'
if (Test-Path $dlSrc) {
    $zipDst = Join-Path $dest 'downloads.zip'
    Write-Host '  Comprimiendo data/downloads/ ...' -ForegroundColor Gray
    Compress-Archive -Path (Join-Path $dlSrc '*') -DestinationPath $zipDst -Force -ErrorAction SilentlyContinue
    if (Test-Path $zipDst) {
        $zipSize = (Get-Item $zipDst).Length
        Write-Host ('  OK: downloads.zip creado ({0:N0} bytes)' -f $zipSize) -ForegroundColor Green
    } else {
        Write-Host '  AVISO: downloads/ esta vacia, no se creo zip.' -ForegroundColor Yellow
    }
} else {
    Write-Host '  AVISO: data/downloads/ no existe, se omite.' -ForegroundColor Yellow
}

# ─── 3. Total ────────────────────────────────────────────────
$totalBytes = (Get-ChildItem $dest -Recurse -File | Measure-Object -Property Length -Sum).Sum
if (-not $totalBytes) { $totalBytes = 0 }
$totalMb = [Math]::Round($totalBytes / 1MB, 2)

Write-Host ''
Write-Host ('Backup completo: {0}' -f $dest) -ForegroundColor Cyan
Write-Host ('Tamano total   : {0:N0} bytes ({1} MB)' -f $totalBytes, $totalMb) -ForegroundColor Gray
Write-Host ''
