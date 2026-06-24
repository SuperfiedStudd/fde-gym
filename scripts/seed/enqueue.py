"""Push pending database jobs onto the local Redis queue."""

import asyncio
import json
import os

import asyncpg
from redis.asyncio import Redis


async def enqueue() -> int:
    database_url = os.getenv(
        "DATABASE_URL", "postgresql://claimops:claimops-local@localhost:5432/claimops"
    ).replace("+asyncpg", "")
    redis = Redis.from_url(
        os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True
    )
    connection = await asyncpg.connect(database_url)
    try:
        rows = await connection.fetch(
            "SELECT id, kind, payload, attempts, max_attempts FROM jobs WHERE status = 'pending'"
        )
        for row in rows:
            job = {key: row[key] for key in row}
            job["id"] = str(job["id"])
            if isinstance(job["payload"], str):
                job["payload"] = json.loads(job["payload"])
            await redis.lpush("claimops:jobs", json.dumps(job))
        return len(rows)
    finally:
        await connection.close()
        await redis.aclose()


if __name__ == "__main__":
    count = asyncio.run(enqueue())
    print(f"enqueued {count} pending jobs")
