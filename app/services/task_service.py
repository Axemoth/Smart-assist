from app.repositories.task_repository import TaskRepository
from sqlalchemy.orm import Session
from app.error.custom_execption import TaskNotFound


class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TaskRepository(db)

    def create_task(self, user_id, payload):
        with self.db.begin_nested():
            return self.repo.create_task_db(user_id, payload.model_dump())

    def get_task_current_user_id(self, user_id):
        with self.db.begin_nested():
            return self.repo.get_user_tasks_db(user_id)

    def get_task_by_id(self, user_id, task_id):
        with self.db.begin_nested():
            task = self.repo.get_by_id_db(user_id, task_id)
            if not task:
                raise TaskNotFound()

            return task

    def update_task(self, user_id, task_id, payload):
        with self.db.begin_nested():
            data = payload.dict(exclude_unset=True)
            return self.repo.update_task_db(user_id, task_id, **data)

    def delete_task(self, user_id, task_id):

        with self.db.begin_nested():
            self.repo.delete_task_db(user_id, task_id)
            return {"message": "task deleted successfully."}
