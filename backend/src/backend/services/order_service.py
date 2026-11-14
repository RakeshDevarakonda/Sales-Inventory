from decimal import Decimal
from fastapi import BackgroundTasks, HTTPException, status
from backend.config.settings import APPROVAL_THRESHOLD_AMOUNT as APPROVAL_THRESHOLD
from backend.repositories.order_repository import OrderRepository
from backend.repositories.product_repository import ProductRepository
from backend.repositories.customer_repository import CustomerRepository
from backend.repositories.user_repository import UserRepository
from backend.schemas.order import OrderCreate, OrderUpdate, OrderApprovalAction
from backend.services.email_service import email_service


class OrderService:
    def __init__(self, conn):
        self.conn = conn
        self.repo = OrderRepository(conn)
        self.product_repo = ProductRepository(conn)
        self.customer_repo = CustomerRepository(conn)
        self.user_repo = UserRepository(conn)

    def get_all(self):
        return self.repo.get_all()

    def get_my_orders(self, user_id: int):
        return self.repo.get_by_user_id(user_id)

    def get_by_id(self, order_id: int, current_user: dict):
        order = self.repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        if current_user["role"] != "MANAGER" and order["created_by_id"] != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        return order

    def create(self, data: OrderCreate, current_user: dict, email_queue: BackgroundTasks = None):
        customer = self.customer_repo.find_by_id(data.customer_id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        total_amount = Decimal("0.00")
        validated_items = []

        for item in data.items:
            product = self.product_repo.find_by_id(item.product_id)
            if not product or not product["is_active"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product ID {item.product_id} is inactive or not found"
                )

            if product["stock_quantity"] < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for '{product['name']}'. Available: {product['stock_quantity']}, requested: {item.quantity}"
                )

            unit_price = Decimal(str(product["price"]))
            subtotal = unit_price * item.quantity
            total_amount += subtotal

            validated_items.append({
                "product": product,
                "quantity": item.quantity,
                "unit_price": unit_price,
                "subtotal": subtotal
            })

        requires_approval = total_amount > APPROVAL_THRESHOLD
        status_val = "PENDING_APPROVAL" if requires_approval else "CONFIRMED"

        try:
            import time
            order_number = f"ORD-{int(time.time())}"

            order_id = self.repo.create(
                order_number=order_number,
                customer_id=data.customer_id,
                created_by_id=current_user["id"],
                total_amount=total_amount,
                status=status_val
            )

            for val_item in validated_items:
                self.repo.add_order_item(
                    order_id=order_id,
                    product_id=val_item["product"]["id"],
                    quantity=val_item["quantity"],
                    unit_price=val_item["unit_price"],
                    subtotal=val_item["subtotal"]
                )

            if status_val == "CONFIRMED":
                for val_item in validated_items:
                    prod = val_item["product"]
                    new_stock = prod["stock_quantity"] - val_item["quantity"]
                    self.product_repo.update_stock(prod["id"], new_stock)

            self.conn.commit()

            if requires_approval and email_queue:
                email_queue.add_task(
                    email_service.send_order_pending_approval_notice,
                    order_number=order_number,
                    total_amount=total_amount,
                    sales_rep_name=current_user.get("username", "Sales Rep")
                )

            return self.repo.get_by_id(order_id)

        except Exception as e:
            self.conn.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to place order: {str(e)}")

    def update_pending_order(self, order_id: int, data: OrderUpdate, current_user: dict):
        order = self.repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        if order["status"] != "PENDING_APPROVAL":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only orders in PENDING_APPROVAL status can be edited. Current status is {order['status']}."
            )

        if current_user["role"] != "MANAGER" and order["created_by_id"] != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        total_amount = Decimal("0.00")
        validated_items = []

        for item in data.items:
            product = self.product_repo.find_by_id(item.product_id)
            if not product or not product["is_active"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Product ID {item.product_id} is inactive or not found")

            if product["stock_quantity"] < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for '{product['name']}'. Available: {product['stock_quantity']}"
                )

            unit_price = Decimal(str(product["price"]))
            subtotal = unit_price * item.quantity
            total_amount += subtotal
            validated_items.append({"product": product, "quantity": item.quantity, "unit_price": unit_price, "subtotal": subtotal})

        try:
            self.repo.clear_order_items(order_id)
            for val_item in validated_items:
                self.repo.add_order_item(
                    order_id=order_id,
                    product_id=val_item["product"]["id"],
                    quantity=val_item["quantity"],
                    unit_price=val_item["unit_price"],
                    subtotal=val_item["subtotal"]
                )

            status_val = "PENDING_APPROVAL" if total_amount > APPROVAL_THRESHOLD else "CONFIRMED"
            self.repo.update_order_totals(order_id, total_amount, status_val)
            self.conn.commit()
            return self.repo.get_by_id(order_id)
        except Exception as e:
            self.conn.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def cancel(self, order_id: int, current_user: dict):
        order = self.repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        if current_user["role"] != "MANAGER" and order["created_by_id"] != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        if order["status"] in ("CANCELLED", "REJECTED"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Order is already {order['status']}")

        try:
            if order["status"] in ("CONFIRMED", "APPROVED"):
                for item in order["items"]:
                    prod = self.product_repo.find_by_id(item["product_id"])
                    new_stock = prod["stock_quantity"] + item["quantity"]
                    self.product_repo.update_stock(prod["id"], new_stock)

            self.repo.update_status(order_id, "CANCELLED")
            self.conn.commit()
            return {"message": "Order cancelled successfully", "order_id": order_id}
        except Exception as e:
            self.conn.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def approve_order(self, order_id: int, action: OrderApprovalAction, manager_user: dict, email_queue: BackgroundTasks = None):
        order = self.repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        if order["status"] != "PENDING_APPROVAL":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order is in '{order['status']}' state; only PENDING_APPROVAL orders can be approved."
            )

        try:
            for item in order["items"]:
                prod = self.product_repo.find_by_id(item["product_id"])
                if prod["stock_quantity"] < item["quantity"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Cannot approve order: '{prod['name']}' has insufficient stock ({prod['stock_quantity']} remaining)."
                    )
                new_stock = prod["stock_quantity"] - item["quantity"]
                self.product_repo.update_stock(prod["id"], new_stock)

            self.repo.update_status(order_id, "APPROVED", reviewed_by_id=manager_user["id"], notes=action.approval_notes)
            self.conn.commit()

            rep_user = self.user_repo.find_by_id(order["created_by_id"])
            if rep_user and email_queue:
                email_queue.add_task(
                    email_service.send_order_decision_notice,
                    sales_rep_email=rep_user["email"],
                    order_number=order["order_number"],
                    decision="APPROVED",
                    notes=action.approval_notes
                )

            return self.repo.get_by_id(order_id)
        except Exception as e:
            self.conn.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def reject_order(self, order_id: int, action: OrderApprovalAction, manager_user: dict, email_queue: BackgroundTasks = None):
        order = self.repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        if order["status"] != "PENDING_APPROVAL":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order is in '{order['status']}' state; only PENDING_APPROVAL orders can be rejected."
            )

        try:
            self.repo.update_status(order_id, "REJECTED", reviewed_by_id=manager_user["id"], notes=action.approval_notes)
            self.conn.commit()

            rep_user = self.user_repo.find_by_id(order["created_by_id"])
            if rep_user and email_queue:
                email_queue.add_task(
                    email_service.send_order_decision_notice,
                    sales_rep_email=rep_user["email"],
                    order_number=order["order_number"],
                    decision="REJECTED",
                    notes=action.approval_notes
                )

            return self.repo.get_by_id(order_id)
        except Exception as e:
            self.conn.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
