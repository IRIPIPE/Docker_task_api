# Docker Task API

Учебный API задач на FastAPI и PostgreSQL.

## Архитектура

Клиент → Nginx → Uvicorn / FastAPI → PostgreSQL

Docker Compose запускает три сервиса:

- `nginx` — принимает HTTP-запросы.
- `api` — создаёт, читает, обновляет и удаляет задачи.
- `db` — хранит задачи в PostgreSQL 16.

Данные БД сохраняются в Docker volume `task-api-pgdata`.
API запускается от пользователя `appuser`.

## Требования

- Docker Engine
- Docker Compose
- Docker Buildx

## Первый запуск

Из корня проекта:

```bash
cp .env.example .env
```

Указать настройки БД в `.env`. Для учебного запуска использовать
пароль из букв, цифр и подчёркиваний: он включается в URL подключения.

Создать внешний том:

```bash
docker volume create task-api-pgdata
```

Собрать и запустить сервисы:

```bash
docker compose up -d --build
docker compose ps
```

API доступен по адресу http://localhost:8000.
Swagger UI: http://localhost:8000/docs.

При первом запуске с пустым томом PostgreSQL выполняет `schema.sql`
и создаёт таблицу задач. При существующей БД скрипт повторно
не выполняется.

## Маршруты

| Метод | Путь | Назначение |
|---|---|---|
| GET | `/health` | Проверка работы API |
| GET | `/health/db` | Проверка подключения к БД |
| POST | `/tasks` | Создание задачи |
| GET | `/tasks` | Список задач |
| PATCH | `/tasks/{id}` | Изменение признака выполнения |
| DELETE | `/tasks/{id}` | Удаление задачи |

Создание задачи:

```bash
curl -X POST http://localhost:8000/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title":"Изучить Docker"}'
```

Получение списка:

```bash
curl http://localhost:8000/tasks
```

## Обновление приложения

```bash
docker compose up -d --build api
```

Дождаться статуса `healthy` у API, затем:

```bash
docker compose restart nginx
```

Перезапуск Nginx обновляет адрес API в текущей конфигурации прокси.

## Логи

```bash
docker compose logs --tail 50 api
docker compose logs --tail 50 db
docker compose logs --tail 50 nginx
```

## Остановка

```bash
docker compose down
```

Контейнеры и сеть проекта удаляются.
Внешний том `task-api-pgdata` и данные сохраняются.

Изменение `POSTGRES_PASSWORD` в `.env` не меняет пароль
пользователя в уже созданной БД.

## Зависимости

`requirements.txt` содержит прямые зависимости приложения.
`constraints.txt` фиксирует версии используемых Python-пакетов.

## Ограничения учебного проекта

- Авторизация и HTTPS пока не настроены.
- PATCH изменяет только поле `completed`.
- Для последующих изменений схемы БД нужны миграции.
