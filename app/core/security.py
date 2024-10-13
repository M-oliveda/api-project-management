import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from . import app_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = timedelta(days=1)):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, app_settings.JWT_SECRET_KEY, algorithm=app_settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    return jwt.decode(
        token, app_settings.JWT_SECRET_KEY, algorithms=[app_settings.JWT_ALGORITHM])
