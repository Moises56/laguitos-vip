from __future__ import annotations

import uuid
from pathlib import Path
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import decode_token, get_current_user
from app.models.db import Download, JobStatus, Share, User
from app.models.schemas import (
    DownloadCreated,
    DownloadDetail,
    DownloadRequest,
    HistoryItem,
    HistoryResponse,
    ShareListItem,
    ShareListResponse,
    ShareRequest,
    ShareResponse,
    SharedWith,
    UserPublic,
)
from app.services.authz import get_accessible_download, get_owned_download
from app.services.job_manager import job_manager

router = APIRouter(prefix="/api/downloads", tags=["downloads"])


# ── Create download ──────────────────────────────────────────────────────

@router.post("", response_model=DownloadCreated, status_code=status.HTTP_202_ACCEPTED)
async def create_download(
    body: DownloadRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    job_id = str(uuid.uuid4())

    download = Download(
        id=job_id,
        user_id=user.id,
        url=body.url,
        mode=body.mode,
        quality=body.quality,
        status=JobStatus.PENDING.value,
    )
    db.add(download)
    await db.flush()

    await job_manager.start_job(
        job_id=job_id,
        url=body.url,
        mode=body.mode,
        quality=body.quality,
        user_id=user.id,
    )

    return DownloadCreated(job_id=job_id)


# ── List downloads (with scope) ─────────────────────────────────────────

@router.get("", response_model=HistoryResponse)
async def list_downloads(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    scope: Literal["own", "shared", "all"] = "own",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    offset = (page - 1) * page_size

    if scope == "own":
        base = select(Download).where(Download.user_id == user.id)
    elif scope == "shared":
        base = (
            select(Download)
            .join(Share, Share.download_id == Download.id)
            .where(Share.shared_with_user_id == user.id)
        )
    else:
        base = (
            select(Download)
            .outerjoin(Share, Share.download_id == Download.id)
            .where(
                or_(
                    Download.user_id == user.id,
                    Share.shared_with_user_id == user.id,
                )
            )
        )

    count_sub = base.with_only_columns(func.count(Download.id.distinct()))
    total = (await db.execute(count_sub)).scalar() or 0

    items_q = (
        base.distinct()
        .order_by(Download.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .options(
            selectinload(Download.owner),
            selectinload(Download.shares).selectinload(Share.shared_with),
        )
    )
    result = await db.execute(items_q)
    downloads = result.scalars().unique().all()

    items = [_to_history_item(dl, user) for dl in downloads]

    return HistoryResponse(
        items=items, total=total, page=page, page_size=page_size, scope=scope
    )


# ── Get single download ─────────────────────────────────────────────────

@router.get("/{job_id}", response_model=DownloadDetail)
async def get_download(
    job_id: str,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    download = await get_accessible_download(db, job_id, user)
    return _to_download_detail(download, user)


# ── Cancel download (owner only) ────────────────────────────────────────

@router.post("/{job_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_download(
    job_id: str,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    download = await get_owned_download(db, job_id, user)

    if download.status not in (JobStatus.PENDING.value, JobStatus.RUNNING.value):
        raise HTTPException(400, "La descarga ya terminó")

    cancelled = await job_manager.cancel_job(job_id)
    if not cancelled:
        download.status = JobStatus.CANCELLED.value
        download.error_message = "Cancelada por el usuario"

    return {"message": "Descarga cancelada"}


# ── Delete download (owner only) ────────────────────────────────────────

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_download(
    job_id: str,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    download = await get_owned_download(db, job_id, user)

    if download.file_path:
        p = Path(download.file_path)
        if p.exists():
            p.unlink()

    await db.delete(download)


# ── Download file ────────────────────────────────────────────────────────

@router.get("/{job_id}/file")
async def download_file(
    job_id: str,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    payload = decode_token(token)
    user_id_raw = payload.get("sub")
    if not user_id_raw:
        raise HTTPException(401, "Token sin subject")

    try:
        user_id = int(user_id_raw)
    except (TypeError, ValueError) as exc:
        raise HTTPException(401, "Subject inválido") from exc

    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active.is_(True))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(401, "Usuario no encontrado")

    download = await get_accessible_download(db, job_id, user)

    if download.status != JobStatus.COMPLETED.value:
        raise HTTPException(400, "La descarga aún no está lista")

    if not download.file_path or not Path(download.file_path).exists():
        raise HTTPException(410, "El archivo expiró después de 48 horas")

    ext = Path(download.file_path).suffix
    safe_title = download.title or "descarga"
    filename = f"{safe_title}{ext}"

    return FileResponse(
        download.file_path,
        filename=filename,
        media_type="application/octet-stream",
    )


# ── Sharing endpoints ───────────────────────────────────────────────────

@router.post(
    "/{job_id}/share",
    response_model=ShareResponse,
    status_code=status.HTTP_201_CREATED,
)
async def share_download(
    job_id: str,
    body: ShareRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    download = await get_owned_download(db, job_id, user)

    if body.user_id == user.id:
        raise HTTPException(400, "No podés compartir contigo mismo")

    target = await db.execute(
        select(User).where(User.id == body.user_id, User.is_active.is_(True))
    )
    if not target.scalar_one_or_none():
        raise HTTPException(404, "Usuario destino no encontrado")

    existing = await db.execute(
        select(Share).where(
            Share.download_id == job_id,
            Share.shared_with_user_id == body.user_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(409, "Ya compartido con este usuario")

    share = Share(
        download_id=job_id,
        shared_by_user_id=user.id,
        shared_with_user_id=body.user_id,
    )
    db.add(share)
    await db.flush()

    return ShareResponse(
        download_id=job_id,
        shared_with_user_id=body.user_id,
        shared_at=share.shared_at,
    )


@router.delete(
    "/{job_id}/share/{target_user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def unshare_download(
    job_id: str,
    target_user_id: int,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await get_owned_download(db, job_id, user)

    result = await db.execute(
        select(Share).where(
            Share.download_id == job_id,
            Share.shared_with_user_id == target_user_id,
        )
    )
    share = result.scalar_one_or_none()
    if not share:
        raise HTTPException(404, "Share no encontrado")

    await db.delete(share)


@router.get("/{job_id}/shares", response_model=ShareListResponse)
async def list_shares(
    job_id: str,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    download = await get_owned_download(db, job_id, user)

    items = [
        ShareListItem(
            user_id=s.shared_with.id,
            user_name=s.shared_with.name,
            shared_at=s.shared_at,
        )
        for s in download.shares
    ]
    return ShareListResponse(items=items)


# ── Helpers ──────────────────────────────────────────────────────────────

def _to_history_item(dl: Download, current_user: User) -> HistoryItem:
    is_mine = dl.user_id == current_user.id
    shared_with: list[SharedWith] = []
    if is_mine:
        shared_with = [
            SharedWith(
                id=s.shared_with.id,
                name=s.shared_with.name,
                shared_at=s.shared_at,
            )
            for s in dl.shares
        ]
    return HistoryItem(
        id=dl.id,
        title=dl.title,
        platform=dl.platform,
        mode=dl.mode,
        status=dl.status,
        file_size_bytes=dl.file_size_bytes,
        thumbnail_url=dl.thumbnail_url,
        created_at=dl.created_at,
        owner=UserPublic(id=dl.owner.id, name=dl.owner.name),
        is_mine=is_mine,
        shared_with=shared_with,
    )


def _to_download_detail(dl: Download, current_user: User) -> DownloadDetail:
    is_mine = dl.user_id == current_user.id
    shared_with: list[SharedWith] = []
    if is_mine:
        shared_with = [
            SharedWith(
                id=s.shared_with.id,
                name=s.shared_with.name,
                shared_at=s.shared_at,
            )
            for s in dl.shares
        ]
    return DownloadDetail(
        id=dl.id,
        url=dl.url,
        title=dl.title,
        platform=dl.platform,
        mode=dl.mode,
        quality=dl.quality,
        status=dl.status,
        file_size_bytes=dl.file_size_bytes,
        duration_seconds=dl.duration_seconds,
        thumbnail_url=dl.thumbnail_url,
        progress_percent=dl.progress_percent,
        error_message=dl.error_message,
        created_at=dl.created_at,
        completed_at=dl.completed_at,
        owner=UserPublic(id=dl.owner.id, name=dl.owner.name),
        is_mine=is_mine,
        shared_with=shared_with,
    )
