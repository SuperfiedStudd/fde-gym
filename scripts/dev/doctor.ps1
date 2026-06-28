[CmdletBinding()]
param(
    [ValidateRange(10, 600)]
    [int]$TimeoutSeconds = 180,
    [ValidateRange(1, 30)]
    [int]$RetryIntervalSeconds = 3
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$expectedServices = @("postgres", "redis", "api", "worker", "edge-service", "web", "prometheus")
$endpoints = [ordered]@{
    "API health"   = "http://localhost:8000/health"
    "Edge health"  = "http://localhost:3001/health"
    "Missions API" = "http://localhost:8000/missions"
    "Prometheus"   = "http://localhost:9090"
}

function Write-Pass([string]$Name, [string]$Detail) {
    Write-Host "[PASS] $Name - $Detail" -ForegroundColor Green
}

function Write-Fail([string]$Name, [string]$Detail) {
    Write-Host "[FAIL] $Name - $Detail" -ForegroundColor Red
}

function Invoke-NativeCommand([scriptblock]$Command) {
    $previousPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $output = @(& $Command 2>&1)
        $exitCode = $LASTEXITCODE
        return [PSCustomObject]@{
            ExitCode = $exitCode
            Output   = $output
        }
    }
    finally {
        $ErrorActionPreference = $previousPreference
    }
}

function Test-Endpoint([string]$Url) {
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3
        return $response.StatusCode -ge 200 -and $response.StatusCode -lt 300
    }
    catch {
        return $false
    }
}

Push-Location $repoRoot
try {
    if ($null -eq (Get-Command "docker.exe" -ErrorAction SilentlyContinue)) {
        Write-Fail "Docker" "docker.exe was not found"
        Write-Host "Next debugging command: docker --version"
        exit 1
    }

    $dockerResult = Invoke-NativeCommand { docker info --format "{{.ServerVersion}}" }
    if ($dockerResult.ExitCode -ne 0) {
        Write-Fail "Docker" "the Docker engine is not reachable"
        Write-Host "Next debugging command: docker info"
        exit 1
    }
    $dockerInfo = ($dockerResult.Output | ForEach-Object { $_.ToString() }) -join ""
    Write-Pass "Docker" "engine $dockerInfo is reachable"

    Write-Host "Waiting up to $TimeoutSeconds seconds for Compose services and HTTP endpoints..."
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    $runningServices = @()
    $endpointStatus = @{}

    while ([DateTime]::UtcNow -lt $deadline) {
        $composeResult = Invoke-NativeCommand {
            docker compose ps --services --status running
        }
        if ($composeResult.ExitCode -eq 0) {
            $runningServices = @(
                $composeResult.Output |
                    ForEach-Object { $_.ToString().Trim() } |
                    Where-Object { $_ }
            )
        }
        else {
            $runningServices = @()
        }

        foreach ($entry in $endpoints.GetEnumerator()) {
            $endpointStatus[$entry.Key] = Test-Endpoint $entry.Value
        }

        $missingServices = @($expectedServices | Where-Object { $_ -notin $runningServices })
        $failedEndpoints = @($endpoints.Keys | Where-Object { -not $endpointStatus[$_] })
        if ($missingServices.Count -eq 0 -and $failedEndpoints.Count -eq 0) {
            break
        }
        Start-Sleep -Seconds $RetryIntervalSeconds
    }

    Write-Host ""
    Write-Host "Docker Compose status:"
    $composePsResult = Invoke-NativeCommand { docker compose ps --all }
    $composePsResult.Output | ForEach-Object { Write-Host $_.ToString() }
    $composePsExit = $composePsResult.ExitCode
    Write-Host ""

    $failed = $false
    if ($composePsExit -eq 0) {
        $missingServices = @($expectedServices | Where-Object { $_ -notin $runningServices })
        if ($missingServices.Count -eq 0) {
            Write-Pass "Compose services" "all $($expectedServices.Count) required services are running"
        }
        else {
            Write-Fail "Compose services" "not running: $($missingServices -join ', ')"
            $failed = $true
        }
    }
    else {
        Write-Fail "Compose status" "docker compose ps failed"
        $failed = $true
    }

    foreach ($entry in $endpoints.GetEnumerator()) {
        if ($endpointStatus[$entry.Key]) {
            Write-Pass $entry.Key $entry.Value
        }
        else {
            Write-Fail $entry.Key $entry.Value
            $failed = $true
        }
    }

    if ($failed) {
        Write-Host ""
        Write-Host "Next debugging command:" -ForegroundColor Yellow
        Write-Host "docker compose logs --tail=200 api edge-service web prometheus postgres redis worker"
        exit 1
    }

    Write-Host ""
    Write-Pass "fde-gym" "the local stack is ready for mission evaluation"
}
finally {
    Pop-Location
}
