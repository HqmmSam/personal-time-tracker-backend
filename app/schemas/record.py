from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


RecordType = Literal["auto", "manual"]


class RecordCreate(BaseModel):
    task_id: int
    duration: int = Field(gt=0, le=86400)  # 1 秒 ~ 24 小时
    record_date: date | None = None
    start_time: datetime | None = None
    type: RecordType = "auto"
    note: str | None = Field(default=None, max_length=500)


class RecordUpdate(BaseModel):
    duration: int | None = Field(default=None, gt=0, le=86400)
    record_date: date | None = None
    note: str | None = Field(default=None, max_length=500)


class RecordOut(BaseModel):
    id: int
    task_id: int
    record_date: date
    start_time: datetime | None
    duration: int
    type: RecordType
    note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RecordListItem(BaseModel):
    id: int
    task_id: int
    task_name: str
    project_id: int
    project_name: str
    project_color: str
    record_date: date
    start_time: datetime | None
    duration: int
    type: RecordType
    note: str | None
    created_at: datetime


class Pagination(BaseModel):
    page: int
    page_size: int
    total: int


class RecordListResponse(BaseModel):
    items: list[RecordListItem]
    pagination: Pagination
