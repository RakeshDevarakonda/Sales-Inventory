class SessionRepository:
    def __init__(self, conn):
        self.conn = conn

    def create(self, user_id: int, refresh_token_hash: str, expires_at) -> str:
        """
        Inserts a new session letting MySQL generate the UUID via UUID(),
        and returns that exact session_id.
        """
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT UUID() AS new_uuid")
            session_id = cursor.fetchone()["new_uuid"]

            cursor.execute(
                """
                INSERT INTO sessions (id, user_id, refresh_token_hash, expires_at)
                VALUES (%s, %s, %s, %s)
                """,
                (session_id, user_id, refresh_token_hash, expires_at)
            )
            self.conn.commit()
            return session_id

    def find_by_id(self, session_id: str):
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, user_id, refresh_token_hash, is_revoked, expires_at, created_at
                FROM sessions
                WHERE id = %s
                """,
                (session_id,)
            )
            return cursor.fetchone()

    def update_refresh_token(self, session_id: str, new_hash: str, new_expires_at):
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE sessions
                SET refresh_token_hash = %s, expires_at = %s
                WHERE id = %s
                """,
                (new_hash, new_expires_at, session_id)
            )
            self.conn.commit()

    def revoke(self, session_id: str):
        with self.conn.cursor() as cursor:
            cursor.execute(
                "UPDATE sessions SET is_revoked = TRUE WHERE id = %s",
                (session_id,)
            )
            self.conn.commit()

    def revoke_all_for_user(self, user_id: int):
        with self.conn.cursor() as cursor:
            cursor.execute(
                "UPDATE sessions SET is_revoked = TRUE WHERE user_id = %s",
                (user_id,)
            )
            self.conn.commit()
