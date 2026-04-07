# Google Calendar and Google Tasks — agent integration

This doc covers **Google Tasks API** and **Google Calendar API** for agents: create, update, and read tasks and events (see **Target** vs **Today** below).

| User intent | Use this API | Where it shows up |
|-------------|--------------|-------------------|
| Task / reminder / to-do the user should complete | **Google Tasks API** | Google Tasks app, Calendar task views |
| Time-blocked meeting or focus block on the grid | **Google Calendar API** (events) | Google Calendar |

**Target:** execution agent writes via Tasks + Calendar; insight agent reads them alongside Firestore. **Today:** agents use Firestore task tools only until steps 2–5 below are implemented.

---

## Authentication

- **Personal Google account:** use **OAuth 2.0** (user signs in). Store refresh token securely (e.g. Secret Manager on Cloud Run).  
  Service accounts **do not** access a normal user’s Tasks/Calendar without **Workspace domain-wide delegation** (org admin setup).
- **Google Workspace:** optional domain-wide delegation for a service account; OAuth is often simpler for demos.

Scopes used in code (`integrations/google_oauth.py`):

- `https://www.googleapis.com/auth/tasks` — Tasks read/write  
- `https://www.googleapis.com/auth/calendar.events` — Calendar events only

### Getting a user token (demo; not Firestore ADC)

Tasks/Calendar need **user OAuth**, separate from the Firestore **service account** (`GOOGLE_APPLICATION_CREDENTIALS` / Cloud Run default SA). **Browser sign-in alone does not create `token.json`.** Use a **Desktop** OAuth client and run `python scripts/google_oauth_login.py` once.

1. Enable **Google Tasks API** and **Google Calendar API** in the GCP project.  
2. Create a **Desktop** client, download JSON → e.g. `secrets/oauth-client.json` (gitignored).  
3. Set `GOOGLE_OAUTH_CLIENT_SECRETS_PATH` and `GOOGLE_OAUTH_TOKEN_PATH` in `.env`, run `google_oauth_login.py` → it writes `token.json`.  
4. **GitHub Codespaces:** forward the **random port** from the script (**Ports** tab), or run login on your laptop and copy `token.json` into `secrets/`.  
5. **Cloud Run:** store the full `token.json` in **Secret Manager**, map to **`GOOGLE_OAUTH_TOKEN_JSON`** ([CLOUD_DEPLOY.md](CLOUD_DEPLOY.md) §4). The app prefers that env var over a file path.

`gcloud auth application-default login` is **ADC** for GCP tooling — **not** a substitute for this token.

Reuse an old `token.json` only if it matches the same OAuth `client_id`; otherwise run `google_oauth_login.py` again.

Do **not** commit `token.json` or client secrets.

### Demo only: OAuth consent **Testing** mode

In Cloud Console → **APIs & Services** → **OAuth consent screen**: keep **Publishing status** as **Testing** and add **Test users** (your Gmail only for a solo demo). While in Testing, **only** those accounts can finish sign-in; others are blocked—ideal for showcasing without opening access to the public. See [COMMANDS.md](COMMANDS.md) for step-by-step with Credentials.

---

## Execution agent — write paths (API design)

- **Tasks:** `tasks.tasks().insert()`, `patch()`, `delete()` on a task list (`tasklist` id; often `@default`).
- **Calendar:** `events.insert()`, `patch()`, `delete()` for timed blocks.

Once wired, Tasks/Calendar are the user-visible source of truth; Firestore can stay for analytics only if you mirror.

---

## Insight agent — read paths (API design)

- **Tasks:** list open tasks, due dates, titles.  
- **Calendar:** list today’s events.  
- **Current tools:** Firestore `list_tasks`, `estimate_day_plan`, `get_user_stats` until Google read tools exist.

---

## Environment variables (suggested)

```env
GOOGLE_OAUTH_CLIENT_SECRETS_PATH=secrets/oauth-client.json
GOOGLE_OAUTH_TOKEN_PATH=secrets/token.json
# Cloud Run / Secret Manager (optional; overrides file when set):
# GOOGLE_OAUTH_TOKEN_JSON=

GOOGLE_TASKS_DEFAULT_LIST_ID=@default
```

---

## Next implementation steps in this repo

1. **OAuth:** `integrations/google_oauth.py` — `GOOGLE_OAUTH_TOKEN_JSON` (Cloud Run) or `GOOGLE_OAUTH_TOKEN_PATH` (file). Run once: `python scripts/google_oauth_login.py`.  
2. Add `integrations/tasks.py` (Tasks API client using `get_google_user_credentials()`).  
3. Add `integrations/calendar.py` (Calendar events client).  
4. Register ADK tools: `create_google_task`, `update_google_task`, `list_google_tasks`, `create_calendar_event`, etc.  
5. Attach those tools to **execution_agent** (writes) and **insight_agent** (reads).

---

## Summary

- **Tasks API** for to-dos and reminders the user completes in Tasks / Calendar.  
- **Calendar API** for events on the calendar grid.
