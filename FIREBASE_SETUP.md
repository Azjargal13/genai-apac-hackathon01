# Firebase / Firestore setup guide

This project uses **Cloud Firestore** as the database. This guide covers what to configure for:

- local development in **Codespaces**
- runtime on **Cloud Run**
- common Firebase/Firestore gotchas

---

## 1) Decide: Firebase project + Firestore location

1. Use one Google Cloud project (same project you deploy Cloud Run into).
2. In Firebase Console, add the project if needed.
3. Create **Firestore (Native mode)** database.
4. Choose region carefully (cannot be changed later):
   - best practice: same region as Cloud Run (or closest practical region)
   - example: `asia-northeast3` or `us-central1`

---

## 2) Enable required APIs

In Google Cloud Console, enable:

- `firestore.googleapis.com`
- `cloudresourcemanager.googleapis.com` (normally already enabled)

If you deploy with Cloud Build/Run, you already also need:

- `run.googleapis.com`
- `artifactregistry.googleapis.com`
- `cloudbuild.googleapis.com`

---

## 3) Local auth in Codespaces (for Firestore client)

You have two practical options:

### Option A (recommended for quick setup): ADC via `gcloud auth application-default login`

In Codespaces terminal:

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

Then set in `.env`:

```bash
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
```

### Option B: service account key JSON (less preferred)

1. Create a service account with Firestore access.
2. Download JSON key (sensitive).
3. In `.env`:

```bash
GOOGLE_APPLICATION_CREDENTIALS=/workspaces/<repo>/secrets/firebase-sa.json
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
```

Never commit key files.

---

## 4) Cloud Run auth (production/staging)

Cloud Run should use **service identity**, not a JSON key:

1. Pick Cloud Run runtime service account (custom SA recommended).
2. Grant Firestore access role:
   - `roles/datastore.user` (read/write app access)
3. Deploy service with that service account.

No `GOOGLE_APPLICATION_CREDENTIALS` needed in Cloud Run when IAM is set correctly.

---

## 5) Environment variables to define

In local `.env` (and Cloud Run env/secrets as needed):

- `GOOGLE_CLOUD_PROJECT` = GCP project ID
- `FIRESTORE_DATABASE_ID` = Firestore DB name (default is `(default)`)
- Optional local key-based auth:
  - `GOOGLE_APPLICATION_CREDENTIALS`

If you keep only one Firestore DB, `(default)` is fine.

---

## 6) Firestore data model starter (recommended)

Suggested collections:

- `tasks`
  - `id`, `title`, `status`, `estimated_minutes`, `created_at`, `completed_at`, `user_id`
- `task_events`
  - append-only log for create/update/complete actions
- `user_stats`
  - running aggregates (`avg_task_minutes`, `tasks_completed`, `last_updated`)

This keeps insight calculations straightforward and auditable.

---

## 7) Security rules and access model

For this backend-driven architecture:

- primary access path is backend (Cloud Run) using IAM
- if you are **not** exposing direct client SDK access, rules can remain strict/minimal

If later you add direct Firebase client access (web/mobile), define explicit Firestore Security Rules per user/session.

---

## 8) Quick connectivity test (Python)

Once credentials/project are configured:

```python
from google.cloud import firestore

db = firestore.Client(project="YOUR_PROJECT_ID")
print([c.id for c in db.collections()])
```

If this fails with permission/auth errors, check:

- active project (`gcloud config get-value project`)
- ADC (`gcloud auth application-default print-access-token`)
- IAM role on runtime service account (`roles/datastore.user`)

---

## 9) Common issues checklist

- Region mismatch between Cloud Run and Firestore (latency)
- Missing `GOOGLE_CLOUD_PROJECT`
- Using key JSON in Cloud Run unnecessarily
- Not granting Firestore role to Cloud Run service account
- Trying to change Firestore location after creation (not supported)

---

## 10) Minimum config summary

For your current project, minimum is:

1. Firestore Native DB created in your chosen region
2. `GOOGLE_CLOUD_PROJECT` set
3. Codespaces authenticated via ADC
4. Cloud Run runtime SA has `roles/datastore.user`

After this, you can start implementing `src/energy_task_manager/persistence/firestore.py`.
