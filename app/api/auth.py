from typing import Annotated, Optional

from fastapi import APIRouter, Response, BackgroundTasks, Depends, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from app.core.dependencies import get_db
from sqlalchemy.orm import Session

from app.services.auth_service import AuthService
from app.services.email_service import VerifyMail
from app.schemas.user import (
    RegisterRequest,
    RegisterResponse,
    RefreshToken,
    VerifyMailModel,
)
from app.schemas.token import Token


router = APIRouter()


@router.post("/register", response_model=RegisterResponse)
def register_user(
    payload: RegisterRequest,
    bg_tasks: BackgroundTasks,
    db: Annotated[Session, Depends(get_db)],
):
    return AuthService(db).register(payload, bg_tasks)


@router.get("/verify/{token}", response_model=VerifyMailModel)
def verify_mail(token: str, db: Annotated[Session, Depends(get_db)]):
    return VerifyMail(db).verify(token)


@router.post("/login", response_model=Token)
def login_user(
    db: Annotated[Session, Depends(get_db)],
    response: Response,
    payload: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    return AuthService(db).login(response, payload)


@router.post("/refresh")
def refresh_token(payload: RefreshToken, db: Annotated[Session, Depends(get_db)]):
    return AuthService(db).refresh_token(payload)


@router.post("/logout")
def logout(
    db: Annotated[Session, Depends(get_db)],
    response: Response,
    refresh_token: Optional[str] = Cookie(None, alias="refresh_token"),
):
    return AuthService(db).logout(response, refresh_token)
