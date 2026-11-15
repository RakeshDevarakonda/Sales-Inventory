import uuid
from datetime import datetime
from decimal import Decimal
from fastapi import BackgroundTasks, HTTPException, status
from backend.config.settings import APPROVAL_THRESHOLD_AMOUNT as APPROVAL_THRESHOLD
from backend.repositories.order_repository import OrderRepository
from backend.repositories.product_repository import ProductRepository
from backend.repositories.customer_repository import CustomerRepository
from backend.repositories.user_repository import UserRepository
from backend.repositories.settings_repository import SettingsRepository
from backend.schemas.order import OrderCreate, OrderUpdate, OrderApprovalAction
from backend.services.email_service import email_service


def generate_order_number() -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    suffix = uuid.uuid4().hex[:6].upper()
    return f"ORD-{timestamp}-{suffix}"


class OrderService:
    def __init__(
        self,
        conn,
        repo: OrderRepository = None,
        product_repo: ProductRepository = None,
        customer_repo: CustomerRepository = None,
        user_repo: UserRepository = None,
        settings_repo: SettingsRepository = None,
        notification_svc = None
    ):
        self.conn = conn
        self.repo = repo or OrderRepository(conn)
        self.product_repo = product_repo or ProductRepository(conn)
        self.customer_repo = customer_repo or CustomerRepository(conn)
        self.user_repo = user_repo or UserRepository(conn)
        self.settings_repo = settings_repo or SettingsRepository(conn)
        self.notification_svc = notification_svc or email_service

    def get_orders(self, current_user: dict):
        if current_user["role"] == "MANAGER":
            return self.repo.get_all()
        return self.repo.get_by_user_id(current_user["id"])

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

        # Sort product IDs to prevent deadlocks on concurrent orders touching the same products
        sorted_items = sorted(data.items, key=lambda x: x.product_id)

        try:
            total_amount = Decimal("0.00")
            validated_items = []

            # 1. Lock rows with FOR UPDATE to prevent concurrent overselling
            for item in sorted_items:
                product = self.product_repo.find_by_id_for_update(item.product_id)
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

            # Dynamic threshold (default ₹1000 from settings, or customized in DB by manager)
            current_threshold = self.settings_repo.get_approval_threshold()

            # Only Sales Rep orders over the threshold require Manager approval.
            # If a Manager places the order, it is directly CONFIRMED (no self-approval needed).
            is_manager = current_user.get("role") == "MANAGER"
            requires_approval = (total_amount > current_threshold) and (not is_manager)
            status_val = "PENDING_APPROVAL" if requires_approval else "CONFIRMED"

            order_number = generate_order_number()

            order_id = self.repo.create(
                order_number=order_number,
                customer_id=data.customer_id,
                created_by_id=current_user["id"],
                total_amount=total_amount,
                status=status_val
            )

            # Insert line items
            for val_item in validated_items:
                self.repo.add_order_item(
                    order_id=order_id,
                    product_id=val_item["product"]["id"],
                    quantity=val_item["quantity"],
                    unit_price=val_item["unit_price"],
                    subtotal=val_item["subtotal"]
                )

            # 2. Reserve stock under the exclusive lock
            for val_item in validated_items:
                prod = val_item["product"]
                new_stock = prod["stock_quantity"] - val_item["quantity"]
                self.product_repo.update_stock(prod["id"], new_stock)

            self.conn.commit()

            if requires_approval and email_queue:
                email_queue.add_task(
                    self.notification_svc.send_order_pending_approval_notice,
                    order_number=order_number,
                    total_amount=total_amount,
                    sales_rep_name=current_user.get("username", "Sales Rep")
                )

            return self.repo.get_by_id(order_id)

        except Exception:
            self.conn.rollback()
            raise

    def update_pending_order(self, order_id: int, data: OrderUpdate, current_user: dict):
        try:
            # Lock order row exclusively
            order = self.repo.get_by_id_for_update(order_id)
            if not order:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

            if order["status"] != "PENDING_APPROVAL":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Only orders in PENDING_APPROVAL status can be edited. Current status is {order['status']}."
                )

            if current_user["role"] != "MANAGER" and order["created_by_id"] != current_user["id"]:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

            # Collect ALL product IDs touched (both old items being restored and new items being added)
            # and sort them strictly to completely eliminate any deadlock risk across concurrent transactions
            all_product_ids = sorted(list(set(
                [item["product_id"] for item in order["items"]] +
                [item.product_id for item in data.items]
            )))

            # Acquire exclusive row locks for all affected products in deterministic ascending order
            locked_products = {}
            for pid in all_product_ids:
                locked_products[pid] = self.product_repo.find_by_id_for_update(pid)

            # 1. Release previously reserved stock to the locked in-memory products
            for old_item in order["items"]:
                prod = locked_products[old_item["product_id"]]
                prod["stock_quantity"] += old_item["quantity"]
                self.product_repo.update_stock(prod["id"], prod["stock_quantity"])

            # 2. Validate new items against updated locked products
            total_amount = Decimal("0.00")
            validated_items = []

            for item in data.items:
                product = locked_products.get(item.product_id)
                if not product or not product["is_active"]:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Product ID {item.product_id} is inactive or not found")

                if product["stock_quantity"] < item.quantity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Insufficient stock for '{product['name']}'. Available: {product['stock_quantity']}, requested: {item.quantity}"
                    )

                unit_price = Decimal(str(product["price"]))
                subtotal = unit_price * item.quantity
                total_amount += subtotal
                validated_items.append({"product": product, "quantity": item.quantity, "unit_price": unit_price, "subtotal": subtotal})

            # 3. Clear old items & insert new
            self.repo.clear_order_items(order_id)
            for val_item in validated_items:
                self.repo.add_order_item(
                    order_id=order_id,
                    product_id=val_item["product"]["id"],
                    quantity=val_item["quantity"],
                    unit_price=val_item["unit_price"],
                    subtotal=val_item["subtotal"]
                )

            # 4. Reserve stock for new items
            for val_item in validated_items:
                prod = val_item["product"]
                prod["stock_quantity"] -= val_item["quantity"]
                self.product_repo.update_stock(prod["id"], prod["stock_quantity"])

            # 5. Check threshold
            status_val = "PENDING_APPROVAL" if total_amount > APPROVAL_THRESHOLD else "CONFIRMED"
            self.repo.update_order_totals(order_id, total_amount, status_val)

            self.conn.commit()
            return self.repo.get_by_id(order_id)

        except Exception:
            self.conn.rollback()
            raise

    def cancel(self, order_id: int, current_user: dict):
        try:
            # Lock order row exclusively
            order = self.repo.get_by_id_for_update(order_id)
            if not order:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

            if current_user["role"] != "MANAGER" and order["created_by_id"] != current_user["id"]:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

            if order["status"] in ("CANCELLED", "REJECTED"):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Order is already {order['status']}")

            # Release reserved stock in deterministic sorted order
            if order["status"] in ("PENDING_APPROVAL", "CONFIRMED", "APPROVED"):
                sorted_items = sorted(order["items"], key=lambda x: x["product_id"])
                for item in sorted_items:
                    prod = self.product_repo.find_by_id_for_update(item["product_id"])
                    new_stock = prod["stock_quantity"] + item["quantity"]
                    self.product_repo.update_stock(prod["id"], new_stock)

            self.repo.update_status(order_id, "CANCELLED")
            self.conn.commit()
            return {"message": "Order cancelled successfully", "order_id": order_id}

        except Exception:
            self.conn.rollback()
            raise

    def approve_order(self, order_id: int, action: OrderApprovalAction, manager_user: dict, email_queue: BackgroundTasks = None):
        try:
            # Lock order row exclusively
            order = self.repo.get_by_id_for_update(order_id)
            if not order:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

            if order["status"] != "PENDING_APPROVAL":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Order is in '{order['status']}' state; only PENDING_APPROVAL orders can be approved."
                )

            # Stock was already reserved under lock during creation/update, finalize to APPROVED
            self.repo.update_status(order_id, "APPROVED", reviewed_by_id=manager_user["id"], notes=action.approval_notes)
            self.conn.commit()

            rep_user = self.user_repo.find_by_id(order["created_by_id"])
            if rep_user and email_queue:
                email_queue.add_task(
                    self.notification_svc.send_order_decision_notice,
                    sales_rep_email=rep_user["email"],
                    order_number=order["order_number"],
                    decision="APPROVED",
                    notes=action.approval_notes
                )

            return self.repo.get_by_id(order_id)

        except Exception:
            self.conn.rollback()
            raise

    def reject_order(self, order_id: int, action: OrderApprovalAction, manager_user: dict, email_queue: BackgroundTasks = None):
        try:
            # Lock order row exclusively
            order = self.repo.get_by_id_for_update(order_id)
            if not order:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

            if order["status"] != "PENDING_APPROVAL":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Order is in '{order['status']}' state; only PENDING_APPROVAL orders can be rejected."
                )

            # Release reserved stock back to products in deterministic sorted order
            sorted_items = sorted(order["items"], key=lambda x: x["product_id"])
            for item in sorted_items:
                prod = self.product_repo.find_by_id_for_update(item["product_id"])
                new_stock = prod["stock_quantity"] + item["quantity"]
                self.product_repo.update_stock(prod["id"], new_stock)

            self.repo.update_status(order_id, "REJECTED", reviewed_by_id=manager_user["id"], notes=action.approval_notes)
            self.conn.commit()

            rep_user = self.user_repo.find_by_id(order["created_by_id"])
            if rep_user and email_queue:
                email_queue.add_task(
                    self.notification_svc.send_order_decision_notice,
                    sales_rep_email=rep_user["email"],
                    order_number=order["order_number"],
                    decision="REJECTED",
                    notes=action.approval_notes
                )

            return self.repo.get_by_id(order_id)

        except Exception:
            self.conn.rollback()
            raise
