from typing import List
from fastapi import APIRouter, Depends, status
from backend.config.database import get_db
from backend.schemas.inventory import StockAdjustmentCreate, StockOut
from backend.handlers.inventory_handler import InventoryHandler
from backend.utils.security import get_current_user, require_role

router = APIRouter(prefix="/api/inventory", tags=["Inventory Management"])


@router.get("", response_model=List[StockOut])
def get_all_stock(
    conn=Depends(get_db),
    _user=Depends(get_current_user)
):
    return InventoryHandler(conn).get_all_stock()


@router.get("/low-stock", response_model=List[StockOut])
def get_low_stock(
    threshold: int = 10,
    conn=Depends(get_db),
    _user=Depends(get_current_user)
):
    return InventoryHandler(conn).get_low_stock(threshold)


@router.get("/{product_id}", response_model=StockOut)
def get_product_stock(
    product_id: int,
    conn=Depends(get_db),
    _user=Depends(get_current_user)
):
    return InventoryHandler(conn).get_product_stock(product_id)


@router.post("/adjustments", status_code=status.HTTP_200_OK)
def adjust_stock(
    data: StockAdjustmentCreate,
    conn=Depends(get_db),
    _manager=Depends(require_role("MANAGER"))
):
    return InventoryHandler(conn).adjust_stock(data)
