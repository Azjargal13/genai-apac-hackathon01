"""ADK tools: Google Tasks + Calendar (OAuth user token)."""

from __future__ import annotations

from typing import Any, Callable, TypeVar

from googleapiclient.errors import HttpError

import energy_task_manager.integrations.calendar as gcal
import energy_task_manager.integrations.tasks as gtasks

T = TypeVar("T")


def _safe_api(fn: Callable[[], T]) -> T | dict[str, Any]:
    try:
        return fn()
    except HttpError as e:
        out: dict[str, Any] = {
            "error": True,
            "http_status": getattr(e.resp, "status", None),
            "message": str(e),
        }
        if e.content:
            try:
                out["body"] = e.content.decode(errors="replace")[:2000]
            except Exception:
                pass
        return out
    except RuntimeError as e:
        return {
            "error": True,
            "message": str(e),
            "hint": (
                "OAuth token missing or unreadable. Use an absolute GOOGLE_OAUTH_TOKEN_PATH, "
                "or keep token at <repo>/secrets/token.json — path resolution now checks repo root "
                "even when adk runs from src/."
            ),
        }
    except Exception as e:
        return {"error": True, "message": str(e)}


def list_google_tasks(max_results: int = 20, tasklist_id: str | None = None) -> dict[str, Any]:
    """List tasks from the user's Google Tasks list (default list if tasklist_id omitted)."""
    return _safe_api(lambda: gtasks.list_tasks(tasklist_id=tasklist_id, max_results=max_results))


def list_google_task_lists() -> dict[str, Any]:
    """List the user's Google Task lists (ids for create/update targeting)."""
    return _safe_api(gtasks.list_task_lists)


def create_google_task(
    title: str,
    notes: str | None = None,
    due_date: str | None = None,
    tasklist_id: str | None = None,
) -> dict[str, Any]:
    """Create a task in Google Tasks. due_date: YYYY-MM-DD or RFC3339."""
    return _safe_api(
        lambda: gtasks.insert_task(
            title,
            notes=notes,
            due=due_date,
            tasklist_id=tasklist_id,
        )
    )


def update_google_task(
    task_id: str,
    title: str | None = None,
    notes: str | None = None,
    due_date: str | None = None,
    tasklist_id: str | None = None,
) -> dict[str, Any]:
    """Update fields on a Google Task (use list_google_tasks for task id)."""
    return _safe_api(
        lambda: gtasks.patch_task(
            task_id,
            title=title,
            notes=notes,
            due=due_date,
            tasklist_id=tasklist_id,
        )
    )


def complete_google_task(task_id: str, tasklist_id: str | None = None) -> dict[str, Any]:
    """Mark a Google Task completed."""
    return _safe_api(
        lambda: gtasks.patch_task(task_id, status="completed", tasklist_id=tasklist_id)
    )


def delete_google_task(task_id: str, tasklist_id: str | None = None) -> dict[str, Any]:
    """Delete a Google Task."""
    return _safe_api(lambda: gtasks.delete_task(task_id, tasklist_id=tasklist_id))


def list_google_calendar_events(days_ahead: int = 7, max_results: int = 15) -> dict[str, Any]:
    """List upcoming events on the user's primary Google Calendar."""
    return _safe_api(
        lambda: gcal.list_primary_calendar_events(
            max_results=max_results, days_ahead=days_ahead
        )
    )


def create_google_calendar_event(
    summary: str,
    start_datetime_iso: str,
    end_datetime_iso: str,
    description: str | None = None,
    time_zone: str | None = None,
) -> dict[str, Any]:
    """Create a timed event on primary calendar. Use ISO datetimes, e.g. 2025-04-08T14:00:00."""
    return _safe_api(
        lambda: gcal.insert_event(
            summary,
            start_datetime_iso,
            end_datetime_iso,
            description=description,
            time_zone=time_zone,
        )
    )


def update_google_calendar_event(
    event_id: str,
    summary: str | None = None,
    description: str | None = None,
    start_datetime_iso: str | None = None,
    end_datetime_iso: str | None = None,
    time_zone: str | None = None,
) -> dict[str, Any]:
    """Patch a calendar event (event id from list_google_calendar_events)."""
    return _safe_api(
        lambda: gcal.patch_event(
            event_id,
            summary=summary,
            description=description,
            start_datetime_iso=start_datetime_iso,
            end_datetime_iso=end_datetime_iso,
            time_zone=time_zone,
        )
    )


def delete_google_calendar_event(event_id: str) -> dict[str, Any]:
    """Delete a calendar event from primary calendar."""
    return _safe_api(lambda: gcal.delete_event(event_id))
