from typing import List
from fastapi import APIRouter, Depends, status
from backend.config.database import get_db
from backend.schemas.customer import CustomerCreate, CustomerUpdate, CustomerOut
from backend.handlers.customer_handler import CustomerHandler
from backend.utils.security import get_current_user

router = APIRouter(prefix="/api/customers", tags=["Customers"])


@router.post("", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(
    customer_data: CustomerCreate,
    conn=Depends(get_db),
    _user=Depends(get_current_user)
):
    return CustomerHandler(conn).create_customer(customer_data)


@router.get("", response_model=List[CustomerOut])
def get_all_customers(
    conn=Depends(get_db),
    _user=Depends(get_current_user)
):
    return CustomerHandler(conn).get_all_customers()


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer_by_id(
    customer_id: int,
    conn=Depends(get_db),
    _user=Depends(get_current_user)
):
    return CustomerHandler(conn).get_customer_by_id(customer_id)


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    conn=Depends(get_db),
    _user=Depends(get_current_user)
):
    return CustomerHandler(conn).update_customer(customer_id, customer_data)


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    conn=Depends(get_db),
    _user=Depends(get_current_user)
):
    return CustomerHandler(conn).delete_customer(customer_id)
