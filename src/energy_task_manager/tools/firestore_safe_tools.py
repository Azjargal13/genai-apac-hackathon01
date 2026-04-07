"""ADK-safe wrappers around Firestore-backed tools.

These wrappers return ``{"error": True, ...}`` instead of raising, so agent runs
can fail gracefully and continue with an LLM-only response when context is missing.
"""

from __future__ import annotations

from typing import Any, Callable, TypeVar

from energy_task_manager.tools import (
    complete_task,
    create_task,
    estimate_day_plan,
    get_task,
    get_user_stats,
    list_tasks,
)

T = TypeVar("T")


def _safe(fn: Callable[[], T]) -> T | dict[str, Any]:
    try:
        return fn()
    except Exception as e:
        msg = str(e)
        out: dict[str, Any] = {"error": True, "message": msg}
        if "Missing user identity" in msg:
            out["hint"] = "Provide user_id (or X-User-Id) before Firestore tool calls."
        return out


def safe_create_task(
    title: str,
    estimated_minutes: int | None = None,
    user_id: str | None = None,
    category: str | None = None,
    description: str | None = None,
    priority: str = "medium",
) -> dict[str, Any]:
    return _safe(
        lambda: create_task(
            title=title,
            estimated_minutes=estimated_minutes,
            user_id=user_id,
            category=category,
            description=description,
            priority=priority,
        )
    )


def safe_complete_task(task_id: str, user_id: str | None = None) -> dict[str, Any]:
    return _safe(lambda: complete_task(task_id=task_id, user_id=user_id))


def safe_get_task(task_id: str, user_id: str | None = None) -> dict[str, Any] | None:
    return _safe(lambda: get_task(task_id=task_id, user_id=user_id))


def safe_list_tasks(
    status: str | None = None,
    limit: int = 20,
    user_id: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    return _safe(lambda: list_tasks(status=status, limit=limit, user_id=user_id))


def safe_get_user_stats(user_id: str | None = None) -> dict[str, Any] | None:
    return _safe(lambda: get_user_stats(user_id=user_id))


def safe_estimate_day_plan(
    total_available_time_minutes: int,
    user_id: str | None = None,
) -> dict[str, Any]:
    return _safe(
        lambda: estimate_day_plan(
            total_available_time_minutes=total_available_time_minutes,
            user_id=user_id,
        )
    )

