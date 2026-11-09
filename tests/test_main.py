import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.core.security import hash_password, verify_password

TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_db"
TEST_JWT_SECRET_KEY = "test-only-secret-key-for-unit-tests"


def test_password_hash_is_not_plaintext():
    password = "a-long-test-password"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong-password", hashed)


def test_password_hash_is_salted():
    password = "a-long-test-password"
    assert hash_password(password) != hash_password(password)


def test_sandbox_allows_debug():
    settings = Settings(
        _env_file=None,
        APP_ENV="sandbox",
        DATABASE_URL=TEST_DATABASE_URL,
        JWT_SECRET_KEY=TEST_JWT_SECRET_KEY,
        DEBUG=True,
    )

    assert settings.APP_ENV == "sandbox"
    assert settings.DEBUG is True


def test_production_rejects_debug():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            APP_ENV="production",
            DATABASE_URL=TEST_DATABASE_URL,
            JWT_SECRET_KEY=TEST_JWT_SECRET_KEY,
            DEBUG=True,
        )


def test_production_allows_debug_disabled():
    settings = Settings(
        _env_file=None,
        APP_ENV="production",
        DATABASE_URL=TEST_DATABASE_URL,
        JWT_SECRET_KEY=TEST_JWT_SECRET_KEY,
        DEBUG=False,
    )

    assert settings.APP_ENV == "production"
    assert settings.DEBUG is False
