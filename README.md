# ⚡ Energy-Aware AI Task Manager

> **AI that doesn’t just manage tasks — it protects your energy.**

---

## 🧠 Overview

Most task managers assume users have unlimited time and energy.

This system takes a different approach:

> It learns how long tasks actually take for you and prevents overplanning.

Instead of just organizing tasks, it provides **personalized decision support**:

* Detects overload
* Estimates realistic workload
* Suggests better plans

---

## 🎤 Pitch

Most people do not fail to plan. They fail to plan against reality.

This system helps users who tend to overestimate their capacity and underestimate how long tasks actually take.  
It learns from real completion behavior, estimates realistic workload, and gives concrete, friendly planning insights so users can adjust early and avoid burnout.

Instead of acting like a task database, it acts like a decision-support coach:

- Shows current load in plain language
- Shows whether today's plan is a good fit for available time and energy
- Suggests clear choices (reduce scope, spread work, or continue)

---

## 🚀 Core Idea

> **Behavioral Time Modeling**

The system observes:

* how many tasks you complete
* how long you take

Then it estimates:

```
estimated_time_per_task = total_available_time / tasks_completed
```

Using this, it can:

* predict workload
* detect burnout risk
* suggest smarter schedules

---

## 🏗️ Architecture

### 🧠 Primary Agent — Orchestrator

* Understands user intent
* Routes requests to sub-agents
* Handles clarification & suggestions

---

### 📊 Insight Agent (Core Intelligence)

* Retrieves task data
* Calculates:

  * average task duration
  * total workload
* Detects:

  * overload
  * imbalance
* Generates personalized insights

---

### ⚡ Execution Agent

* Creates / updates tasks
* Marks tasks complete
* Uses **Google Calendar API** for meetings / time blocks (via tools)
* Validates actions before execution

---

### 🗄️ Data Layer

**Firestore** for:

* tasks
* completion timestamps
* user statistics (avg task duration)

---

## 🔄 System Flow

### 1. Add Task

```
User → Orchestrator → Execution Agent → DB
```

---

### 2. Complete Task

```
User → Execution Agent → DB
→ Insight Agent updates behavior model
```

---

### 3. Plan Day (Key Feature)

```
User → Orchestrator → Insight Agent
→ workload estimation → response
```

---

## ✨ Example Interaction

**User:**

> Plan my day

**System:**

> You have 5 tasks.
> You usually spend ~2 hours per task.
> That’s ~10 hours of work.
>
> You typically perform best for ~6 hours.
> This may lead to overload.
>
> Do you want to:
>
> 1. Reduce workload
> 2. Spread tasks across days
> 3. Keep as is

---

## 🎯 Key Features

* ✅ Task creation & completion
* ✅ Workload estimation
* ✅ Overload detection
* ✅ Personalized time modeling
* ✅ Decision support suggestions

---

## 🧩 Tech Stack

| Layer | Choice |
|--------|--------|
| Agents & reasoning | **Google ADK** with **Gemini** (Vertex AI or API per your ADK config) |
| API | **FastAPI** (`uvicorn` on Cloud Run) |
| Database | **Cloud Firestore** |
| External integration | **Google Calendar API** + **Google Tasks API** (see [GOOGLE_TASKS_CALENDAR.md](GOOGLE_TASKS_CALENDAR.md)) |
| Deployment | **Google Cloud Run** (image built by **Cloud Build** on **git push**) |
| Remote dev | **GitHub Codespaces** + `.devcontainer` — see [CODESPACES.md](CODESPACES.md) |
| Local secrets | **`.env`** (not committed); copy from `.env.example` |
| Production secrets | **Secret Manager** + Cloud Run env / volume references |

**Push → deploy:** connect the repo to **Cloud Build** and use [CLOUD_DEPLOY.md](CLOUD_DEPLOY.md) (trigger on `main`, `cloudbuild.yaml` builds `Dockerfile` and deploys to Run).

**Firestore/Firebase config:** see [FIREBASE_SETUP.md](FIREBASE_SETUP.md) for local auth, IAM, env vars, and DB setup.

**Rough monthly cost (GCP + GitHub Codespaces + Gemini):** [BILLING_ESTIMATE.md](BILLING_ESTIMATE.md) (illustrative; use Google’s pricing calculator and GitHub’s Codespaces billing docs for real quotes).

---

## 📁 Repository layout

