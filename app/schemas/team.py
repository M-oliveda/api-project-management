from pydantic import BaseModel
from uuid import UUID


class TeamBase(BaseModel):
    name: str


class TeamCreate(TeamBase):
    owner_id: UUID


class TeamUpdate(TeamBase):
    pass


class TeamInDBBase(TeamBase):
    id: UUID
    owner_id: UUID


class Team(TeamInDBBase):
    pass


class TeamWithMembers(TeamInDBBase):
    members: list[UUID]


class TeamWithProjects(TeamInDBBase):
    projects: list[UUID]


class AddTeamMember(BaseModel):
    team_id: UUID
    user_to_add_id: UUID


class RemoveTeamMember(BaseModel):
    team_id: UUID
    user_to_remove_id: UUID
