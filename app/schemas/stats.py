from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


RangeType = Literal["today", "week", "month"]


class OverviewOut(BaseModel):
    range: str
    total_seconds: int
    record_count: int
    average_session_minutes: float
    longest_session_minutes: float
    streak_days: int


class DailyItem(BaseModel):
    date: date
    total_seconds: int
    record_count: int


class DailyResponse(BaseModel):
    items: list[DailyItem]


class ProjectStatItem(BaseModel):
    project_id: int
    project_name: str
    color: str
    total_seconds: int
    percentage: float


class ProjectStatResponse(BaseModel):
    items: list[ProjectStatItem]
    total_seconds: int


class HourItem(BaseModel):
    hour: int
    total_seconds: int


class HourResponse(BaseModel):
    items: list[HourItem]


class NextWeekPrediction(BaseModel):
    predicted_hours: float
    confidence: float
    method: str
    based_on_weeks: int
    historical_average_hours: float
    trend: Literal["up", "down", "stable"]
    insufficient_data: bool


class GoalPrediction(BaseModel):
    period: str
    goal_minutes: int
    completed_minutes: int
    remaining_minutes: int
    remaining_days: int
    required_daily_minutes: int
    predicted_completion_rate: float
    is_likely_to_complete: bool


class SettingsOut(BaseModel):
    daily_goal_minutes: int
    dark_mode: bool
    timezone: str
    week_start: int

    model_config = {"from_attributes": True}


class SettingsUpdate(BaseModel):
    daily_goal_minutes: int | None = Field(default=None, ge=0, le=1440)
    dark_mode: bool | None = None
    timezone: str | None = Field(default=None, max_length=50)
    week_start: int | None = Field(default=None, ge=0, le=6)
