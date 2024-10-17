from sqlalchemy.orm import Session
from app.models import Task, User, Project
from app.schemas.task import TaskCreate, TaskUpdate
from uuid import UUID


def create_task(db: Session, task_data: TaskCreate):
    db_task = Task(
        title=task_data.title,
        description=task_data.description,
        project_id=task_data.project_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: UUID, task_data: TaskUpdate):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        return None

    task.title = task_data.title or task.title
    task.description = task_data.description or task.description
    task.status = task_data.status or task.status

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: UUID):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
    return task


def get_task_by_id(db: Session, task_id: UUID):
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks(db: Session, user_email: str):
    user = db.query(User).filter(User.email == user_email).first()

    if not user:
        return None

    projects = db.query(Project).filter(Project.owner_id == user.id).all()

    return db.query(Task).filter(Task.project_id.in_([project.id for project in projects])).all()


def get_tasks_by_project(db: Session, project_id: UUID, user_email: str):

    user_projects = db.query(Project).filter(
        Project.owner_id == user_email).all()

    if not user_projects or not [project.id == project_id for project in user_projects]:
        return None

    tasks = db.query(Task).filter(Task.project_id.in_(
        [project.id for project in user_projects])).all()

    if not tasks:
        return None

    return tasks
