# app/api/v1/home.py
from fastapi import APIRouter, Depends

from app.api.deps import get_current_admin, get_current_user
from app.models.user import User

router = APIRouter(prefix="/home", tags=["Home"])


@router.get("/user")
async def user_home(current_user: User = Depends(get_current_user)):
    return {"message": f"Welcome back, user {current_user.full_name}!"}


@router.get("/admin")
async def admin_home(current_user: User = Depends(get_current_admin)):
    return {"message": f"Welcome to the Admin Dashboard, {current_user.full_name}."}
