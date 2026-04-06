"""FastAPI application entrypoint (Cloud Run serves this module)."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from energy_task_manager.api.routes import plan_router, tasks_router
from energy_task_manager.context import clear_request_context, set_request_context

app = FastAPI(title="Energy-Aware AI Task Manager")
app.include_router(tasks_router)
app.include_router(plan_router)


@app.middleware("http")
async def bind_request_identity(request: Request, call_next):
    user_id = request.headers.get("X-User-Id")
    session_id = request.headers.get("X-Session-Id")
    if request.url.path != "/health" and not user_id:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Missing X-User-Id header",
                "hint": "Send X-User-Id per request (Option A identity strategy).",
            },
        )
    set_request_context(user_id=user_id, session_id=session_id)
    try:
        return await call_next(request)
    finally:
        clear_request_context()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
