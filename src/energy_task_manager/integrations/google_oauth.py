"""Load user OAuth credentials for Tasks + Calendar (token from ``google_oauth_login.py`` paste flow).

``GOOGLE_OAUTH_TOKEN_JSON`` (Cloud Run) or ``GOOGLE_OAUTH_TOKEN_PATH`` (file). Refreshes access
tokens; file path is updated on refresh, env JSON is not."""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Tasks + calendar events only (narrower than full calendar scope).
GOOGLE_TASKS_CALENDAR_SCOPES: tuple[str, ...] = (
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/calendar.events",
)


def _find_project_root() -> Path | None:
    """Detect repo root so relative ``secrets/token.json`` works when cwd is ``src/`` (e.g. ``adk web``)."""
    here = Path(__file__).resolve()
    for d in here.parents:
        if (d / "requirements.txt").is_file() and (d / "src" / "energy_task_manager").is_dir():
            return d
    return None


def _load_project_dotenv() -> None:
    root = _find_project_root()
    if root and (root / ".env").is_file():
        load_dotenv(root / ".env", override=False)


def _resolve_existing_file(raw: str) -> Path | None:
    """Resolve a config path; try repo root first, then cwd (relative paths)."""
    p = Path(raw.strip())
    if p.is_absolute():
        return p if p.is_file() else None
    candidates: list[Path] = []
    root = _find_project_root()
    if root:
        candidates.append((root / p).resolve())
    candidates.append((Path.cwd() / p).resolve())
    seen: set[Path] = set()
    for c in candidates:
        if c in seen:
            continue
        seen.add(c)
        if c.is_file():
            return c
    return None


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
    _load_project_dotenv()
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

    raw = _token_path()
    if not raw:
        return None
    path = _resolve_existing_file(raw)
    if path is None:
        return None

    creds = Credentials.from_authorized_user_file(str(path), list(GOOGLE_TASKS_CALENDAR_SCOPES))
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        path.write_text(creds.to_json(), encoding="utf-8")
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
    _load_project_dotenv()
    js = _token_json_from_env()
    if js:
        try:
            json.loads(js)
        except json.JSONDecodeError:
            return False
        return True
    raw = _token_path()
    return bool(raw and _resolve_existing_file(raw) is not None)
