from datetime import date, timedelta
from statistics import mean, stdev

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.time_record import TimeRecord
from app.models.user_settings import UserSettings


class PredictionService:
    def __init__(self, db: Session):
        self.db = db

    def next_week_hours(self, user_id: int) -> dict:
        today = date.today()
        weeks = []
        for i in range(4):
            week_end = today - timedelta(days=i * 7)
            week_start = week_end - timedelta(days=6)
            total = (
                self.db.query(func.coalesce(func.sum(TimeRecord.duration), 0))
                .filter(
                    TimeRecord.user_id == user_id,
                    TimeRecord.record_date >= week_start,
                    TimeRecord.record_date <= week_end,
                )
                .scalar()
            )
            weeks.append(int(total) / 3600)

        if all(w == 0 for w in weeks):
            return {
                "predicted_hours": 0.0,
                "confidence": 0.0,
                "method": "moving_average_4w",
                "based_on_weeks": 4,
                "historical_average_hours": 0.0,
                "trend": "stable",
                "insufficient_data": True,
            }

        weights = [0.4, 0.3, 0.2, 0.1]
        predicted = sum(w * v for w, v in zip(weights, weeks))
        avg = mean(weeks)

        recent = mean(weeks[:2])
        prev = mean(weeks[2:])
        if recent > prev * 1.1:
            trend = "up"
        elif recent < prev * 0.9:
            trend = "down"
        else:
            trend = "stable"

        try:
            sd = stdev(weeks)
            confidence = max(0.0, min(1.0, 1 - sd / (avg + 0.001)))
        except Exception:
            confidence = 0.5

        return {
            "predicted_hours": round(predicted, 1),
            "confidence": round(confidence, 2),
            "method": "moving_average_4w",
            "based_on_weeks": 4,
            "historical_average_hours": round(avg, 1),
            "trend": trend,
            "insufficient_data": False,
        }

    def goal_completion(self, user_id: int) -> dict:
        settings = (
            self.db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        )
        daily_goal_minutes = settings.daily_goal_minutes if settings else 240

        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        days_passed = (today - week_start).days + 1
        days_remaining = 7 - days_passed

        completed_seconds = (
            self.db.query(func.coalesce(func.sum(TimeRecord.duration), 0))
            .filter(
                TimeRecord.user_id == user_id,
                TimeRecord.record_date >= week_start,
                TimeRecord.record_date <= today,
            )
            .scalar()
        ) or 0
        completed_minutes = int(completed_seconds) // 60

        goal_minutes = daily_goal_minutes * 7
        remaining = max(0, goal_minutes - completed_minutes)
        required_daily = (
            remaining // max(1, days_remaining) if days_remaining > 0 else remaining
        )
        avg_daily = completed_minutes / days_passed if days_passed else 0
        predicted_total = avg_daily * 7
        predicted_rate = min(1.0, predicted_total / goal_minutes) if goal_minutes else 0

        return {
            "period": "this_week",
            "goal_minutes": goal_minutes,
            "completed_minutes": int(completed_minutes),
            "remaining_minutes": int(remaining),
            "remaining_days": days_remaining,
            "required_daily_minutes": int(required_daily),
            "predicted_completion_rate": round(predicted_rate, 2),
            "is_likely_to_complete": predicted_rate >= 0.95,
        }
