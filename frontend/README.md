# CheckStock — React UI

Отдельный фронт (Vite + React + TypeScript). Бэкенд не трогаем: только HTTP к FastAPI.

## Запуск

### Всё в Docker (бэк + фронт)

Из корня репозитория:

```bash
docker compose up --build
```

| Сервис | URL |
|--------|-----|
| UI | http://localhost:4006 |
| API напрямую | http://localhost:4005/docs |
| PostgreSQL | `localhost:5440` |

В контейнере фронта nginx отдаёт статику и проксирует `/api` → сервис `app`.

### Локальная разработка фронта

1. API (Docker или `poetry run app`), порт **4005**:

   ```bash
   docker compose up -d db app
   ```

2. Фронт:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Браузер: [http://localhost:5173](http://localhost:5173)

В dev запросы идут через прокси `/api` → `http://127.0.0.1:4005` (см. `vite.config.ts`).

Прямой URL API (без прокси):

```bash
VITE_API_URL=http://127.0.0.1:4005 npm run dev
```

## Экран

Три вкладки как на макете: **ФФ** → **Товары** → **Артикул**, крошки, таблица с колонками-неделями. Данные: `GET /inventory/snapshot`.