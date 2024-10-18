from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class TeamMember(Base):
    __tablename__ = "team_members"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    team_id: Mapped[UUID] = mapped_column(ForeignKey("teams.id"), primary_key=True)
