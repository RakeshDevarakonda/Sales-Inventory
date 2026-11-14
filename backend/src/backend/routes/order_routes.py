from typing import List
from fastapi import APIRouter, Depends, BackgroundTasks, status
from backend.config.database import get_db
from backend.schemas.order import OrderCreate, OrderUpdate, OrderOut, OrderApprovalAction
from backend.handlers.order_handler import OrderHandler
from backend.utils.security import get_current_user, require_role

router = APIRouter(prefix="/api/orders", tags=["Sales Order Management"])


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    data: OrderCreate,
    background_tasks: BackgroundTasks,
    conn=Depends(get_db),
    current_user=Depends(get_current_user)
):
    return OrderHandler(conn).create(data, current_user, background_tasks)


@router.get("", response_model=List[OrderOut])
def get_all_orders(
    conn=Depends(get_db),
    _user=Depends(get_current_user)
):
    return OrderHandler(conn).get_all()


@router.get("/my-orders", response_model=List[OrderOut])
def get_my_orders(
    conn=Depends(get_db),
    current_user=Depends(get_current_user)
):
    return OrderHandler(conn).get_my_orders(current_user)


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
    background_tasks: BackgroundTasks,
    conn=Depends(get_db),
    manager_user=Depends(require_role("MANAGER"))
):
    return OrderHandler(conn).approve(order_id, action, manager_user, background_tasks)


@router.post("/{order_id}/reject", response_model=OrderOut)
def reject_order(
    order_id: int,
    action: OrderApprovalAction,
    background_tasks: BackgroundTasks,
    conn=Depends(get_db),
    manager_user=Depends(require_role("MANAGER"))
):
    return OrderHandler(conn).reject(order_id, action, manager_user, background_tasks)
