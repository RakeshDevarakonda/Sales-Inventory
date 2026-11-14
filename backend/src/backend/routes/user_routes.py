from typing import List
from fastapi import APIRouter, Depends, status
from backend.config.database import get_db
from backend.schemas.user import UserCreate, UserUpdate, UserRoleUpdate, UserStatusUpdate
from backend.schemas.auth import UserOut
from backend.handlers.user_handler import UserHandler
from backend.utils.security import require_role

router = APIRouter(prefix="/api/users", tags=["User Management"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    conn=Depends(get_db),
    _manager=Depends(require_role("MANAGER"))
):
    return UserHandler(conn).create_user(user_data)


@router.get("", response_model=List[UserOut])
def get_all_users(
    conn=Depends(get_db),
    _manager=Depends(require_role("MANAGER"))
):
    return UserHandler(conn).get_all_users()


@router.get("/{user_id}", response_model=UserOut)
def get_user_by_id(
    user_id: int,
    conn=Depends(get_db),
    _manager=Depends(require_role("MANAGER"))
):
    return UserHandler(conn).get_user_by_id(user_id)


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    update_data: UserUpdate,
    conn=Depends(get_db),
    _manager=Depends(require_role("MANAGER"))
):
    return UserHandler(conn).update_user(user_id, update_data)


@router.patch("/{user_id}/role", response_model=UserOut)
def update_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    conn=Depends(get_db),
    _manager=Depends(require_role("MANAGER"))
):
    return UserHandler(conn).update_user_role(user_id, role_data)


@router.patch("/{user_id}/status", response_model=UserOut)
def update_user_status(
    user_id: int,
    status_data: UserStatusUpdate,
    conn=Depends(get_db),
    _manager=Depends(require_role("MANAGER"))
):
    return UserHandler(conn).update_user_status(user_id, status_data)
