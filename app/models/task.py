from sqlalchemy import Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.schemas.task import TaskStatus, TaskPriority

from app.db.base import Base

class Task(Base):
    __tablename__ = "tasks"

    task_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.PENDING)
    priority: Mapped[TaskPriority] = mapped_column(default=TaskPriority.MEDIUM)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False, index=True)

    user = relationship("User", back_populates="tasks")
