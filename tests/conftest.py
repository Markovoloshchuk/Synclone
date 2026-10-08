"""Фікстури pytest: тестова БД, TestClient, користувачі для сценаріїв доступу."""

import os
from pathlib import Path


def _load_test_database_url() -> str:
    """Бере DATABASE_URL із .env і переводить його на базу synclone_test.

    Пароль БД залишається поза репозиторієм — тести читають локальний .env.
    """
    base_url = "postgresql+psycopg2://synclone:password@localhost:5432/synclone"
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("DATABASE_URL="):
                base_url = line.split("=", 1)[1].strip()
    # Останній сегмент шляху — ім'я бази даних
    return base_url.rsplit("/", 1)[0] + "/synclone_test"


# Налаштування ТЕСТОВОГО середовища — ОБОВ'ЯЗКОВО до імпорту застосунку
TEST_DATABASE_URL = _load_test_database_url()
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["ADMIN_EMAIL"] = "admin@test.local"
os.environ["ADMIN_PASSWORD"] = "admin-test-pass1"
os.environ["JWT_SECRET"] = "test-secret-key-with-at-least-32-bytes-long!"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.engine import make_url  # noqa: E402


def _ensure_test_database() -> None:
    """Створює базу synclone_test, якщо її ще немає (підключення до postgres)."""
    import psycopg2

    url = make_url(TEST_DATABASE_URL)
    connection = psycopg2.connect(
        host=url.host,
        port=url.port or 5432,
        user=url.username,
        password=url.password,
        dbname="postgres",
    )
    connection.autocommit = True
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", ("synclone_test",)
        )
        if cursor.fetchone() is None:
            cursor.execute("CREATE DATABASE synclone_test")
    connection.close()


_ensure_test_database()

# Імпорт застосунку створює таблиці та сідить адміністратора в тестовій БД
from app.core.database import engine  # noqa: E402
from app.main import app, ensure_admin  # noqa: E402

PASSWORD = "password123"
ADMIN_EMAIL = "admin@test.local"
ADMIN_PASSWORD = "admin-test-pass1"


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_database():
    """Очищає таблиці перед кожним тестом і повертає адміністратора."""
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "TRUNCATE memory_backups, users RESTART IDENTITY CASCADE"
        )
    ensure_admin()
    yield


def register_user(client: TestClient, email: str, password: str = PASSWORD) -> dict:
    response = client.post(
        "/api/auth/register", json={"email": email, "password": password}
    )
    assert response.status_code == 201, response.text
    return response.json()


def auth_headers(client: TestClient, email: str, password: str = PASSWORD) -> dict:
    response = client.post(
        "/api/auth/login", json={"username": email, "password": password}
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_a(client: TestClient) -> dict:
    return register_user(client, "user-a@test.local")


@pytest.fixture
def user_b(client: TestClient) -> dict:
    return register_user(client, "user-b@test.local")


@pytest.fixture
def user_a_headers(client: TestClient, user_a: dict) -> dict:
    # залежність від user_a ГАРАНТУЄ реєстрацію перед логіном
    return auth_headers(client, "user-a@test.local")


@pytest.fixture
def user_b_headers(client: TestClient, user_b: dict) -> dict:
    return auth_headers(client, "user-b@test.local")


@pytest.fixture
def admin_headers(client: TestClient) -> dict:
    return auth_headers(client, ADMIN_EMAIL, ADMIN_PASSWORD)
