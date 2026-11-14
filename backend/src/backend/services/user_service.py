from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from backend.repositories.user_repository import UserRepository
from backend.repositories.session_repository import SessionRepository
from backend.schemas.auth import UserRegister, UserLogin, ChangePasswordRequest
from backend.schemas.user import UserCreate, UserUpdate, UserRoleUpdate, UserStatusUpdate
from backend.config.settings import REFRESH_TOKEN_EXPIRE_DAYS
from backend.utils.security import (
    hash_password,
    verify_password,
    hash_token,
    create_access_token,
    create_refresh_token,
    decode_token
)


class UserService:
    def __init__(self, conn):
        self.conn = conn
        self.repo = UserRepository(conn)
        self.session_repo = SessionRepository(conn)

    def register(self, data: UserRegister):
        if self.repo.find_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered"
            )

        hashed = hash_password(data.password)
        # Strictly assign SALES_REP role for public registration
        user_id = self.repo.create(
            username=data.username,
            email=data.email,
            phone=data.phone,
            password_hash=hashed,
            role="SALES_REP"
        )
        return self.repo.find_by_id(user_id)

    def login(self, credentials: UserLogin):
        user = self.repo.find_by_username_or_email(credentials.username_or_email)
        if not user or not verify_password(credentials.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        session_id = self.session_repo.create(
            user_id=user["id"],
            refresh_token_hash="pending",
            expires_at=expires_at
        )

        access_token = create_access_token(user_id=user["id"], session_id=session_id, role=user["role"])
        refresh_token, ref_expires = create_refresh_token(user_id=user["id"], session_id=session_id, role=user["role"])
        self.session_repo.update_refresh_token(session_id, hash_token(refresh_token), ref_expires)

        user.pop("password_hash", None)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user
        }

    def refresh_access_token(self, refresh_token: str):
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is missing",
                headers={"WWW-Authenticate": "Bearer"}
            )

        payload = decode_token(refresh_token)
        if payload.get("token_type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"}
            )

        session_id = payload.get("session_id")
        user_id = payload.get("user_id")

        session = self.session_repo.find_by_id(session_id)
        if not session or session["is_revoked"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session has been revoked or expired",
                headers={"WWW-Authenticate": "Bearer"}
            )

        if hash_token(refresh_token) != session["refresh_token_hash"]:
            self.session_repo.revoke(session_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"}
            )

        user = self.repo.find_by_id(user_id)
        if not user or not user["is_active"]:
            self.session_repo.revoke(session_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User inactive or not found",
                headers={"WWW-Authenticate": "Bearer"}
            )

        new_access_token = create_access_token(user_id=user["id"], session_id=session_id, role=user["role"])
        new_refresh_token, new_expires = create_refresh_token(user_id=user["id"], session_id=session_id, role=user["role"])
        self.session_repo.update_refresh_token(session_id, hash_token(new_refresh_token), new_expires)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    def change_password(self, user_id: int, data: ChangePasswordRequest):
        user = self.get_user_by_id(user_id)
        if not verify_password(data.current_password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        new_hashed = hash_password(data.new_password)
        self.repo.update_password(user_id, new_hashed)

        # Invalidate all existing sessions for security
        self.session_repo.revoke_all_for_user(user_id)
        return {"message": "Password changed successfully. Please log in again."}

    def logout(self, session_id: str):
        if session_id:
            self.session_repo.revoke(session_id)

    def get_all_users(self):
        return self.repo.get_all()

    def get_user_by_id(self, user_id: int):
        user = self.repo.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def create_user_by_manager(self, data: UserCreate):
        if self.repo.find_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered"
            )

        hashed = hash_password(data.password)
        user_id = self.repo.create(
            username=data.username,
            email=data.email,
            phone=data.phone,
            password_hash=hashed,
            role=data.role.value if data.role else "SALES_REP"
        )
        return self.repo.find_by_id(user_id)

    def update_user(self, user_id: int, data: UserUpdate):
        self.get_user_by_id(user_id)

        updates = {}
        if data.email:
            if self.repo.find_by_email(data.email, exclude_id=user_id):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
            updates["email"] = data.email

        if data.username:
            updates["username"] = data.username
        if data.phone is not None:
            updates["phone"] = data.phone
        if data.password:
            updates["password_hash"] = hash_password(data.password)

        if updates:
            self.repo.update(user_id, updates)

        return self.repo.find_by_id(user_id)

    def update_role(self, user_id: int, data: UserRoleUpdate):
        self.get_user_by_id(user_id)
        self.repo.update_role(user_id, data.role.value)
        return self.repo.find_by_id(user_id)

    def update_status(self, user_id: int, data: UserStatusUpdate):
        self.get_user_by_id(user_id)
        self.repo.update_status(user_id, data.is_active)
        if not data.is_active:
            self.session_repo.revoke_all_for_user(user_id)
        return self.repo.find_by_id(user_id)
