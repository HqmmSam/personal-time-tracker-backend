from sqlalchemy import Column, BigInteger, Integer, Boolean, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    daily_goal_minutes = Column(Integer, nullable=False, default=240)
    dark_mode = Column(Boolean, nullable=False, default=False)
    timezone = Column(String(50), nullable=False, default="Asia/Shanghai")
    week_start = Column(Integer, nullable=False, default=1)  # 0=Sunday, 1=Monday
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
