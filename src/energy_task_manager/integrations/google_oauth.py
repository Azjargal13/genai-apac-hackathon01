"""Load Google OAuth user credentials for Tasks and Calendar APIs.

Obtain a user token once (see ``scripts/google_oauth_login.py``), then either:

- **File:** set ``GOOGLE_OAUTH_TOKEN_PATH`` (good for Codespaces / local ``secrets/token.json``).
- **Env JSON:** set ``GOOGLE_OAUTH_TOKEN_JSON`` to the full token JSON string (typical for
  **Cloud Run** + **Secret Manager**, where the secret is mounted as an environment variable).

The library refreshes expired access tokens when a refresh_token is present. Refreshed tokens
are written back only when using the **file** path, not when using ``GOOGLE_OAUTH_TOKEN_JSON``
(Cloud Run usually does not write back to Secret Manager from the app).
"""

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
