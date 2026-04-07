"""Google Tasks API (user OAuth)."""

from __future__ import annotations

import os
from typing import Any

from googleapiclient.discovery import build

from energy_task_manager.integrations.google_oauth import require_google_user_credentials


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
    tid = tasklist_id or os.getenv("GOOGLE_TASKS_DEFAULT_LIST_ID", "@default")
    return (
        build_tasks_service()
        .tasks()
        .list(tasklist=tid, maxResults=max_results)
        .execute()
    )
