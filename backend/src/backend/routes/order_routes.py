from typing import List, Optional, Union
from fastapi import APIRouter, Depends, Query, BackgroundTasks, status
from backend.config.database import get_db
from backend.schemas.order import OrderCreate, OrderUpdate, OrderOut, OrderApprovalAction
from backend.schemas.pagination import PaginatedResponse
from backend.handlers.order_handler import OrderHandler
from backend.utils.security import get_current_user, require_role

router = APIRouter(prefix="/api/orders", tags=["Sales Order Management"])


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    data: OrderCreate,
    email_queue: BackgroundTasks,
    conn=Depends(get_db),
    current_user=Depends(get_current_user)
):
    return OrderHandler(conn).create(data, current_user, email_queue)


@router.get("", response_model=Union[PaginatedResponse[OrderOut], List[OrderOut]])
def get_orders(
    status: Optional[str] = Query(None, description="Filter by order status"),
    page: Optional[int] = Query(None, ge=1, description="Page number"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Items per page"),
    conn=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Managers retrieve all orders; Sales Reps retrieve only their own orders."""
    return OrderHandler(conn).get_orders(current_user, status=status, page=page, limit=limit)


@router.get("/my-orders", response_model=Union[PaginatedResponse[OrderOut], List[OrderOut]])
def get_my_orders(
    status: Optional[str] = Query(None, description="Filter by order status"),
    page: Optional[int] = Query(None, ge=1, description="Page number"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Items per page"),
    conn=Depends(get_db),
    current_user=Depends(get_current_user)
):
    return OrderHandler(conn).get_my_orders(current_user, status=status, page=page, limit=limit)


@router.get("/{order_id}", response_model=OrderOut)
def get_order_by_id(
    order_id: int,
    conn=Depends(get_db),
    current_user=Depends(get_current_user)
):
    return OrderHandler(conn).get_by_id(order_id, current_user)


@router.patch("/{order_id}", response_model=OrderOut)
def update_pending_order(
    order_id: int,
    data: OrderUpdate,
    conn=Depends(get_db),
    current_user=Depends(get_current_user)
):
    return OrderHandler(conn).update_pending(order_id, data, current_user)


@router.post("/{order_id}/cancel")
def cancel_order(
    order_id: int,
    conn=Depends(get_db),
    current_user=Depends(get_current_user)
):
    return OrderHandler(conn).cancel(order_id, current_user)


@router.post("/{order_id}/approve", response_model=OrderOut)
def approve_order(
    order_id: int,
    action: OrderApprovalAction,
    email_queue: BackgroundTasks,
    conn=Depends(get_db),
    manager_user=Depends(require_role("MANAGER"))
):
    return OrderHandler(conn).approve(order_id, action, manager_user, email_queue)


@router.post("/{order_id}/reject", response_model=OrderOut)
def reject_order(
    order_id: int,
    action: OrderApprovalAction,
    email_queue: BackgroundTasks,
    conn=Depends(get_db),
    manager_user=Depends(require_role("MANAGER"))
):
    return OrderHandler(conn).reject(order_id, action, manager_user, email_queue)
