from typing import List, Optional, Union
from fastapi import APIRouter, Depends, Query, status
from backend.config.database import get_db
from backend.schemas.product import ProductCreate, ProductUpdate, ProductStatusUpdate, ProductOut
from backend.schemas.pagination import PaginatedResponse
from backend.handlers.product_handler import ProductHandler
from backend.utils.security import get_current_user, require_role

router = APIRouter(prefix="/api/products", tags=["Product Management"])


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate,
    conn=Depends(get_db),
    _manager=Depends(require_role("MANAGER"))
):
    return ProductHandler(conn).create(data)


@router.get("", response_model=Union[PaginatedResponse[ProductOut], List[ProductOut]])
def get_all_products(
    active_only: bool = False,
    page: Optional[int] = Query(None, ge=1, description="Page number"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Items per page"),
    conn=Depends(get_db),
    _user=Depends(get_current_user)
):
    return ProductHandler(conn).get_all(active_only=active_only, page=page, limit=limit)


@router.get("/{product_id}", response_model=ProductOut)
def get_product_by_id(
    product_id: int,
    conn=Depends(get_db),
    _user=Depends(get_current_user)
):
    return ProductHandler(conn).get_by_id(product_id)


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    data: ProductUpdate,
    conn=Depends(get_db),
    _manager=Depends(require_role("MANAGER"))
):
    return ProductHandler(conn).update(product_id, data)


@router.patch("/{product_id}/status", response_model=ProductOut)
def update_product_status(
    product_id: int,
    data: ProductStatusUpdate,
    conn=Depends(get_db),
    _manager=Depends(require_role("MANAGER"))
):
    return ProductHandler(conn).update_status(product_id, data)
