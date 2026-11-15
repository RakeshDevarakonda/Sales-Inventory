from typing import Optional, List, Dict, Any
from backend.repositories.base_repository import IBaseRepository


class CustomerRepository(IBaseRepository):
    def __init__(self, conn):
        self.conn = conn

    def find_by_id(self, customer_id: int) -> Optional[Dict[str, Any]]:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, email, phone, address, created_at, updated_at
                FROM customers
                WHERE id = %s
                """,
                (customer_id,)
            )
            return cursor.fetchone()

    def get_all(self):
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, email, phone, address, created_at, updated_at
                FROM customers
                ORDER BY id DESC
                """
            )
            return cursor.fetchall()

    def create(self, name: str, email: str, phone: str = None, address: str = None) -> int:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO customers (name, email, phone, address)
                VALUES (%s, %s, %s, %s)
                """,
                (name, email, phone, address)
            )
            return cursor.lastrowid

    def update(self, customer_id: int, updates: dict):
        if not updates:
            return
        fields = [f"{col} = %s" for col in updates.keys()]
        values = list(updates.values())
        values.append(customer_id)

        sql = f"UPDATE customers SET {', '.join(fields)} WHERE id = %s"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, tuple(values))

    def delete(self, customer_id: int):
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM customers WHERE id = %s", (customer_id,))
