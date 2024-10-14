from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from uuid import UUID, uuid4

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, index=True, default=uuid4)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    subscription_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "subscriptions.id"), nullable=True, default=None)

    projects = relationship(
        "Project", back_populates="owner")

    owned_teams = relationship("Team", secondary="team_members",
                               back_populates="owner")

    team_member = relationship(
        "Team", secondary="team_members", back_populates="members")
