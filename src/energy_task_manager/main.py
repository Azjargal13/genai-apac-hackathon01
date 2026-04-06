"""FastAPI application entrypoint (Cloud Run serves this module)."""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from energy_task_manager.api.routes import plan_router, tasks_router
from energy_task_manager.context import clear_request_context, get_session_id, get_user_id, set_request_context

load_dotenv()

logger = logging.getLogger(__name__)

app = FastAPI(title="Energy-Aware AI Task Manager")
app.include_router(tasks_router)
app.include_router(plan_router)


@app.middleware("http")
async def bind_request_identity(request: Request, call_next):
    user_id = request.headers.get("X-User-Id") or get_user_id()
    session_id = request.headers.get("X-Session-Id") or get_session_id()
    if request.url.path != "/health" and not user_id:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Missing X-User-Id header",
                "hint": "Send X-User-Id per request, or set DEFAULT_USER_ID in .env for local testing.",
            },
        )
    set_request_context(user_id=user_id, session_id=session_id)
    try:
        return await call_next(request)
    finally:
        clear_request_context()


@app.exception_handler(Exception)
async def catch_unhandled_errors(request: Request, exc: Exception):
    logger.exception("Unhandled API error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "hint": "Check Firestore auth (ADC) and GOOGLE_CLOUD_PROJECT.",
        },
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
