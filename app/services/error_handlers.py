import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from ..core.exceptions import BookingNotFoundError, SlotConflictError


logger = logging.getLogger(__name__)


def register_errors_handlers(app: FastAPI) -> None:
    """Регистрирует маппинг доменных исключений на HTTP-ответы 404/409."""

    @app.exception_handler(BookingNotFoundError)
    async def _booking_not_found(request: Request, exc: BookingNotFoundError) -> JSONResponse:
        logger.warning("404 %s %s: %s", request.method, request.url.path, exc)
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})

    @app.exception_handler(SlotConflictError)
    async def _slot_conflict(request: Request, exc: SlotConflictError) -> JSONResponse:
        logger.warning("409 %s %s: %s", request.method, request.url.path, exc)
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})
