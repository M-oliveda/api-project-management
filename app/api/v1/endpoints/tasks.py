from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.schemas.task import TaskCreate, TaskUpdate, TaskInDB
from app.services import create_task, update_task, delete_task, get_task_by_id, get_tasks_by_project, get_tasks
from app.db import get_db
from app.services import verify_token, verify_user_subscription
from app.core.security import decode_access_token
from app.schemas import Token
from uuid import UUID
from app.services.auth import get_user_by_email


router = APIRouter()


@router.post("/new", response_model=TaskInDB, status_code=status.HTTP_201_CREATED)
def create_new_task(request: Request, task_data: TaskCreate, db: Session = Depends(get_db)):
    token = request.headers.get("Authorization")
    if not token or not verify_token(db, Token(access_token=token, token_type="bearer")):
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = decode_access_token(token)

    if verify_user_subscription(db, user["sub"]):
        return create_task(db, task_data)
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.get("/", response_model=List[TaskInDB])
def get_tasks_list(request: Request, db: Session = Depends(get_db)):
    token = request.headers.get("Authorization")
    if not token or not verify_token(db, Token(access_token=token, token_type="bearer")):
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = decode_access_token(token)

    user = get_user_by_email(db, user["sub"])

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return get_tasks(db, user.email)


@router.get("/{task_id}", response_model=TaskInDB)
def read_task(request: Request, task_id: UUID, db: Session = Depends(get_db)):
    token = request.headers.get("Authorization")
    if not token or not verify_token(db, Token(access_token=token, token_type="bearer")):
        raise HTTPException(status_code=401, detail="Unauthorized")

    task = get_task_by_id(db, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskInDB)
def update_existing_task(request: Request, task_id: UUID, task_data: TaskUpdate, db: Session = Depends(get_db)):

    token = request.headers.get("Authorization")
    if not token or not verify_token(db, Token(access_token=token, token_type="bearer")):
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = decode_access_token(token)

    if verify_user_subscription(db, user["sub"]):
        task = update_task(db, task_id, task_data)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return task
    return HTTPException(status_code=401, detail="Unauthorized")


@router.delete("/{task_id}", response_model=TaskInDB)
def delete_existing_task(request: Request, task_id: UUID, db: Session = Depends(get_db)):
    token = request.headers.get("Authorization")
    if not token or not verify_token(db, Token(access_token=token, token_type="bearer")):
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = decode_access_token(token)

    if verify_user_subscription(db, user["sub"]):
        task = delete_task(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return task

    return HTTPException(status_code=401, detail="Unauthorized")


@router.get("/project/{project_id}", response_model=List[TaskInDB])
def read_tasks_by_project(request: Request, project_id: UUID, db: Session = Depends(get_db)):
    token = request.headers.get("Authorization")
    if not token or not verify_token(db, Token(access_token=token, token_type="bearer")):
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = decode_access_token(token)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return get_tasks_by_project(db, project_id, user.email)
