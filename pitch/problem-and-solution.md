# Problem and solution

## Problem

- Task lists grow faster than available time and energy. Users **overcommit** because tools rarely connect **estimated effort** to **real completion behavior**.
- Classic task managers are **passive storage**: they do not learn duration patterns or flag **overload** before the day collapses.
- Assistants that only chat or only use one datastore miss **where users actually live**: **Google Calendar** (time blocks, calls, meetings) and **Google Tasks** (quick capture)—separate from any app-specific backlog.

## Insight

> Planning fails when it ignores **how long this user** finishes work and **what is already on their calendar**.

## Solution (this project)

1. **Behavioral time modeling** — Uses completion history to drive a transparent estimate (see README for the core formula and `estimate_day_plan` tool). Surfaces **overload risk** and **actionable choices**, not just a longer to-do list.
2. **Multi-agent design** — **Orchestrator** routes intent; **Insight** agent focuses on workload, stats, and planning language; **Execution** agent performs CRUD and integrations. Clear separation matches how judges expect “coordination between agents.”
3. **Dual persistence** — **Firestore** holds structured app tasks, categories, and stats for the energy model. **Google Tasks + Calendar APIs** mirror real user workflows so the solution is demonstrably connected to **Google’s ecosystem**, not an isolated demo DB.

## Outcome for the user

Fewer surprise crunches, earlier rebalance decisions, and one assistant that can both **reason about load** and **write to Google** when that is what the user means.
