# Architecture and tech stack

## High-level architecture

```text
User (ADK Web / CLI or API clients)
        │
        ▼
┌───────────────────┐
│  Root agent (ADK) │  intent routing, brevity / structure rules
└─────────┬─────────┘
          │
    ┌─────┴─────┐
    ▼           ▼
┌─────────┐ ┌─────────────┐
│ Insight │ │ Execution   │
│ agent   │ │ agent       │
└────┬────┘ └──────┬──────┘
     │             │
     │ tools       │ tools
     ▼             ├──────────────────────────────┐
 Firestore        ▼                              ▼
 planning &   Firestore CRUD              Google Tasks API
 stats        (tasks, complete,           Google Calendar API
              list, get, stats)            (OAuth user token)
```

## Stack table

| Layer | Technology |
|--------|------------|
| Agents & orchestration | **Google ADK** (`LlmAgent`, sub-agents) |
| LLM | **Gemini** (model via `ADK_MODEL`, e.g. `gemini-3-flash-preview`; Vertex or API per env) |
| Structured app data | **Cloud Firestore** (tasks, completions, user stats) |
| HTTP API | **FastAPI** + **Uvicorn** |
| Google user data | **Google Tasks API v1**, **Calendar API v3** (`google-api-python-client`) |
| Auth (user) | **OAuth 2.0** desktop flow, token file or `GOOGLE_OAUTH_TOKEN_JSON` |
| Auth (GCP) | **Application Default Credentials** / service account for Firestore |
| Language | **Python 3** |
| Container & deploy | **Dockerfile**, **Google Cloud Run**, **Cloud Build** (`cloudbuild.yaml`) |
| Dev environment | **GitHub Codespaces** + `.devcontainer` (optional) |

## Repository layout (pitch shorthand)

- `src/energy_task_manager/agents/` — root, insight, execution agent definitions and model config.
- `src/energy_task_manager/tools/` — ADK tools: Firestore operations + `google_tools.py` (Tasks/Calendar with `HttpError` handling).
- `src/energy_task_manager/integrations/` — OAuth, Tasks, Calendar clients.
- `src/energy_task_manager/persistence/` — Firestore repository and schemas.
- `src/energy_task_manager/api/` — REST routes for tasks and plan (parallel to ADK demo).

## Multi-step workflows

Agents chain **tool calls**: list/read stats → estimate plan → optional create/complete task or Google write. The orchestrator can delegate follow-ups without repeating long templated answers (token-efficient behavior encoded in instructions).

## Alignment with hackathon brief

From [PROBLEM_STATEMENT.md](../PROBLEM_STATEMENT.md): primary agent + sub-agents, structured database, multiple tools, multi-step workflows, API-based deployment—each is reflected in the above architecture.
