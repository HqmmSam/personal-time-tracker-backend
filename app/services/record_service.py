from datetime import date

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.exceptions import PermissionDenied, ResourceNotFound
from app.models.project import Project
from app.models.task import Task
from app.models.time_record import TimeRecord
from app.schemas.record import RecordCreate, RecordUpdate, RecordListItem, Pagination


class RecordService:
    def __init__(self, db: Session):
        self.db = db

    def _check_task_owned(self, user_id: int, task_id: int) -> Task:
        task = (
            self.db.query(Task)
            .filter(
                Task.id == task_id,
                Task.user_id == user_id,
                Task.deleted_at.is_(None),
            )
            .first()
        )
        if not task:
            raise ResourceNotFound("Task", task_id)
        return task

    def create(self, user_id: int, payload: RecordCreate) -> TimeRecord:
        self._check_task_owned(user_id, payload.task_id)
        record = TimeRecord(
            user_id=user_id,
            task_id=payload.task_id,
            record_date=payload.record_date or date.today(),
            start_time=payload.start_time,
            duration=payload.duration,
            type=payload.type,
            note=payload.note,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list(
        self,
        user_id: int,
        project_id: int | None = None,
        task_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        type_: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[RecordListItem], Pagination]:
        q = (
            self.db.query(
                TimeRecord.id,
                TimeRecord.task_id,
                Task.name.label("task_name"),
                Project.id.label("project_id"),
                Project.name.label("project_name"),
                Project.color.label("project_color"),
                TimeRecord.record_date,
                TimeRecord.start_time,
                TimeRecord.duration,
                TimeRecord.type,
                TimeRecord.note,
                TimeRecord.created_at,
            )
            .join(Task, Task.id == TimeRecord.task_id)
            .join(Project, Project.id == Task.project_id)
            .filter(TimeRecord.user_id == user_id, Project.deleted_at.is_(None))
        )
        if project_id:
            q = q.filter(Project.id == project_id)
        if task_id:
            q = q.filter(Task.id == task_id)
        if start_date:
            q = q.filter(TimeRecord.record_date >= start_date)
        if end_date:
            q = q.filter(TimeRecord.record_date <= end_date)
        if type_:
            q = q.filter(TimeRecord.type == type_)

        total = q.count()
        rows = (
            q.order_by(desc(TimeRecord.record_date), desc(TimeRecord.id))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        items = [
            RecordListItem(
                id=r.id,
                task_id=r.task_id,
                task_name=r.task_name,
                project_id=r.project_id,
                project_name=r.project_name,
                project_color=r.project_color,
                record_date=r.record_date,
                start_time=r.start_time,
                duration=r.duration,
                type=r.type,
                note=r.note,
                created_at=r.created_at,
            )
            for r in rows
        ]
        return items, Pagination(page=page, page_size=page_size, total=total)

    def _get_owned(self, user_id: int, record_id: int) -> TimeRecord:
        record = (
            self.db.query(TimeRecord)
            .filter(TimeRecord.id == record_id, TimeRecord.user_id == user_id)
            .first()
        )
        if not record:
            raise ResourceNotFound("Record", record_id)
        return record

    def update(self, user_id: int, record_id: int, payload: RecordUpdate) -> TimeRecord:
        record = self._get_owned(user_id, record_id)
        data = payload.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(record, k, v)
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, user_id: int, record_id: int) -> None:
        record = self._get_owned(user_id, record_id)
        self.db.delete(record)
        self.db.commit()
