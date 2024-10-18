from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.services.auth import verify_token
from app.schemas import Token
from sqlalchemy.orm import Session
from app.schemas import (
    TeamBase,
    TeamUpdate,
    Team,
    TeamWithMembers,
    TeamCreate,
    AddTeamMember,
    RemoveTeamMember,
)
from app.services import (
    create_team,
    get_team,
    update_team,
    delete_team,
    add_member_to_team,
    remove_member_from_team,
    get_team_by_owned_by,
)
from app.db.session import get_db
from uuid import UUID
from app.services.auth import get_user_by_email
from app.services import verify_user_subscription
from app.core.security import decode_access_token


router = APIRouter()


@router.post("/new", response_model=Team, status_code=201)
def add_new_team_endpoint(
    request: Request, team_data: TeamBase, db: Session = Depends(get_db)
):
    token = request.headers.get("Authorization")
    if not token or not verify_token(
        db, Token(access_token=token, token_type="bearer")
    ):
        raise HTTPException(status_code=401, detail="Unauthorized")

    decode_token = decode_access_token(token)

    user = get_user_by_email(db, decode_token["sub"])

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if verify_user_subscription(db, user.email):
        team_info = TeamCreate(name=team_data.name, owner_id=user.id)
        return create_team(db, team_info)
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.get("/{team_id}", response_model=TeamWithMembers)
def get_team_endpoint(request: Request, team_id: UUID, db: Session = Depends(get_db)):
    token = request.headers.get("Authorization")
    if not token or not verify_token(
        db, Token(access_token=token, token_type="bearer")
    ):
        raise HTTPException(status_code=401, detail="Unauthorized")

    team = get_team(db, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    return TeamWithMembers(
        id=team_id,
        name=team.name,
        owner_id=team.owner_id,
        members=[member.id for member in team.members],
    )


@router.get("/owner/{owner_id}", response_model=list[Team])
def get_teams_by_owner(request: Request, owner_id: UUID, db: Session = Depends(get_db)):
    token = request.headers.get("Authorization")
    if not token or not verify_token(
        db, Token(access_token=token, token_type="bearer")
    ):
        raise HTTPException(status_code=401, detail="Unauthorized")

    teams = get_team_by_owned_by(db, owner_id)

    if not teams:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Teams not found"
        )
    return teams


@router.put("/{team_id}", response_model=Team)
def update_team_endpoint(
    request: Request,
    team_id: UUID,
    team_data: TeamUpdate,
    db: Session = Depends(get_db),
):
    token = request.headers.get("Authorization")
    if not token or not verify_token(
        db, Token(access_token=token, token_type="bearer")
    ):
        raise HTTPException(status_code=401, detail="Unauthorized")

    decode_token = decode_access_token(token)

    user = get_user_by_email(db, decode_token["sub"])

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if verify_user_subscription(db, user.email):
        return update_team(db, team_id, user.id, team_data)
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.delete("/{team_id}")
def delete_team_endpoint(
    request: Request, team_id: UUID, db: Session = Depends(get_db)
):
    token = request.headers.get("Authorization")
    if not token or not verify_token(
        db, Token(access_token=token, token_type="bearer")
    ):
        raise HTTPException(status_code=401, detail="Unauthorized")

    decode_token = decode_access_token(token)

    user = get_user_by_email(db, decode_token["sub"])

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if verify_user_subscription(db, user.email):
        return delete_team(db, user.id, team_id)


@router.post("/members/add")
def add_member_endpoint(
    request: Request, add_team_member: AddTeamMember, db: Session = Depends(get_db)
):
    token = request.headers.get("Authorization")
    if not token or not verify_token(
        db, Token(access_token=token, token_type="bearer")
    ):
        raise HTTPException(status_code=401, detail="Unauthorized")

    decode_token = decode_access_token(token)

    user = get_user_by_email(db, decode_token["sub"])

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if verify_user_subscription(db, user.email):
        return add_member_to_team(db, user.id, add_team_member)
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.delete("/members/remove")
def remove_member_endpoint(
    request: Request, user_to_remove: RemoveTeamMember, db: Session = Depends(get_db)
):
    token = request.headers.get("Authorization")
    if not token or not verify_token(
        db, Token(access_token=token, token_type="bearer")
    ):
        raise HTTPException(status_code=401, detail="Unauthorized")

    decode_token = decode_access_token(token)

    user = get_user_by_email(db, decode_token["sub"])

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if verify_user_subscription(db, user.email):
        return remove_member_from_team(db, user.id, user_to_remove)
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")
