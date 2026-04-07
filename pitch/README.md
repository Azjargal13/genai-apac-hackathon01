# Pitch pack — Energy-Aware AI Task Manager

Use this folder when preparing demos, slides, or judge Q&A. Each file is short on purpose; the main [README.md](../README.md) stays the full project reference.

| Document | Use for |
|----------|---------|
| [problem-and-solution.md](problem-and-solution.md) | Opening: pain, insight, what we built |
| [usp-and-differentiators.md](usp-and-differentiators.md) | Why us vs generic task bots |
| [tech-stack.md](tech-stack.md) | Engineering depth, how it hangs together |
| [google-services.md](google-services.md) | Google Cloud / APIs / ADK story |
| [opportunities-and-next-steps.md](opportunities-and-next-steps.md) | Roadmap, business, extensions |
| [diagrams/](diagrams/) | **Use-case** + **process flow** (Mermaid; export to PNG for slides) |

---

## ~45 second elevator pitch

Most people do not fail to plan—they fail to plan against **reality**. Generic assistants add tasks; they do not learn how long **you** actually take or whether today’s plan fits your **real** calendar and energy.

We built a **multi-agent** system on **Google ADK** and **Gemini**: an **Insight** agent does behavioral time modeling and overload detection; an **Execution** agent writes to **Firestore** for in-app planning **and** to the user’s real **Google Tasks** and **Google Calendar** via OAuth—so the demo is not a silo, it touches **live** Google surfaces.

**One line:** *AI that does not just manage tasks—it estimates load from your history, warns before overload, and syncs actions to Google Tasks and Calendar.*

---

## Suggested live demo flow (3–4 minutes)

1. **Context:** “I have six hours today—how does my plan look?” → Insight path, formula + capacity fit.
2. **Google:** “Remind me to call Alex tomorrow at 4pm” → Calendar event (or task if checklist-style).
3. **App:** “Add deep-work block for the proposal” → Firestore task with category (shows dual store).
4. **Optional:** Complete a task → stats update → show personalization.

Close with deployment: **Cloud Run**, **Firestore**, **Secret Manager** for tokens—production-shaped hackathon build.

---

## Repo pointers for judges

- Architecture & features: [README.md](../README.md)
- Google Tasks + Calendar integration: [GOOGLE_TASKS_CALENDAR.md](../GOOGLE_TASKS_CALENDAR.md)
- Hackathon requirements alignment: [PROBLEM_STATEMENT.md](../PROBLEM_STATEMENT.md)
- Deploy path: [CLOUD_DEPLOY.md](../CLOUD_DEPLOY.md)
