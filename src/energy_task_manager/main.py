"""FastAPI application entrypoint (Cloud Run serves this module)."""

from fastapi import FastAPI

app = FastAPI(title="Energy-Aware AI Task Manager")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
