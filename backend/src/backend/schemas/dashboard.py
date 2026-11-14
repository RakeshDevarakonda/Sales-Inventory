from decimal import Decimal
from typing import List
from pydantic import BaseModel
from backend.schemas.order import OrderOut


class DashboardStatsOut(BaseModel):
    total_revenue: Decimal
    total_orders_count: int
    pending_approvals_count: int
    confirmed_orders_count: int
    approved_orders_count: int
    rejected_orders_count: int
    total_products_count: int
    low_stock_products_count: int
    total_customers_count: int
    recent_orders: List[OrderOut] = []
