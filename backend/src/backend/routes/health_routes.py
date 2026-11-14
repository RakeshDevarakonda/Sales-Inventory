from fastapi import APIRouter, Depends, status
from backend.config.database import get_db
from backend.handlers.health_handler import HealthHandler

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", status_code=status.HTTP_200_OK)
def health_check(conn=Depends(get_db)):
    return HealthHandler(conn).check_health()
