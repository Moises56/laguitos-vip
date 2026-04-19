# ═══════════════════════════════════════════════════════════════
#  Laguitos Docker — create-user.ps1
# ═══════════════════════════════════════════════════════════════
#  Crea un usuario en la BD del container backend.
#  Valida que el container este healthy antes de ejecutar.
#
#  Modos:
#    1. Interactivo (sin parametros): pide email, password y name.
#    2. No interactivo: pasar -Email, -Password y -Name.
#
#  Uso:
#    .\scripts\docker\create-user.ps1
#    .\scripts\docker\create-user.ps1 -Email a@b.com -Password secret -Name "Moises"
# ═══════════════════════════════════════════════════════════════

param(
    [string]$Email,
    [string]$Password,
    [string]$Name
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $projectRoot

. "$PSScriptRoot\_common.ps1"

if (-not (Test-DockerRunning)) {
    Write-Host 'Error: Docker Desktop no esta corriendo.' -ForegroundColor Red
    exit 1
}

if (-not (Test-ContainerHealthy)) {
    Write-Host 'Error: el container backend no esta healthy.' -ForegroundColor Red
    Write-Host 'Levantalo antes con: .\scripts\docker\start.ps1' -ForegroundColor Yellow
    exit 1
}

Write-Header 'Laguitos Docker Create User'

# ─── Resolver datos (interactivo o por parametro) ────────────
if (-not $Email) {
    $Email = Read-Host 'Email'
}
if (-not $Email) {
    Write-Host 'Error: email es obligatorio.' -ForegroundColor Red
    exit 1
}

if (-not $Password) {
    $securePwd = Read-Host 'Password' -AsSecureString
    $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePwd)
    try {
        $Password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
    } finally {
        [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
}
if (-not $Password) {
    Write-Host 'Error: password es obligatorio.' -ForegroundColor Red
    exit 1
}

if (-not $Name) {
    $Name = Read-Host 'Nombre visible'
}
if (-not $Name) {
    Write-Host 'Error: name es obligatorio.' -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host ('Creando usuario: {0} <{1}>' -f $Name, $Email) -ForegroundColor Yellow
Write-Host ''

docker compose exec backend python -m app.scripts.create_user `
    --email $Email `
    --password $Password `
    --name $Name

if ($LASTEXITCODE -ne 0) {
    Write-Host ''
    Write-Host 'Error: el comando create_user fallo.' -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host 'OK.' -ForegroundColor Green
Write-Host ''
