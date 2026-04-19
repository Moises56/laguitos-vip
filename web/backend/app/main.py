from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from app.core.config import settings
from app.core.database import async_session, engine
from app.core.logging import setup_logging
from app.models.db import Base, Download, JobStatus
from app.models.schemas import HealthResponse
from app.routers import auth, downloads, websocket
from app.scripts.seed_initial_users import seed_users
from app.services.job_manager import job_manager

logger = logging.getLogger(__name__)

_cleanup_task: asyncio.Task | None = None


async def _cleanup_old_files_loop() -> None:
    while True:
        try:
            await asyncio.sleep(settings.cleanup_interval_seconds)
            cutoff = datetime.now(UTC) - timedelta(hours=settings.file_ttl_hours)
            count = 0
            async with async_session() as db:
                result = await db.execute(
                    select(Download).where(
                        Download.completed_at < cutoff,
                        Download.file_path.isnot(None),
                        Download.status == JobStatus.COMPLETED.value,
                    )
                )
                expired = result.scalars().all()
                for dl in expired:
                    p = Path(dl.file_path)
                    if p.exists():
                        p.unlink()
                        count += 1
                    dl.file_path = None
                await db.commit()
            if count:
                logger.info("Cleanup: removed %d expired files", count)
        except asyncio.CancelledError:
            break
        except Exception:
            logger.exception("Error in cleanup task")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _cleanup_task

    setup_logging()
    logger.info("Starting %s", settings.app_name)

    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.downloads_dir.mkdir(parents=True, exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")

    async with async_session() as db:
        await seed_users(db)

    job_manager.set_loop(asyncio.get_running_loop())
    _cleanup_task = asyncio.create_task(_cleanup_old_files_loop())
    logger.info("Cleanup task started (interval=%ds, ttl=%dh)",
                settings.cleanup_interval_seconds, settings.file_ttl_hours)

    yield

    if _cleanup_task:
        _cleanup_task.cancel()
        try:
            await _cleanup_task
        except asyncio.CancelledError:
            pass

    await job_manager.shutdown()
    await engine.dispose()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(downloads.router)
app.include_router(websocket.router)


@app.get("/api/health", response_model=HealthResponse, tags=["health"])
async def health():
    return HealthResponse(
        status="ok", app=settings.app_name, debug=settings.debug
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    detail = str(exc) if settings.debug else "Error interno del servidor"
    return JSONResponse(status_code=500, content={"detail": detail})


# ── Dev: servir el frontend estático desde el mismo proceso ─────────────
# En prod nginx sirve el frontend; este bloque solo corre con debug=True.
# Debe ir DESPUÉS de todos los include_router para que /api y /ws ganen
# sobre el mount de "/".
if settings.debug:
    frontend_path = Path(__file__).resolve().parents[3] / "web" / "frontend"
    if frontend_path.exists():
        app.mount(
            "/",
            StaticFiles(directory=str(frontend_path), html=True),
            name="frontend",
        )
        logger.info("Serving frontend from %s", frontend_path)
    else:
        logger.warning("Frontend path not found: %s", frontend_path)
