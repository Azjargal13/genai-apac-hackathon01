FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .
RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -r requirements.txt

COPY src/ /app/src/
ENV PYTHONPATH=/app/src

# Cloud Run sets PORT; default 8080 for local docker run
CMD ["sh", "-c", "exec uvicorn energy_task_manager.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
