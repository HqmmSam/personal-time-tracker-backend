from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut
from app.services.task_service import TaskService


# 嵌套路由（按项目列任务、按项目建任务）与扁平路由（按 task_id 操作）混合
nested_router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["任务"])
flat_router = APIRouter(prefix="/tasks", tags=["任务"])


@nested_router.get("", response_model=list[TaskOut])
def list_tasks(
    project_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return TaskService(db).list_for_project(current.id, project_id)


@nested_router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    project_id: int,
    payload: TaskCreate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return TaskService(db).create(current.id, project_id, payload)


@flat_router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return TaskService(db).get_owned(current.id, task_id)


@flat_router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return TaskService(db).update(current.id, task_id, payload)


@flat_router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    TaskService(db).delete(current.id, task_id)
