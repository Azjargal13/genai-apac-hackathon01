# Command cheat sheet

Copy-paste reference. Run from **repository root** unless noted. On Windows Git Bash/WSL, paths and `export` work the same.

---

## Setup

```bash
cp .env.example .env
# Edit .env (never commit real secrets)

pip3 install --user -r requirements.txt
# or: pip install -r requirements.txt  (inside a venv)

export PYTHONPATH="${PWD}/src"
```

**Optional venv (Linux/macOS/Codespaces):**

```bash
bash scripts/bootstrap-venv.sh
source .venv/bin/activate
pip install -r requirements.txt
```

---

## ADK (demo / CLI chat)

From repo root:

```bash
cd src
adk run energy_task_manager
```

**Web UI:**

```bash
cd src
adk web --port 8000
```

Forward port **8000** in the Ports panel (Codespaces). Package entry: `energy_task_manager` → `root_agent` in `agent.py`.

---

## FastAPI (local API)

From repo root:

```bash
export PYTHONPATH="${PWD}/src"
uvicorn energy_task_manager.main:app --host 0.0.0.0 --port 8080
```

Forward **8080** (Codespaces). Check **`GET /health`**.

---

## Google OAuth (Tasks / Calendar token)

Prereqs: Desktop OAuth client JSON in `secrets/`, vars in `.env` — see [GOOGLE_TASKS_CALENDAR.md](GOOGLE_TASKS_CALENDAR.md).

```bash
export PYTHONPATH="${PWD}/src"
python scripts/google_oauth_login.py
```

**If Google sign-in never appears**

- The script always prints `Please visit this URL to authorize...` — open **that** `https://accounts.google.com/...` link in your browser (auto-open often fails on **Codespaces**, **SSH**, or **headless**).
- **Codespaces:** open the **Ports** tab and forward the **localhost port** printed next to the redirect URL (`http://localhost:XXXX/`), then complete sign-in so the redirect reaches the container.
- **Local machine:** set `OAUTH_NO_BROWSER=1` and use the printed URL only.

**Check token visible to the app:**

```bash
export PYTHONPATH="${PWD}/src"
python -c "from dotenv import load_dotenv; load_dotenv(); from energy_task_manager.integrations.google_oauth import google_oauth_configured; print('oauth_ok:', google_oauth_configured())"
```

---

## API examples (`curl`)

Assumes API at `http://localhost:8080` and headers as in `.env` / README.

**Create task**

```bash
curl -X POST "http://localhost:8080/task" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: beta-user-1" \
  -H "X-Session-Id: s1" \
  -d '{"title":"Write architecture overview"}'
```

**Complete task**

```bash
curl -X POST "http://localhost:8080/task/<task_id>/complete" \
  -H "X-User-Id: beta-user-1" \
  -H "X-Session-Id: s1"
```

**Plan day**

```bash
curl -X POST "http://localhost:8080/plan" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: beta-user-1" \
  -d '{"total_available_time_minutes":360}'
```

**Smoke script** (with API running):

```bash
bash scripts/smoke_test.sh
```

---

## Git

```bash
git status
git add -A
git commit -m "Describe change"
git push origin main
```

---

## Deploy / GCP (see [CLOUD_DEPLOY.md](CLOUD_DEPLOY.md))

**Enable APIs (example):**

```bash
gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com iam.googleapis.com
```

**OAuth token → Secret Manager → Cloud Run (example):**

```bash
gcloud secrets create google-user-oauth-token --data-file=secrets/token.json
gcloud run services update YOUR_SERVICE \
  --set-secrets=GOOGLE_OAUTH_TOKEN_JSON=google-user-oauth-token:latest \
  --region=YOUR_REGION
```

---

## Env vars (reminder)

| Variable | Purpose |
|----------|---------|
| `ADK_MODEL` | Gemini model id for agents |
| `ADK_MAX_OUTPUT_TOKENS` / `ADK_TEMPERATURE` | Shorter, steadier replies |
| `GOOGLE_CLOUD_PROJECT` / `FIRESTORE_DATABASE_ID` | Firestore |
| `GOOGLE_APPLICATION_CREDENTIALS` | SA JSON (local/Codespaces; not needed on Cloud Run with IAM) |
| `GOOGLE_OAUTH_*` | User token for Google Tasks/Calendar |

Full list: [.env.example](.env.example).

---

## Deeper docs

| Topic | File |
|--------|------|
| Codespaces | [CODESPACES.md](CODESPACES.md) |
| Cloud Build / Run | [CLOUD_DEPLOY.md](CLOUD_DEPLOY.md) |
| Firestore | [FIREBASE_SETUP.md](FIREBASE_SETUP.md) |
| Google Tasks + Calendar | [GOOGLE_TASKS_CALENDAR.md](GOOGLE_TASKS_CALENDAR.md) |
