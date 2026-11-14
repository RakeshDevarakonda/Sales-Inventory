from backend.schemas.inventory import StockAdjustmentCreate
from backend.services.inventory_service import InventoryService


class InventoryHandler:
    def __init__(self, conn):
        self.service = InventoryService(conn)

    def get_all_stock(self):
        return self.service.get_all_stock()

    def get_product_stock(self, product_id: int):
        return self.service.get_product_stock(product_id)

    def get_low_stock(self, threshold: int = 10):
        return self.service.get_low_stock(threshold)

    def adjust_stock(self, data: StockAdjustmentCreate):
        return self.service.adjust_stock(data)
