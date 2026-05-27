from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


TaskStatus = Literal["active", "completed", "archived"]


class TaskCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    note: str | None = Field(default=None, max_length=2000)
    status: TaskStatus = "active"


class TaskUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    note: str | None = Field(default=None, max_length=2000)
    status: TaskStatus | None = None
    sort_order: int | None = None


class TaskOut(BaseModel):
    id: int
    project_id: int
    name: str
    note: str | None
    status: TaskStatus
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
