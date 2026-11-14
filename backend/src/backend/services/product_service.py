from fastapi import HTTPException, status
from backend.repositories.product_repository import ProductRepository
from backend.schemas.product import ProductCreate, ProductUpdate, ProductStatusUpdate


class ProductService:
    def __init__(self, conn):
        self.conn = conn
        self.repo = ProductRepository(conn)

    def get_all(self):
        return self.repo.get_all()

    def get_by_id(self, product_id: int):
        product = self.repo.find_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product

    def create(self, data: ProductCreate):
        if self.repo.find_by_sku(data.sku):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with SKU '{data.sku}' already exists"
            )
        try:
            product_id = self.repo.create(
                sku=data.sku,
                name=data.name,
                description=data.description,
                price=data.price,
                stock_quantity=data.stock_quantity
            )
            self.conn.commit()
            return self.repo.find_by_id(product_id)
        except Exception as e:
            self.conn.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def update(self, product_id: int, data: ProductUpdate):
        self.get_by_id(product_id)

        updates = {}
        if data.name is not None:
            updates["name"] = data.name
        if data.description is not None:
            updates["description"] = data.description
        if data.price is not None:
            updates["price"] = data.price
        if data.stock_quantity is not None:
            updates["stock_quantity"] = data.stock_quantity

        if updates:
            try:
                self.repo.update(product_id, updates)
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        return self.repo.find_by_id(product_id)

    def update_status(self, product_id: int, data: ProductStatusUpdate):
        self.get_by_id(product_id)
        try:
            self.repo.update_status(product_id, data.is_active)
            self.conn.commit()
            return self.repo.find_by_id(product_id)
        except Exception as e:
            self.conn.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
