# Push to GitHub → Cloud Build → Cloud Run

Use **GitHub Codespaces** (see [CODESPACES.md](CODESPACES.md)) or any machine to edit, **`git push`** to your default branch, and **Google Cloud Build** builds the `Dockerfile` and deploys to **Cloud Run**.

## 1. Develop remotely (Codespaces)

1. In GitHub: **Code → Codespaces → Create codespace** on this repo.
2. After the container starts, install deps if the devcontainer did not finish:  
   `pip install -r requirements.txt`  
   (or rely on **postCreateCommand** from `.devcontainer/devcontainer.json`.)
3. Set secrets in the Codespace (or **Settings → Secrets** for the repo): e.g. `GOOGLE_API_KEY` from `.env.example` guidance.
4. Run ADK / FastAPI locally in the Codespace terminal as you build out the app (`adk run …`, `uvicorn …`, etc.).

**Persist work:** commit and **`git push`** so GitHub is always the source of truth.

---

## 2. One-time Google Cloud setup

Do this once per GCP project (replace IDs/regions as needed).

### APIs

Enable (Console **APIs & Services** or `gcloud services enable …`):

- `cloudbuild.googleapis.com`
- `run.googleapis.com`
- `artifactregistry.googleapis.com`
- `iam.googleapis.com`

### Artifact Registry

Create a Docker repository (name must match `cloudbuild.yaml` default or change the substitution):

- **Repository:** `app` (see `_AR_REPOSITORY` in `cloudbuild.yaml`)
- **Format:** Docker
- **Region:** e.g. `us-central1` (must match `_REGION`)

### Allow Cloud Build to deploy Cloud Run

The Cloud Build **service account** (`PROJECT_NUMBER@cloudbuild.gserviceaccount.com`) needs:

- **Cloud Run Admin** (`roles/run.admin`)
- **Service Account User** on the runtime service account Cloud Run uses (often the default compute SA) — `roles/iam.serviceAccountUser`
- **Artifact Registry Writer** (`roles/artifactregistry.writer`) on the repo’s region/project

In Console: **Cloud Build → Settings** (or IAM) and grant the above, or use `gcloud projects add-iam-policy-binding` / `gcloud artifacts repositories add-iam-policy-binding` as in Google’s docs.

### Connect GitHub to Cloud Build

1. **Cloud Build → Triggers → Connect repository** → choose **GitHub**, install the Cloud Build app, select this repo.
2. **Create trigger**
   - **Event:** Push to branch (e.g. `main`)
   - **Configuration:** Cloud Build configuration file  
     **Location:** `/cloudbuild.yaml`
3. Save. Optional: add substitutions in the trigger UI to override `_REGION`, `_AR_REPOSITORY`, `_SERVICE_NAME` if you did not use the defaults.

First run may fail until IAM and Artifact Registry exist; fix errors in the **Build history** log.

---

## 3. What happens on each push

1. Trigger runs **`cloudbuild.yaml`**.
2. **Docker build** using the repo `Dockerfile`.
3. **Push** image to `REGION-docker.pkg.dev/PROJECT_ID/app/energy-task-manager:SHORT_SHA` (and `:latest`).
4. **`gcloud run deploy`** updates (or creates) the service **`energy-task-manager`**.

After deploy, open the **Cloud Run** URL and hit **`GET /health`** to verify.

---

## 4. Secrets on Cloud Run

Do **not** bake API keys into the image. For production:

- Store values in **Secret Manager** and mount or map them to env vars in the **Cloud Run** service configuration, **or**
- Extend `cloudbuild.yaml` deploy step with `--set-secrets` / `--update-env-vars` once you know the names.

Local/Codespaces **`.env`** stays gitignored; Cloud Run uses GCP secret wiring.

### Google user OAuth token (Tasks / Calendar)

After you run `scripts/google_oauth_login.py` locally or in Codespaces, you have a **`token.json`** (user refresh token + client fields). For Cloud Run:

1. Create a secret whose **value is the full file contents** of `token.json` (one blob; JSON can be minified to one line).
2. Grant the **Cloud Run runtime service account** `roles/secretmanager.secretAccessor` on that secret.
3. On the service, add an environment variable **`GOOGLE_OAUTH_TOKEN_JSON`** referencing the secret (Console: **Edit & deploy new revision** → **Variables & secrets** → **Reference a secret**).

Example (adjust names / region / project):

```bash
gcloud secrets create google-user-oauth-token --data-file=secrets/token.json
gcloud run services update YOUR_SERVICE \
  --set-secrets=GOOGLE_OAUTH_TOKEN_JSON=google-user-oauth-token:latest \
  --region=YOUR_REGION
```

The application reads `GOOGLE_OAUTH_TOKEN_JSON` before `GOOGLE_OAUTH_TOKEN_PATH`. Do not commit `token.json`.

---

## 5. Optional: GitHub Actions instead of Cloud Build triggers

Some teams use **GitHub Actions** with **Workload Identity Federation** to call `gcloud run deploy` without storing a JSON key. Either pattern is fine; this repo ships **Cloud Build** as the Google-native path.

---

## Summary

| Step | Where |
|------|--------|
| Edit + run ADK / API | **Codespaces** (or laptop) |
| Source of truth | **GitHub** |
| Build + deploy | **Cloud Build** → **Artifact Registry** → **Cloud Run** |
| Remote dev | **Codespaces** — no separate GCP dev VM required |
