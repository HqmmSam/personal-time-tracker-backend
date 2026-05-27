from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.stats import NextWeekPrediction, GoalPrediction
from app.services.prediction_service import PredictionService


router = APIRouter(prefix="/predictions", tags=["预测"])


@router.get("/next-week-hours", response_model=NextWeekPrediction)
def next_week_hours(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return PredictionService(db).next_week_hours(current.id)


@router.get("/goal-completion", response_model=GoalPrediction)
def goal_completion(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return PredictionService(db).goal_completion(current.id)
