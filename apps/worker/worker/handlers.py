import asyncio
import logging
from typing import Any

import asyncpg

logger = logging.getLogger(__name__)


async def process_claim(pool: asyncpg.Pool, payload: dict[str, Any]) -> None:
    claim_id = payload["claim_id"]
    async with pool.acquire() as connection:
        await connection.execute(
            """
            INSERT INTO claim_events (claim_id, event_type, payload)
            VALUES ($1::uuid, 'claim.processed', $2::jsonb)
            """,
            claim_id,
            {"worker": "claimops-worker"},
        )


async def generate_document(pool: asyncpg.Pool, payload: dict[str, Any]) -> None:
    await asyncio.sleep(0.05)
    if payload.get("simulate_failure"):
        raise RuntimeError("document renderer unavailable")
    logger.info("document_generated", extra={"claim_id": payload.get("claim_id")})


async def dispatch(pool: asyncpg.Pool, kind: str, payload: dict[str, Any]) -> None:
    if kind == "claim.process":
        # MISSION_BUG(lv3-async-claims-processor): coroutine is created but never awaited.
        process_claim(pool, payload)
        return
    if kind == "document.generate":
        await generate_document(pool, payload)
        return
    raise ValueError(f"unknown job kind: {kind}")