```text
hackathon01/
├── src/
│   └── energy_task_manager/     # Python package (install with pip -e . or PYTHONPATH)
│       ├── main.py              # FastAPI app entry (Cloud Run target)
│       ├── api/                 # Routers, Pydantic models
│       │   └── routes/
│       │   └── models.py
│       ├── agents/              # ADK root + sub-agents (orchestrator, insight, execution)
│       ├── tools/               # ADK tools (Firestore task + planning tools)
│       ├── integrations/        # OAuth for Google Tasks/Calendar (see GOOGLE_TASKS_CALENDAR.md)
│       └── persistence/         # Firestore repositories & schemas
├── tests/
├── .devcontainer/
│   └── devcontainer.json        # GitHub Codespaces: Python + pip install + PYTHONPATH
├── scripts/
│   ├── google_oauth_login.py    # One-time OAuth → secrets/token.json (see GOOGLE_TASKS_CALENDAR.md)
│   └── bootstrap-venv.sh      # Optional: project .venv (Codespaces or Linux)
├── CODESPACES.md                # Dev environment: GitHub Codespaces + ADK / FastAPI
├── CLOUD_DEPLOY.md              # GitHub → Cloud Build → Cloud Run (one-time setup)
├── FIREBASE_SETUP.md            # Firestore/Firebase setup and auth config
├── GOOGLE_TASKS_CALENDAR.md     # Calendar + Tasks API integration notes
├── SCHEMA.md                    # Firestore collections and field contracts
├── BILLING_ESTIMATE.md          # Rough monthly cost (Codespaces + GCP + Gemini)
├── cloudbuild.yaml              # Build image + deploy Run (used by trigger)
├── Dockerfile                   # Container for Cloud Run
├── .env.example                 # Variable names only (no real secrets)
├── requirements.txt             # Python deps
└── pyproject.toml               # (optional)
```

Diagrams and problem statement stay at repo root (`multi-agent-architecture.drawio`, `PROBLEM_STATEMENT.md`).

---

## ⚙️ API Endpoints

All task endpoints use header-based identity: send `X-User-Id` on each request.  
Optional for tracing/threading: `X-Session-Id`.

For local agent/CLI testing, you can set defaults in `.env`:

```env
DEFAULT_USER_ID=beta-user-1
DEFAULT_SESSION_ID=local-session-1
```

Then requests/tools can resolve identity even when headers are omitted.

### Add Task

```
POST /task
```

`category` and `estimated_minutes` are optional for API compatibility.  
In agent flow, the **agent** is expected to decide both.  
If category is omitted, backend defaults to `others`.  
If `estimated_minutes` is omitted, backend derives it from learned user history
(`user_stats.avg_task_minutes`), with cold-start default `60`.

Category is strictly constrained to schema values only:
`deep_work`, `errand`, `personal`, `admin`, `meeting`, `learning`, `health`, `others`.  
The agent must map user intent into one of these and never invent new category labels.

Example:

```bash
curl -X POST "http://localhost:8080/task" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: beta-user-1" \
  -H "X-Session-Id: s1" \
  -d '{"title":"Write architecture overview"}'
```

### Complete Task

```
POST /task/{id}/complete
```

Example:

```bash
curl -X POST "http://localhost:8080/task/<task_id>/complete" \
  -H "X-User-Id: beta-user-1" \
  -H "X-Session-Id: s1"
```

### Plan Day

```
POST /plan
```

Example body:

```json
{
  "total_available_time_minutes": 360
}
```

Example:

```bash
curl -X POST "http://localhost:8080/plan" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: beta-user-1" \
  -d '{"total_available_time_minutes":360}'
```

### Quick smoke test

With API running on `http://localhost:8080`:

```bash
bash scripts/smoke_test.sh
```

Override defaults if needed:

```bash
BASE_URL=http://localhost:8080 USER_ID=beta-user-1 SESSION_ID=s1 bash scripts/smoke_test.sh
```

---

## 💡 Why This Matters

> People don’t burn out because they don’t plan.
> They burn out because they overcommit.

This system helps users:

* understand their real capacity
* avoid unrealistic schedules
* make better decisions daily

---

## 🏁 Future Improvements

* Energy-aware scheduling (morning vs evening)
* Task categorization (deep vs quick work)
* Deeper Calendar workflows (recurring events, availability sync)
* Adaptive learning over time
* Additional MCP-style or third-party tools beyond Calendar

---

## 🧠 Final Thought

> This is not just a task manager.
> It’s a system that understands human limits — and plans accordingly.

---
