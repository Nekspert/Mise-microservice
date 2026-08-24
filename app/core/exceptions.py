class BookingNotFoundError(Exception):
    """Вызывается, когда бронирование с переданным id не найдено."""


class SlotConflictError(Exception):
    """Вызывается, когда запрашиваемый слот на выбранные дату/время уже занят."""
