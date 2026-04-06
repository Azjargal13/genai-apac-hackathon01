"""Task routes using header-based user identity."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from energy_task_manager.tools import complete_task, create_task, get_task, get_user_stats, list_tasks

router = APIRouter(prefix="/task", tags=["task"])


class CreateTaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    estimated_minutes: int = Field(ge=1)
    category: str = "others"
    description: str | None = None
    priority: str = "medium"


@router.post("")
def add_task(payload: CreateTaskRequest) -> dict:
    return create_task(
        title=payload.title,
        estimated_minutes=payload.estimated_minutes,
        category=payload.category,
        description=payload.description,
        priority=payload.priority,
    )


@router.post("/{task_id}/complete")
def mark_task_complete(task_id: str) -> dict:
    return complete_task(task_id=task_id)


@router.get("/stats/me")
def read_my_stats() -> dict | None:
    return get_user_stats()


@router.get("/{task_id}")
def read_task(task_id: str) -> dict | None:
    return get_task(task_id=task_id)


@router.get("")
def read_tasks(status: str | None = None, limit: int = 20) -> list[dict]:
    return list_tasks(status=status, limit=limit)

