"""Async SQLAlchemy engine and session factory."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings


def _async_database_url() -> str:
    """Return the configured URL for SQLAlchemy's async psycopg dialect."""
    return settings.database_url.get_secret_value()


engine: AsyncEngine = create_async_engine(
    _async_database_url(),
    pool_pre_ping=True,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    """Yield a database session for a request."""
    async with SessionLocal() as session:
        yield session
