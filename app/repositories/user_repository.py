from datetime import datetime, timedelta

from app.models.user import User
from app.models.refresh_token import RefreshToken
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from app.core.config import settings


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user_db(self, data: dict) -> User:
        new_user = User(**data)
        self.db.add(new_user)
        self.db.flush()

        return new_user

    def get_by_email(self, email: str):
        return self.db.execute(select(User).where(User.email == email)).scalar()

    def get_by_id(self, user_id: int):
        return self.db.execute(select(User).where(User.user_id == user_id)).scalar()

    def list_users(self):
        return self.db.execute(select(User)).scalars().all()

    def store_refresh_token(self, user_id, refresh_token):
        db_token = RefreshToken(
            token=refresh_token,
            user_id=user_id,
            expires_at=datetime.utcnow()
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            is_used=False,
        )
        self.db.add(db_token)
        self.db.flush()

    def get_refresh_token(self, refresh_token):
        return self.db.execute(
            select(RefreshToken).where(RefreshToken.token == refresh_token)
        ).scalar()

    def security_check(self, user_id):
        self.db.execute(delete(RefreshToken).where(RefreshToken.user_id == user_id))
        self.db.commit()

    def delete_refresh_token(self, refresh_token):
        self.db.execute(
            delete(RefreshToken).where(RefreshToken.token == refresh_token)
        )
        self.db.commit()
