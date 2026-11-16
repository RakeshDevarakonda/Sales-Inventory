from backend.repositories.dashboard_repository import DashboardRepository


class DashboardService:
    def __init__(self, conn):
        self.repo = DashboardRepository(conn)

    def get_stats(self, current_user: dict):
        user_id = None if current_user.get("role") == "MANAGER" else current_user.get("id")
        return self.repo.get_stats(user_id=user_id)
