from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field


class MovementType(str, Enum):
    ORDER_FULFILLMENT = "ORDER_FULFILLMENT"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    MANUAL_ADJUSTMENT = "MANUAL_ADJUSTMENT"
    RESTOCK = "RESTOCK"


class StockAdjustmentCreate(BaseModel):
    product_id: int
    change_quantity: int = Field(..., description="Positive for addition, negative for reduction")
    movement_type: MovementType = MovementType.MANUAL_ADJUSTMENT
    notes: Optional[str] = None


class InventoryMovementOut(BaseModel):
    id: int
    product_id: int
    change_quantity: int
    previous_stock: int
    new_stock: int
    movement_type: MovementType
    reference_id: Optional[str] = None
    performed_by_id: int
    notes: Optional[str] = None
    created_at: datetime


class StockOut(BaseModel):
    product_id: int
    sku: str
    name: str
    stock_quantity: int
    is_active: bool
