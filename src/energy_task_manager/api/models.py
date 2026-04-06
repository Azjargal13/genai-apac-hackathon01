"""Shared API and persistence schema models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskCategory(str, Enum):
    DEEP_WORK = "deep_work"
    ERRAND = "errand"
    PERSONAL = "personal"
    ADMIN = "admin"
    MEETING = "meeting"
    LEARNING = "learning"
    HEALTH = "health"
    OTHERS = "others"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskRecord(BaseModel):
    task_id: str
    user_id: str
    title: str = Field(min_length=1, max_length=200)
    status: TaskStatus = TaskStatus.TODO
    category: TaskCategory
    estimated_minutes: int = Field(ge=1)
    created_at: datetime
    updated_at: datetime
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    energy_level: Optional[str] = Field(default=None, pattern="^(low|medium|high)$")
    labels: list[str] = Field(default_factory=list)


class TaskEventRecord(BaseModel):
    task_id: str
    user_id: str
    event_type: str
    created_at: datetime
    payload: dict = Field(default_factory=dict)


class UserStatsRecord(BaseModel):
    user_id: str
    tasks_completed: int = Field(ge=0, default=0)
    avg_task_minutes: float = Field(ge=0, default=0)
    last_updated: datetime
    best_focus_hours: int = Field(ge=1, le=12, default=6)
    weekly_capacity_minutes: Optional[int] = Field(default=None, ge=0)
    recent_overload_flags: int = Field(ge=0, default=0)

