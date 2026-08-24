from datetime import date

from fastapi import APIRouter, Depends, Query, status

from ..dependencies.service import get_service
from ..models.booking import BookingModel
from ..schemas.booking import BookingCreate, BookingOut
from ..services.booking_service import BookingService


router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "",
    summary="Создать бронь",
    description="Создаёт бронирование столика. Возвращает 201 с объектом брони "
                "(статус `active`). При занятом слоте - 409.",
    status_code=status.HTTP_201_CREATED,
    response_model=BookingOut,
)
async def create_booking(
    payload: BookingCreate,
    service: BookingService = Depends(get_service),
) -> BookingOut:
    booking: BookingModel = await service.create(payload)
    return BookingOut.model_validate(booking)


@router.get(
    "/{booking_id}",
    summary="Получить бронь",
    description="Возвращает одну бронь по `id`. 404, если бронь не найдена.",
    status_code=status.HTTP_200_OK,
    response_model=BookingOut,
)
async def get_booking(
    booking_id: int,
    service: BookingService = Depends(get_service),
) -> BookingOut:
    booking: BookingModel = await service.get(booking_id)
    return BookingOut.model_validate(booking)


@router.get(
    "",
    summary="Список броней",
    description="Возвращает список броней. Поддерживает фильтр по дате "
                "(`?date=YYYY-MM-DD`) и пагинацию (`limit`, `offset`).",
    status_code=status.HTTP_200_OK,
    response_model=list[BookingOut],
)
async def get_bookings(
    booking_date: date | None = Query(default=None, alias="date"),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: BookingService = Depends(get_service),
) -> list[BookingOut]:
    bookings: list[BookingModel] = await service.list(
        booking_date=booking_date,
        limit=limit,
        offset=offset,
    )
    return [BookingOut.model_validate(b) for b in bookings]


@router.delete(
    "/{booking_id}",
    summary="Отменить бронь",
    description="Переводит бронь в статус `cancelled` (запись физически не удаляется). ",
    status_code=status.HTTP_200_OK,
    response_model=BookingOut,
)
async def cancel_booking(
    booking_id: int,
    service: BookingService = Depends(get_service),
) -> BookingOut:
    booking = await service.cancel(booking_id)
    return BookingOut.model_validate(booking)
