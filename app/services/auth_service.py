from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.token import Token
from app.error.custom_execption import AdminNotAuthenticated
from app.error.custom_execption import (
    UserAlreadyExists,
    UserNotFound,
    InvalidCredentials,
    InvalidToken,
    UserNotVerified,
)
from app.utlis.cache import redis_client, get_failed_attempts, increment_failed_login
from app.services.email_service import EmailService
from app.core.config import settings

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)
        self.email_service = EmailService()

    def authorize_admin(self, user):
        if user.role != "admin":
            raise AdminNotAuthenticated()

    def register(self, payload, bg_tasks):
        hashed = hash_password(payload.password)
        payload.password = hashed

        with self.db.begin():
            email = payload.email
            user = self.repo.get_by_email(email)
            if user:
                raise UserAlreadyExists()

            new_user = self.repo.create_user_db(payload.model_dump())

        # if db tran fail -> bg task will keep running coz it was already scheduled
        # Hence, it is better to set task after we have completed our tran
        self.email_service.send_mail(email, bg_tasks)

        return {
            "message": "Account Created. Check email to verify your account",
            "email": new_user.email,
        }

    def login(self, response, payload):
        cache_key = f"login_fail:{payload.username}"

        if get_failed_attempts(cache_key) >= 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many attempts. Your account has been locked. try after 10 minutes",
            )

        with self.db.begin():
            user = self.repo.get_by_email(payload.username)

            if not user:
                increment_failed_login(cache_key)
                raise UserNotFound()
            if not user.is_verified:
                raise UserNotVerified()
            if not verify_password(payload.password, user.password):
                increment_failed_login(cache_key)
                raise InvalidCredentials()

            access_token = create_access_token(
                {"user_id": user.user_id, "role": user.role}
            )

            refresh_token = create_refresh_token(
                {"user_id": user.user_id, "role": user.role}
            )

            self.repo.store_refresh_token(user.user_id, refresh_token)

            refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=int(refresh_token_expires.total_seconds()),
            )

            redis_client.delete(cache_key)

            return Token(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
            )

    def refresh_token(self, payload):
        with self.db.begin():
            db_token = self.repo.get_refresh_token(payload.refresh_token)

            if not db_token:
                raise InvalidToken()

            if db_token.is_used:
                self.repo.security_check(db_token.user_id)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="All sessions discontinued. Please login again.",
                )

            if db_token.expires_at < datetime.now():
                self.repo.delete_refresh_token(db_token.token)
                raise InvalidToken()

            db_token.is_used = True
            db_user_id = db_token.user_id
            user = self.repo.get_by_id(db_user_id)

            if not user:
                raise UserNotFound

            access_token = create_access_token(
                {"user_id": user.user_id, "role": user.role}
            )

            refresh_token = create_refresh_token(
                {"user_id": user.user_id, "role": user.role}
            )

            self.repo.store_refresh_token(user.user_id, refresh_token)

            return Token(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
            )

    def logout(self, response, refresh_token):
        self.repo.delete_refresh_token(refresh_token)

        response.delete_cookie(
            key="refresh_token",
            httponly=True,
            secure=True,
            samesite="lax",
        )

        return {"message": "logged out successfully."}
