from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    get_current_user,
    verify_password,
)
from app.models.db import User
from app.models.schemas import (
    LoginRequest,
    LoginResponse,
    UserMe,
    UserPublic,
    UsersResponse,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    body: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(User).where(User.email == body.email, User.is_active.is_(True))
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )

    token = create_access_token({"sub": str(user.id)})

    return LoginResponse(
        access_token=token,
        user=UserMe(id=user.id, email=user.email, name=user.name),
    )


@router.get("/me", response_model=UserMe)
async def me(user: Annotated[User, Depends(get_current_user)]):
    return UserMe(id=user.id, email=user.email, name=user.name)


@router.get("/users", response_model=UsersResponse)
async def list_other_users(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(User).where(User.id != user.id, User.is_active.is_(True))
    )
    others = result.scalars().all()
    return UsersResponse(
        items=[UserPublic(id=u.id, name=u.name) for u in others]
    )
