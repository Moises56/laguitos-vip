from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.db import Download, Share, User


async def get_accessible_download(
    db: AsyncSession,
    job_id: str,
    user: User,
) -> Download:
    """Devuelve el Download si el user es owner o tiene share."""
    stmt = (
        select(Download)
        .outerjoin(Share, Share.download_id == Download.id)
        .where(
            Download.id == job_id,
            or_(
                Download.user_id == user.id,
                Share.shared_with_user_id == user.id,
            ),
        )
        .options(
            selectinload(Download.owner),
            selectinload(Download.shares).selectinload(Share.shared_with),
        )
    )
    result = await db.execute(stmt)
    download = result.scalars().unique().first()
    if not download:
        raise HTTPException(404, "Descarga no encontrada o sin acceso")
    return download


async def get_owned_download(
    db: AsyncSession,
    job_id: str,
    user: User,
) -> Download:
    """Devuelve el Download solo si el user es owner."""
    stmt = (
        select(Download)
        .where(Download.id == job_id, Download.user_id == user.id)
        .options(
            selectinload(Download.owner),
            selectinload(Download.shares).selectinload(Share.shared_with),
        )
    )
    result = await db.execute(stmt)
    download = result.scalar_one_or_none()
    if not download:
        raise HTTPException(404, "Descarga no encontrada o no es tuya")
    return download
