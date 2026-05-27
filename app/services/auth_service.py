from datetime import datetime

from sqlalchemy.orm import Session

from app.exceptions import BusinessException
from app.models.user import User
from app.models.user_settings import UserSettings
from app.schemas.auth import RegisterRequest, UpdateProfileRequest
from app.utils.security import hash_password, verify_password


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, payload: RegisterRequest) -> User:
        email = payload.email.lower().strip()
        existing = self.db.query(User).filter(User.email == email).first()
        if existing:
            raise BusinessException("EMAIL_ALREADY_EXISTS", "邮箱已被注册", 409)

        user = User(
            email=email,
            password_hash=hash_password(payload.password),
            nickname=payload.nickname or email.split("@")[0],
        )
        self.db.add(user)
        self.db.flush()  # 拿到 user.id

        # 级联创建默认设置
        settings = UserSettings(user_id=user.id)
        self.db.add(settings)

        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> User:
        user = (
            self.db.query(User)
            .filter(User.email == email.lower().strip(), User.deleted_at.is_(None))
            .first()
        )
        if not user or not verify_password(password, user.password_hash):
            # 防账号枚举：邮箱不存在与密码错误使用相同响应
            raise BusinessException("INVALID_CREDENTIALS", "邮箱或密码错误", 401)
        if not user.is_active:
            raise BusinessException("ACCOUNT_DISABLED", "账号已停用", 403)
        return user

    def update_profile(self, user: User, payload: UpdateProfileRequest) -> User:
        data = payload.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(user, k, v)
        self.db.commit()
        self.db.refresh(user)
        return user

    def change_password(self, user: User, old_password: str, new_password: str) -> None:
        if not verify_password(old_password, user.password_hash):
            raise BusinessException("INVALID_OLD_PASSWORD", "原密码错误", 422)
        if old_password == new_password:
            raise BusinessException("SAME_PASSWORD", "新密码不能与原密码相同", 422)
        user.password_hash = hash_password(new_password)
        self.db.commit()

    def soft_delete(self, user: User) -> None:
        user.deleted_at = datetime.utcnow()
        user.email = f"deleted_{user.id}_{user.email}"[:100]
        user.is_active = False
        self.db.commit()
