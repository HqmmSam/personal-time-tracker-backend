from sqlalchemy import Column, BigInteger, String, Text, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(7), nullable=False, default="#3b82f6")
    description = Column(Text, nullable=True)
    due_date = Column(Date, nullable=True)
    sort_order = Column(BigInteger, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_user_deleted", "user_id", "deleted_at"),
    )
