# Synclone

Навчальний проєкт керування метаданими резервних копій із FastAPI, PostgreSQL та окремим React frontend.

## Функціональність

- Реєстрація користувача через email і пароль.
- Вхід із видачею JWT access token.
- Ролі `admin` і `user`; публічна реєстрація завжди створює роль `user`.
- Початковий адміністратор створюється при першому запуску API зі змінних `INITIAL_ADMIN_*`.
- Адміністратор переглядає користувачів, змінює ролі та активність.
- Користувач бачить і створює лише власні записи резервних копій.
- Окремий React frontend: `http://localhost:5173`.
- Swagger: `http://localhost:8000/docs`.

> Поточна реалізація зберігає метадані й хеш, а не сам файл/вміст резервної копії. Статус `synced` означає, що запис прийнято API, а не те, що вміст перевірено або відновлено.

## Запуск через Docker

1. Скопіюй `.env.example` у `.env`.
2. Заміни `POSTGRES_PASSWORD`, `DATABASE_URL` (пароль у URI має відповідати `POSTGRES_PASSWORD`), `JWT_SECRET_KEY` на випадковий секрет і `INITIAL_ADMIN_PASSWORD` на унікальний пароль довжиною щонайменше 12 символів.
3. Запусти:

   ```bash
   docker compose up --build
   ```

4. Відкрий frontend: http://localhost:5173
5. Увійди з `INITIAL_ADMIN_EMAIL` і `INITIAL_ADMIN_PASSWORD`.
6. Створи звичайного користувача через форму реєстрації.

Приклад генерації секрету JWT у Linux/macOS:

```bash
openssl rand -hex 32
```

### Важливо про зміну пароля PostgreSQL

Якщо раніше вже створювався Docker volume `postgres_data`, зміна змінних `POSTGRES_*` не змінює пароль у вже ініціалізованій БД. Для локального тестового середовища, якщо дані не потрібні, можна видалити volume командою `docker compose down -v`, після чого `docker compose up --build`. Увага: `down -v` видаляє дані БД.

## Запуск backend локально

Потрібен Python 3.11+ і доступний PostgreSQL. Створи віртуальне середовище, встанови `requirements.txt`, налаштуй `.env`, потім:

```bash
uvicorn app.main:app --reload
```

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
- Таблиці створюються на старті через `Base.metadata.create_all` для простоти навчального проєкту. Для production слід додати Alembic-міграції.
- Потрібно налаштувати rate limiting для входу/реєстрації, політику паролів, аудит дій адміністратора, резервування БД і повноцінні інтеграційні тести перед production.
- Frontend очікує API на `http://localhost:8000`; для іншого розміщення задай `VITE_API_URL` під час збірки frontend.
