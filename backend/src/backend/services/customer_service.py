from fastapi import HTTPException, status
from backend.repositories.customer_repository import CustomerRepository
from backend.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    def __init__(self, conn):
        self.conn = conn
        self.repo = CustomerRepository(conn)

    def get_all(self):
        return self.repo.get_all()

    def get_by_id(self, customer_id: int):
        customer = self.repo.find_by_id(customer_id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        return customer

    def create(self, data: CustomerCreate):
        try:
            customer_id = self.repo.create(
                name=data.name,
                email=data.email,
                phone=data.phone,
                address=data.address
            )
            self.conn.commit()
            return self.repo.find_by_id(customer_id)
        except Exception as e:
            self.conn.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def update(self, customer_id: int, data: CustomerUpdate):
        self.get_by_id(customer_id)

        updates = {}
        if data.name is not None:
            updates["name"] = data.name
        if data.email is not None:
            updates["email"] = data.email
        if data.phone is not None:
            updates["phone"] = data.phone
        if data.address is not None:
            updates["address"] = data.address

        if updates:
            try:
                self.repo.update(customer_id, updates)
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        return self.repo.find_by_id(customer_id)

    def delete(self, customer_id: int):
        self.get_by_id(customer_id)
        try:
            self.repo.delete(customer_id)
            self.conn.commit()
            return {"message": "Customer deleted successfully"}
        except Exception as e:
            self.conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete customer because orders are associated with them"
            )
