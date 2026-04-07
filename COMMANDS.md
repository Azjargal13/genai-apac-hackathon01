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

### Where the OAuth client JSON comes from (Google Cloud Console)

Use the **same GCP project** where you enabled Tasks API + Calendar API.

1. Open [Google Cloud Console](https://console.cloud.google.com/) and select your project (top bar).
2. **APIs & Services** → **Credentials** (left menu).
3. **+ Create credentials** → **OAuth client ID**.
4. If asked for a **consent screen** first: see **Demo: Testing mode** below, then return to Credentials.
5. **Application type:** choose **Desktop app** (name it anything, e.g. `energy-task-demo`).
6. **Create** → **Download JSON** (arrow icon). That file is your client secret JSON.

### Demo: OAuth consent in **Testing** (only you / invited testers)

For a **hackathon or internal demo**, keep the app **unpublished** so random users cannot sign in—only accounts you allow.

1. **APIs & Services** → **OAuth consent screen** (not Credentials).
2. **User type:** **External** is fine (unless you use a Workspace-only internal option).
3. **Publishing status:** leave **Testing** (do **not** click *Publish app* unless you go through Google verification).
4. **Test users:** **+ Add users** → add the **exact Gmail address(es)** that will run `google_oauth_login.py` and the demo (yourself only is OK). Only these accounts can complete consent while status is Testing (Google limit ~100 test users).
5. Save scopes as needed (Tasks + Calendar are requested at login time by the script).

Anyone **not** listed as a test user will see an error when trying to authorize—good for “showcase only.” For production you’d publish + verify the app; that’s out of scope for a quick demo.

Put the client JSON in the repo (do **not** commit):

```bash
mkdir -p secrets
# Save the downloaded file as e.g. secrets/oauth-client.json
```

In **`.env`** (repo root):

```env
GOOGLE_OAUTH_CLIENT_SECRETS_PATH=secrets/oauth-client.json
GOOGLE_OAUTH_TOKEN_PATH=secrets/token.json
```

Then run:

```bash
export PYTHONPATH="${PWD}/src"
python scripts/google_oauth_login.py
```

**Why the browser goes to `accounts.google.com` first, then `localhost`:**  
Sign-in always happens on Google. The `redirect_uri=http://localhost:PORT` in that long URL is where Google sends you **after** you click Allow so your app can read the `code`. **Desktop OAuth clients must use loopback** (`localhost` / `127.0.0.1`); you cannot “remove localhost” without switching to a **Web** OAuth client and a public HTTPS redirect URL.

**Codespaces / `MismatchingStateError`:** use paste mode (no redirect server):

```bash
export PYTHONPATH="${PWD}/src"
python scripts/google_oauth_login.py --paste
```

Or set `OAUTH_PASTE_REDIRECT=1`. After consent, copy the **full** URL from the address bar (even if the page errors) and paste into the terminal.

**If Google sign-in never appears**

- The script always prints `Please visit this URL to authorize...` — open **that** `https://accounts.google.com/...` link in your browser (auto-open often fails on **Codespaces**, **SSH**, or **headless**).

**Codespaces: blank page after “Allow” on `localhost`**

- Google redirects to `http://localhost:PORT/?code=...` on **your laptop**. That port must tunnel to the container **before** you finish consent.
- This repo uses a **fixed port `55555`** for the redirect when `CODESPACE_NAME` is set (override with `OAUTH_REDIRECT_PORT`). **`.devcontainer`** pre-lists **55555** — check **Ports** and forward it, **then** open the Google URL and approve.
- If 55555 is busy, set `OAUTH_REDIRECT_PORT=55666` in `.env`, forward **55666**, and re-run the script.
- **Easiest bypass:** run `google_oauth_login.py` on your **local PC** once, then copy `secrets/token.json` into the Codespace.

**Local machine:** set `OAUTH_NO_BROWSER=1` and use the printed URL only if the browser does not open.

**`ERR_CONNECTION_REFUSED` on localhost after Google**

- The terminal running `python scripts/google_oauth_login.py` must **still be running** (waiting). **Do not Ctrl+C** until you see `Saved credentials`. A venv is optional; what matters is that **this Python process** is listening.
- **Codespaces:** in **Ports**, the redirect port (default **55555**) must show as **forwarded** to your laptop before you finish the Google consent screen.
- If it keeps failing: run the script **on your local PC** once, then copy `secrets/token.json` into the remote environment.

**`MismatchingStateError` / CSRF state not equal**

- The script skips spurious first hits (port probe / favicon) and only accepts a callback that contains `?code=`. It also avoids corrupting `iss=https://...` in the query string. Use **one** fresh run (don’t reuse an old Google URL). If it still fails, use **`--paste`** (above).

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
