from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class JobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    downloads: Mapped[list[Download]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
        foreign_keys="Download.user_id",
    )
    shares_given: Mapped[list[Share]] = relationship(
        back_populates="shared_by",
        cascade="all, delete-orphan",
        foreign_keys="Share.shared_by_user_id",
    )
    shares_received: Mapped[list[Share]] = relationship(
        back_populates="shared_with",
        cascade="all, delete-orphan",
        foreign_keys="Share.shared_with_user_id",
    )


class Download(Base):
    __tablename__ = "downloads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    url: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(String(500), default="")
    platform: Mapped[str] = mapped_column(String(50), default="", index=True)
    mode: Mapped[str] = mapped_column(String(20))
    quality: Mapped[str] = mapped_column(String(20))
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), index=True, default=JobStatus.PENDING)
    progress_percent: Mapped[float] = mapped_column(Float, default=0.0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    owner: Mapped[User] = relationship(
        back_populates="downloads", foreign_keys=[user_id]
    )
    shares: Mapped[list[Share]] = relationship(
        back_populates="download", cascade="all, delete-orphan"
    )


class Share(Base):
    __tablename__ = "shares"

    id: Mapped[int] = mapped_column(primary_key=True)
    download_id: Mapped[str] = mapped_column(
        ForeignKey("downloads.id", ondelete="CASCADE"), index=True
    )
    shared_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True
    )
    shared_with_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True
    )
    shared_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    download: Mapped[Download] = relationship(back_populates="shares")
    shared_by: Mapped[User] = relationship(
        back_populates="shares_given", foreign_keys=[shared_by_user_id]
    )
    shared_with: Mapped[User] = relationship(
        back_populates="shares_received", foreign_keys=[shared_with_user_id]
    )

    __table_args__ = (
        UniqueConstraint(
            "download_id",
            "shared_with_user_id",
            name="uq_share_download_user",
        ),
    )
