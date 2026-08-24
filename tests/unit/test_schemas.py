from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.schemas.booking import BookingCreate


TODAY = date.today()


def payload_test(**kwargs) -> dict:
    base = {
        "name": "Тимур",
        "phone": "+79123456789",
        "booking_date": TODAY + timedelta(days=1),
        "booking_time": "20:00",
        "guests": 2,
    }
    base.update(kwargs)
    return base


@pytest.mark.parametrize("name", ["Тимур", "Тимур-Бер", "Иван Петров", "Ёлка", "Tim-Ber"])
def test_name_valid(name: str) -> None:
    assert BookingCreate(**payload_test(name=name)).name == name


@pytest.mark.parametrize("name", ["A", "---", "  ", "A  B", "Тимур\tБер", "123", "Тимур!"])
def test_name_invalid(name: str) -> None:
    with pytest.raises(ValidationError):
        BookingCreate(**payload_test(name=name))


@pytest.mark.parametrize(
    ("phone", "expected"),
    [
        ("+79123456789", "+79123456789"),
        ("89123456789", "+79123456789"),
        ("79123456789", "+79123456789"),
        ("+7 912 345 67 89", "+79123456789"),
        ("8 (912) 345-67-89", "+79123456789"),
    ],
)
def test_phone_normalized(phone: str, expected: str) -> None:
    assert BookingCreate(**payload_test(phone=phone)).phone == expected


@pytest.mark.parametrize("phone", ["+7912345678", "791234567890", "12345", "", "abc"])
def test_phone_invalid(phone: str) -> None:
    with pytest.raises(ValidationError):
        BookingCreate(**payload_test(phone=phone))


def test_date_today_and_plus_90_valid() -> None:
    BookingCreate(**payload_test(booking_date=TODAY))
    BookingCreate(**payload_test(booking_date=TODAY + timedelta(days=90)))


def test_date_yesterday_invalid() -> None:
    with pytest.raises(ValidationError):
        BookingCreate(**payload_test(booking_date=TODAY - timedelta(days=1)))


def test_date_plus_91_invalid() -> None:
    with pytest.raises(ValidationError):
        BookingCreate(**payload_test(booking_date=TODAY + timedelta(days=91)))


@pytest.mark.parametrize("t", ["12:00", "13:00", "22:00"])
def test_time_valid(t: str) -> None:
    BookingCreate(**payload_test(booking_time=t))


@pytest.mark.parametrize("t", ["11:00", "23:00", "12:30", "12:00:30", "12:00:00.500", "00:00"])
def test_time_invalid(t: str) -> None:
    with pytest.raises(ValidationError):
        BookingCreate(**payload_test(booking_time=t))


@pytest.mark.parametrize("guests", [1, 12])
def test_guests_boundaries_valid(guests: int) -> None:
    BookingCreate(**payload_test(guests=guests))


@pytest.mark.parametrize("guests", [0, 13])
def test_guests_out_of_range_invalid(guests: int) -> None:
    with pytest.raises(ValidationError):
        BookingCreate(**payload_test(guests=guests))
