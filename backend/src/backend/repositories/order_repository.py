class OrderRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_all(self):
        with self.conn.cursor() as cursor:
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
                """
            )
            return cursor.fetchall()

    def get_by_user_id(self, user_id: int):
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT o.id, o.order_number, o.customer_id, c.name AS customer_name,
                       o.created_by_id, u.username AS created_by_username,
                       o.total_amount, o.status, o.reviewed_by_id, o.reviewed_at,
                       o.approval_notes, o.created_at, o.updated_at
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                JOIN users u ON o.created_by_id = u.id
                WHERE o.created_by_id = %s
                ORDER BY o.id DESC
                """,
                (user_id,)
            )
            return cursor.fetchall()

    def get_by_id(self, order_id: int):
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT o.id, o.order_number, o.customer_id, c.name AS customer_name,
                       o.created_by_id, u.username AS created_by_username,
                       o.total_amount, o.status, o.reviewed_by_id, o.reviewed_at,
                       o.approval_notes, o.created_at, o.updated_at
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                JOIN users u ON o.created_by_id = u.id
                WHERE o.id = %s
                """,
                (order_id,)
            )
            order = cursor.fetchone()
            if not order:
                return None

            cursor.execute(
                """
                SELECT oi.id, oi.product_id, p.name AS product_name, p.sku AS product_sku,
                       oi.quantity, oi.unit_price, oi.subtotal
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = %s
                """,
                (order_id,)
            )
            order["items"] = cursor.fetchall()
            return order

    def create(self, order_number: str, customer_id: int, created_by_id: int, total_amount, status: str) -> int:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO orders (order_number, customer_id, created_by_id, total_amount, status)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (order_number, customer_id, created_by_id, total_amount, status)
            )
            order_id = cursor.lastrowid
            return order_id

    def add_order_item(self, order_id: int, product_id: int, quantity: int, unit_price, subtotal):
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (order_id, product_id, quantity, unit_price, subtotal)
            )

    def clear_order_items(self, order_id: int):
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))

    def update_order_totals(self, order_id: int, total_amount, status: str):
        with self.conn.cursor() as cursor:
            cursor.execute(
                "UPDATE orders SET total_amount = %s, status = %s WHERE id = %s",
                (total_amount, status, order_id)
            )

    def update_status(self, order_id: int, status: str, reviewed_by_id: int = None, notes: str = None):
        with self.conn.cursor() as cursor:
            if reviewed_by_id:
                cursor.execute(
                    """
                    UPDATE orders
                    SET status = %s, reviewed_by_id = %s, approval_notes = %s, reviewed_at = NOW()
                    WHERE id = %s
                    """,
                    (status, reviewed_by_id, notes, order_id)
                )
            else:
                cursor.execute(
                    "UPDATE orders SET status = %s WHERE id = %s",
                    (status, order_id)
                )
            self.conn.commit()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()
