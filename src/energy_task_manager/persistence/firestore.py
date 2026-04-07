"""Firestore repository for tasks, events, and user stats."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from energy_task_manager.api.models import (
    TaskCategory,
    TaskEventRecord,
    TaskPriority,
    TaskRecord,
    TaskStatus,
    UserStatsRecord,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _to_firestore_value(value: Any) -> Any:
    """Convert enums recursively while preserving datetime objects."""
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {k: _to_firestore_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_firestore_value(v) for v in value]
    return value


class FirestoreRepository:
    """Thin repository wrapper with schema validation via Pydantic models."""

    TASKS_COLLECTION = "tasks"
    EVENTS_COLLECTION = "task_events"
    STATS_COLLECTION = "user_stats"

    def __init__(
        self,
        project_id: str | None = None,
        database_id: str | None = None,
        client: firestore.Client | None = None,
    ) -> None:
        resolved_project = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        resolved_database = database_id or os.getenv("FIRESTORE_DATABASE_ID", "(default)")
        self.client = client or firestore.Client(
            project=resolved_project,
            database=resolved_database,
        )

    def create_task(
        self,
        *,
        user_id: str,
        title: str,
        category: TaskCategory,
        estimated_minutes: int,
        description: str | None = None,
        due_at: datetime | None = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        energy_level: str | None = None,
        labels: list[str] | None = None,
        task_id: str | None = None,
    ) -> TaskRecord:
        now = _utcnow()
        task = TaskRecord(
            task_id=task_id or str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            status=TaskStatus.TODO,
            category=category,
            estimated_minutes=estimated_minutes,
            created_at=now,
            updated_at=now,
            description=description,
            due_at=due_at,
            completed_at=None,
            priority=priority,
            energy_level=energy_level,
            labels=labels or [],
        )
        self.client.collection(self.TASKS_COLLECTION).document(task.task_id).set(
            _to_firestore_value(task.model_dump())
        )
        self.log_task_event(
            task_id=task.task_id,
            user_id=user_id,
            event_type="created",
            payload={"title": title, "category": category.value},
        )
        return task

    def get_task(self, *, task_id: str, user_id: str | None = None) -> TaskRecord | None:
        snapshot = self.client.collection(self.TASKS_COLLECTION).document(task_id).get()
        if not snapshot.exists:
            return None
        data = snapshot.to_dict() or {}
        task = TaskRecord.model_validate(data)
        if user_id is not None and task.user_id != user_id:
            return None
        return task

    def list_tasks(
        self,
        *,
        user_id: str,
        status: TaskStatus | None = None,
        limit: int = 50,
    ) -> list[TaskRecord]:
        query = (
            self.client.collection(self.TASKS_COLLECTION)
            .where(filter=FieldFilter("user_id", "==", user_id))
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )
        if status is not None:
            query = query.where(filter=FieldFilter("status", "==", status.value))
        docs = query.stream()
        return [TaskRecord.model_validate(doc.to_dict()) for doc in docs]

    def complete_task(self, *, task_id: str, user_id: str) -> TaskRecord:
        ref = self.client.collection(self.TASKS_COLLECTION).document(task_id)
        snap = ref.get()
        if not snap.exists:
            raise ValueError(f"Task '{task_id}' not found")

        current = TaskRecord.model_validate(snap.to_dict() or {})
        if current.user_id != user_id:
            raise ValueError("Task does not belong to user")

        now = _utcnow()
        completed = current.model_copy(
            update={
                "status": TaskStatus.DONE,
                "completed_at": now,
                "updated_at": now,
            }
        )
        ref.set(_to_firestore_value(completed.model_dump()), merge=False)
        self.log_task_event(
            task_id=task_id,
            user_id=user_id,
            event_type="completed",
            payload={"estimated_minutes": current.estimated_minutes},
        )
        self.increment_user_stats(
            user_id=user_id,
            completed_task_minutes=current.estimated_minutes,
        )
        return completed

    def log_task_event(
        self,
        *,
        task_id: str,
        user_id: str,
        event_type: str,
        payload: dict[str, Any] | None = None,
    ) -> TaskEventRecord:
        event = TaskEventRecord(
            task_id=task_id,
            user_id=user_id,
            event_type=event_type,
            created_at=_utcnow(),
            payload=payload or {},
        )
        self.client.collection(self.EVENTS_COLLECTION).add(_to_firestore_value(event.model_dump()))
        return event

    def get_user_stats(self, *, user_id: str) -> UserStatsRecord | None:
        snap = self.client.collection(self.STATS_COLLECTION).document(user_id).get()
        if not snap.exists:
            return None
        return UserStatsRecord.model_validate(snap.to_dict() or {})

    def increment_user_stats(self, *, user_id: str, completed_task_minutes: int) -> UserStatsRecord:
        current = self.get_user_stats(user_id=user_id)
        now = _utcnow()
        if current is None:
            updated = UserStatsRecord(
                user_id=user_id,
                tasks_completed=1,
                avg_task_minutes=float(completed_task_minutes),
                last_updated=now,
            )
        else:
            prev_total = current.avg_task_minutes * current.tasks_completed
            new_count = current.tasks_completed + 1
            new_avg = (prev_total + completed_task_minutes) / new_count
            updated = current.model_copy(
                update={
                    "tasks_completed": new_count,
                    "avg_task_minutes": round(new_avg, 2),
                    "last_updated": now,
                }
            )

        self.client.collection(self.STATS_COLLECTION).document(user_id).set(
            _to_firestore_value(updated.model_dump()),
            merge=False,
        )
        return updated
