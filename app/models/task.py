from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey, Index, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    project_id = Column(BigInteger, ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    note = Column(Text, nullable=True)
    status = Column(
        Enum("active", "completed", "archived", name="task_status"),
        nullable=False,
        default="active",
    )
    sort_order = Column(BigInteger, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="tasks")
    records = relationship("TimeRecord", back_populates="task", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_project_deleted", "project_id", "deleted_at"),
    )
