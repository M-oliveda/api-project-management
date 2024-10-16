from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: UUID4
    owner_id: UUID4
    created_at: datetime
