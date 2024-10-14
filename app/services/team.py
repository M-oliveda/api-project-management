from sqlalchemy.orm import Session
from app.models.user import User
from app.models.team import Team
from app.schemas import TeamCreate, TeamUpdate, AddTeamMember, RemoveTeamMember
from fastapi import HTTPException, status
from uuid import UUID


def create_team(db: Session, team_data: TeamCreate):
    already_existing_team = db.query(Team).filter(
        Team.name == team_data.name).first()
    if already_existing_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Team already exists")
    team = Team(name=team_data.name, owner_id=team_data.owner_id)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def get_team(db: Session, team_id: UUID):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Team not found")
    return team


def get_team_by_owned_by(db: Session, owner_id: UUID):
    return db.query(Team).filter(Team.owner_id == owner_id).all()


def update_team(db: Session, team_id: UUID, user_id: UUID, team_data: TeamUpdate):
    team = get_team(db, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    if team.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not the owner of this team")

    for key, value in team_data.model_dump(exclude_unset=True).items():
        setattr(team, key, value)

    db.commit()
    db.refresh(team)
    return team


def delete_team(db: Session, user_id: UUID, team_id: UUID):
    team = get_team(db, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    if team.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not the owner of this team")

    db.delete(team)
    db.commit()
    return {"message": "Team deleted successfully"}


def add_member_to_team(db: Session, user_id: UUID, add_team_member: AddTeamMember):
    team = get_team(db, add_team_member.team_id)
    user = db.query(User).filter(
        User.id == add_team_member.user_to_add_id).first()
    if not team or not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Team or user not found")

    if team.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not the owner of this team")

    if user in team.members:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User already in team")

    team.members.append(user)
    db.commit()
    db.refresh(team)
    return team


def remove_member_from_team(db: Session, user_id: UUID, user_to_remove: RemoveTeamMember):
    team = get_team(db, user_to_remove.team_id)
    user = db.query(User).filter(
        User.id == user_to_remove.user_to_remove_id).first()
    if not team or not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Team or user not found")

    if team.owner_id == user_to_remove.user_to_remove_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You cannot remove the owner of the team")

    if team.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not the owner of this team")

    team.members.remove(user)
    db.commit()
    db.refresh(team)
    return team
