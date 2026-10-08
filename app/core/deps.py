"""Залежності FastAPI: поточний користувач (401) та перевірка ролей (403)."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import PyJWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

# auto_error=False: відсутність токена обробляємо самі — саме 401, не 403
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Дістає користувача з JWT-заголовка; без токена/з помилкою → 401."""
    unauthorized_headers = {"WWW-Authenticate": "Bearer"}
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers=unauthorized_headers,
        )
    try:
        payload = decode_access_token(credentials.credentials)
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers=unauthorized_headers,
        )
    user = db.get(User, int(payload["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated",
            headers=unauthorized_headers,
        )
    return user


def require_role(*roles: str):
    """Фабрика dependency: користувач НЕ в дозволених ролях → 403."""

    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return checker


# Готова залежність для адмін-маршрутів
admin_required = require_role("admin")
