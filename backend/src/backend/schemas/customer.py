from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., pattern=r"^\d{10}$", description="10-digit mobile number")
    address: str = Field(..., min_length=1)


class CustomerUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., pattern=r"^\d{10}$", description="10-digit mobile number")
    address: str = Field(..., min_length=1)


class CustomerOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    address: str
    created_at: datetime
    updated_at: datetime
