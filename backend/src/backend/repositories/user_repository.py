class UserRepository:
    def __init__(self, conn):
        self.conn = conn

    def find_by_id(self, user_id: int):
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, username, email, phone, password_hash, role, is_active, created_at, updated_at
                FROM users
                WHERE id = %s
                """,
                (user_id,)
            )
            return cursor.fetchone()

    def find_by_email(self, email: str, exclude_id: int = None):
        with self.conn.cursor() as cursor:
            if exclude_id:
                cursor.execute(
                    "SELECT id, username, email FROM users WHERE email = %s AND id != %s",
                    (email, exclude_id)
                )
            else:
                cursor.execute(
                    "SELECT id, username, email FROM users WHERE email = %s",
                    (email,)
                )
            return cursor.fetchone()

    def find_by_username_or_email(self, identifier: str):
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, username, email, phone, password_hash, role, is_active, created_at, updated_at
                FROM users
                WHERE username = %s OR email = %s
                """,
                (identifier, identifier)
            )
            return cursor.fetchone()

    def get_all(self):
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, username, email, phone, role, is_active, created_at, updated_at
                FROM users
                ORDER BY id DESC
                """
            )
            return cursor.fetchall()

    def create(self, email: str, password_hash: str, username: str = None, phone: str = None, role: str = "SALES_REP") -> int:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (username, email, phone, password_hash, role)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (username, email, phone, password_hash, role)
            )
            user_id = cursor.lastrowid
            self.conn.commit()
            return user_id

    def update(self, user_id: int, updates: dict):
        if not updates:
            return
        fields = [f"{col} = %s" for col in updates.keys()]
        values = list(updates.values())
        values.append(user_id)

        sql = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, tuple(values))
            self.conn.commit()

    def update_role(self, user_id: int, role: str):
        with self.conn.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET role = %s WHERE id = %s",
                (role, user_id)
            )
            self.conn.commit()

    def update_status(self, user_id: int, is_active: bool):
        with self.conn.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET is_active = %s WHERE id = %s",
                (is_active, user_id)
            )
            self.conn.commit()

    def update_password(self, user_id: int, password_hash: str):
        with self.conn.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE id = %s",
                (password_hash, user_id)
            )
            self.conn.commit()
