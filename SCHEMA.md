# Data schema (Firestore + API contract)

This file defines the canonical data contract for the task manager.  
Agents and tools should follow this schema instead of inventing fields dynamically.

---

## Collections

## `tasks`

Document ID: `task_id` (string, UUID recommended)

Required fields:

- `user_id` (string)
- `title` (string, 1..200)
- `status` (enum: `todo`, `in_progress`, `done`, `cancelled`)
- `category` (enum, see categories below)
- `estimated_minutes` (int, `>= 1`)
- `created_at` (timestamp, UTC)
- `updated_at` (timestamp, UTC)

Optional fields:

- `description` (string)
- `due_at` (timestamp, UTC)
- `completed_at` (timestamp, UTC or `null`)
- `priority` (enum: `low`, `medium`, `high`, `urgent`, default `medium`)
- `energy_level` (enum: `low`, `medium`, `high`) for scheduling by energy
- `labels` (array of string)

---

## `task_events` (append-only audit log)

Document ID: auto-id

Required fields:

- `task_id` (string)
- `user_id` (string)
- `event_type` (enum: `created`, `updated`, `completed`, `reopened`, `cancelled`)
- `created_at` (timestamp, UTC)

Optional fields:

- `payload` (map/object; changed fields snapshot)

---

## `user_stats`

Document ID: `user_id`

Required fields:

- `user_id` (string)
- `tasks_completed` (int, `>= 0`)
- `avg_task_minutes` (float, `>= 0`)
- `last_updated` (timestamp, UTC)

Optional fields:

- `best_focus_hours` (int, default `6`)
- `weekly_capacity_minutes` (int)
- `recent_overload_flags` (int, default `0`)

---

## Task categories

Initial category enum:

- `deep_work`
- `errand`
- `personal`
- `admin`
- `meeting`
- `learning`
- `health`
- `others`

Why these are useful:

- `deep_work`: high-focus tasks, often longer blocks
- `errand`: quick logistical tasks
- `personal`: personal life tasks
- `admin`: low-cognitive overhead but necessary work
- `meeting`: scheduled collaboration and calls
- `learning`: skill-building and research
- `health`: exercise, sleep, meal prep, appointments
- `others`: fallback when intent does not clearly match any known category

### Agent classification rule

Category should be inferred by the agent from natural-language task input.

- User is not required to choose a category manually.
- If confidence is low or input is ambiguous, assign `others`.

If you want fewer categories for MVP, start with:
`deep_work`, `admin`, `meeting`, `errand`, `personal`, `others`.

---

## Index recommendations (Firestore)

Start with single-field indexes (automatic), then add composite only as needed:

1. `tasks`: `(user_id, status, due_at)`
2. `tasks`: `(user_id, category, created_at desc)`
3. `task_events`: `(task_id, created_at desc)`

Add indexes after observing failed query messages in Firestore logs/console.

