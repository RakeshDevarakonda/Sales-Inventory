from decimal import Decimal


class DashboardRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_stats(self):
        with self.conn.cursor() as cursor:
            # 1. Total revenue from completed/confirmed/approved orders
            cursor.execute(
                """
                SELECT COALESCE(SUM(total_amount), 0.00) AS total_revenue
                FROM orders
                WHERE status IN ('CONFIRMED', 'APPROVED')
                """
            )
            total_revenue = cursor.fetchone()["total_revenue"]

            # 2. Order counts breakdown
            cursor.execute(
                """
                SELECT
                    COUNT(1) AS total_orders,
                    SUM(CASE WHEN status = 'PENDING_APPROVAL' THEN 1 ELSE 0 END) AS pending_approvals,
                    SUM(CASE WHEN status = 'CONFIRMED' THEN 1 ELSE 0 END) AS confirmed_orders,
                    SUM(CASE WHEN status = 'APPROVED' THEN 1 ELSE 0 END) AS approved_orders,
                    SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) AS rejected_orders
                FROM orders
                """
            )
            order_counts = cursor.fetchone()

            # 3. Product & stock counts
            cursor.execute(
                """
                SELECT
                    COUNT(1) AS total_products,
                    SUM(CASE WHEN stock_quantity <= 10 THEN 1 ELSE 0 END) AS low_stock_products
                FROM products
                WHERE is_active = TRUE
                """
            )
            product_counts = cursor.fetchone()

            # 4. Customer counts
            cursor.execute("SELECT COUNT(1) AS total_customers FROM customers")
            total_customers = cursor.fetchone()["total_customers"]

            # 5. Recent 5 orders
            cursor.execute(
                """
                SELECT o.id, o.order_number, o.customer_id, c.name AS customer_name,
                       o.created_by_id, u.username AS created_by_username,
                       o.total_amount, o.status, o.reviewed_by_id, o.reviewed_at,
                       o.approval_notes, o.created_at, o.updated_at
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                JOIN users u ON o.created_by_id = u.id
                ORDER BY o.id DESC
                LIMIT 5
                """
            )
            recent_orders = cursor.fetchall()

            return {
                "total_revenue": Decimal(str(total_revenue)),
                "total_orders_count": order_counts["total_orders"] or 0,
                "pending_approvals_count": order_counts["pending_approvals"] or 0,
                "confirmed_orders_count": order_counts["confirmed_orders"] or 0,
                "approved_orders_count": order_counts["approved_orders"] or 0,
                "rejected_orders_count": order_counts["rejected_orders"] or 0,
                "total_products_count": product_counts["total_products"] or 0,
                "low_stock_products_count": product_counts["low_stock_products"] or 0,
                "total_customers_count": total_customers or 0,
                "recent_orders": recent_orders
            }
