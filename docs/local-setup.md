# Local setup

## Fastest path: Docker Compose

1. Install Docker Desktop and confirm `docker compose version` works.
2. Copy `.env.example` to `.env`.
3. Bootstrap the Python 3.12 host environment.
4. Start the stack in detached mode.
5. Run the doctor and wait for a complete PASS result.

From a clean PowerShell terminal:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
powershell -ExecutionPolicy Bypass -File .\scripts\dev\bootstrap.ps1 -Recreate
.\.venv\Scripts\Activate.ps1
docker compose up --build -d
powershell -ExecutionPolicy Bypass -File .\scripts\dev\doctor.ps1
```

The `-Recreate` option cleanly replaces an existing or damaged `.venv`. Later bootstrap runs can omit it when the environment is already healthy.

Detached mode (`-d`) is the recommended default because it keeps the stack running in the background. Use attached mode (`docker compose up --build`) when you want combined live logs in the terminal and do not mind occupying that shell.

The doctor waits up to 180 seconds by default and checks:

- Docker engine access.
- All required services in `docker compose ps`.
- API health at <http://localhost:8000/health>.
- Edge health at <http://localhost:3001/health>.
- Mission catalog at <http://localhost:8000/missions>.
- Prometheus at <http://localhost:9090>.

To allow more startup time:

```powershell
.\scripts\dev\doctor.ps1 -TimeoutSeconds 300
```

Manual smoke checks:

```powershell
docker compose ps
curl.exe http://localhost:8000/health
curl.exe http://localhost:3001/health
curl.exe http://localhost:8000/missions
curl.exe http://localhost:9090
```

In Windows PowerShell, plain `curl` can resolve to `Invoke-WebRequest` and produce confusing output. Use `curl.exe` for consistent curl behavior.

Run `python scripts/evaluate/run.py --mission <mission-id>` only after the doctor passes. Intended mission failures should come from the exercise, not from services still warming up. The recommended first mission is `lv1-request-validation`:

```powershell
python scripts/evaluate/run.py --mission lv1-request-validation
```

## Python 3.12 host environment

Use Python 3.12 exactly for local scripts, tests, and evaluators. Do not use Python 3.13 or newer for this repo yet.

The root `requirements-dev.txt` is the single source of truth for host Python dependencies. It includes the API dependencies, pytest, pytest-asyncio, and Ruff. The bootstrap prefers binary wheels and verifies the compiled `asyncpg` and `pydantic-core` extensions.

If you see errors such as `asyncpg.protocol.protocol` or `pydantic_core._pydantic_core`, recreate the environment:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\bootstrap.ps1 -Recreate
.\.venv\Scripts\Activate.ps1
```

## Host development

Docker can provide only the dependencies while services run on the host:

```powershell
docker compose up -d postgres redis prometheus
```

The root .env is used by Docker Compose. Host processes use explicit shell environment values and do not auto-load Docker-only paths or service hostnames from that file.

PowerShell environment values for the API:

```powershell
$env:DATABASE_URL="postgresql+asyncpg://claimops:claimops-local@localhost:5432/claimops"
$env:REDIS_URL="redis://localhost:6379/0"
$env:MISSION_ROOT="missions"
$env:PROGRESS_FILE="data/progress.json"
uvicorn app.main:app --app-dir apps/api --reload --port 8000
```

In separate terminals:

```powershell
$env:DATABASE_URL="postgresql://claimops:claimops-local@localhost:5432/claimops"
$env:REDIS_URL="redis://localhost:6379/0"
python -m worker.main
```

```powershell
npm install
npm run dev:edge
npm run dev:web
```

The API must be available before the web dashboard can show live missions and health. Do not run the full mission test directory unless you want all 17 exercises' failures at once.

## Reset boundaries

- `python scripts/seed/reset.py`: destroys this project's Postgres and Redis volumes, recreates services, and enqueues jobs.
- Delete `data/progress.json`: clears only mission completion state.
- `docker compose down`: stops services and preserves data.
- `docker compose down --volumes`: destroys local ClaimOps database and queue data.

After a reset or rebuild, rerun `.\scripts\dev\doctor.ps1` before enqueueing jobs or evaluating a mission.

## Test layers

```powershell
python -m pytest tests/platform
python scripts/evaluate/list.py
python scripts/evaluate/run.py --mission <mission-id>
npm --workspace @fde-gym/edge-service test
npm run typecheck
```

Platform tests protect the scaffolding. Focused mission evaluation is expected to fail first, then pass after your repair. A pytest collection or dependency failure is reported as a setup error and points back to the bootstrap script.

## Frontend review before missions

After the doctor passes, send screenshots of these pages to the Codex thread:

- <http://localhost:3000>
- <http://localhost:3000/missions>
- One mission detail page.
- <http://localhost:3000/progress>

Review the cockpit scaffold before starting the first mission.
