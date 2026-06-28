[CmdletBinding()]
param(
    [switch]$Recreate
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$venvPath = Join-Path $repoRoot ".venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"
$requirements = Join-Path $repoRoot "requirements-dev.txt"

function Write-Pass([string]$Message) {
    Write-Host "[PASS] $Message" -ForegroundColor Green
}

function Write-Step([string]$Message) {
    Write-Host "[....] $Message" -ForegroundColor Cyan
}

function Invoke-CheckedPython {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Executable,
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed with exit code $LASTEXITCODE."
    }
}

Push-Location $repoRoot
try {
    $pyLauncher = Get-Command "py.exe" -ErrorAction SilentlyContinue
    if ($null -eq $pyLauncher) {
        throw "Python Launcher for Windows was not found. Install Python 3.12 with the py launcher enabled."
    }

    $python312 = (& $pyLauncher.Source -3.12 -c "import sys; print(sys.executable); raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)" 2>$null)
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($python312)) {
        throw "Python 3.12 was not found. Install it, then confirm 'py -3.12 --version' succeeds. Do not use Python 3.13 or newer for this repo yet."
    }
    Write-Pass "Python 3.12 available at $python312"

    if ($Recreate -and (Test-Path $venvPath)) {
        Write-Step "Removing the existing .venv"
        Remove-Item -Recurse -Force $venvPath
    }

    if (-not (Test-Path $venvPython)) {
        Write-Step "Creating .venv with Python 3.12"
        & $pyLauncher.Source -3.12 -m venv $venvPath
        if ($LASTEXITCODE -ne 0) {
            throw "Unable to create .venv with Python 3.12."
        }
    }

    $venvVersion = (& $venvPython -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if ($LASTEXITCODE -ne 0 -or $venvVersion.Trim() -ne "3.12") {
        throw ".venv is not using Python 3.12. Rerun: .\scripts\dev\bootstrap.ps1 -Recreate"
    }
    Write-Pass ".venv uses Python $venvVersion"

    Write-Step "Upgrading pip, setuptools, and wheel"
    Invoke-CheckedPython -Executable $venvPython -Arguments @("-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel")

    Write-Step "Installing host development dependencies from requirements-dev.txt"
    Invoke-CheckedPython -Executable $venvPython -Arguments @("-m", "pip", "install", "--upgrade", "--prefer-binary", "--only-binary", "asyncpg,pydantic-core", "-r", $requirements)

    Write-Step "Verifying installed packages and compiled extensions"
    Invoke-CheckedPython -Executable $venvPython -Arguments @("-m", "pip", "check")
    Invoke-CheckedPython -Executable $venvPython -Arguments @("-c", "import asyncpg.protocol.protocol; import pydantic_core._pydantic_core; import fastapi; import pytest; import redis; import ruff; import sqlalchemy; print('compiled and host imports are healthy')")

    Write-Pass "Host Python environment is ready"
    Write-Host "Activate it with: .\.venv\Scripts\Activate.ps1"
    Write-Host "Then list missions with: python scripts/evaluate/list.py"
}
catch {
    Write-Host "[FAIL] $($_.Exception.Message)" -ForegroundColor Red
    if (Test-Path $venvPath) {
        Write-Host "If compiled dependencies are damaged, rerun: .\scripts\dev\bootstrap.ps1 -Recreate"
    }
    exit 1
}
finally {
    Pop-Location
}
