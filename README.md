# CheckStock

Учёт остатков по SKU и фулфилмент-центрам (ФФ): перемещения, FBS/FBO, журнал операций.

**Стек:** Python, FastAPI, Tortoise ORM, PostgreSQL, React (Vite).

## Запуск

```bash
docker compose up --build
```

| Сервис | Адрес |
|--------|--------|
| Веб-интерфейс | http://localhost:4006 |
| API (Swagger) | http://localhost:4005/docs |
| PostgreSQL | `localhost:5440`, user/db/password: `checkstock` |

Данные БД лежат в `./tmp/postgres-data` и переживают перезапуск контейнеров.

## Локально (бэкенд)

```bash
cp .env.example .env   # при необходимости
docker compose up -d db
poetry install
poetry run aerich upgrade   # после init-db один раз
poetry run app
```

Переменные подключения: `PG_HOST`, `PG_PORT`, `PG_USER`, `PG_PASSWORD`, `PG_DB` (см. `.env.example`).

## Локально (фронт)

```bash
cd frontend
npm install
npm run dev
```

http://localhost:5173 — прокси на API `4005` (см. `frontend/vite.config.ts`).

## Миграции

```bash
poetry run aerich init-db    # один раз на пустой БД
poetry run aerich migrate --name имя
poetry run aerich upgrade
```

## Структура

```
checkstock_backend/   — API (routes, schemas, utils, db/models)
frontend/             — React UI
migrations/           — Aerich
```

## Операции учёта

Одна ручка: `POST /operations/` с полем `type` (`arrival`, `transfer_ship`, `fbs_reserve`, …).  
Сводка для UI: `GET /inventory/snapshot`.

Опционально: заголовок `Idempotency-Key` или `idempotency_key` в JSON.

https://drive.google.com/file/d/1G6v8WRCbN1saBq3Sh4mbS0-JVG_140sE/view?usp=sharing