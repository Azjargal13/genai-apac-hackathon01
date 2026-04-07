"""Execution sub-agent: Firestore app tasks + Google Tasks/Calendar (user OAuth)."""

import os

from google.adk.agents import LlmAgent

from .model_config import build_llm_generate_config
from energy_task_manager.tools import (
    complete_google_task,
    create_google_calendar_event,
    create_google_task,
    delete_google_calendar_event,
    delete_google_task,
    list_google_calendar_events,
    list_google_task_lists,
    list_google_tasks,
    update_google_calendar_event,
    update_google_task,
)
from energy_task_manager.tools.firestore_safe_tools import (
    safe_complete_task,
    safe_create_task,
    safe_get_task,
    safe_get_user_stats,
    safe_list_tasks,
)

MODEL = os.getenv("ADK_MODEL", "gemini-3-flash-preview")

execution_agent = LlmAgent(
    name="execution_agent",
    model=MODEL,
    generate_content_config=build_llm_generate_config(),
    description=(
        "Handles app Firestore tasks and the user's Google Tasks + Google Calendar."
    ),
    instruction=(
        "Execute user actions with minimal tool calls (default max 2 per turn). "
        "Use Google tools for items users expect in Google apps: "
        "timed events/calls/meetings/reminders at a time -> create_google_calendar_event; "
        "checklist todos or day-level reminders -> create_google_task. "
        "Use Firestore tools only for in-app workload/planning tasks. "
        "Never use safe_create_task for something meant for Google Tasks/Calendar. "
        "For updates/deletes, fetch IDs first only when needed (list_google_tasks or list_google_calendar_events). "
        "If tool returns error:true, report failure briefly and suggest OAuth reconnect for auth issues. "
        "If successful, confirm briefly and include returned id/title. "
        "For Firestore task creation, choose category from: deep_work, errand, personal, admin, meeting, learning, health, others; "
        "use safe_get_user_stats for personalized estimated_minutes when needed. "
        "Do not ask the user to choose category or estimated minutes unless they explicitly want to choose. "
        "Infer both from task title/context by default and proceed. "
        "Ask one concise clarification only if the task title/action itself is ambiguous or missing."
    ),
    tools=[
        safe_create_task,
        safe_complete_task,
        safe_get_task,
        safe_list_tasks,
        safe_get_user_stats,
        list_google_task_lists,
        list_google_tasks,
        list_google_calendar_events,
        create_google_task,
        update_google_task,
        complete_google_task,
        delete_google_task,
        create_google_calendar_event,
        update_google_calendar_event,
        delete_google_calendar_event,
    ],
)
