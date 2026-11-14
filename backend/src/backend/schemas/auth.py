import re
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, model_validator


class UserRole(str, Enum):
    SALES_REP = "SALES_REP"
    MANAGER = "MANAGER"


def validate_password_strength(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter (a-z)")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter (A-Z)")
    if not re.search(r"[0-9]", password):
        raise ValueError("Password must contain at least one digit (0-9)")
    return password


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)

    @model_validator(mode="after")
    def validate_passwords_and_defaults(self):
        validate_password_strength(self.password)

        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")

        if not self.username:
            self.username = self.email.split("@")[0]

        return self


class UserLogin(BaseModel):
    username_or_email: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    @model_validator(mode="after")
    def validate_passwords(self):
        validate_password_strength(self.new_password)
        if self.new_password != self.confirm_password:
            raise ValueError("New password and confirm password do not match")
        if self.current_password == self.new_password:
            raise ValueError("New password cannot be the same as current password")
        return self


class UserOut(BaseModel):
    id: int
    username: Optional[str] = None
    email: str
    phone: Optional[str] = None
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
