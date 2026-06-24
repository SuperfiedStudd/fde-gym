from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import ClaimEvent

router = APIRouter(tags=["events"])


@router.get("/events")
async def list_events(
    claim_id: UUID | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, object]]:
    query = select(ClaimEvent).order_by(ClaimEvent.created_at.desc()).limit(limit)
    if claim_id:
        query = query.where(ClaimEvent.claim_id == claim_id)
    events = (await session.execute(query)).scalars()
    return [
        {
            "id": str(event.id),
            "claim_id": str(event.claim_id),
            "type": event.event_type,
            "payload": event.payload,
            "created_at": event.created_at,
        }
        for event in events
    ]
