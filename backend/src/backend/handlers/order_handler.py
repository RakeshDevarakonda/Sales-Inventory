from fastapi import BackgroundTasks
from backend.schemas.order import OrderCreate, OrderUpdate, OrderApprovalAction
from backend.services.order_service import OrderService


class OrderHandler:
    def __init__(self, conn):
        self.service = OrderService(conn)

    def create(self, data: OrderCreate, current_user: dict, email_queue: BackgroundTasks = None):
        return self.service.create(data, current_user, email_queue)

    def get_all(self):
        return self.service.get_all()

    def get_my_orders(self, current_user: dict):
        return self.service.get_my_orders(current_user["id"])

    def get_by_id(self, order_id: int, current_user: dict):
        return self.service.get_by_id(order_id, current_user)

    def update_pending(self, order_id: int, data: OrderUpdate, current_user: dict):
        return self.service.update_pending_order(order_id, data, current_user)

    def cancel(self, order_id: int, current_user: dict):
        return self.service.cancel(order_id, current_user)

    def approve(self, order_id: int, action: OrderApprovalAction, manager_user: dict, email_queue: BackgroundTasks = None):
        return self.service.approve_order(order_id, action, manager_user, email_queue)

    def reject(self, order_id: int, action: OrderApprovalAction, manager_user: dict, email_queue: BackgroundTasks = None):
        return self.service.reject_order(order_id, action, manager_user, email_queue)
