# Local setup

## Fastest path: Docker Compose

1. Install Docker Desktop and confirm `docker compose version` works.
2. Copy `.env.example` to `.env`.
3. Start the stack with `docker compose up --build`.
4. Wait for API health, then open <http://localhost:3000>.

Useful commands:

```bash
docker compose ps
docker compose logs -f api worker edge-service
python scripts/seed/enqueue.py
python scripts/evaluate/list.py
```

## Host development

The dependencies still run in Docker:

```bash
docker compose up -d postgres redis prometheus
```

Create the Python environment:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r apps/api/requirements-dev.txt
```

PowerShell environment values:

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

```bash
npm install
npm run dev:edge
npm run dev:web
```

The API must be available before the web dashboard can show live missions and health. Do not run the full mission test directory unless you want 17 exercises' failures at once.

## Reset boundaries

- `python scripts/seed/reset.py`: destroys this project's Postgres and Redis volumes, recreates services, enqueues jobs.
- Delete `data/progress.json`: clears only mission completion state.
- `docker compose down`: stops services and preserves data.
- `docker compose down --volumes`: destroys local ClaimOps database and queue data.

## Test layers

```bash
python -m pytest tests/platform
python scripts/evaluate/run.py --mission <mission-id>
npm --workspace @fde-gym/edge-service test
npm run typecheck
```

Platform tests protect the scaffolding. Focused mission evaluation is expected to fail first, then pass after your repair.

