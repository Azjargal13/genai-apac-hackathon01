"""Load user OAuth credentials for Tasks + Calendar (token from ``google_oauth_login.py`` paste flow).

``GOOGLE_OAUTH_TOKEN_JSON`` (Cloud Run) or ``GOOGLE_OAUTH_TOKEN_PATH`` (file). Refreshes access
tokens; file path is updated on refresh, env JSON is not."""

from __future__ import annotations

import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Tasks + calendar events only (narrower than full calendar scope).
GOOGLE_TASKS_CALENDAR_SCOPES: tuple[str, ...] = (
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/calendar.events",
)


def _token_path() -> str | None:
    path = os.getenv("GOOGLE_OAUTH_TOKEN_PATH")
    if not path or not path.strip():
        return None
    return path.strip()


def _token_json_from_env() -> str | None:
    raw = os.getenv("GOOGLE_OAUTH_TOKEN_JSON")
    if raw is None or not str(raw).strip():
        return None
    return str(raw).strip()


def get_google_user_credentials() -> Credentials | None:
    """Return valid user Credentials, refreshing the access token if expired.

    Prefers ``GOOGLE_OAUTH_TOKEN_JSON`` if set; otherwise reads ``GOOGLE_OAUTH_TOKEN_PATH``.

    Returns ``None`` if neither source is configured or the file is missing.
    """
    json_str = _token_json_from_env()
    if json_str:
        try:
            info = json.loads(json_str)
        except json.JSONDecodeError:
            return None
        creds = Credentials.from_authorized_user_info(info, list(GOOGLE_TASKS_CALENDAR_SCOPES))
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds

    path = _token_path()
    if not path or not Path(path).is_file():
        return None

    creds = Credentials.from_authorized_user_file(path, list(GOOGLE_TASKS_CALENDAR_SCOPES))
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        Path(path).write_text(creds.to_json(), encoding="utf-8")
    return creds


def require_google_user_credentials() -> Credentials:
    """Return credentials or raise with a short hint if the token is missing."""
    creds = get_google_user_credentials()
    if creds is None:
        raise RuntimeError(
            "Missing Google user OAuth token. Set GOOGLE_OAUTH_TOKEN_PATH or "
            "GOOGLE_OAUTH_TOKEN_JSON and run scripts/google_oauth_login.py"
        )
    return creds


def google_oauth_configured() -> bool:
    """True when token JSON env is set and valid, or token file path exists on disk."""
    js = _token_json_from_env()
    if js:
        try:
            json.loads(js)
        except json.JSONDecodeError:
            return False
        return True
    p = _token_path()
    return bool(p and Path(p).is_file())
