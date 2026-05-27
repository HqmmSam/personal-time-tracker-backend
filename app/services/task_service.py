from datetime import datetime

from sqlalchemy.orm import Session

from app.exceptions import PermissionDenied, ResourceNotFound
from app.models.project import Project
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, db: Session):
        self.db = db

    def _check_project_owned(self, user_id: int, project_id: int) -> Project:
        project = (
            self.db.query(Project)
            .filter(Project.id == project_id, Project.deleted_at.is_(None))
            .first()
        )
        if not project:
            raise ResourceNotFound("Project", project_id)
        if project.user_id != user_id:
            raise PermissionDenied()
        return project

    def list_for_project(self, user_id: int, project_id: int) -> list[Task]:
        self._check_project_owned(user_id, project_id)
        return (
            self.db.query(Task)
            .filter(Task.project_id == project_id, Task.deleted_at.is_(None))
            .order_by(Task.sort_order.asc(), Task.created_at.desc())
            .all()
        )

    def create(self, user_id: int, project_id: int, payload: TaskCreate) -> Task:
        self._check_project_owned(user_id, project_id)
        task = Task(user_id=user_id, project_id=project_id, **payload.model_dump())
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_owned(self, user_id: int, task_id: int) -> Task:
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

    def update(self, user_id: int, task_id: int, payload: TaskUpdate) -> Task:
        task = self.get_owned(user_id, task_id)
        data = payload.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(task, k, v)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, user_id: int, task_id: int) -> None:
        task = self.get_owned(user_id, task_id)
        task.deleted_at = datetime.utcnow()
        self.db.commit()
