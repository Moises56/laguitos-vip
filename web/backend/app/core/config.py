from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Laguitos Web"
    debug: bool = False
    secret_key: str = "change-me-to-a-random-string-at-least-32-chars"
    access_token_expire_minutes: int = 1440

    database_url: str = "sqlite+aiosqlite:///./data/laguitos.db"

    data_dir: Path = Path("./data")

    seed_user_1_email: str | None = None
    seed_user_1_password: str | None = None
    seed_user_1_name: str | None = None
    seed_user_2_email: str | None = None
    seed_user_2_password: str | None = None
    seed_user_2_name: str | None = None

    file_ttl_hours: int = 48
    cleanup_interval_seconds: int = 3600

    @property
    def downloads_dir(self) -> Path:
        return self.data_dir / "downloads"


settings = Settings()
