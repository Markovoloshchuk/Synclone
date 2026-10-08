"""Хешування паролів (bcrypt) та створення/перевірка JWT."""

from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from app.core.config import settings

# bcrypt — сольований хеш; у БД зберігається ЛИШЕ хеш, ніколи — пароль
password_hash = PasswordHash([BcryptHasher()])


def hash_password(password: str) -> str:
    """Повертає bcrypt-хеш пароля (з унікальною сіллю)."""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Перевіряє пароль проти хеша; False замість винятку на битий хеш."""
    try:
        return password_hash.verify(plain_password, hashed_password)
    except ValueError:
        return False


def create_access_token(*, user_id: int, role: str) -> str:
    """Створює підписаний JWT з терміном дії jwt_expire_minutes."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """Декодує JWT; кидає jwt.PyJWTError при протермінні чи підробці."""
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
