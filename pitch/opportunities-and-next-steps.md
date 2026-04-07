# Opportunities and next steps

## Near-term product opportunities

- **Richer calendar intelligence** — Factor existing Google events into `estimate_day_plan` automatically (today: agents can read calendar; deeper fusion would subtract busy time from “available minutes” in the formula layer).
- **Mirroring / sync policies** — User-defined rules (“every Firestore `meeting` task also creates a Calendar hold”) for fewer manual splits between stores.
- **Notifications & digests** — Push or email summaries using the same stats (Firebase Cloud Messaging, Gmail API, or Workspace add-ons—future scope).
- **Teams / family** — Shared lists or delegated tasks with permission-scoped OAuth (more complex consent and data model).

## Technical extensions

- **MCP servers** — The hackathon brief mentions MCP (e.g. calendar, notes). This repo integrates Google via **native Python clients** and ADK tools; wrapping or adding **MCP** would align wording with the spec and could unify third-party tools.
- **Evals & guardrails** — Regression tests for tool routing (Firestore vs Google), structured outputs for plan JSON, and red-team prompts for “claimed success without tool call.”
- **Mobile / PWA** — Thin client over existing FastAPI + session headers; ADK Web already supports interactive demos.

## Business / GTM angles (high level)

- **Knowledge workers and students** with chronic overcommitment and context switching.
- **Coaching and wellness adjacency**—position as “capacity coach” rather than full project management (avoid competing head-on with Asana/Jira on day one).
- **B2B** — Same engine behind a Workspace-integrated assistant for small teams (OAuth + admin approval story).

## Research and ethics

- **Transparency** — Keep the behavioral formula explainable; avoid black-box “trust score.”
- **Privacy** — User OAuth tokens and task content are sensitive; Secret Manager, minimal retention, and clear data boundaries are part of a credible pitch.

## Closing line for Q&A

> The core is **proven patterns** (stats + multi-agent tools + Google APIs) with a **clear path** to deeper calendar-aware planning and optional MCP—without changing the fundamental USP: **protect energy through realistic load modeling**.
