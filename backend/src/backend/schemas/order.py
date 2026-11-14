from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    CONFIRMED = "CONFIRMED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItemCreate] = Field(..., min_length=1)


class OrderUpdate(BaseModel):
    items: List[OrderItemCreate] = Field(..., min_length=1)


class OrderApprovalAction(BaseModel):
    approval_notes: Optional[str] = None


class OrderOut(BaseModel):
    id: int
    order_number: str
    customer_id: int
    customer_name: Optional[str] = None
    created_by_id: int
    created_by_username: Optional[str] = None
    total_amount: Decimal
    status: OrderStatus
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    approval_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: Optional[List[OrderItemOut]] = []
