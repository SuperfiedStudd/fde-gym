import asyncio
import json
import logging
import signal
from contextlib import suppress
from typing import Any

import asyncpg
from pythonjsonlogger.json import JsonFormatter
from redis.asyncio import Redis

from worker.config import Settings
from worker.handlers import dispatch

logger = logging.getLogger(__name__)


def configure_logging(level: str) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logging.basicConfig(level=level, handlers=[handler], force=True)


class Worker:
    def __init__(self, settings: Settings, redis: Redis, pool: asyncpg.Pool) -> None:
        self.settings = settings
        self.redis = redis
        self.pool = pool
        self.stopping = asyncio.Event()

    async def run(self) -> None:
        logger.info("worker_started", extra={"queue": self.settings.queue_name})
        while not self.stopping.is_set():
            # MISSION_BUG(lv2-worker-retries): BRPOP removes work before processing is durable.
            item = await self.redis.brpop(
                self.settings.queue_name, timeout=self.settings.poll_timeout_seconds
            )
            if item is None:
                continue
            _, raw_job = item
            await self.handle(json.loads(raw_job))

    async def handle(self, job: dict[str, Any]) -> None:
        try:
            await dispatch(self.pool, job["kind"], job.get("payload", {}))
            await self._mark(job["id"], "completed")
            logger.info("job_completed", extra={"job_id": job["id"], "kind": job["kind"]})
        except Exception as exc:
            # MISSION_BUG(lv2-worker-retries): failures are terminal; attempts, retry delay,
            # and the configured dead-letter queue are never used.
            await self._mark(job["id"], "failed", str(exc))
            logger.exception("job_failed", extra={"job_id": job.get("id")})

    async def _mark(self, job_id: str, status: str, error: str | None = None) -> None:
        async with self.pool.acquire() as connection:
            await connection.execute(
                "UPDATE jobs SET status = $1, last_error = $2 WHERE id = $3::uuid",
                status,
                error,
                job_id,
            )


async def serve() -> None:
    settings = Settings()
    configure_logging(settings.log_level)
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    pool = await asyncpg.create_pool(settings.database_url, min_size=1, max_size=5)
    worker = Worker(settings, redis, pool)
    loop = asyncio.get_running_loop()
    for signal_name in (signal.SIGINT, signal.SIGTERM):
        with suppress(NotImplementedError):
            loop.add_signal_handler(signal_name, worker.stopping.set)
    try:
        await worker.run()
    finally:
        await redis.aclose()
        await pool.close()


if __name__ == "__main__":
    asyncio.run(serve())
