from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import AdminUser, DbSession
from app.models.user import User
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/api/v1/admin", tags=["Administration"])


@router.get("/users", response_model=list[UserResponse])
async def list_users(_: AdminUser, db: DbSession):
    result = await db.scalars(select(User).order_by(User.created_at.desc()))
    return list(result.all())


@router.patch("/users/{user_id}/role", response_model=UserResponse)
async def change_role(user_id: int, role: str, admin: AdminUser, db: DbSession):
    if role not in {"admin", "user"}:
        raise HTTPException(status_code=422, detail="Role must be 'admin' or 'user'")
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id and role != "admin":
        raise HTTPException(
            status_code=400, detail="You cannot remove your own administrator role"
        )
    user.role = role
    await db.commit()
    await db.refresh(user)
    return user


@router.patch("/users/{user_id}/active", response_model=UserResponse)
async def change_active(user_id: int, is_active: bool, admin: AdminUser, db: DbSession):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id and not is_active:
        raise HTTPException(
            status_code=400, detail="You cannot deactivate your own account"
        )
    user.is_active = is_active
    await db.commit()
    await db.refresh(user)
    return user
