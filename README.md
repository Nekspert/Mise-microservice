# Nekspert-Mise-Microservice
REST API для бронирования столика в ресторане

## Стек

Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), SQLite, Alembic, Uvicorn, Poetry.

## Возможности

- Создание брони: `POST /bookings`
- Список броней с фильтром по дате и пагинацией: `GET /bookings`
- Получение брони по id: `GET /bookings/{id}`
- Отмена брони: `DELETE /bookings/{id}`

Валидация входных данных, понятные ошибки `422`, `404`, `409`, Swagger на /docs и ReDoc на /redoc.

## Клонирование

```bash
git clone https://github.com/Nekspert/Mise-Microservice.git
cd Mise-Microservice
```

## Запуск без Docker

Требуется Python 3.11+ и Poetry.

Установка зависимостей:

```bash
poetry install
```

Создание файла окружения:

```bash
cp .env.example .env
```

Применение миграций:

```bash
poetry run alembic upgrade head
```

Запуск сервера:

```bash
poetry run uvicorn app.main:create_app --factory --reload
```

После запуска:

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Тесты

```bash
poetry run pytest
```

## Docker

Запуск:

```bash
docker compose up --build
```

После запуска:

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Решения

- Хранилище - SQLite через async SQLAlchemy 2.0.
- Код разделён на слои: роуты, сервисы, схемы, модели, зависимости. Роутер отвечает только за HTTP, бизнес-логика живёт в сервисе.
- Доменные ошибки вынесены в отдельные исключения, которые мапятся на 404 и 409 в одном месте.
- Для защиты слота от двойной брони используется частичный уникальный индекс по активным броням. Отмена освобождает слот, а одновременные запросы не могут создать две активные брони на один слот.

## Что бы доделал

- Проверку полного datetime вместо даты, чтобы нельзя было забронировать прошедшее время сегодня.
- Обновление брони (PUT/PATCH).
- Учёт часовых поясов.
- Дописал бы тестов.
- Ограничение частоты запросов и метрики.