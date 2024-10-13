from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import Base
from enum import Enum as PyEnum
from uuid import UUID, uuid4
from datetime import datetime, timezone


class TaskStatus(PyEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True,
                                     default=uuid4)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.TODO)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        onupdate=datetime.now(timezone.utc), nullable=True, default=None)

    project = relationship("Project", back_populates="tasks")
