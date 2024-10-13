from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.task import TaskStatus


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO


class TaskCreate(TaskBase):
    project_id: UUID


class TaskUpdate(TaskBase):
    status: Optional[TaskStatus] = None


class TaskInDB(TaskBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
