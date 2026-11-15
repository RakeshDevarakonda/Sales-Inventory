from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from backend.config.database import get_db
from backend.repositories.settings_repository import SettingsRepository
from backend.utils.security import get_current_user, require_role

router = APIRouter(prefix="/api/settings", tags=["System Settings"])


class ThresholdUpdate(BaseModel):
    approval_threshold: Decimal = Field(..., gt=0, description="Minimum order amount requiring manager review")


class ThresholdOut(BaseModel):
    approval_threshold: Decimal


@router.get("/threshold", response_model=ThresholdOut)
def get_approval_threshold(
    conn=Depends(get_db),
    _user=Depends(get_current_user)
):
    threshold = SettingsRepository(conn).get_approval_threshold()
    return {"approval_threshold": threshold}


@router.patch("/threshold", response_model=ThresholdOut)
def update_approval_threshold(
    data: ThresholdUpdate,
    conn=Depends(get_db),
    manager_user=Depends(require_role("MANAGER"))
):
    updated = SettingsRepository(conn).set_approval_threshold(data.approval_threshold, manager_user["id"])
    return {"approval_threshold": updated}
