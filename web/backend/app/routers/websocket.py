from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketException, status
from sqlalchemy import select

from app.core.database import async_session
from app.core.security import decode_token
from app.models.db import Download, User
from app.services.job_manager import job_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])

PING_INTERVAL = 30


@router.websocket("/ws/downloads/{job_id}")
async def ws_download_progress(websocket: WebSocket, job_id: str):
    token = websocket.query_params.get("token")

    # Accept first so we can send proper WS close codes
    await websocket.accept()

    reject_reason: str | None = None

    if not token:
        reject_reason = "Token requerido"
    else:
        try:
            payload = decode_token(token)
        except Exception:
            reject_reason = "Token inválido"

    if not reject_reason:
        user_id_raw = payload.get("sub")  # type: ignore[possibly-undefined]
        if not user_id_raw:
            reject_reason = "Token sin subject"
        else:
            try:
                user_id = int(user_id_raw)
            except (TypeError, ValueError):
                reject_reason = "Subject inválido"

    if not reject_reason:
        async with async_session() as db:
            result = await db.execute(
                select(User).where(User.id == user_id, User.is_active.is_(True))  # type: ignore[possibly-undefined]
            )
            user = result.scalar_one_or_none()
            if not user:
                reject_reason = "Usuario no encontrado"
            else:
                dl_result = await db.execute(
                    select(Download).where(Download.id == job_id)
                )
                download = dl_result.scalar_one_or_none()
                if not download:
                    reject_reason = "Descarga no encontrada"
                elif download.user_id != user_id:  # type: ignore[possibly-undefined]
                    reject_reason = "Solo el dueño puede ver el progreso en vivo"

    if reject_reason:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=reject_reason)
        return

    await job_manager.register_ws(job_id, websocket)

    try:
        while True:
            try:
                await asyncio.wait_for(
                    websocket.receive_text(), timeout=PING_INTERVAL
                )
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "ping"})
    except Exception:
        pass
    finally:
        await job_manager.unregister_ws(job_id, websocket)
