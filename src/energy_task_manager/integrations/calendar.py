"""Google Calendar API — events on primary calendar (user OAuth)."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from googleapiclient.discovery import build

from energy_task_manager.integrations.google_oauth import require_google_user_credentials


def _default_tz() -> str:
    return os.getenv("GOOGLE_CALENDAR_TIMEZONE", "Asia/Ulaanbaatar")


def build_calendar_service():
    return build(
        "calendar",
        "v3",
        credentials=require_google_user_credentials(),
        cache_discovery=False,
    )


def list_primary_calendar_events(*, max_results: int = 10, days_ahead: int = 7) -> dict[str, Any]:
    """Upcoming events on the user's primary calendar in the next ``days_ahead`` days."""
    svc = build_calendar_service()
    now = datetime.now(timezone.utc)
    return (
        svc.events()
        .list(
            calendarId="primary",
            timeMin=now.isoformat(),
            timeMax=(now + timedelta(days=days_ahead)).isoformat(),
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )


def insert_event(
    summary: str,
    start_datetime_iso: str,
    end_datetime_iso: str,
    *,
    description: str | None = None,
    time_zone: str | None = None,
) -> dict[str, Any]:
    tz = time_zone or _default_tz()
    body: dict[str, Any] = {
        "summary": summary,
        "start": {"dateTime": start_datetime_iso, "timeZone": tz},
        "end": {"dateTime": end_datetime_iso, "timeZone": tz},
    }
    if description:
        body["description"] = description
    return (
        build_calendar_service()
        .events()
        .insert(calendarId="primary", body=body)
        .execute()
    )


def patch_event(
    event_id: str,
    *,
    summary: str | None = None,
    description: str | None = None,
    start_datetime_iso: str | None = None,
    end_datetime_iso: str | None = None,
    time_zone: str | None = None,
) -> dict[str, Any]:
    tz = time_zone or _default_tz()
    body: dict[str, Any] = {}
    if summary is not None:
        body["summary"] = summary
    if description is not None:
        body["description"] = description
    if start_datetime_iso is not None:
        body["start"] = {"dateTime": start_datetime_iso, "timeZone": tz}
    if end_datetime_iso is not None:
        body["end"] = {"dateTime": end_datetime_iso, "timeZone": tz}
    return (
        build_calendar_service()
        .events()
        .patch(calendarId="primary", eventId=event_id, body=body)
        .execute()
    )


def delete_event(event_id: str) -> dict[str, Any]:
    build_calendar_service().events().delete(calendarId="primary", eventId=event_id).execute()
    return {"deleted": True, "event_id": event_id}
