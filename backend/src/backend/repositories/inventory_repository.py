class InventoryRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_all_stock(self):
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id AS product_id, sku, name, stock_quantity, is_active
                FROM products
                ORDER BY stock_quantity ASC
                """
            )
            return cursor.fetchall()

    def get_product_stock(self, product_id: int):
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id AS product_id, sku, name, stock_quantity, is_active
                FROM products
                WHERE id = %s
                """,
                (product_id,)
            )
            return cursor.fetchone()

    def get_low_stock(self, threshold: int = 10):
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id AS product_id, sku, name, stock_quantity, is_active
                FROM products
                WHERE stock_quantity <= %s AND is_active = TRUE
                ORDER BY stock_quantity ASC
                """,
                (threshold,)
            )
            return cursor.fetchall()

    def get_movements(self, limit: int = 100):
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, product_id, change_quantity, previous_stock, new_stock,
                       movement_type, reference_id, performed_by_id, notes, created_at
                FROM inventory_movements
                ORDER BY id DESC
                LIMIT %s
                """,
                (limit,)
            )
            return cursor.fetchall()

    def record_movement(self, product_id: int, change_quantity: int, previous_stock: int,
                        new_stock: int, movement_type: str, performed_by_id: int,
                        reference_id: str = None, notes: str = None) -> int:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO inventory_movements
                (product_id, change_quantity, previous_stock, new_stock, movement_type, reference_id, performed_by_id, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (product_id, change_quantity, previous_stock, new_stock, movement_type, reference_id, performed_by_id, notes)
            )
            movement_id = cursor.lastrowid
            self.conn.commit()
            return movement_id
