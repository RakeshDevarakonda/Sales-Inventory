import re
import uuid
from fastapi import HTTPException, status
from backend.repositories.product_repository import ProductRepository
from backend.schemas.product import ProductCreate, ProductUpdate, ProductStatusUpdate


def generate_sku(name: str) -> str:
    """Generate a clean, standardized, unique SKU on the server side."""
    # Take first 3-4 alphanumeric characters of the product name as prefix
    cleaned = re.sub(r"[^A-Za-z0-9]", "", name).upper()
    prefix = cleaned[:4] if len(cleaned) >= 3 else "PROD"
    suffix = uuid.uuid4().hex[:6].upper()
    return f"{prefix}-{suffix}"


class ProductService:
    def __init__(self, conn):
        self.conn = conn
        self.repo = ProductRepository(conn)

    def get_all(self, active_only: bool = False, page: int = None, limit: int = None):
        res = self.repo.get_all(active_only=active_only, page=page, limit=limit)
        if isinstance(res, dict):
            total = res["total"]
            total_pages = (total + limit - 1) // limit if limit else 1
            return {
                "items": res["items"],
                "total": total,
                "page": page or 1,
                "limit": limit or total,
                "total_pages": total_pages,
            }
        return res

    def get_by_id(self, product_id: int):
        product = self.repo.find_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product

    def create(self, data: ProductCreate):
        # Auto-generate unique SKU strictly on the server side
        sku = None
        for _ in range(10):
            candidate = generate_sku(data.name)
            if not self.repo.find_by_sku(candidate):
                sku = candidate
                break
        if not sku:
            sku = f"PROD-{uuid.uuid4().hex[:8].upper()}"

        try:
            product_id = self.repo.create(
                sku=sku,
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
