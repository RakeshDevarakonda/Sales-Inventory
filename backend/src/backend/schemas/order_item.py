from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    created_at: datetime
    updated_at: datetime
