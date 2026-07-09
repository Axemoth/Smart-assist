from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str):
    return  pwd_context.hash(password)


def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)

def create_access_token(data: dict):
    expire_access_token = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    data.update({"exp_access_token": int(expire_access_token.timestamp())})

    return jwt.encode(data, settings.ACCESS_SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict):
    expire_refresh_token = datetime.utcnow() + timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    data.update({"exp_refresh_token": int(expire_refresh_token.timestamp())})

    return jwt.encode(data, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM)
