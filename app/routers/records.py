from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.record import (
    RecordCreate,
    RecordUpdate,
    RecordOut,
    RecordListResponse,
)
from app.services.record_service import RecordService


router = APIRouter(prefix="/records", tags=["时间记录"])


@router.get("", response_model=RecordListResponse)
def list_records(
    project_id: int | None = None,
    task_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    type: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, pagination = RecordService(db).list(
        user_id=current.id,
        project_id=project_id,
        task_id=task_id,
        start_date=start_date,
        end_date=end_date,
        type_=type,
        page=page,
        page_size=page_size,
    )
    return RecordListResponse(items=items, pagination=pagination)


@router.post("", response_model=RecordOut, status_code=status.HTTP_201_CREATED)
def create_record(
    payload: RecordCreate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return RecordService(db).create(current.id, payload)


@router.put("/{record_id}", response_model=RecordOut)
def update_record(
    record_id: int,
    payload: RecordUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return RecordService(db).update(current.id, record_id, payload)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    RecordService(db).delete(current.id, record_id)
