from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from redis.asyncio import Redis
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import current_user
from app.db import get_session
from app.models import Assignment, Claim, ClaimEvent, ClaimNote
from app.schemas import (
    AssignmentCreate,
    ClaimCreate,
    ClaimList,
    ClaimRead,
    NoteCreate,
    StatusTransition,
)

router = APIRouter(prefix="/claims", tags=["claims"])


def get_redis(request: Request) -> Redis:
    return request.app.state.redis


@router.post("", response_model=ClaimRead, status_code=status.HTTP_201_CREATED)
async def create_claim(
    payload: ClaimCreate,
    session: AsyncSession = Depends(get_session),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> Claim:
    # MISSION_BUG(lv2-claim-idempotency): the header is read but never enforced or persisted.
    del idempotency_key
    claim = Claim(**payload.model_dump(), status="submitted")
    session.add(claim)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail="external_id already exists") from exc
    await session.refresh(claim)
    session.add(
        ClaimEvent(claim_id=claim.id, event_type="claim.submitted", payload={"source": "api"})
    )
    await session.commit()
    return claim


@router.get("", response_model=ClaimList)
async def list_claims(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    status_filter: str | None = Query(default=None, alias="status"),
    search: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> ClaimList:
    query = select(Claim)
    count_query = select(func.count()).select_from(Claim)
    if status_filter:
        # MISSION_BUG(lv1-sql-status-filter): status is compared to the claimant name.
        query = query.where(Claim.claimant_name == status_filter)
        count_query = count_query.where(Claim.claimant_name == status_filter)
    if search:
        # MISSION_BUG(lv3-search-latency): leading wildcard and lower() defeat a useful index.
        needle = f"%{search.lower()}%"
        query = query.where(func.lower(Claim.claimant_name).like(needle))
        count_query = count_query.where(func.lower(Claim.claimant_name).like(needle))
    total = int((await session.execute(count_query)).scalar_one())
    # MISSION_BUG(lv1-claims-pagination): page/page_size are reported but not applied.
    items = list((await session.execute(query.order_by(Claim.created_at.desc()))).scalars())
    return ClaimList(items=items, page=page, page_size=page_size, total=total)


@router.get("/{claim_id}", response_model=ClaimRead)
async def get_claim(
    claim_id: UUID,
    redis: Redis = Depends(get_redis),
    session: AsyncSession = Depends(get_session),
) -> ClaimRead:
    cache_key = f"claim:{claim_id}"
    if cached := await redis.get(cache_key):
        return ClaimRead.model_validate_json(cached)
    claim = await session.get(Claim, claim_id)
    if claim is None:
        raise HTTPException(status_code=404, detail="claim not found")
    result = ClaimRead.model_validate(claim)
    await redis.set(cache_key, result.model_dump_json(), ex=60)
    return result


@router.post("/{claim_id}/transition", response_model=ClaimRead)
async def transition_claim(
    claim_id: UUID,
    payload: StatusTransition,
    session: AsyncSession = Depends(get_session),
) -> Claim:
    claim = await session.get(Claim, claim_id)
    if claim is None:
        raise HTTPException(status_code=404, detail="claim not found")
    # MISSION_BUG(lv1-status-transitions): any state may transition to any other state.
    claim.status = payload.status
    claim.version += 1
    await session.commit()
    await session.refresh(claim)
    return claim


@router.post("/{claim_id}/notes", status_code=status.HTTP_201_CREATED)
async def add_note(
    claim_id: UUID,
    payload: NoteCreate,
    x_user_id: str | None = Header(default=None),
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    user, role = await current_user(session, x_user_id)
    claim = await session.get(Claim, claim_id)
    if claim is None:
        raise HTTPException(status_code=404, detail="claim not found")
    # MISSION_BUG(lv2-notes-rbac): adjusters can write notes on claims they do not own.
    if role not in {"admin", "supervisor", "adjuster"}:
        raise HTTPException(status_code=403, detail="role cannot create notes")
    note = ClaimNote(claim_id=claim_id, author_id=user.id, **payload.model_dump())
    session.add(note)
    await session.commit()
    return {"id": str(note.id)}


@router.post("/{claim_id}/assign", response_model=ClaimRead)
async def assign_claim(
    claim_id: UUID,
    payload: AssignmentCreate,
    redis: Redis = Depends(get_redis),
    session: AsyncSession = Depends(get_session),
) -> Claim:
    claim = await session.get(Claim, claim_id)
    if claim is None:
        raise HTTPException(status_code=404, detail="claim not found")
    # MISSION_BUG(lv3-assignment-race): expected_version is ignored and writes are not serialized.
    await session.execute(
        update(Assignment).where(Assignment.claim_id == claim_id).values(active=False)
    )
    session.add(Assignment(claim_id=claim_id, user_id=payload.user_id))
    claim.version += 1
    await session.commit()
    await session.refresh(claim)
    # MISSION_BUG(lv2-cache-invalidation): the claim cache is left stale after mutation.
    del redis
    return claim


@router.post("/{claim_id}/payments/simulate")
async def simulate_payment(
    claim_id: UUID, session: AsyncSession = Depends(get_session)
) -> dict[str, str]:
    claim = await session.get(Claim, claim_id)
    if claim is None:
        raise HTTPException(status_code=404, detail="claim not found")
    # MISSION_BUG(lv2-payment-logging): unstructured output has no request/claim context.
    print("starting payment")
    result = "queued" if claim.status == "approved" else "skipped"
    print("payment result", result)
    return {"status": result}
