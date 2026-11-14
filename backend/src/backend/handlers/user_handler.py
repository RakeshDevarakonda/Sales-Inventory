from backend.schemas.user import UserCreate, UserUpdate, UserRoleUpdate, UserStatusUpdate
from backend.services.user_service import UserService


class UserHandler:
    def __init__(self, conn):
        self.service = UserService(conn)

    def create_user(self, user_data: UserCreate):
        return self.service.create_user_by_manager(user_data)

    def get_all_users(self):
        return self.service.get_all_users()

    def get_user_by_id(self, user_id: int):
        return self.service.get_user_by_id(user_id)

    def update_user(self, user_id: int, update_data: UserUpdate):
        return self.service.update_user(user_id, update_data)

    def update_user_role(self, user_id: int, role_data: UserRoleUpdate):
        return self.service.update_role(user_id, role_data)

    def update_user_status(self, user_id: int, status_data: UserStatusUpdate):
        return self.service.update_status(user_id, status_data)
