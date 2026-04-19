from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.models.db import User

logger = logging.getLogger(__name__)


async def seed_users(db: AsyncSession) -> None:
    """Crea usuarios seed si las env vars están configuradas y no existen aún."""
    seeds: list[tuple[str, str, str]] = []

    if all([settings.seed_user_1_email, settings.seed_user_1_password, settings.seed_user_1_name]):
        seeds.append((
            settings.seed_user_1_email,  # type: ignore[arg-type]
            settings.seed_user_1_password,  # type: ignore[arg-type]
            settings.seed_user_1_name,  # type: ignore[arg-type]
        ))

    if all([settings.seed_user_2_email, settings.seed_user_2_password, settings.seed_user_2_name]):
        seeds.append((
            settings.seed_user_2_email,  # type: ignore[arg-type]
            settings.seed_user_2_password,  # type: ignore[arg-type]
            settings.seed_user_2_name,  # type: ignore[arg-type]
        ))

    if not seeds:
        logger.info("No seed user env vars configured, skipping")
        return

    created = 0
    for email, password, name in seeds:
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            logger.info("Seed user %s already exists, skipping", email)
            continue

        user = User(
            email=email,
            password_hash=hash_password(password),
            name=name,
        )
        db.add(user)
        created += 1
        logger.info("Seed user created: %s <%s>", name, email)

    if created:
        await db.commit()
        logger.info("Seeded %d user(s)", created)
