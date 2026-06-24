from uuid import UUID

from fastapi import Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Role, User


async def current_user(
    session: AsyncSession, x_user_id: str | None = Header(default=None)
) -> tuple[User, str]:
    if not x_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="x-user-id required")
    try:
        user_id = UUID(x_user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid user id"
        ) from exc
    row = await session.execute(
        select(User, Role.name).join(Role, User.role_id == Role.id).where(User.id == user_id)
    )
    result = row.one_or_none()
    if result is None or not result[0].active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unknown user")
    return result[0], result[1]
