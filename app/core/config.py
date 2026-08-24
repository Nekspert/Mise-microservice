import logging
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


LOG_DEFAULT_FORMAT = (
    "[%(asctime)s] #%(levelname)s %(filename)s:%(lineno)d - %(name)s - %(message)s"
)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class LoggingConfig(BaseModel):
    """Настройки логирования (уровень и формат)."""

    log_level: Literal["debug", "info", "warning", "error", "critical"] = "info"
    log_format: str = LOG_DEFAULT_FORMAT

    @property
    def log_level_value(self) -> int:
        return logging.getLevelNamesMapping()[self.log_level.upper()]


class SettingsBase(BaseSettings):
    """Базовый класс настроек: читает переменные из .env."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


class DatabaseConfig(SettingsBase):
    """Настройки подключения к базе данных."""

    database_url: str = "sqlite+aiosqlite:///./bookings.db"


class ProjectConfig(SettingsBase):
    """Название и описание проекта (для сваггера)."""

    project_title: str = "MISE Bookings API"
    project_description: str = "REST API для бронирования столика в ресторане"


class RunConfig(SettingsBase):
    """Параметры запуска uvicorn (хост, порт, дебаг)."""

    run_host: str = "0.0.0.0"
    run_port: int = 8000
    debug: bool = True


class Config(BaseModel):
    """Корневой конфиг: агрегирует все группы настроек."""

    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    run: RunConfig = Field(default_factory=RunConfig)


config = Config()
