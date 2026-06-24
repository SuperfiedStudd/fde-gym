# Troubleshooting

## The cockpit says the API is offline

```bash
docker compose ps
docker compose logs api
curl http://localhost:8000/health
```

The web container uses `API_INTERNAL_URL=http://api:8000`; your browser uses `NEXT_PUBLIC_API_URL=http://localhost:8000` for progress mutations. Keep both values distinct.

## Postgres is unhealthy

Check credentials in `.env` against Compose. Bootstrap SQL runs only when the Postgres volume is first created. To rebuild local data:

```bash
docker compose down --volumes
docker compose up postgres
```

This destroys only the local `fde-gym` database volume.

## The worker is idle

Seed jobs in Postgres are not automatically pushed to Redis so you can control mission timing.

```bash
python scripts/seed/enqueue.py
docker compose logs -f worker
```

Queue depth is visible at `GET /system/health` and in Redis with `docker compose exec redis redis-cli LLEN claimops:jobs`.

## A mission check fails immediately on imports

Install Python development dependencies in your active environment:

```bash
pip install -r apps/api/requirements-dev.txt
```

The evaluator sets `PYTHONPATH` for API and worker packages. Run it from the repository root.

## Every mission is failing

That is the starter state. Do not run `pytest tests/missions` as a platform health check. Use one focused command:

```bash
python scripts/evaluate/run.py --mission lv1-request-validation
```

Platform health is `python -m pytest tests/platform`.

## Port conflicts

Defaults are web 3000, edge 3001, Postgres 5432, Redis 6379, API 8000, and Prometheus 9090. Stop the conflicting process or change only the host-side port in `docker-compose.yml`; service-to-service ports should remain unchanged.

## Windows file sharing or bind mount errors

Confirm Docker Desktop can access `D:\fde-gym`. Progress and mission bind mounts are the only runtime host mounts; source code is copied into service images.

## Reset script cannot call Docker

Confirm `docker compose version` succeeds in the same terminal. You can always run the three reset steps manually from [local-setup.md](local-setup.md).

