from enum import StrEnum


class BookingStatus(StrEnum):
    """Статусы бронирования."""

    active = "active"
    cancelled = "cancelled"
