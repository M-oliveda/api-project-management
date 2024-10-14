from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from app.services import create_project, get_user_projects, update_project, delete_project, get_project
from app.schemas import ProjectCreate, ProjectResponse, ProjectUpdate
from app.db import get_db
from app.services.auth import verify_token
from app.schemas import Token
from app.core.security import decode_access_token
from app.services import verify_user_subscription
from uuid import UUID
from app.services.auth import get_user_by_email

router = APIRouter()


@router.post("/new", response_model=ProjectResponse | None, status_code=201 | 400)
def create_new_project(
    request: Request,
    project_data: ProjectCreate,
    db: Session = Depends(get_db)
):
    token = request.headers.get("Authorization")
    if not token or not verify_token(db, Token(access_token=token, token_type="bearer")):
        raise HTTPException(status_code=401, detail="Unauthorized")

    decode_token = decode_access_token(token)

    user = get_user_by_email(db, decode_token["sub"])

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if verify_user_subscription(db, user.email):
        return create_project(db, user, project_data)

    raise HTTPException(status_code=401, detail="Unauthorized")


@router.get("/", response_model=List[ProjectResponse])
def list_user_projects(
    request: Request,
    skip: int = 0, limit: int = 10,
    db: Session = Depends(get_db),
):
    token = request.headers.get("Authorization")
    if not token or not verify_token(db, Token(access_token=token, token_type="bearer")):
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = decode_access_token(token)

    user = get_user_by_email(db, user["sub"])

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return get_user_projects(db, user, skip=skip, limit=limit)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project_by_id(
    request: Request,
    project_id: UUID,
    db: Session = Depends(get_db),
):

    token = request.headers.get("Authorization")
    if not token or not verify_token(db, Token(access_token=token, token_type="bearer")):
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = decode_access_token(token)

    user = get_user_by_email(db, user["sub"])

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return get_project(db, project_id, user)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_existing_project(
    request: Request,
    project_id: UUID,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
):

    token = request.headers.get("Authorization")
    if not token or not verify_token(db, Token(access_token=token, token_type="bearer")):
        raise HTTPException(status_code=401, detail="Unauthorized")

    decode_token = decode_access_token(token)

    user = get_user_by_email(db, decode_token["sub"])

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if verify_user_subscription(db, user.email):
        return update_project(db, project_id, user, project_data)

    return HTTPException(status_code=401, detail="Unauthorized")


@router.delete("/{project_id}")
def delete_existing_project(
    request: Request,
    project_id: UUID,
    db: Session = Depends(get_db),
):
    token = request.headers.get("Authorization")
    if not token or not verify_token(db, Token(access_token=token, token_type="bearer")):
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = decode_access_token(token)

    decode_token = decode_access_token(token)

    user = get_user_by_email(db, decode_token["sub"])

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if verify_user_subscription(db, user.email):
        return delete_project(db, project_id, user)

    return HTTPException(status_code=401, detail="Unauthorized")
