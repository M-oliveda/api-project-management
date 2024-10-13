from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import Project, User
from app.schemas.project import ProjectCreate, ProjectUpdate
from datetime import datetime
from uuid import UUID


def create_project(db: Session, user: User, project_data: ProjectCreate):
    project = Project(
        name=project_data.name,
        description=project_data.description,
        owner_id=user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_project(db: Session, project_id: UUID, user: User):
    project = db.query(Project).filter(
        Project.id == project_id, Project.owner_id == user.id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project


def get_user_projects(db: Session, user: User, skip: int = 0, limit: int = 10):
    return db.query(Project).filter(Project.owner_id == user.id).offset(skip).limit(limit).all()


def update_project(db: Session, project_id: UUID, user: User, project_data: ProjectUpdate):
    project = get_project(db, project_id, user)
    if project_data.name:
        project.name = project_data.name
    if project_data.description:
        project.description = project_data.description
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: UUID, user: User):
    project = get_project(db, project_id, user)
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}
