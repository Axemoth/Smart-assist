from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTError
from sqlalchemy.orm import Session
from app.db.session import session
from app.core.config import settings
from app.repositories.user_repository import UserRepository

from app.error.custom_execption import UserNotAuthenticated, UserNotFound

from app.schemas.token import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_db():
    with session() as db:
        yield db


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    if token is None:
        raise UserNotAuthenticated()

    try:
        payload = jwt.decode(
            token, settings.ACCESS_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except JWTError:
        raise UserNotAuthenticated()

    user = UserRepository(db).get_by_id(payload["user_id"])

    if not user:
        raise UserNotFound()

    return TokenData(user_id=user.user_id, role=user.role)
