$ErrorActionPreference = "Stop"

python -m pytest tests/platform
python -m ruff check apps/api apps/worker scripts tests/platform
npm run typecheck
npm test
docker compose config --quiet

Write-Host "Platform checks passed. Mission checks are intentionally excluded."

