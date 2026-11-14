from typing import Optional
from pydantic import BaseModel, EmailStr, Field, model_validator
from backend.schemas.auth import UserRole, UserOut, validate_password_strength


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[UserRole] = UserRole.SALES_REP

    @model_validator(mode="after")
    def validate_and_defaults(self):
        validate_password_strength(self.password)
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        if not self.username:
            self.username = self.email.split("@")[0]
        return self


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    password: Optional[str] = None

    @model_validator(mode="after")
    def validate_password_if_present(self):
        if self.password:
            validate_password_strength(self.password)
        return self


class UserRoleUpdate(BaseModel):
    role: UserRole


class UserStatusUpdate(BaseModel):
    is_active: bool
