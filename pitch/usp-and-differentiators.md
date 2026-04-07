# USP and differentiators

## Unique selling proposition (USP)

**Energy- and capacity-aware planning tied to real Google Tasks and Calendar—not a generic chatbot with a hidden database.**

The product story is **decision support**: learn from behavior, estimate feasibility, warn on overload, then **act** in the right system (app store vs Google) based on natural language.

## Differentiators

| Theme | What we do |
|--------|------------|
| **Personalized time math** | Estimates use **your** completion history (`get_user_stats`, `estimate_day_plan`), not static defaults. |
| **Overload as a first-class output** | Explicit capacity fit, ratio, and suggestions—not only “here are your tasks.” |
| **Real Google surfaces** | OAuth to **Google Tasks** and **Calendar**; create/update/list tools agents call intentionally (vs claiming sync without API proof). |
| **Multi-agent orchestration** | Orchestrator + Insight + Execution matches hackathon “primary + sub-agents” narrative with clear roles. |
| **Production-shaped stack** | **FastAPI** API, **Firestore**, **Cloud Run**, **Cloud Build**, secrets pattern—credible path beyond the demo. |
| **Transparent formula** | The core relationship between available time, completed tasks, and per-task estimate is **explainable** to users and judges. |

## One-sentence competitor contrast

> Unlike flat task CRUD or a single LLM with no memory model, we combine **learned duration behavior**, **overload detection**, and **native Google task/calendar writes** behind a routed multi-agent flow.
