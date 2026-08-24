import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI

from .api import bookings
from .core.config import config
from .core.database import build_async_db_manager
from .services.error_handlers import register_errors_handlers


logging.basicConfig(
    format=config.logging.log_format,
    level=config.logging.log_level_value,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Поднимает менеджер БД на старте и закрывает его на завершении."""
    logger.info("Starting application lifespan")

    manager = build_async_db_manager(config.db)
    app.state.manager = manager

    await manager.connect()

    try:
        yield
    finally:
        await manager.close()

    logger.info("Application lifespan stopped")


def create_app() -> FastAPI:
    """Фабрика приложения: конфигурация, хендлеры ошибок и роутеры."""
    logger.info("Creating FastAPI application")

    app = FastAPI(
        title=config.project.project_title,
        description=config.project.project_description,
        lifespan=lifespan,
    )

    logger.info("Registering error handlers")

    register_errors_handlers(app)

    logger.info("Registering routers")

    app.include_router(bookings.router)

    return app


if __name__ == "__main__":
    logger.info(
        "Starting uvicorn on %s:%s (reload=%s)",
        config.run.run_host, config.run.run_port, config.run.debug,
    )
    uvicorn.run(
        app="app.main:create_app",
        host=config.run.run_host,
        port=config.run.run_port,
        reload=config.run.debug,
        factory=True,
    )
