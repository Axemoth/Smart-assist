from typing import Annotated
from fastapi import APIRouter, Depends
from app.core.dependencies import get_db
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.schemas.token import TokenData

from app.schemas.task import TaskRequest, TaskResponse, TaskUpdateRequest, TaskDeleteResponse
from app.services.task_service import TaskService
from app.schemas.ai import AIPromptRequest, AIRewriteRequest, AIBreakdownRequest, AIParsedTask, AIRewrittenTask, AITaskBreakdown
from app.services.ai_service import AIService

router =  APIRouter()

@router.post("/tasks/ai/parse", response_model=AIParsedTask)
def ai_parse_task(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    payload: AIPromptRequest
):
    return AIService().parse_raw_task(payload.prompt)

@router.post("/tasks/ai/rewrite", response_model=AIRewrittenTask)
def ai_rewrite_task(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    payload: AIRewriteRequest
):
    return AIService().rewrite_task(payload.title, payload.description)

@router.post("/tasks/ai/breakdown", response_model=AITaskBreakdown)
def ai_breakdown_task(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    payload: AIBreakdownRequest
):
    return AIService().breakdown_task(payload.title, payload.description)

@router.post("/tasks", response_model=TaskResponse)
def create_task(current_user: Annotated[TokenData, Depends(get_current_user)], payload: TaskRequest, db: Annotated[Session, Depends(get_db)] ):
    return TaskService(db).create_task(current_user.user_id, payload)

@router.get("/tasks")
def current_user_task(current_user: Annotated[TokenData, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    return TaskService(db).get_task_current_user_id(current_user.user_id)

@router.get("/tasks/{task_id}")
def get_task(current_user: Annotated[TokenData, Depends(get_current_user)], task_id: int, db: Annotated[Session, Depends(get_db)]):
    return TaskService(db).get_task_by_id(current_user.user_id, task_id)

@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(current_user: Annotated[TokenData, Depends(get_current_user)], task_id: int, payload: TaskUpdateRequest, db: Annotated[Session, Depends(get_db)]):
    return TaskService(db).update_task(current_user.user_id, task_id, payload)

@router.delete("/tasks/{task_id}", response_model=TaskDeleteResponse)
def delete_task(current_user: Annotated[TokenData, Depends(get_current_user)], task_id: int, db: Annotated[Session, Depends(get_db)]):
    return TaskService(db).delete_task(current_user.user_id, task_id)
