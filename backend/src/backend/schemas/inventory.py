from pydantic import BaseModel, Field


class StockAdjustmentCreate(BaseModel):
    product_id: int
    change_quantity: int = Field(..., description="Positive for addition, negative for reduction")


class StockOut(BaseModel):
    product_id: int
    sku: str
    name: str
    stock_quantity: int
    is_active: bool
