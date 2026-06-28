"""Push pending database jobs onto the local Redis queue."""

import asyncio
import json
import os

import asyncpg
from redis.asyncio import Redis

SETUP_HINT = (
    "Stack is not reachable. Run docker compose up --build -d, "
    "then ./scripts/dev/doctor.ps1."
)


class StackConnectionError(RuntimeError):
    """Raised when local Postgres or Redis cannot be reached during startup."""


async def connect_dependencies(
    database_url: str,
    redis_url: str,
    *,
    attempts: int = 3,
    retry_delay: float = 1.0,
) -> tuple[asyncpg.Connection, Redis]:
    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        connection: asyncpg.Connection | None = None
        redis = Redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        try:
            connection = await asyncpg.connect(database_url, timeout=3)
            await redis.ping()
            return connection, redis
        except Exception as exc:
            last_error = exc
            if connection is not None:
                await connection.close()
            await redis.aclose()
            if attempt < attempts:
                await asyncio.sleep(retry_delay)

    assert last_error is not None
    message = str(last_error).strip() or "connection attempt timed out"
    detail = f"{type(last_error).__name__}: {message}"
    raise StackConnectionError(detail) from last_error


async def enqueue() -> int:
    database_url = os.getenv(
        "DATABASE_URL", "postgresql://claimops:claimops-local@localhost:5432/claimops"
    ).replace("+asyncpg", "")
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    connection, redis = await connect_dependencies(database_url, redis_url)

    try:
        rows = await connection.fetch(
            "SELECT id, kind, payload, attempts, max_attempts FROM jobs WHERE status = 'pending'"
        )
        for row in rows:
            job = dict(row)
            job["id"] = str(job["id"])
            if isinstance(job["payload"], str):
                job["payload"] = json.loads(job["payload"])
            await redis.lpush("claimops:jobs", json.dumps(job))
        return len(rows)
    finally:
        await connection.close()
        await redis.aclose()


def main() -> int:
    try:
        count = asyncio.run(enqueue())
    except StackConnectionError as exc:
        print(SETUP_HINT)
        print(f"Connection detail: {exc}")
        return 2

    print(f"enqueued {count} pending jobs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
