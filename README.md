# Synclone

Навчальний проєкт керування метаданими резервних копій із FastAPI, PostgreSQL та окремим React frontend.

## Функціональність

- Реєстрація користувача через email і пароль.
- Вхід із видачею JWT access token.
- Ролі `admin` і `user`; публічна реєстрація завжди створює роль `user`.
- Адміністратор переглядає користувачів, змінює ролі та активність.
- Користувач бачить і створює лише власні записи резервних копій.
- Окремий React frontend: `http://localhost:5173`.
- Swagger у Sandbox: `http://localhost:8000/docs`.

> Поточна реалізація зберігає метадані й хеш, а не сам файл/вміст резервної копії. Статус `synced` означає, що запис прийнято API, а не те, що вміст перевірено або відновлено.

## Запуск

Backend та PostgreSQL запускаються через Docker Compose. Перед запуском API окремий одноразовий сервіс `migrate` застосовує Alembic-міграції, а потім за потреби створює початкового адміністратора. API не стартує, якщо міграції завершилися помилкою.

### Sandbox

1. Створи локальний конфігураційний файл:

```bash
cp .env.sandbox.example .env.sandbox
```

2. Відредагуй `.env.sandbox`: встанови власні `POSTGRES_PASSWORD`, `DATABASE_URL` з тим самим паролем і випадковий `JWT_SECRET_KEY` (наприклад, `openssl rand -hex 32`).

3. За потреби налаштуй початкового адміністратора: розкоментуй і заповни всі три змінні `INITIAL_ADMIN_EMAIL`, `INITIAL_ADMIN_PASSWORD` (мінімум 8 символів) і `INITIAL_ADMIN_NAME`. Цей обліковий запис створюється лише якщо email ще не існує; наявні облікові записи bootstrap не змінює.

4. Запусти:

```bash
docker compose -p synclone-sandbox -f docker-compose.yml up --build -d
```

API: `http://localhost:8000`; Swagger: `http://localhost:8000/docs`; PostgreSQL host port: `5433`.

Frontend запускається окремо:

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`. Дозволені frontend origins налаштовуються через `CORS_ORIGINS` у відповідному env-файлі.

### Production

1. Створи конфігурацію:

```bash
cp .env.production.example .env.production
```

2. Встанови унікальні production-значення для пароля PostgreSQL, `DATABASE_URL`, `JWT_SECRET_KEY`, `CORS_ORIGINS` (точний HTTPS origin frontend) та `DEBUG=false`. Не використовуй секрети Sandbox у Production.

3. За потреби налаштуй початкового адміністратора тими самими трьома `INITIAL_ADMIN_*` змінними.

4. Запусти:

```bash
docker compose -p synclone-production -f docker-compose.production.yml up --build -d
```

API: `http://localhost:8001`. Swagger та ReDoc у Production вимкнені.

### Керування середовищами

Зупинити Sandbox:

```bash
docker compose -p synclone-sandbox -f docker-compose.yml down
```

Зупинити Production:

```bash
docker compose -p synclone-production -f docker-compose.production.yml down
```

Команда `down` без `-v` зберігає томи PostgreSQL. Не використовуй `down -v`, якщо потрібно зберегти дані.

## Міграції бази даних

Схема БД версіонується через Alembic. Нова міграція додається до `alembic/versions/` і застосовується командою:

```bash
docker compose -p synclone-sandbox -f docker-compose.yml run --rm migrate
```

У штатному запуску Compose сервіс `migrate` виконує `alembic upgrade head` перед запуском API. Це працює окремо для Sandbox та Production, кожне зі своєю БД.

Початкова міграція створює відсутні таблиці та індекси `users` і `clone_backups`, але не видаляє наявні таблиці або записи. Вона також дозволяє підхопити локальні бази, у яких таблиці раніше створювалися вручну через SQLAlchemy. Подальші зміни схеми потрібно оформлювати окремими Alembic-міграціями; не додавай `create_all` у startup застосунку.

Для локального запуску backend без Docker після встановлення залежностей і налаштування env-файлу спочатку виконай `alembic upgrade head`, а потім `uvicorn app.main:app --reload`.

## API

- `POST /api/v1/auth/register` — реєстрація звичайного користувача.
- `POST /api/v1/auth/login` — вхід, повертає bearer token.
- `GET /api/v1/auth/me` — поточний користувач.
- `GET /api/v1/clones/backups/` — список власних копій (потрібен токен).
- `POST /api/v1/clones/backups/` — створити запис (потрібен токен).
- `GET /api/v1/clones/backups/{clone_identifier}` — отримати останній власний запис.
- `GET /api/v1/admin/users` — список користувачів (admin).
- `PATCH /api/v1/admin/users/{user_id}/role?role=admin|user` — зміна ролі (admin).
- `PATCH /api/v1/admin/users/{user_id}/active?is_active=true|false` — активувати/заблокувати (admin).

Для захищених маршрутів передавай заголовок `Authorization: Bearer <access_token>`.

## Архітектурні нотатки

- Паролі зберігаються як Argon2-хеші, не у відкритому вигляді.
- Токени — JWT із часом завершення дії. Поточна версія зберігає токен у `localStorage` для простоти навчального SPA; для production краще розглянути HttpOnly Secure cookies, CSRF-захист, ротацію/відкликання сесій і HTTPS.
- CORS origins задаються явно через `CORS_ORIGINS`; не використовуй wildcard для production.
- Перед production потрібні rate limiting для входу/реєстрації, аудит дій адміністратора, резервування БД і повноцінні інтеграційні тести.

## CI/CD

GitHub Actions запускає Ruff, Black та pytest при push і pull request у `main`.
