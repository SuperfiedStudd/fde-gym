# fde-gym

`fde-gym` is a personal Forward-Deployed Engineering practice environment. Its fictional ClaimOps platform is intentionally production-shaped and intentionally imperfect: APIs, workers, data flows, permissions, caching, queues, telemetry, migrations, and deployment controls all contain bounded failures for you to diagnose and repair.

This is not a tutorial app or a polished product. Codex can maintain the environment; you should solve one mission at a time in Cursor or VS Code.

## What is in the sandbox

| Component | Stack | Local port | Purpose |
|---|---|---:|---|
| Mission cockpit | Next.js + TypeScript | 3000 | Browse missions, system signals, and progress |
| ClaimOps API | FastAPI + SQLAlchemy | 8000 | Mission, progress, claims, notes, events, and health APIs |
| Worker | Python asyncio | -- | Process Redis jobs and write claim events |
| Edge service | Hono + TypeScript | 3001 | Typed profile/event boundary and TS testing surface |
| Database | Postgres 16 | 5432 | Seeded fictional ClaimOps data |
| Queue | Redis 7 | 6379 | Local asynchronous job transport |
| Metrics | Prometheus | 9090 | Scrape API RED metrics |

The cloud path maps API/web to Cloud Run, Postgres to Cloud SQL, queueing to Pub/Sub, objects to GCS, secrets to Secret Manager, logs to Cloud Logging, and images to Artifact Registry.

## Start locally

Requirements: Docker Desktop with Compose v2. Optional host tooling: Python 3.12+, Node 22+, and npm 10+.

Prefer Python 3.12 for host-side scripts and evaluation. If your machine defaults to Python 3.13, use an explicit 3.12 interpreter for the project virtual environment to match the service/runtime assumptions.

```bash
copy .env.example .env
docker compose up --build -d
```

On macOS/Linux use `cp .env.example .env`. Then open:

- Cockpit: <http://localhost:3000>
- FastAPI docs: <http://localhost:8000/docs>
- Edge health: <http://localhost:3001/health>
- Prometheus: <http://localhost:9090>

Detached mode (`-d`) is the normal path when you want the stack to keep running in the background. Use attached mode (`docker compose up --build`) when you want live combined logs in the terminal and do not mind occupying that shell.

Smoke check the stack before running mission evaluators:

```bash
curl http://localhost:8000/health
curl http://localhost:3001/health
curl http://localhost:8000/missions
```

The database initializes automatically from `infra/docker/postgres/`. Push pending seed jobs to Redis when a mission needs the worker:

```bash
python scripts/seed/enqueue.py
docker compose logs -f api worker edge-service
```

See [docs/local-setup.md](docs/local-setup.md) for host-only workflows and troubleshooting.

## Work a mission

1. Open the cockpit and choose one operation.
2. Read its `missions/<level>/<name>/README.md` completely.
3. Run the focused evaluator and confirm the expected failure.
4. Diagnose and repair only that mission's scope in Cursor.
5. Add or strengthen tests; rerun the evaluator.
6. Mark it complete in the cockpit and capture the story in [docs/interview-story-bank.md](docs/interview-story-bank.md).

```bash
python scripts/evaluate/list.py
python scripts/evaluate/run.py --mission lv1-request-validation
```

Run mission evaluation after the stack is healthy. Mission evaluation failures are expected before you solve a mission. Platform smoke tests are separate:

```bash
python -m pytest tests/platform
npm run typecheck
npm test
```

## Recommended first mission

Start with `lv1-request-validation`. Open:

- `missions/lv1/request-validation/README.md`
- `apps/api/app/schemas.py`
- `tests/missions/test_lv1_request_validation.py`

Run:

```bash
python scripts/evaluate/run.py --mission lv1-request-validation
```

Do not fix other `MISSION_BUG` markers while you are there. They are future exercises, not a cleanup backlog.

## Reset seed data

The reset command destroys only this Compose project's named volumes, recreates the local services, and enqueues pending jobs:

```bash
python scripts/seed/reset.py
```

For a manual reset:

```bash
docker compose down --volumes
docker compose up --build -d
python scripts/seed/enqueue.py
```

Local mission progress lives in the ignored file `data/progress.json`. Delete it to clear completion state without resetting ClaimOps data.

## Repository map

```text
apps/              Next.js, FastAPI, worker, and Hono services
packages/shared/   Shared TypeScript API types
infra/docker/      Postgres bootstrap and Prometheus configuration
infra/gcp/         Optional Terraform and deployment helpers
missions/          5 LV1, 5 LV2, 4 LV3, and 3 LV4 mission briefs
scripts/evaluate/  Mission catalog and focused grading runner
scripts/seed/      Deterministic local reset and queue helpers
tests/platform/    Gym smoke tests expected to pass
tests/missions/    Mission checks expected to fail until solved
docs/              Architecture, operations, authoring, and learning path
```

## Add a mission

Use [docs/mission-authoring.md](docs/mission-authoring.md). A mission needs a machine-readable `mission.json`, a complete brief, a focused test file, a catalog lint target when useful, and a deliberately bounded starter defect.

## Deploy to GCP later

Cloud deployment is optional and never required for local missions. Start with [docs/gcp-setup.md](docs/gcp-setup.md). Terraform includes API enablement, Artifact Registry, Cloud SQL, Pub/Sub, GCS, Secret Manager, service accounts, and Cloud Run definitions. Read the billing and teardown sections before applying anything.

## Intentional failure policy

- `tests/platform` should pass and protects the gym itself.
- `tests/missions` are red acceptance tests for the exercises.
- `MISSION_BUG(<mission-id>)` identifies a seeded seam, not necessarily the entire solution.
- LV3/LV4 missions also contain incomplete technical notes/runbooks on purpose.
- Never make the full mission suite green in one cleanup pass; that would solve the gym instead of using it.
