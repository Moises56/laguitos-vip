from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.db import JobStatus


# ── Auth ─────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class UserMe(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    name: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserMe


class UsersResponse(BaseModel):
    items: list[UserPublic]


# ── Downloads ────────────────────────────────────────────────────────────

class DownloadRequest(BaseModel):
    url: str = Field(min_length=1)
    mode: Literal["audio", "video"] = "video"
    quality: Literal["mejor", "1080", "720", "480", "360"] = "mejor"


class DownloadCreated(BaseModel):
    job_id: str
    status: str = "pending"
    message: str = "Descarga encolada"


class DownloadDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    url: str
    title: str
    platform: str
    mode: str
    quality: str
    status: str
    file_size_bytes: int | None = None
    duration_seconds: float | None = None
    thumbnail_url: str | None = None
    progress_percent: float = 0.0
    error_message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None
    owner: UserPublic
    is_mine: bool
    shared_with: list[SharedWith] = []


# ── History ──────────────────────────────────────────────────────────────

class SharedWith(BaseModel):
    id: int
    name: str
    shared_at: datetime


class HistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    platform: str
    mode: str
    status: str
    file_size_bytes: int | None = None
    thumbnail_url: str | None = None
    created_at: datetime
    owner: UserPublic
    is_mine: bool
    shared_with: list[SharedWith] = []


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
    total: int
    page: int
    page_size: int
    scope: Literal["own", "shared", "all"]


# ── Sharing ──────────────────────────────────────────────────────────────

class ShareRequest(BaseModel):
    user_id: int = Field(gt=0)


class ShareResponse(BaseModel):
    download_id: str
    shared_with_user_id: int
    shared_at: datetime


class ShareListItem(BaseModel):
    user_id: int
    user_name: str
    shared_at: datetime


class ShareListResponse(BaseModel):
    items: list[ShareListItem]


# ── Progress (WebSocket) ────────────────────────────────────────────────

class ProgressUpdate(BaseModel):
    job_id: str
    status: str
    percent: float = 0.0
    speed_bytes_per_sec: int | None = None
    eta_seconds: int | None = None
    downloaded_bytes: int | None = None
    total_bytes: int | None = None
    message: str | None = None


# ── Health ───────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"
    app: str
    debug: bool
