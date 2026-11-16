from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    sku: Optional[str] = Field(None, min_length=2, max_length=50)
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0)
    stock_quantity: int = Field(0, ge=0)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    stock_quantity: Optional[int] = Field(None, ge=0)


class ProductStatusUpdate(BaseModel):
    is_active: bool


class ProductOut(BaseModel):
    id: int
    sku: str
    name: str
    description: Optional[str] = None
    price: Decimal
    stock_quantity: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
