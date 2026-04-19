#!/usr/bin/env python3
"""CLI para crear usuarios manualmente en la BD de Laguitos."""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Asegurar que los imports funcionen al ejecutar directamente
_backend_root = Path(__file__).resolve().parents[2]
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

_project_root = _backend_root.parents[1]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


async def _create(email: str, password: str, name: str) -> None:
    from app.core.database import async_session, engine
    from app.core.security import hash_password
    from app.models.db import Base, User
    from sqlalchemy import select

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            print(f"Usuario {email} ya existe, omitiendo.")
            return

        user = User(
            email=email,
            password_hash=hash_password(password),
            name=name,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"Usuario creado: {name} <{email}> (id={user.id})")

    await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Crear usuario en Laguitos")
    parser.add_argument("--email", required=True, help="Email del usuario")
    parser.add_argument("--password", required=True, help="Contraseña")
    parser.add_argument("--name", required=True, help="Nombre visible")
    args = parser.parse_args()

    asyncio.run(_create(args.email, args.password, args.name))


if __name__ == "__main__":
    main()
