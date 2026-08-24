from datetime import date, time

from sqlalchemy import Date, Enum, Index, Integer, String, text, Time
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from ..core.enums import BookingStatus


class BookingModel(Base):
    """Модель таблицы бронирований."""

    __tablename__ = "bookings"
    __table_args__ = (
        Index("ix_bookings_booking_date", "booking_date"),
        Index(
            "ix_unique_active_slot",
            "booking_date",
            "booking_time",
            unique=True,
            sqlite_where=text("status = 'active'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(20))
    booking_date: Mapped[date] = mapped_column(Date())
    booking_time: Mapped[time] = mapped_column(Time())
    guests: Mapped[int] = mapped_column(Integer())
    status: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus), server_default=BookingStatus.active)
