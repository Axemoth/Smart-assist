from app.models.task import Task
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.error.custom_execption import TaskNotFound


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_task_db(self, user_id, data: dict) -> Task:
        data.update({"user_id": user_id})
        new_task = Task(**data)
        self.db.add(new_task)
        self.db.flush()

        return new_task

    def get_user_tasks_db(self, user_id: int):
        return (
            self.db.execute(select(Task).where(Task.user_id == user_id)).scalars().all()
        )

    def get_by_id_db(self, user_id: int, task_id: int):
        return (
            self.db.execute(
                select(Task).where(Task.task_id == task_id, Task.user_id == user_id)
            )
            .scalar()
        )

    def update_task_db(self, user_id: int, task_id: int, **data: dict) -> Task:
        task = self.db.execute(
            select(Task).where(Task.task_id == task_id, Task.user_id == user_id)
        ).scalar()

        if not task:
            raise TaskNotFound()

        for key, value in data.items():
            setattr(task, key, value)

        self.db.flush()

        return task

    def delete_task_db(self, user_id: int, task_id: int):
        task = self.db.execute(
            select(Task).where(Task.task_id == task_id, Task.user_id == user_id)
        ).scalar()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="task not found."
            )

        return self.db.execute(
            delete(Task).where(Task.task_id == task_id, Task.user_id == user_id)
        )
