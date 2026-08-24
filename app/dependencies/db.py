from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import AsyncDatabaseManager


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Зависимость: отдаёт сессию БД на время жизни запроса."""

    manager: AsyncDatabaseManager = request.app.state.manager
    sessionmaker = manager.async_sessionmaker
    if sessionmaker is None:
        raise RuntimeError("Database is not initialized: run lifespan first")

    async with sessionmaker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
