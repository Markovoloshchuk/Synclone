"""Профілі користувачів: свої дані (JWT) та контроль власності (IDOR)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import hash_password
from app.models.user import ROLE_ADMIN, User
from app.schemas import UserOut, UserUpdate

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)) -> User:
    """Дані поточного користувача; анонім або протермінований токен → 401."""
    return current_user


@router.patch("/{user_id}", response_model=UserOut)
def update_profile(
    user_id: int,
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """Оновлення профілю. Чужий профіль (IDOR) → 403, не 404."""
    target = db.get(User, user_id)
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if target.id != current_user.id and current_user.role != ROLE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot edit another user's profile",
        )
    if payload.email is not None and payload.email != target.email:
        taken = db.scalar(select(User).where(User.email == payload.email))
        if taken is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        target.email = payload.email
    if payload.password is not None:
        target.hashed_password = hash_password(payload.password)
    db.commit()
    db.refresh(target)
    return target
