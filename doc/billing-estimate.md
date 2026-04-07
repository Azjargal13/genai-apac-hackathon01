# Rough monthly billing estimate (illustrative)

This document gives **order-of-magnitude** USD costs for **about one month** if you use the services aligned with this project. **Your bill will differ** by region, exact SKUs, free tiers, discounts, and how much you actually run things.

**Always verify** with:

- [Google Cloud Pricing Calculator](https://cloud.google.com/products/calculator) for GCP
- [GitHub Codespaces billing](https://docs.github.com/en/billing/managing-billing-for-github-codespaces/about-billing-for-github-codespaces) for dev environments

Generative AI usage (Gemini) is often the **largest variable** and may appear on Google AI Studio / Vertex billing rather than only GCP infrastructure.

---

## Services in scope

| Service | Role in this project |
|---------|----------------------|
| **GitHub Codespaces** | Remote VS Code + Linux: Python, ADK, edit, run, `git push` |
| **Cloud Run** | Host FastAPI / agent HTTP API |
| **Artifact Registry** | Store container images (builds from GitHub) |
| **Cloud Build** | Build Docker image on push (trigger) |
| **Firestore** | Tasks, completions, stats |
| **Secret Manager** | API keys / secrets for Cloud Run |
| **Gemini** | ADK reasoning — **Google AI Studio (API key)** and/or **Vertex AI** |
| **Google Calendar API** | Create/list events (usually negligible vs LLM) |

GitHub **public repos** and typical **Actions** usage for a small team often stay within free allowances; this doc does **not** assume GitHub Actions for deploy (this repo uses **Cloud Build**).

---

## Assumptions used below

- GCP region **us-central1** for Run / Build / Artifact Registry examples; prices vary by region.
- **No Cloud Workstations** (dev is Codespaces per [codespaces.md](codespaces.md)).
- Cloud Run: **low traffic** hackathon API (not always-on high QPS).
- Firestore: **small** dataset and modest read/write rates.
- Gemini: **two illustrative volumes** (light vs heavier prototyping).
- Codespaces: mix of **included allowance** (personal accounts get monthly free use — check current GitHub docs) vs **overage** hours and **storage** for stopped codespaces.

---

## 1. GitHub Codespaces (development)

Billing is **GitHub-side**, not Google Cloud. It depends on:

- **Compute**: core-hours while the codespace is **running**
- **Storage**: provisioned disk for **stopped** codespaces (cheaper than running, but not zero if you keep many large codespaces around)

Official numbers change; see [About billing for GitHub Codespaces](https://docs.github.com/en/billing/managing-billing-for-github-codespaces/about-billing-for-github-codespaces).

**Illustrative monthly bands (not a quote):**

| Pattern | Rough Codespaces cost hint |
|---------|----------------------------|
| **Inside free included minutes** (light solo use, stop when done) | **~$0** |
| **Regular evenings + weekends** beyond allowance | **~$15–60/mo** (highly variable) |
| **Heavy daily use, large machine, always-on habits** | **~$80–200+/mo** |

**Cost levers:** **Stop** the codespace when not coding; **delete** old codespaces you do not need; pick a **smaller** machine type in Codespace settings; rely on **`git push`** so you can recreate from GitHub if needed.

---

## 2. Cloud Run (API)

- Charged for **requests**, **CPU/memory while handling requests**, and **minimum instances** if you set them > 0.
- **Free tier** (region-dependent) often covers **small** demos; many hackathon backends stay in **~$0–25/month** if traffic is low and you do not keep warm instances.

**Illustrative:** **$0–30/month** for light usage; **$50+** if you add always-on minimum instances or steady load.

---

## 3. Firestore

- Strong dependency on **document reads/writes** and **stored data**.
- For a **prototype** with a single user and modest traffic, it is often **within free tier** or **under ~$5–15/month**.

**Illustrative:** **$0–20/month** (wide band if you scale tests or add lots of writes).

---

## 4. Container build & registry (GitHub → Cloud Build → deploy)

- **Cloud Build:** free tier includes **build minutes per day**; small images often stay **low or $0**.
- **Artifact Registry:** storage + egress; small images often **~$0–5/month** unless you store many versions.

**Illustrative:** **$0–10/month** combined for a small project.

---

## 5. Secret Manager

- Secrets and access operations are **cheap** at hackathon scale.

**Illustrative:** **under ~$1–5/month** (often negligible).

---

## 6. Gemini (ADK / multi-agent) — highest uncertainty

Depends on:

- **Model** (Flash vs Pro, thinking vs not),
- **Tokens in + out** per day,
- Whether you bill through **Google AI Studio** (API key) or **Vertex AI**.

**Illustrative only (not a quote):**

| Usage pattern | Rough monthly hint |
|---------------|-------------------|
| **Light** — solo dev, dozens of short turns/day | **~$5–30** |
| **Heavy** — long sessions, Pro model, many tool loops | **~$50–300+** |

Use **AI Studio usage / quotas** or **Vertex billing export** to see real numbers after a week.

---

## 7. Google Calendar API

- Calendar API has **generous free quotas** for normal personal/calendar use.

**Illustrative:** **~$0** unless you hit quota and need billing enabled / higher limits.

---

## Total “all services” ballpark (one month)

Combine **GitHub (Codespaces)** + **GCP (Run, Firestore, Build, registry, secrets)** + **Gemini**. Example scenarios:

| Scenario | Codespaces (illustrative) | Cloud Run | Firestore | Build + Registry + Secrets | Gemini (illustrative) | **Very rough total** |
|----------|---------------------------|-----------|-----------|----------------------------|------------------------|----------------------|
| **Lean hackathon** | ~$0–25 | ~$0–15 | ~$0–5 | ~$0–5 | ~$10–40 | **~$15–90/mo** |
| **Steadier dev + more LLM** | ~$30–80 | ~$15–40 | ~$5–20 | ~$5–15 | ~$50–150 | **~$105–305/mo** |

If **Gemini usage spikes** or you run **many** active codespaces, totals can go **higher** quickly.

---

## After your Codespace is ready

Open a codespace, let dependencies install (or run `pip3 install --user -r requirements.txt`), then start implementing agents (ADK `LlmAgent` graph, tools, Firestore) and the FastAPI surface. **`git push`** triggers your **Cloud Build** pipeline when configured — see [cloud-deploy.md](cloud-deploy.md).

---

## What to do next for accurate numbers

1. **GCP:** **Billing → Budgets & alerts** (e.g. alert at $50 / $150).
2. **GCP:** [Pricing Calculator](https://cloud.google.com/products/calculator) — Run, Firestore, Build, Artifact Registry (skip Workstations if unused).
3. **GitHub:** Organization/account billing → **Codespaces** usage and included minutes.
4. **Gemini:** AI Studio or Vertex usage dashboards weekly during development.

---

*Figures are estimates, not a quote. Google and GitHub may change prices; see official pages for current SKUs.*
