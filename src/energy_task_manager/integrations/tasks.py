"""Google Tasks API (user OAuth)."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from googleapiclient.discovery import build

from energy_task_manager.integrations.google_oauth import require_google_user_credentials


def _default_tasklist() -> str:
    return os.getenv("GOOGLE_TASKS_DEFAULT_LIST_ID", "@default")


def _due_rfc3339(due: str) -> str:
    """Accept YYYY-MM-DD or full RFC3339."""
    due = due.strip()
    if "T" in due:
        return due if due.endswith("Z") or "+" in due else due + "Z"
    return f"{due}T00:00:00.000Z"


def build_tasks_service():
    return build(
        "tasks",
        "v1",
        credentials=require_google_user_credentials(),
        cache_discovery=False,
    )


def list_task_lists() -> dict[str, Any]:
    """Return API response with ``items`` (task lists)."""
    return build_tasks_service().tasklists().list().execute()


def list_tasks(tasklist_id: str | None = None, *, max_results: int = 20) -> dict[str, Any]:
    """List tasks in the given list (default ``@default`` or ``GOOGLE_TASKS_DEFAULT_LIST_ID``)."""
    tid = tasklist_id or _default_tasklist()
    return (
        build_tasks_service()
        .tasks()
        .list(tasklist=tid, maxResults=max_results)
        .execute()
    )


def insert_task(
    title: str,
    *,
    notes: str | None = None,
    due: str | None = None,
    tasklist_id: str | None = None,
) -> dict[str, Any]:
    tid = tasklist_id or _default_tasklist()
    body: dict[str, Any] = {"title": title}
    if notes:
        body["notes"] = notes
    if due:
        body["due"] = _due_rfc3339(due)
    return build_tasks_service().tasks().insert(tasklist=tid, body=body).execute()


def patch_task(
    task_id: str,
    *,
    title: str | None = None,
    notes: str | None = None,
    due: str | None = None,
    tasklist_id: str | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    tid = tasklist_id or _default_tasklist()
    body: dict[str, Any] = {}
    if title is not None:
        body["title"] = title
    if notes is not None:
        body["notes"] = notes
    if due is not None:
        body["due"] = _due_rfc3339(due)
    if status is not None:
        body["status"] = status
        if status == "completed":
            body["completed"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    return (
        build_tasks_service()
        .tasks()
        .patch(tasklist=tid, task=task_id, body=body)
        .execute()
    )


def delete_task(task_id: str, *, tasklist_id: str | None = None) -> dict[str, Any]:
    tid = tasklist_id or _default_tasklist()
    build_tasks_service().tasks().delete(tasklist=tid, task=task_id).execute()
    return {"deleted": True, "task_id": task_id, "tasklist_id": tid}
