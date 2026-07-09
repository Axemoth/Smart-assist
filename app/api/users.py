from typing import Annotated, List
from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.models.user import User
from app.schemas.user import User
from app.schemas.token import TokenData
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/users/me")
def get_user(current_user: Annotated[TokenData, Depends(get_current_user)], db: Annotated[Session, Depends(get_db) ]):
    return UserService(db).get_user(current_user.user_id)

@router.get("/users", response_model=List[User])
def get_users(current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    AuthService(db).authorize_admin(current_user)
    return UserService(db).get_all_users()
