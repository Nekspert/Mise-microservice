from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Базовая абстрактная модель."""

    __abstract__ = True
