from datetime import date, timedelta

from httpx import AsyncClient


def payload_test(**kwargs) -> dict:
    base = {
        "name": "Тимур",
        "phone": "+79123456789",
        "booking_date": (date.today() + timedelta(days=1)).isoformat(),
        "booking_time": "20:00",
        "guests": 2,
    }
    base.update(kwargs)
    return base


async def test_create_booking_201(client: AsyncClient) -> None:
    response = await client.post("/bookings", json=payload_test())

    assert response.status_code == 201

    body = response.json()
    assert body["id"] > 0
    assert body["status"] == "active"
    assert body["phone"] == "+79123456789"


async def test_create_invalid_name_422(client: AsyncClient) -> None:
    assert (await client.post("/bookings", json=payload_test(name="T"))).status_code == 422


async def test_create_invalid_phone_422(client: AsyncClient) -> None:
    assert (await client.post("/bookings", json=payload_test(phone="123"))).status_code == 422


async def test_create_invalid_date_422(client: AsyncClient) -> None:
    assert (await client.post("/bookings", json=payload_test(booking_date="2005-07-19"))).status_code == 422


async def test_create_invalid_time_422(client: AsyncClient) -> None:
    assert (await client.post("/bookings", json=payload_test(booking_time="13:30"))).status_code == 422


async def test_create_invalid_guests_422(client: AsyncClient) -> None:
    assert (await client.post("/bookings", json=payload_test(guests=0))).status_code == 422


async def test_create_conflict_409(client: AsyncClient) -> None:
    payload = payload_test()

    assert (await client.post("/bookings", json=payload)).status_code == 201

    response = await client.post("/bookings", json=payload)
    assert response.status_code == 409
    assert response.json() == {"detail": "Slot is already booked"}


async def test_get_booking_200(client: AsyncClient) -> None:
    created = (await client.post("/bookings", json=payload_test())).json()
    response = await client.get(f"/bookings/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


async def test_get_booking_404(client: AsyncClient) -> None:
    response = await client.get("/bookings/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Booking not found"}


async def test_cancel_booking_200(client: AsyncClient) -> None:
    created = (await client.post("/bookings", json=payload_test())).json()
    response = await client.delete(f"/bookings/{created['id']}")

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


async def test_cancel_booking_404(client: AsyncClient) -> None:
    assert (await client.delete("/bookings/999999")).status_code == 404


async def test_list_all(client: AsyncClient) -> None:
    await client.post("/bookings", json=payload_test(name="Ти"))
    await client.post("/bookings", json=payload_test(name="Тм", booking_time="19:00"))

    response = await client.get("/bookings")
    assert response.status_code == 200
    assert len(response.json()) == 2


async def test_list_by_date(client: AsyncClient) -> None:
    target = (date.today() + timedelta(days=3)).isoformat()   # ✅ строка
    await client.post("/bookings", json=payload_test(name="Ти"))
    await client.post("/bookings", json=payload_test(name="Тм", booking_date=target))
    response = await client.get("/bookings", params={"date": target})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == "Тм"


async def test_list_pagination(client: AsyncClient) -> None:
    names = ["Тим", "Тимур", "Тимофей"]
    for i, name in enumerate(names):
        resp = await client.post(
            "/bookings",
            json=payload_test(name=name, booking_time=f"{12 + i}:00"),
        )
        assert resp.status_code == 201

    resp = await client.get("/bookings", params={"limit": 2, "offset": 1})
    assert resp.status_code == 200
    assert len(resp.json()) == 2
