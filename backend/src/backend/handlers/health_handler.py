from fastapi import HTTPException, status


class HealthHandler:
    def __init__(self, conn):
        self.conn = conn

    def check_health(self):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT 1 AS status")
                result = cursor.fetchone()
            return {
                "status": "healthy",
                "database_connected": bool(result and result.get("status") == 1)
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database unreachable: {str(e)}"
            )
