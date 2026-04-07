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

### Option B: service account key JSON (recommended when `gcloud` is unavailable)

1. Create a service account (example: `energy-task-sa`).
2. Grant IAM role: `roles/datastore.user`.
3. Create/download JSON key (sensitive).
4. Place it locally under repo `secrets/` (do not commit).
5. In `.env`:

```bash
GOOGLE_APPLICATION_CREDENTIALS=/workspaces/<repo>/secrets/energy-task-sa-key.json
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
```

If you are on local Windows/Git Bash instead of Codespaces, use an absolute local path, for example:

```bash
GOOGLE_APPLICATION_CREDENTIALS=/c/Users/<you>/Documents/projects/<repo>/secrets/energy-task-sa-key.json
```

Never commit key files (`secrets/` must stay in `.gitignore`).

#### Example IAM binding command

```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:energy-task-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/datastore.user" \
  --condition=None
```

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

## 6) Required composite indexes for this project

The current query patterns in `tasks` require composite indexes.  
Without these, Firestore returns: "The query requires an index".

Create these indexes in Firebase/Firestore Console:

1. Collection: `tasks`
   - Fields:
     - `user_id` ascending
     - `created_at` descending
2. Collection: `tasks`
   - Fields:
     - `status` ascending
     - `user_id` ascending
     - `created_at` descending

Fastest path: when Firestore returns an index URL in API error, open it and click **Create index**.
Wait until status is **Enabled**, then retry requests.

---

## 7) Firestore data model starter (recommended)

Suggested collections:

- `tasks`
  - `id`, `title`, `status`, `estimated_minutes`, `created_at`, `completed_at`, `user_id`
- `task_events`
  - append-only log for create/update/complete actions
- `user_stats`
  - running aggregates (`avg_task_minutes`, `tasks_completed`, `last_updated`)

This keeps insight calculations straightforward and auditable.

---

## 8) Security rules and access model

For this backend-driven architecture:

- primary access path is backend (Cloud Run) using IAM
- if you are **not** exposing direct client SDK access, rules can remain strict/minimal

If later you add direct Firebase client access (web/mobile), define explicit Firestore Security Rules per user/session.

---

## 9) Quick connectivity test (Python)

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

## 10) Common issues checklist

- Region mismatch between Cloud Run and Firestore (latency)
- Missing `GOOGLE_CLOUD_PROJECT`
- Wrong `GOOGLE_APPLICATION_CREDENTIALS` path for your environment (Codespaces vs local)
- Using key JSON in Cloud Run unnecessarily
- Not granting Firestore role to Cloud Run service account
- Missing Firestore composite index for filtered + ordered task queries
- Trying to change Firestore location after creation (not supported)

---

## 11) Minimum config summary

For your current project, minimum is:

1. Firestore Native DB created in your chosen region
2. `GOOGLE_CLOUD_PROJECT` set
3. Valid local auth (ADC or `GOOGLE_APPLICATION_CREDENTIALS`)
4. Required composite indexes for `tasks` created and enabled
5. Cloud Run runtime SA has `roles/datastore.user`

After this, you can start implementing `src/energy_task_manager/persistence/firestore.py`.
