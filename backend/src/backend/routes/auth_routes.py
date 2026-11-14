from fastapi import APIRouter, Depends, Request, Response, status
from backend.config.database import get_db
from backend.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserOut,
    RefreshTokenRequest,
    ChangePasswordRequest
)
from backend.handlers.auth_handler import AuthHandler
from backend.utils.security import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, conn=Depends(get_db)):
    return AuthHandler(conn).register(user_data)


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, response: Response, conn=Depends(get_db)):
    return AuthHandler(conn).login(credentials, response)


@router.post("/logout")
def logout(response: Response, current_user=Depends(get_current_user), conn=Depends(get_db)):
    return AuthHandler(conn).logout(response, current_user)


@router.get("/me", response_model=UserOut)
def get_me(current_user=Depends(get_current_user), conn=Depends(get_db)):
    return AuthHandler(conn).get_me(current_user)


@router.post("/refresh")
def refresh_token(request: Request, response: Response, body: RefreshTokenRequest = None, conn=Depends(get_db)):
    return AuthHandler(conn).refresh_token(request, response, body)


@router.patch("/change-password")
def change_password(
    data: ChangePasswordRequest,
    response: Response,
    current_user=Depends(get_current_user),
    conn=Depends(get_db)
):
    return AuthHandler(conn).change_password(current_user, data, response)
