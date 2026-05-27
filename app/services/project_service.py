from datetime import datetime

from sqlalchemy.orm import Session

from app.exceptions import BusinessException, PermissionDenied, ResourceNotFound
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


MAX_PROJECTS_PER_USER = 50


class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    def list_for_user(self, user_id: int) -> list[Project]:
        return (
            self.db.query(Project)
            .filter(Project.user_id == user_id, Project.deleted_at.is_(None))
            .order_by(Project.sort_order.asc(), Project.created_at.desc())
            .all()
        )

    def create(self, user_id: int, payload: ProjectCreate) -> Project:
        count = (
            self.db.query(Project)
            .filter(Project.user_id == user_id, Project.deleted_at.is_(None))
            .count()
        )
        if count >= MAX_PROJECTS_PER_USER:
            raise BusinessException("PROJECT_LIMIT_EXCEEDED", "项目数量已达上限", 422)

        dup = (
            self.db.query(Project)
            .filter(
                Project.user_id == user_id,
                Project.name == payload.name,
                Project.deleted_at.is_(None),
            )
            .first()
        )
        if dup:
            raise BusinessException("PROJECT_NAME_DUPLICATE", "项目名已存在", 409)

        project = Project(user_id=user_id, **payload.model_dump())
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_owned(self, user_id: int, project_id: int) -> Project:
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

    def update(self, user_id: int, project_id: int, payload: ProjectUpdate) -> Project:
        project = self.get_owned(user_id, project_id)
        data = payload.model_dump(exclude_unset=True)
        if "name" in data and data["name"] != project.name:
            dup = (
                self.db.query(Project)
                .filter(
                    Project.user_id == user_id,
                    Project.name == data["name"],
                    Project.deleted_at.is_(None),
                    Project.id != project_id,
                )
                .first()
            )
            if dup:
                raise BusinessException("PROJECT_NAME_DUPLICATE", "项目名已存在", 409)
        for k, v in data.items():
            setattr(project, k, v)
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, user_id: int, project_id: int) -> None:
        project = self.get_owned(user_id, project_id)
        project.deleted_at = datetime.utcnow()
        # 级联软删除任务
        for task in project.tasks:
            if task.deleted_at is None:
                task.deleted_at = datetime.utcnow()
        self.db.commit()
