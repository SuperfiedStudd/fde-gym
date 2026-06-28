# Troubleshooting

## The stack is still starting or the cockpit says the API is offline

Run the doctor instead of testing endpoints immediately after `docker compose up`:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\doctor.ps1
```

It retries readiness checks before reporting PASS or FAIL. If it fails, inspect the status and logs it recommends:

```powershell
docker compose ps --all
docker compose logs --tail=200 api edge-service web prometheus postgres redis worker
```

The web container uses `API_INTERNAL_URL=http://api:8000`; your browser uses `NEXT_PUBLIC_API_URL=http://localhost:8000` for progress mutations. Keep both values distinct.

## PowerShell curl output is confusing

Windows PowerShell can map plain `curl` to `Invoke-WebRequest`. Use the real curl executable:

```powershell
curl.exe http://localhost:8000/health
curl.exe http://localhost:3001/health
curl.exe http://localhost:8000/missions
```

You can also use `Invoke-RestMethod`, but the docs use `curl.exe` consistently.

## Postgres is unhealthy

Check credentials in `.env` against Compose. Bootstrap SQL runs only when the Postgres volume is first created. To rebuild local data:

```powershell
docker compose down --volumes
docker compose up --build -d
.\scripts\dev\doctor.ps1
```

This destroys only the local `fde-gym` database and queue volumes.

## The worker is idle

Seed jobs in Postgres are not automatically pushed to Redis so you can control mission timing. Wait for the doctor to pass first:

```powershell
python scripts/seed/enqueue.py
docker compose logs -f worker
```

Queue depth is visible at `GET /system/health` and in Redis with `docker compose exec redis redis-cli LLEN claimops:jobs`.

## A host script or mission check fails on imports

Use Python 3.12 exactly. Do not use Python 3.13 or newer for this repo yet.

If imports such as `asyncpg.protocol.protocol` or `pydantic_core._pydantic_core` fail, the virtual environment contains incomplete or mismatched compiled packages. Delete it through the bootstrap's clean recreation path:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\bootstrap.ps1 -Recreate
.\.venv\Scripts\Activate.ps1
python scripts/evaluate/list.py
```

Do not repair this by installing individual packages ad hoc. `requirements-dev.txt` is the host dependency source of truth.

## The evaluator reports a setup error

A setup error means pytest could not meaningfully collect or run the mission check. Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\bootstrap.ps1 -Recreate
.\.venv\Scripts\Activate.ps1
```

After the host environment and stack doctor pass, a red `[INTENDED MISSION FAILURE]` result is the expected starting state for an unsolved mission.

## Every mission is failing

That is the starter state. Do not run `pytest tests/missions` as a platform health check. Use one focused command:

```powershell
python scripts/evaluate/run.py --mission lv1-request-validation
```

Platform health is `python -m pytest tests/platform`.

## Port conflicts

Defaults are web 3000, edge 3001, Postgres 5432, Redis 6379, API 8000, and Prometheus 9090. Stop the conflicting process or change only the host-side port in `docker-compose.yml`; service-to-service ports should remain unchanged.

## Windows file sharing or bind mount errors

Confirm Docker Desktop can access `D:\fde-gym`. The web service bind-mounts its source for the Next.js development server; mission and progress data are also mounted for local iteration.

## Reset script cannot call Docker

Confirm `docker compose version` succeeds in the same terminal. You can always run the reset steps manually from [local-setup.md](local-setup.md).
