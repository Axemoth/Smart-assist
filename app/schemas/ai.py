from pydantic import BaseModel
from typing import List
from app.schemas.task import TaskPriority

class AIPromptRequest(BaseModel):
    prompt: str

class AIRewriteRequest(BaseModel):
    title: str
    description: str

class AIBreakdownRequest(BaseModel):
    title: str
    description: str

class AIParsedTask(BaseModel):
    title: str
    description: str
    priority: TaskPriority

class AIRewrittenTask(BaseModel):
    title: str
    description: str
    priority: TaskPriority

class AITaskBreakdown(BaseModel):
    subtasks: List[str]
