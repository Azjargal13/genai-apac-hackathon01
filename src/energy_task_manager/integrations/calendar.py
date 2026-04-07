"""Google Calendar API — events on primary calendar (user OAuth)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from googleapiclient.discovery import build

from energy_task_manager.integrations.google_oauth import require_google_user_credentials


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
