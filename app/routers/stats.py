from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.stats import (
    OverviewOut,
    DailyResponse,
    ProjectStatResponse,
    HourResponse,
)
from app.services.stats_service import StatsService


router = APIRouter(prefix="/stats", tags=["统计"])


@router.get("/overview", response_model=OverviewOut)
def overview(
    range: Literal["today", "week", "month"] = "week",
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return StatsService(db).overview(current.id, range)


@router.get("/daily", response_model=DailyResponse)
def daily(
    days: int = Query(7, ge=1, le=90),
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = StatsService(db).daily(current.id, days)
    return DailyResponse(items=items)


@router.get("/by-project", response_model=ProjectStatResponse)
def by_project(
    range: Literal["today", "week", "month"] = "week",
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return StatsService(db).by_project(current.id, range)


@router.get("/by-hour", response_model=HourResponse)
def by_hour(
    range: Literal["today", "week", "month"] = "week",
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = StatsService(db).by_hour(current.id, range)
    return HourResponse(items=items)
