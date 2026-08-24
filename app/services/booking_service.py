import logging
from dataclasses import dataclass
from datetime import date

from sqlalchemy import select, Select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.enums import BookingStatus
from ..core.exceptions import BookingNotFoundError, SlotConflictError
from ..models.booking import BookingModel
from ..schemas.booking import BookingCreate


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class BookingService:
    """Сервис бронирования: бизнес-правила и работа с БД.

    Получает сессию через DI и не управляет её жизненным циклом.
    """

    session: AsyncSession

    async def _find_active(self, payload: BookingCreate) -> BookingModel | None:
        """Активная бронь на ту же дату/время или None, если слот свободен."""

        stmt: Select[tuple[BookingModel]] = select(BookingModel).where(
            BookingModel.booking_date == payload.booking_date,
            BookingModel.booking_time == payload.booking_time,
            BookingModel.status == BookingStatus.active,
        )
        return await self.session.scalar(stmt)

    async def create(self, payload: BookingCreate) -> BookingModel:
        """Создаёт бронь. Бросает SlotConflictError, если слот занят."""

        if await self._find_active(payload) is not None:
            logger.warning("Slot conflict: %s %s already active", payload.booking_date, payload.booking_time)
            raise SlotConflictError("Slot is already booked")

        instance: BookingModel = BookingModel(**payload.model_dump())
        self.session.add(instance)

        try:
            await self.session.commit()
        except IntegrityError as exc:
            logger.warning("Race on slot %s %s: %s", payload.booking_date, payload.booking_time, exc)
            await self.session.rollback()
            raise SlotConflictError("Slot is already booked") from exc

        await self.session.refresh(instance)
        logger.info("Booking created id=%s slot=%s %s", instance.id, instance.booking_date, instance.booking_time)
        return instance

    async def get(self, booking_id: int) -> BookingModel:
        """Возвращает бронь по id. Бросает BookingNotFoundError, если её нет."""

        instance: BookingModel | None = await self.session.get(BookingModel, booking_id)
        if instance is None:
            raise BookingNotFoundError("Booking not found")
        return instance

    async def list(
        self,
        booking_date: date | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[BookingModel]:
        """Список броней с опциональным фильтром по дате и пагинацией."""
        logger.debug("List bookings: date=%s limit=%s offset=%s", booking_date, limit, offset)

        stmt: Select[tuple[BookingModel]] = select(BookingModel).order_by(
            BookingModel.booking_date, BookingModel.booking_time,
        )
        if booking_date is not None:
            stmt = stmt.where(BookingModel.booking_date == booking_date)
        stmt = stmt.limit(limit).offset(offset)

        result: list[BookingModel] = list(await self.session.scalars(stmt))
        logger.debug("List bookings returned %s rows", len(result))
        return result

    async def cancel(self, booking_id: int) -> BookingModel:
        """Отменяет бронь. 404, если брони нет."""
        
        instance: BookingModel | None = await self.session.get(BookingModel, booking_id)
        if instance is None:
            raise BookingNotFoundError("Booking not found")
        if instance.status is not BookingStatus.cancelled:
            instance.status = BookingStatus.cancelled
            await self.session.commit()
            logger.info("Booking %s cancelled", booking_id)
        else:
            logger.debug("Booking %s already cancelled", booking_id)
        return instance
