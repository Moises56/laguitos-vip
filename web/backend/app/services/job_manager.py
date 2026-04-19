from __future__ import annotations

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import WebSocket
from sqlalchemy import select

from app.core.config import settings
from app.core.database import async_session
from app.models.db import Download, JobStatus
from app.services.downloader_adapter import create_downloader, parse_progress

logger = logging.getLogger(__name__)


@dataclass
class JobState:
    job_id: str
    user_id: int
    status: JobStatus = JobStatus.PENDING
    downloader: Any = None
    future: Any = None


class JobManager:
    """Singleton que coordina descargas concurrentes en un ThreadPoolExecutor."""

    _instance: JobManager | None = None

    def __new__(cls) -> JobManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="dl")
        self._jobs: dict[str, JobState] = {}
        self._ws_connections: dict[str, set[WebSocket]] = {}
        self._loop: asyncio.AbstractEventLoop | None = None

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    @property
    def _event_loop(self) -> asyncio.AbstractEventLoop:
        return self._loop or asyncio.get_event_loop()

    # ── Job lifecycle ────────────────────────────────────────────────────

    async def start_job(
        self,
        job_id: str,
        url: str,
        mode: str,
        quality: str,
        user_id: int,
    ) -> None:
        state = JobState(job_id=job_id, user_id=user_id)
        self._jobs[job_id] = state

        carpeta = settings.downloads_dir / str(user_id)
        carpeta.mkdir(parents=True, exist_ok=True)

        loop = self._event_loop
        future = loop.run_in_executor(
            self._executor,
            self._run_download,
            job_id,
            url,
            mode,
            quality,
            user_id,
            carpeta,
        )
        state.future = future

    def _run_download(
        self,
        job_id: str,
        url: str,
        mode: str,
        quality: str,
        user_id: int,
        carpeta: Path,
    ) -> None:
        state = self._jobs.get(job_id)
        if not state:
            return

        loop = self._event_loop

        def progress_hook(d: dict[str, Any]) -> None:
            update = parse_progress(job_id, d)
            asyncio.run_coroutine_threadsafe(
                self._broadcast_progress(job_id, update), loop
            )

        downloader = create_downloader(carpeta, progress_hook)
        state.downloader = downloader
        state.status = JobStatus.RUNNING

        asyncio.run_coroutine_threadsafe(
            self._update_db_status(job_id, JobStatus.RUNNING), loop
        ).result(timeout=10)

        solo_audio = mode == "audio"
        calidad_map = {"1080": "1080p", "720": "720p", "480": "480p", "360": "480p"}
        calidad = calidad_map.get(quality, quality)

        try:
            result = downloader.descargar(url, solo_audio=solo_audio, calidad=calidad)

            if result.get("success"):
                original = Path(result["file_path"])
                ext = original.suffix
                new_path = carpeta / f"{job_id}{ext}"
                original.rename(new_path)

                file_size = new_path.stat().st_size if new_path.exists() else None

                asyncio.run_coroutine_threadsafe(
                    self._complete_job(
                        job_id,
                        title=result.get("title", "Sin título"),
                        platform=result.get("platform", "Desconocida"),
                        file_path=str(new_path),
                        file_size=file_size,
                    ),
                    loop,
                ).result(timeout=10)
            else:
                error_msg = result.get("message", "Error desconocido")
                cancelled = "cancelad" in error_msg.lower()
                asyncio.run_coroutine_threadsafe(
                    self._fail_job(job_id, error_msg, cancelled=cancelled), loop
                ).result(timeout=10)

        except Exception as exc:
            logger.exception("Download failed for job %s", job_id)
            asyncio.run_coroutine_threadsafe(
                self._fail_job(job_id, str(exc)), loop
            ).result(timeout=10)
        finally:
            final_state = self._jobs.get(job_id)
            if final_state:
                asyncio.run_coroutine_threadsafe(
                    self._broadcast_progress(
                        job_id,
                        {
                            "job_id": job_id,
                            "status": final_state.status.value,
                            "percent": 100.0
                            if final_state.status == JobStatus.COMPLETED
                            else 0.0,
                            "speed_bytes_per_sec": None,
                            "eta_seconds": None,
                            "downloaded_bytes": None,
                            "total_bytes": None,
                            "message": "Descarga completada"
                            if final_state.status == JobStatus.COMPLETED
                            else final_state.status.value,
                        },
                    ),
                    loop,
                )

    # ── DB persistence ───────────────────────────────────────────────────

    async def _update_db_status(self, job_id: str, status: JobStatus) -> None:
        async with async_session() as db:
            result = await db.execute(
                select(Download).where(Download.id == job_id)
            )
            download = result.scalar_one_or_none()
            if download:
                download.status = status.value
                await db.commit()

    async def _complete_job(
        self,
        job_id: str,
        title: str,
        platform: str,
        file_path: str,
        file_size: int | None,
    ) -> None:
        state = self._jobs.get(job_id)
        if state:
            state.status = JobStatus.COMPLETED

        async with async_session() as db:
            result = await db.execute(
                select(Download).where(Download.id == job_id)
            )
            download = result.scalar_one_or_none()
            if download:
                download.status = JobStatus.COMPLETED.value
                download.title = title
                download.platform = platform
                download.file_path = file_path
                download.file_size_bytes = file_size
                download.progress_percent = 100.0
                download.completed_at = datetime.now(UTC)
                await db.commit()

    async def _fail_job(
        self, job_id: str, error: str, *, cancelled: bool = False
    ) -> None:
        status = JobStatus.CANCELLED if cancelled else JobStatus.FAILED
        state = self._jobs.get(job_id)
        if state:
            state.status = status

        async with async_session() as db:
            result = await db.execute(
                select(Download).where(Download.id == job_id)
            )
            download = result.scalar_one_or_none()
            if download:
                download.status = status.value
                download.error_message = error
                download.completed_at = datetime.now(UTC)
                await db.commit()

    # ── Cancel ───────────────────────────────────────────────────────────

    async def cancel_job(self, job_id: str) -> bool:
        state = self._jobs.get(job_id)
        if not state or not state.downloader:
            return False
        state.downloader.cancelar()
        return True

    # ── WebSocket management ─────────────────────────────────────────────

    async def register_ws(self, job_id: str, ws: WebSocket) -> None:
        if job_id not in self._ws_connections:
            self._ws_connections[job_id] = set()
        self._ws_connections[job_id].add(ws)

    async def unregister_ws(self, job_id: str, ws: WebSocket) -> None:
        if job_id in self._ws_connections:
            self._ws_connections[job_id].discard(ws)
            if not self._ws_connections[job_id]:
                del self._ws_connections[job_id]

    async def _broadcast_progress(self, job_id: str, data: dict) -> None:
        connections = self._ws_connections.get(job_id, set()).copy()
        dead: list[WebSocket] = []
        for ws in connections:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.unregister_ws(job_id, ws)

    # ── Housekeeping ─────────────────────────────────────────────────────

    def cleanup_finished_jobs(self) -> None:
        terminal = {JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED}
        finished = [jid for jid, s in self._jobs.items() if s.status in terminal]
        for jid in finished:
            self._jobs.pop(jid, None)
            self._ws_connections.pop(jid, None)

    async def shutdown(self) -> None:
        for state in self._jobs.values():
            if state.downloader:
                state.downloader.cancelar()
        self._executor.shutdown(wait=False, cancel_futures=True)
        self._jobs.clear()
        self._ws_connections.clear()


job_manager = JobManager()
