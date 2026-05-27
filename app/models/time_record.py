from sqlalchemy import Column, BigInteger, String, Text, Date, DateTime, ForeignKey, Integer, Index, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class TimeRecord(Base):
    __tablename__ = "time_records"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    task_id = Column(BigInteger, ForeignKey("tasks.id"), nullable=False, index=True)
    record_date = Column(Date, nullable=False, index=True)
    start_time = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=False)  # seconds
    type = Column(
        Enum("auto", "manual", name="record_type"),
        nullable=False,
        default="auto",
    )
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    task = relationship("Task", back_populates="records")

    __table_args__ = (
        Index("idx_user_date", "user_id", "record_date"),
    )
