from backend.schemas.product import ProductCreate, ProductUpdate, ProductStatusUpdate
from backend.services.product_service import ProductService


class ProductHandler:
    def __init__(self, conn):
        self.service = ProductService(conn)

    def create(self, data: ProductCreate):
        return self.service.create(data)

    def get_all(self, active_only: bool = False, page: int = None, limit: int = None):
        return self.service.get_all(active_only=active_only, page=page, limit=limit)

    def get_by_id(self, product_id: int):
        return self.service.get_by_id(product_id)

    def update(self, product_id: int, data: ProductUpdate):
        return self.service.update(product_id, data)

    def update_status(self, product_id: int, data: ProductStatusUpdate):
        return self.service.update_status(product_id, data)
