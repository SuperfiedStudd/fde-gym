$ErrorActionPreference = "Stop"

if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
}

docker compose up --build -d
if ($LASTEXITCODE -ne 0) {
    throw "docker compose up failed"
}

& "$PSScriptRoot\doctor.ps1"
