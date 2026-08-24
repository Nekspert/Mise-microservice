from datetime import date, time, timedelta
from re import fullmatch, sub

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..core.enums import BookingStatus


class BookingBase(BaseModel):
    """Базовая схема бронирования: общие поля запроса и ответа."""

    name: str = Field(
        min_length=2,
        max_length=50,
        description="Имя гостя. Буквы, пробелы или дефисы. Минимум 2 символа.",
        examples=["Тимур"],
    )
    phone: str = Field(
        description="Номер телефона в российском формате +7XXXXXXXXXX или 8XXXXXXXXXX.",
        examples=["+79124676355", "89124676355"],
    )
    booking_date: date = Field(
        description="Дата бронирования. Не раньше сегодняшнего дня. Не позднее +90 дней.",
        examples=["2026-08-23"],
    )
    booking_time: time = Field(
        description="Временной слот бронирования. 12:00–22:00, шаг 1 час.",
        examples=["21:00"],
    )
    guests: int = Field(
        ge=1,
        le=12,
        description="Количество гостей (от 1 до 12).",
        examples=[1],
    )


class BookingCreate(BookingBase):
    """Схема создания бронирования: применяются бизнес-валидаторы."""

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2 or not fullmatch(r"[А-ЯЁа-яёA-Za-z]+([ -][А-ЯЁа-яёA-Za-z]+)*", value):
            raise ValueError("Name must contain only letters, spaces and hyphens")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        digits = sub(r"\D", "", value)
        if len(digits) == 11 and digits[0] in ("7", "8"):
            return "+7" + digits[1:]
        raise ValueError("Phone must be +7XXXXXXXXXX or 8XXXXXXXXXX (10 digits)")

    @field_validator("booking_date")
    @classmethod
    def validate_booking_date(cls, value: date) -> date:
        today = date.today()
        max_date = today + timedelta(days=90)
        if value < today or value > max_date:
            raise ValueError("Date must be today or within the next 90 days")
        return value

    @field_validator("booking_time")
    @classmethod
    def validate_booking_time(cls, value: time) -> time:
        if value.hour < 12 or value.hour > 22 or value.minute != 0 or value.second != 0 or value.microsecond != 0:
            raise ValueError("Available slots are 12:00 to 22:00, hourly")
        return value


class BookingOut(BookingBase):
    """Схема ответа: без бизнес-валидаторов, читается из ORM-объекта."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        description="Идентификатор бронирования.",
        examples=[1]
    )
    status: BookingStatus = Field(
        description="Статус бронирования: active | cancelled.",
        examples=[BookingStatus.active],
    )
