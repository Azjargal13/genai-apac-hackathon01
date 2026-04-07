"""ADK-callable tools: Firestore app store + Google Tasks/Calendar (user OAuth)."""

from __future__ import annotations

from energy_task_manager.tools.google_tools import (
    complete_google_task,
    create_google_calendar_event,
    create_google_task,
    delete_google_calendar_event,
    delete_google_task,
    list_google_calendar_events,
    list_google_task_lists,
    list_google_tasks,
    update_google_calendar_event,
    update_google_task,
)

from datetime import datetime
from typing import Any

from energy_task_manager.api.models import TaskCategory, TaskPriority, TaskStatus
from energy_task_manager.context import get_user_id
from energy_task_manager.persistence import FirestoreRepository

_repo: FirestoreRepository | None = None


def _get_repo() -> FirestoreRepository:
    global _repo
    if _repo is None:
        _repo = FirestoreRepository()
    return _repo


def _serialize(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, dict):
        return {k: _serialize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_serialize(v) for v in value]
    return value


def _parse_category(raw: str | None) -> TaskCategory:
    if not raw:
        return TaskCategory.OTHERS
    normalized = raw.strip().lower().replace(" ", "_")
    try:
        return TaskCategory(normalized)
    except ValueError:
        return TaskCategory.OTHERS


def _parse_priority(raw: str | None) -> TaskPriority:
    if not raw:
        return TaskPriority.MEDIUM
    normalized = raw.strip().lower()
    try:
        return TaskPriority(normalized)
    except ValueError:
        return TaskPriority.MEDIUM


def _resolve_user_id(explicit_user_id: str | None) -> str:
    user_id = explicit_user_id or get_user_id()
    if not user_id:
        raise ValueError("Missing user identity. Provide X-User-Id header or user_id.")
    return user_id


def create_task(
    title: str,
    estimated_minutes: int | None = None,
    user_id: str | None = None,
    category: str | None = None,
    description: str | None = None,
    priority: str = "medium",
) -> dict[str, Any]:
    """Create a task document in Firestore.

    Agent should pass category and estimated_minutes when available.
    If estimated_minutes is missing, derive from learned user history.
    """
    resolved_user_id = _resolve_user_id(user_id)
    if estimated_minutes is None:
        stats = _get_repo().get_user_stats(user_id=resolved_user_id)
        # Learned baseline: use user's historical average completion time.
        estimated_minutes = (
            max(1, int(round(stats.avg_task_minutes)))
            if stats and stats.avg_task_minutes > 0
            else 60
        )
    resolved_category = _parse_category(category)
    task = _get_repo().create_task(
        user_id=resolved_user_id,
        title=title,
        estimated_minutes=estimated_minutes,
        category=resolved_category,
        description=description,
        priority=_parse_priority(priority),
    )
    return _serialize(task.model_dump())


def complete_task(task_id: str, user_id: str | None = None) -> dict[str, Any]:
    """Mark a task as done, create event, and update user stats."""
    resolved_user_id = _resolve_user_id(user_id)
    task = _get_repo().complete_task(task_id=task_id, user_id=resolved_user_id)
    return _serialize(task.model_dump())


def get_task(task_id: str, user_id: str | None = None) -> dict[str, Any] | None:
    """Get a single task for user."""
    resolved_user_id = _resolve_user_id(user_id)
    task = _get_repo().get_task(task_id=task_id, user_id=resolved_user_id)
    if task is None:
        return None
    return _serialize(task.model_dump())


def list_tasks(
    status: str | None = None,
    limit: int = 20,
    user_id: str | None = None,
) -> list[dict[str, Any]]:
    """List user tasks, optionally filtered by status."""
    resolved_user_id = _resolve_user_id(user_id)
    status_enum = None
    if status:
        try:
            status_enum = TaskStatus(status.strip().lower())
        except ValueError:
            status_enum = None
    tasks = _get_repo().list_tasks(
        user_id=resolved_user_id,
        status=status_enum,
        limit=max(1, min(limit, 100)),
    )
    return [_serialize(task.model_dump()) for task in tasks]


def get_user_stats(user_id: str | None = None) -> dict[str, Any] | None:
    """Get aggregate user productivity stats."""
    resolved_user_id = _resolve_user_id(user_id)
    stats = _get_repo().get_user_stats(user_id=resolved_user_id)
    if stats is None:
        return None
    return _serialize(stats.model_dump())


def estimate_day_plan(
    total_available_time_minutes: int,
    user_id: str | None = None,
) -> dict[str, Any]:
    """Estimate workload with the core behavioral time-modeling formula."""
    if total_available_time_minutes <= 0:
        raise ValueError("total_available_time_minutes must be > 0")

    resolved_user_id = _resolve_user_id(user_id)
    stats = _get_repo().get_user_stats(user_id=resolved_user_id)
    open_tasks = _get_repo().list_tasks(user_id=resolved_user_id, status=TaskStatus.TODO, limit=100)
    in_progress_tasks = _get_repo().list_tasks(
        user_id=resolved_user_id,
        status=TaskStatus.IN_PROGRESS,
        limit=100,
    )
    active_tasks = open_tasks + in_progress_tasks
    active_count = len(active_tasks)

    # Core UVP formula:
    # estimated_time_per_task = total_available_time / tasks_completed
    if stats and stats.tasks_completed > 0:
        estimated_time_per_task = total_available_time_minutes / stats.tasks_completed
        formula_applied = True
        formula_note = "Core formula applied using historical tasks_completed."
    else:
        # Fallback only for cold-start users with no completions yet.
        estimated_time_per_task = 60.0
        formula_applied = False
        formula_note = "No completion history yet; used 60-minute fallback."

    predicted_total_minutes = round(estimated_time_per_task * active_count, 2)
    overload_ratio = (
        round(predicted_total_minutes / total_available_time_minutes, 2)
        if total_available_time_minutes > 0
        else 0
    )
    overload_risk = overload_ratio > 1.0

    recommendations: list[str] = []
    if active_count == 0:
        recommendations.append("No active tasks. Add tasks to plan your day.")
    elif overload_risk:
        recommendations.append("Reduce today's tasks to avoid overload.")
        recommendations.append("Move lower-priority tasks to another day.")
    else:
        recommendations.append("Current plan looks feasible for available time.")
        recommendations.append("Keep buffer time for interruptions.")

    return {
        "user_id": resolved_user_id,
        "total_available_time_minutes": total_available_time_minutes,
        "tasks_completed": stats.tasks_completed if stats else 0,
        "active_task_count": active_count,
        "estimated_time_per_task_minutes": round(estimated_time_per_task, 2),
        "predicted_total_minutes": predicted_total_minutes,
        "overload_ratio": overload_ratio,
        "overload_risk": overload_risk,
        "formula_applied": formula_applied,
        "formula": "estimated_time_per_task = total_available_time / tasks_completed",
        "formula_note": formula_note,
        "recommendations": recommendations,
    }


__all__ = [
    "complete_google_task",
    "complete_task",
    "create_google_calendar_event",
    "create_google_task",
    "create_task",
    "delete_google_calendar_event",
    "delete_google_task",
    "estimate_day_plan",
    "get_task",
    "get_user_stats",
    "list_google_calendar_events",
    "list_google_task_lists",
    "list_google_tasks",
    "list_tasks",
    "update_google_calendar_event",
    "update_google_task",
]
