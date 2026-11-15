from decimal import Decimal
from typing import Optional
from backend.config.settings import APPROVAL_THRESHOLD_AMOUNT


class SettingsRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_approval_threshold(self) -> Decimal:
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT setting_value FROM system_settings WHERE setting_key = 'APPROVAL_THRESHOLD_AMOUNT'"
            )
            row = cursor.fetchone()
            if row and row["setting_value"]:
                return Decimal(str(row["setting_value"]))
            return APPROVAL_THRESHOLD_AMOUNT

    def set_approval_threshold(self, amount: Decimal, updated_by_id: int) -> Decimal:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO system_settings (setting_key, setting_value, description, updated_by_id)
                VALUES ('APPROVAL_THRESHOLD_AMOUNT', %s, 'Order approval threshold limit', %s)
                ON DUPLICATE KEY UPDATE
                    setting_value = VALUES(setting_value),
                    updated_by_id = VALUES(updated_by_id),
                    updated_at = CURRENT_TIMESTAMP
                """,
                (str(amount), updated_by_id)
            )
        self.conn.commit()
        return amount
