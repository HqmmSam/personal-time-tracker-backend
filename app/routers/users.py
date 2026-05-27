from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.auth import UpdateProfileRequest, ChangePasswordRequest, UserOut
from app.services.auth_service import AuthService


router = APIRouter(prefix="/users", tags=["用户"])


@router.put("/me", response_model=UserOut)
def update_me(
    payload: UpdateProfileRequest,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AuthService(db).update_profile(current, payload)


@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: ChangePasswordRequest,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    AuthService(db).change_password(current, payload.old_password, payload.new_password)
    return None


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    AuthService(db).soft_delete(current)
    return None
