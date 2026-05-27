from datetime import date, timedelta
from typing import Literal

from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.task import Task
from app.models.time_record import TimeRecord
from app.schemas.stats import DailyItem, ProjectStatItem, HourItem


def _range_to_dates(range_: Literal["today", "week", "month"]) -> tuple[date, date]:
    today = date.today()
    if range_ == "today":
        return today, today
    if range_ == "week":
        return today - timedelta(days=today.weekday()), today
    if range_ == "month":
        return today.replace(day=1), today
    return today, today


class StatsService:
    def __init__(self, db: Session):
        self.db = db

    def overview(self, user_id: int, range_: str) -> dict:
        start, end = _range_to_dates(range_)
        row = (
            self.db.query(
                func.coalesce(func.sum(TimeRecord.duration), 0).label("total_seconds"),
                func.count(TimeRecord.id).label("record_count"),
                func.coalesce(func.avg(TimeRecord.duration), 0).label("avg_duration"),
                func.coalesce(func.max(TimeRecord.duration), 0).label("max_duration"),
            )
            .filter(
                TimeRecord.user_id == user_id,
                TimeRecord.record_date >= start,
                TimeRecord.record_date <= end,
            )
            .one()
        )
        # 连续天数：从今天往前找连续有记录的天数
        streak = self._streak_days(user_id)
        return {
            "range": range_,
            "total_seconds": int(row.total_seconds),
            "record_count": int(row.record_count),
            "average_session_minutes": round(float(row.avg_duration) / 60, 1),
            "longest_session_minutes": round(float(row.max_duration) / 60, 1),
            "streak_days": streak,
        }

    def _streak_days(self, user_id: int) -> int:
        rows = (
            self.db.query(TimeRecord.record_date)
            .filter(TimeRecord.user_id == user_id)
            .distinct()
            .all()
        )
        dates = {r.record_date for r in rows}
        if not dates:
            return 0
        streak = 0
        cur = date.today()
        while cur in dates:
            streak += 1
            cur -= timedelta(days=1)
        return streak

    def daily(self, user_id: int, days: int = 7) -> list[DailyItem]:
        end = date.today()
        start = end - timedelta(days=days - 1)
        rows = (
            self.db.query(
                TimeRecord.record_date,
                func.sum(TimeRecord.duration).label("total"),
                func.count(TimeRecord.id).label("cnt"),
            )
            .filter(
                TimeRecord.user_id == user_id,
                TimeRecord.record_date >= start,
                TimeRecord.record_date <= end,
            )
            .group_by(TimeRecord.record_date)
            .all()
        )
        data = {r.record_date: (int(r.total), int(r.cnt)) for r in rows}
        result = []
        for i in range(days):
            d = start + timedelta(days=i)
            total, cnt = data.get(d, (0, 0))
            result.append(DailyItem(date=d, total_seconds=total, record_count=cnt))
        return result

    def by_project(self, user_id: int, range_: str) -> dict:
        start, end = _range_to_dates(range_)
        rows = (
            self.db.query(
                Project.id,
                Project.name,
                Project.color,
                func.sum(TimeRecord.duration).label("total"),
            )
            .join(Task, Task.project_id == Project.id)
            .join(TimeRecord, TimeRecord.task_id == Task.id)
            .filter(
                TimeRecord.user_id == user_id,
                TimeRecord.record_date >= start,
                TimeRecord.record_date <= end,
                Project.deleted_at.is_(None),
            )
            .group_by(Project.id, Project.name, Project.color)
            .order_by(func.sum(TimeRecord.duration).desc())
            .all()
        )
        total = sum(int(r.total) for r in rows) or 1
        items = [
            ProjectStatItem(
                project_id=r.id,
                project_name=r.name,
                color=r.color,
                total_seconds=int(r.total),
                percentage=round(int(r.total) * 100 / total, 1),
            )
            for r in rows
        ]
        return {"items": items, "total_seconds": int(total) if rows else 0}

    def by_hour(self, user_id: int, range_: str) -> list[HourItem]:
        start, end = _range_to_dates(range_)
        rows = (
            self.db.query(
                extract("hour", TimeRecord.start_time).label("hour"),
                func.sum(TimeRecord.duration).label("total"),
            )
            .filter(
                TimeRecord.user_id == user_id,
                TimeRecord.record_date >= start,
                TimeRecord.record_date <= end,
                TimeRecord.start_time.isnot(None),
            )
            .group_by("hour")
            .all()
        )
        data = {int(r.hour): int(r.total) for r in rows if r.hour is not None}
        return [HourItem(hour=h, total_seconds=data.get(h, 0)) for h in range(24)]
