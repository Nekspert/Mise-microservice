from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_session
from ..services.booking_service import BookingService


async def get_service(session: AsyncSession = Depends(get_session)) -> BookingService:
    """Зависимость: создаёт сервис бронирования с сессией запроса."""

    return BookingService(session=session)
