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
