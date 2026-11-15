from fastapi import APIRouter, Depends
from backend.config.database import get_db
from backend.schemas.dashboard import DashboardStatsOut
from backend.handlers.dashboard_handler import DashboardHandler
from backend.utils.security import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard & Analytics"])


@router.get("/summary", response_model=DashboardStatsOut)
def get_dashboard_stats(
    conn=Depends(get_db),
    _user=Depends(get_current_user)
):
    return DashboardHandler(conn).get_stats()
