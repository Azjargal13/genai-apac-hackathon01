"""Per-request context for user and session identity (FastAPI + tools).

``X-Session-Id`` / ``X-User-Id`` identify who is calling and which *conversation thread*
it belongs to. For LLM chat, keeping a **stable session id per thread** is the right
pattern: the model can rely on prior turns in that session instead of you resending
or restating long summaries every time—pair that with short follow-up replies and
output token limits (see ``agents/``) to stay within rate limits.

This module is request-scoped (``contextvars``); wire the same ids to ADK ``Session``
when the HTTP API drives the agent runtime.
"""

from __future__ import annotations

import os
from contextvars import ContextVar

_user_id_ctx: ContextVar[str | None] = ContextVar("user_id", default=None)
_session_id_ctx: ContextVar[str | None] = ContextVar("session_id", default=None)


def set_request_context(*, user_id: str | None, session_id: str | None) -> None:
    _user_id_ctx.set(user_id)
    _session_id_ctx.set(session_id)


def clear_request_context() -> None:
    _user_id_ctx.set(None)
    _session_id_ctx.set(None)


def get_user_id() -> str | None:
    # Demo-safe fallback to avoid missing identity errors in ADK/local runs.
    return _user_id_ctx.get() or os.getenv("DEFAULT_USER_ID") or "beta-user-1"


def get_session_id() -> str | None:
    return _session_id_ctx.get() or os.getenv("DEFAULT_SESSION_ID")

