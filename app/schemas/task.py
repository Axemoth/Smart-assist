from typing import Literal, Optional
from enum import Enum
from pydantic import BaseModel, ConfigDict

class TaskStatus(str, Enum):
    COMPLETED =  "completed"
    PENDING = "pending"

class TaskPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaskRequest(BaseModel):
    title: str
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM

class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True , use_enum_values=True)

    task_id: int
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority

class TaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None

class TaskDeleteResponse(BaseModel):
    message: str
