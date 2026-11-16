from backend.services.dashboard_service import DashboardService


class DashboardHandler:
    def __init__(self, conn):
        self.service = DashboardService(conn)

    def get_stats(self, current_user: dict):
        return self.service.get_stats(current_user)
