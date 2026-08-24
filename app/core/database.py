import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, AsyncSession, create_async_engine

from ..core.config import DatabaseConfig


logger = logging.getLogger(__name__)


class AsyncDatabaseManager:
    """Работает с двигателем и фабрикой сессий. Создаётся один раз в lifespan."""

    def __init__(self, async_url: str) -> None:
        self.async_url = async_url
        self.async_engine: AsyncEngine | None = None
        self.async_sessionmaker: async_sessionmaker[AsyncSession] | None = None

    async def connect(self) -> None:
        """Создаёт engine и фабрику сессий, проверяет подключение к БД."""

        if self.async_engine is None:
            self.async_engine = create_async_engine(self.async_url, pool_pre_ping=True)
        if self.async_sessionmaker is None:
            self.async_sessionmaker = async_sessionmaker(
                bind=self.async_engine,
                autoflush=False,
                expire_on_commit=False,
            )

        await self.log_db_version()

    async def log_db_version(self) -> None:
        """Логирует версию SQLite (диагностика)."""

        async with self.async_engine.connect() as conn:
            version: str | None = (await conn.execute(text("SELECT sqlite_version();"))).scalar()
            logger.info("Connected to SQLite %s", version)

    async def close(self) -> None:
        """Закрывает пул соединений."""

        if self.async_engine is not None:
            await self.async_engine.dispose()
            logger.info("SQLite connection pool closed")


def build_async_db_manager(config: DatabaseConfig) -> AsyncDatabaseManager:
    """Фабрика асинхронного менеджера базы данных."""

    return AsyncDatabaseManager(async_url=config.database_url)
