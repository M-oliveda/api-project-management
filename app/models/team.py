from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from uuid import UUID, uuid4
from app.models import Base


class Team(Base):
    __tablename__ = 'teams'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey('users.id'), nullable=False)

    owner = relationship("User", back_populates="owned_teams")
    members = relationship(
        "User", secondary="team_members", back_populates="team_member", overlaps="owned_teams")
    projects = relationship("Project", back_populates="team")
