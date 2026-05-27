from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.stats import SettingsOut, SettingsUpdate
from app.services.settings_service import SettingsService


router = APIRouter(prefix="/users/me/settings", tags=["用户设置"])


@router.get("", response_model=SettingsOut)
def get_settings(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SettingsService(db).get_or_create(current.id)


@router.put("", response_model=SettingsOut)
def update_settings(
    payload: SettingsUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SettingsService(db).update(current.id, payload)
