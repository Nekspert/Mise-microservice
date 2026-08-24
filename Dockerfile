FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN pip install --no-cache-dir poetry==2.3.0

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --without dev

COPY app ./app
COPY migrations ./migrations
COPY alembic.ini ./

RUN mkdir -p /app/data

CMD alembic upgrade head && python -m app.main