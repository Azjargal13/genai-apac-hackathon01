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
| External integration | **Google Calendar API** (Python client; exposed to agents as tools) |
| Deployment | **Google Cloud Run** |
| Local secrets | **`.env`** (not committed); copy from `.env.example` |
| Production secrets | **Secret Manager** + Cloud Run env / volume references |

---

## 📁 Repository layout

```text
hackathon01/
├── src/
│   └── energy_task_manager/     # Python package (install with pip -e . or PYTHONPATH)
│       ├── main.py              # FastAPI app entry (Cloud Run target)
│       ├── api/                 # Routers, Pydantic models
│       │   └── routes/
│       ├── agents/              # ADK root + sub-agents (orchestrator, insight, execution)
│       ├── tools/               # ADK tools (Firestore ops, calendar, validation)
│       ├── integrations/        # Google Calendar API client code
│       └── persistence/         # Firestore repositories & schemas
├── tests/
├── .env.example                 # Variable names only (no real secrets)
├── Dockerfile                   # (add when containerizing for Cloud Run)
└── requirements.txt or pyproject.toml   # (add when pinning dependencies)
```

Diagrams and problem statement stay at repo root (`multi-agent-architecture.drawio`, `PROBLEM_STATEMENT.md`).

---

## ⚙️ API Endpoints

### Add Task

```
POST /task
```

### Complete Task

```
POST /task/{id}/complete
```

### Plan Day

```
POST /plan
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
