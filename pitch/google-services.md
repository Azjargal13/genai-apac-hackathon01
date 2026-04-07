# Google services and platform story

This section is optimized for “why Google” and “what did you use from Google” questions.

## Google AI / developer surface

| Service | Role in the project |
|---------|---------------------|
| **Google Agent Development Kit (ADK)** | Defines **root_agent**, **insight_agent**, **execution_agent**; binds **tools** (functions) to Gemini for grounded actions. |
| **Gemini** | Reasoning, routing, natural-language planning dialogue, tool selection. |

## Google Workspace APIs (user OAuth)

| API | Scope (conceptually) | What we do |
|-----|----------------------|------------|
| **Google Tasks API** | User task lists and tasks | List lists/tasks; create, update, complete, delete tasks on the user’s account. |
| **Google Calendar API** | Events on primary calendar | List upcoming events; create, patch, delete timed events. |

**Why it matters for the pitch:** Judges can see items appear in **familiar Google products**, not only in a custom UI—strong “integration” proof.

## Google Cloud Platform (GCP)

| Service | Role |
|---------|------|
| **Cloud Firestore** | Durable structured storage for app tasks, completion events, and aggregate user statistics used by the time model. |
| **Cloud Run** | Runs the FastAPI container serverlessly; scales to zero friendly for demos. |
| **Cloud Build** | CI/CD from GitHub: build image on push, deploy to Run (see [CLOUD_DEPLOY.md](../CLOUD_DEPLOY.md)). |
| **Secret Manager** (recommended) | Store `GOOGLE_OAUTH_TOKEN_JSON` and other secrets for production; referenced from Run. |
| **IAM / service accounts** | Firestore access from API runtime; separate from end-user OAuth. |

## Optional talking points

- **Vertex AI** — If ADK is configured with `GOOGLE_GENAI_USE_VERTEXAI`, tie the story to enterprise Gemini on GCP.
- **Firebase** — Firestore is often provisioned via a Firebase project; [FIREBASE_SETUP.md](../FIREBASE_SETUP.md) documents the link.
- **Testing OAuth** — Consent screen in **Testing** mode with explicit test users is appropriate for hackathon demos ([GOOGLE_TASKS_CALENDAR.md](../GOOGLE_TASKS_CALENDAR.md)).

## One-liner for slides

> **Gemini + ADK** for multi-agent reasoning; **Firestore** for behavioral analytics; **Tasks + Calendar APIs** so the assistant writes where users already work; **Cloud Run** to ship it like a product.
