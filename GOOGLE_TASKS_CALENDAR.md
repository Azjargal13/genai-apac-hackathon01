# Google Calendar and Google Tasks — agent integration

This doc covers **Google Tasks API** and **Google Calendar API** for agents: create, update, and read tasks and events (see **Target** vs **Today** below).

| User intent | Use this API | Where it shows up |
|-------------|--------------|-------------------|
| Task / reminder / to-do the user should complete | **Google Tasks API** | Google Tasks app, Calendar task views |
| Time-blocked meeting or focus block on the grid | **Google Calendar API** (events) | Google Calendar |

**Implemented:** `integrations/tasks.py` and `integrations/calendar.py` call the APIs; ADK tools live in `tools/google_tools.py` (prefixed `*_google_*` to avoid clashing with Firestore `list_tasks` / `create_task`). **execution_agent** has full Google Tasks + Calendar CRUD plus Firestore tools; **insight_agent** reads Google Tasks + Calendar plus Firestore stats/plan tools.

---

## Authentication

- **Personal Google account:** use **OAuth 2.0** (user signs in). Store refresh token securely (e.g. Secret Manager on Cloud Run).  
  Service accounts **do not** access a normal user’s Tasks/Calendar without **Workspace domain-wide delegation** (org admin setup).
- **Google Workspace:** optional domain-wide delegation for a service account; OAuth is often simpler for demos.

Scopes used in code (`integrations/google_oauth.py`):

- `https://www.googleapis.com/auth/tasks` — Tasks read/write  
- `https://www.googleapis.com/auth/calendar.events` — Calendar events only

### Getting a user token (demo; not Firestore ADC)

Tasks/Calendar need **user OAuth** (not the Firestore SA). Use a **Desktop** client JSON + `python scripts/google_oauth_login.py`. **Paste method:** after consent, paste the full `http://localhost:...?code=...` from the address bar (default in Codespaces; see [COMMANDS.md](COMMANDS.md)).

1. Enable **Google Tasks API** and **Google Calendar API**.  
2. Desktop client → save JSON e.g. `secrets/oauth-client.json`.  
3. `.env`: `GOOGLE_OAUTH_CLIENT_SECRETS_PATH`, `GOOGLE_OAUTH_TOKEN_PATH` → run the script → `token.json`.  
4. **Cloud Run:** `GOOGLE_OAUTH_TOKEN_JSON` from Secret Manager ([CLOUD_DEPLOY.md](CLOUD_DEPLOY.md) §4).

Do **not** commit `token.json` or client secrets. ADC (`gcloud auth application-default login`) is not this token.

### Demo only: OAuth consent **Testing** mode

In Cloud Console → **APIs & Services** → **OAuth consent screen**: keep **Publishing status** as **Testing** and add **Test users** (your Gmail only for a solo demo). While in Testing, **only** those accounts can finish sign-in; others are blocked—ideal for showcasing without opening access to the public. See [COMMANDS.md](COMMANDS.md) for step-by-step with Credentials.

---

## Execution agent — tools

- **Firestore:** `create_task`, `complete_task`, `get_task`, `list_tasks`, `get_user_stats`.  
- **Google Tasks:** `list_google_task_lists`, `list_google_tasks`, `create_google_task`, `update_google_task`, `complete_google_task`, `delete_google_task`.  
- **Google Calendar:** `list_google_calendar_events`, `create_google_calendar_event`, `update_google_calendar_event`, `delete_google_calendar_event`.

Underlying API calls: Tasks `insert` / `patch` / `delete`; Calendar `events.insert` / `patch` / `delete` on `primary`.

---

## Insight agent — tools

- **Firestore:** `list_tasks`, `get_user_stats`, `estimate_day_plan`.  
- **Google (read):** `list_google_tasks`, `list_google_calendar_events`.

---

## Environment variables (suggested)

```env
GOOGLE_OAUTH_CLIENT_SECRETS_PATH=secrets/oauth-client.json
GOOGLE_OAUTH_TOKEN_PATH=secrets/token.json
# Cloud Run / Secret Manager (optional; overrides file when set):
# GOOGLE_OAUTH_TOKEN_JSON=

GOOGLE_TASKS_DEFAULT_LIST_ID=@default
GOOGLE_CALENDAR_TIMEZONE=Asia/Ulaanbaatar
```

---

## Checklist (repo)

1. **OAuth:** `integrations/google_oauth.py` + `scripts/google_oauth_login.py`.  
2. **Integrations:** `integrations/tasks.py`, `integrations/calendar.py` — smoke-test with `scripts/test_google_tokens.py`.  
3. **ADK:** `tools/google_tools.py` + exports in `tools/__init__.py`; agents in `agents/execution.py` and `agents/insight.py`.

---

## Summary

- **Tasks API** for to-dos and reminders the user completes in Tasks / Calendar.  
- **Calendar API** for events on the calendar grid.
