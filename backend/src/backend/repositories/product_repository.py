from typing import Optional, List, Dict, Any
from backend.repositories.base_repository import IBaseRepository


class ProductRepository(IBaseRepository):
    def __init__(self, conn):
        self.conn = conn

    def find_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, sku, name, description, price, stock_quantity, is_active, created_at, updated_at
                FROM products
                WHERE id = %s
                """,
                (product_id,)
            )
            return cursor.fetchone()

    def find_by_id_for_update(self, product_id: int):
        """Acquires an exclusive row lock on the product row to prevent concurrent overselling."""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, sku, name, description, price, stock_quantity, is_active, created_at, updated_at
                FROM products
                WHERE id = %s
                FOR UPDATE
                """,
                (product_id,)
            )
            return cursor.fetchone()

    def find_by_sku(self, sku: str, exclude_id: int = None):
        with self.conn.cursor() as cursor:
            if exclude_id:
                cursor.execute(
                    "SELECT id FROM products WHERE sku = %s AND id != %s",
                    (sku, exclude_id)
                )
            else:
                cursor.execute("SELECT id FROM products WHERE sku = %s", (sku,))
            return cursor.fetchone()

    def get_all(self):
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, sku, name, description, price, stock_quantity, is_active, created_at, updated_at
                FROM products
                ORDER BY id DESC
                """
            )
            return cursor.fetchall()

    def create(self, sku: str, name: str, description: str, price, stock_quantity: int) -> int:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO products (sku, name, description, price, stock_quantity)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (sku, name, description, price, stock_quantity)
            )
            return cursor.lastrowid

    def update(self, product_id: int, updates: dict):
        if not updates:
            return
        fields = [f"{col} = %s" for col in updates.keys()]
        values = list(updates.values())
        values.append(product_id)

        sql = f"UPDATE products SET {', '.join(fields)} WHERE id = %s"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, tuple(values))

    def update_status(self, product_id: int, is_active: bool):
        with self.conn.cursor() as cursor:
            cursor.execute(
                "UPDATE products SET is_active = %s WHERE id = %s",
                (is_active, product_id)
            )

    def update_stock(self, product_id: int, new_stock: int):
        with self.conn.cursor() as cursor:
            cursor.execute(
                "UPDATE products SET stock_quantity = %s WHERE id = %s",
                (new_stock, product_id)
            )
