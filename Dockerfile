FROM python:3.11-slim

WORKDIR /app

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && pip install --no-cache-dir poetry==2.1.3 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock README.md ./
RUN poetry install --no-ansi --no-root

COPY checkstock_backend ./checkstock_backend
COPY migrations ./migrations

RUN poetry install --no-ansi