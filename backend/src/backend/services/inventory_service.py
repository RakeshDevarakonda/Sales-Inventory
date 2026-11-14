from fastapi import HTTPException, status
from backend.repositories.inventory_repository import InventoryRepository
from backend.repositories.product_repository import ProductRepository
from backend.schemas.inventory import StockAdjustmentCreate


class InventoryService:
    def __init__(self, conn):
        self.conn = conn
        self.repo = InventoryRepository(conn)
        self.product_repo = ProductRepository(conn)

    def get_all_stock(self):
        return self.repo.get_all_stock()

    def get_product_stock(self, product_id: int):
        stock = self.repo.get_product_stock(product_id)
        if not stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return stock

    def get_low_stock(self, threshold: int = 10):
        return self.repo.get_low_stock(threshold)

    def adjust_stock(self, data: StockAdjustmentCreate):
        product = self.product_repo.find_by_id(data.product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        current_stock = product["stock_quantity"]
        new_stock = current_stock + data.change_quantity

        if new_stock < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot reduce stock below 0. Current stock is {current_stock}."
            )

        try:
            self.product_repo.update_stock(data.product_id, new_stock)
            self.conn.commit()
            return {
                "product_id": data.product_id,
                "previous_stock": current_stock,
                "change_quantity": data.change_quantity,
                "new_stock": new_stock
            }
        except Exception as e:
            self.conn.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
