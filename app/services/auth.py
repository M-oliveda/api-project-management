from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, Token, UserInfo
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.db import get_db


def get_user_by_email(db: Session, email: str) -> User | None:
    """Retrieve a user by email."""
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(db: Session, user_data: UserCreate):
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise ValueError("Email is already registered")

    hashed_password = get_password_hash(user_data.password)
    db_user = User(email=user_data.email,
                   hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def login_user(db: Session, login_data: UserLogin):
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


def verify_token(db: Session, token: Token):
    data = decode_access_token(token.access_token)
    user = db.query(User).filter(User.email == data.get("sub")).first()
    return user is not None


def get_user_info(db: Session, token: Token):
    data = decode_access_token(token.access_token)
    user = db.query(User).filter(User.email == data.get("sub")).first()

    if user is not None:

        return UserInfo(
            email=user.email,
            subscription_id=user.subscription_id,
            id=user.id,
            is_active=user.is_active
        )
