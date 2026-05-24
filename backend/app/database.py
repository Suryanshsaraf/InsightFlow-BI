"""
Async SQLAlchemy engine, session factory, and base model.

Supports both PostgreSQL (asyncpg) and SQLite (aiosqlite) backends.
Provides a dependency-injectable ``get_db`` async generator for FastAPI routes.
"""

from __future__ import annotations

from typing import AsyncGenerator
from uuid import uuid4

from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# ── Naming conventions for Alembic auto-generation ───────────────
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)


class Base(AsyncAttrs, DeclarativeBase):
    """Declarative base for all ORM models."""

    metadata = metadata


# ── Engine configuration ─────────────────────────────────────────
_engine_kwargs: dict = {
    "echo": settings.debug,
    "future": True,
}

if settings.is_sqlite:
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    _engine_kwargs.update(
        {
            "pool_size": 20,
            "max_overflow": 10,
            "pool_pre_ping": True,
            "pool_recycle": 300,
        }
    )

engine = create_async_engine(settings.database_url, **_engine_kwargs)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables (for development / testing). Use Alembic in production."""
    async with engine.begin() as conn:
        # Create user_data schema for dynamic tables (PostgreSQL only)
        if not settings.is_sqlite:
            await conn.execute(
                text(f"CREATE SCHEMA IF NOT EXISTS {settings.user_data_schema}")
            )
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Dispose of the engine connection pool."""
    await engine.dispose()


def generate_uuid() -> str:
    """Generate a new UUID4 string for use as a primary key."""
    return str(uuid4())
