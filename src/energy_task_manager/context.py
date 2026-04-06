"""Per-request context storage for user and session identity."""

from __future__ import annotations

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
    return _user_id_ctx.get()


def get_session_id() -> str | None:
    return _session_id_ctx.get()

