from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserCreated(BaseModel):
    message: str


class UserInfo(BaseModel):
    email: EmailStr
    subscription_id: UUID | None = None
    id: UUID
    is_active: bool
