from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut
from app.services.project_service import ProjectService


router = APIRouter(prefix="/projects", tags=["项目"])


@router.get("", response_model=list[ProjectOut])
def list_projects(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ProjectService(db).list_for_user(current.id)


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ProjectService(db).create(current.id, payload)


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ProjectService(db).get_owned(current.id, project_id)


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ProjectService(db).update(current.id, project_id, payload)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ProjectService(db).delete(current.id, project_id)
