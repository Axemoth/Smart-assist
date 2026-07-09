from app.repositories.user_repository import UserRepository
from sqlalchemy.orm import Session
from app.error.custom_execption import UserNotFound

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def get_user(self, user_id: int):
        with self.db.begin_nested():
            user =  self.repo.get_by_id(user_id)
            if not user:
                raise UserNotFound()

            return user

    def get_all_users(self):
        with self.db.begin_nested():
            return self.repo.list_users()
