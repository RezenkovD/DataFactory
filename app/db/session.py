from __future__ import annotations

from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ..core.config import settings

_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


async def init_engine() -> None:
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.sqlalchemy_url, echo=False, pool_pre_ping=True
        )


def init_session_factory() -> None:
    global _session_factory
    if _session_factory is None:
        if _engine is None:
            raise RuntimeError("Engine not initialized yet")
        _session_factory = async_sessionmaker(
            bind=_engine, expire_on_commit=False, autoflush=False
        )


async def ensure_initialized() -> None:
    if _engine is None:
        await init_engine()
    if _session_factory is None:
        init_session_factory()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    await ensure_initialized()
    async with _session_factory() as session:
        yield session


def get_engine() -> AsyncEngine:
    if _engine is None:
        raise RuntimeError("Engine not initialized yet")
    return _engine


async def dispose_engine() -> None:
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
