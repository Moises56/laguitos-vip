# ═══════════════════════════════════════════════════════════════
#  Laguitos Docker — _common.ps1
# ═══════════════════════════════════════════════════════════════
#  Helpers compartidos para los scripts de scripts/docker/.
#  No se ejecuta directamente: se importa con dot-sourcing:
#    . "$PSScriptRoot\_common.ps1"
#
#  Exporta:
#    Write-Header        Banner con separadores y color
#    Test-DockerRunning  $true si Docker Desktop responde
#    Test-ContainerHealthy  $true si el backend esta healthy
#    Get-ContainerUptime Uptime del container en texto legible
# ═══════════════════════════════════════════════════════════════

function Write-Header {
    param(
        [Parameter(Mandatory=$true)][string]$Title,
        [string]$Color = 'Cyan'
    )
    $line = '=' * 63
    Write-Host ''
    Write-Host $line -ForegroundColor $Color
    Write-Host "  $Title" -ForegroundColor $Color
    Write-Host $line -ForegroundColor $Color
    Write-Host ''
}

function Test-DockerRunning {
    try {
        $null = docker info 2>&1
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

function Test-ContainerHealthy {
    param(
        [string]$ContainerName = 'laguitos-backend'
    )
    try {
        $status = docker inspect --format '{{.State.Health.Status}}' $ContainerName 2>$null
        if ($LASTEXITCODE -ne 0) { return $false }
        return ($status.Trim() -eq 'healthy')
    } catch {
        return $false
    }
}

function Get-ContainerUptime {
    param(
        [string]$ContainerName = 'laguitos-backend'
    )
    try {
        $startedAt = docker inspect --format '{{.State.StartedAt}}' $ContainerName 2>$null
        if ($LASTEXITCODE -ne 0) { return 'desconocido' }
        $start = [DateTime]::Parse($startedAt).ToUniversalTime()
        $span = (Get-Date).ToUniversalTime() - $start
        if ($span.TotalDays -ge 1) {
            return ('{0}d {1}h {2}m' -f [int]$span.Days, [int]$span.Hours, [int]$span.Minutes)
        } elseif ($span.TotalHours -ge 1) {
            return ('{0}h {1}m' -f [int]$span.Hours, [int]$span.Minutes)
        } else {
            return ('{0}m {1}s' -f [int]$span.Minutes, [int]$span.Seconds)
        }
    } catch {
        return 'desconocido'
    }
}
