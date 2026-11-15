from backend.schemas.customer import CustomerCreate, CustomerUpdate
from backend.services.customer_service import CustomerService


class CustomerHandler:
    def __init__(self, conn):
        self.service = CustomerService(conn)

    def create_customer(self, customer_data: CustomerCreate):
        return self.service.create(customer_data)

    def get_all_customers(self, page: int = None, limit: int = None):
        return self.service.get_all(page=page, limit=limit)

    def get_customer_by_id(self, customer_id: int):
        return self.service.get_by_id(customer_id)

    def update_customer(self, customer_id: int, customer_data: CustomerUpdate):
        return self.service.update(customer_id, customer_data)

    def delete_customer(self, customer_id: int):
        return self.service.delete(customer_id)
