from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    LoginResponse,
    UserOut,
)
from app.services.auth_service import AuthService
from app.utils.security import create_access_token


router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = AuthService(db).register(payload)
    token, expires_in = create_access_token(user.id, user.email)
    return LoginResponse(
        user=UserOut.model_validate(user),
        token=token,
        expires_in=expires_in,
    )


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = AuthService(db).authenticate(payload.email, payload.password)
    token, expires_in = create_access_token(user.id, user.email)
    return LoginResponse(
        user=UserOut.model_validate(user),
        token=token,
        expires_in=expires_in,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current: User = Depends(get_current_user)):
    # JWT 无状态，前端清掉 token 即可（生产环境可接 Redis 黑名单）
    return None


@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return current
