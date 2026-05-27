from datetime import datetime, timedelta, timezone

import bcrypt as _bcrypt
from jose import jwt

from app.config import settings


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")[:72]
    return _bcrypt.hashpw(password_bytes, _bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    plain_bytes = plain.encode("utf-8")[:72]
    hashed_bytes = hashed.encode("utf-8") if isinstance(hashed, str) else hashed
    return _bcrypt.checkpw(plain_bytes, hashed_bytes)


def create_access_token(user_id: int, email: str) -> tuple[str, int]:
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expires,
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, settings.jwt_expire_minutes * 60


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
