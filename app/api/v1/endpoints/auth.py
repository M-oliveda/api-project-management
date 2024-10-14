from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.schemas.auth import UserCreate, UserLogin, Token, UserCreated, UserInfo
from app.services.auth import create_user, login_user, get_user_info
from app.db.session import get_db

router = APIRouter()


@router.post("/register", response_model=UserCreated, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = create_user(db, user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User could not be created")
    return {"message": "User created successfully"}


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    return login_user(db, login_data)


@router.get("/userinfo", response_model=UserInfo)
def get_user_info_endpoint(request: Request, db: Session = Depends(get_db)):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = get_user_info(db, Token(access_token=token, token_type="bearer"))

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user.model_dump()
