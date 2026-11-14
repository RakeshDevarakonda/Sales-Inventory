from backend.repositories.dashboard_repository import DashboardRepository


class DashboardService:
    def __init__(self, conn):
        self.repo = DashboardRepository(conn)

    def get_stats(self):
        return self.repo.get_stats()
