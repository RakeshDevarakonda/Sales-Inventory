from fastapi import HTTPException, Request, Response, status
from backend.config.settings import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from backend.schemas.auth import UserRegister, UserLogin, RefreshTokenRequest, ChangePasswordRequest
from backend.services.user_service import UserService


class AuthHandler:
    def __init__(self, conn):
        self.service = UserService(conn)

    def register(self, user_data: UserRegister):
        return self.service.register(user_data)

    def login(self, credentials: UserLogin, response: Response):
        result = self.service.login(credentials)

        # 1. Set short-lived Access Token in an HttpOnly cookie
        response.set_cookie(
            key="access_token",
            value=result["access_token"],
            httponly=True,
            samesite="lax",
            secure=False,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

        # 2. Set long-lived Refresh Token in an HttpOnly cookie
        response.set_cookie(
            key="refresh_token",
            value=result["refresh_token"],
            httponly=True,
            samesite="lax",
            secure=False,
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )

        return {
            "access_token": result["access_token"],
            "token_type": "bearer",
            "user": result["user"]
        }

    def refresh_token(self, request: Request, response: Response, body: RefreshTokenRequest = None):
        token = request.cookies.get("refresh_token")
        if not token and body and body.refresh_token:
            token = body.refresh_token

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is required"
            )

        result = self.service.refresh_access_token(token)

        # 1. Update access_token cookie
        response.set_cookie(
            key="access_token",
            value=result["access_token"],
            httponly=True,
            samesite="lax",
            secure=False,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

        # 2. Update rotated refresh_token cookie
        response.set_cookie(
            key="refresh_token",
            value=result["refresh_token"],
            httponly=True,
            samesite="lax",
            secure=False,
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )

        return {
            "access_token": result["access_token"],
            "token_type": "bearer"
        }

    def change_password(self, current_user: dict, data: ChangePasswordRequest, response: Response):
        result = self.service.change_password(current_user["id"], data)
        # Clear cookies since sessions are revoked
        response.delete_cookie(key="access_token", httponly=True, samesite="lax")
        response.delete_cookie(key="refresh_token", httponly=True, samesite="lax")
        return result

    def get_me(self, current_user: dict):
        return current_user

    def logout(self, response: Response, current_user: dict):
        self.service.logout(current_user.get("session_id"))

        response.delete_cookie(key="access_token", httponly=True, samesite="lax")
        response.delete_cookie(key="refresh_token", httponly=True, samesite="lax")

        return {"message": "Successfully logged out"}
