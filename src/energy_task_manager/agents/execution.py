"""Execution sub-agent: Firestore app tasks + Google Tasks/Calendar (user OAuth)."""

import os

from google.adk.agents import LlmAgent

from .model_config import build_llm_generate_config
from energy_task_manager.tools import (
    complete_google_task,
    complete_task,
    create_google_calendar_event,
    create_google_task,
    create_task,
    delete_google_calendar_event,
    delete_google_task,
    get_task,
    get_user_stats,
    list_google_calendar_events,
    list_google_task_lists,
    list_google_tasks,
    list_tasks,
    update_google_calendar_event,
    update_google_task,
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
        "You are the Execution Agent for an energy-aware task manager. "
        "Two stores: (1) Firestore tools create_task, complete_task, get_task, list_tasks—"
        "the in-app task store with categories and estimates. "
        "(2) Google tools (list_google_*, create_google_*, update_google_*, "
        "complete_google_task, delete_google_*) sync with the user's real Google Tasks "
        "and primary Calendar. Use Google tools when the user asks to add/change/remove "
        "items in Google or Calendar; use Firestore when they mean the app or energy plan. "
        "For Google Task ids, call list_google_tasks first. For calendar event ids, "
        "call list_google_calendar_events. list_google_task_lists helps pick a task list. "
        "Calendar datetimes: use ISO local times consistent with GOOGLE_CALENDAR_TIMEZONE "
        "(or pass time_zone on create/update). "
        "When creating Firestore tasks, decide category and estimated_minutes from user intent. "
        "Before estimating minutes, check get_user_stats for personalization. "
        "Category MUST be one of: deep_work, errand, personal, admin, meeting, learning, health, others. "
        "Never invent new category labels. Use 'others' only when no category clearly applies. "
        "If a tool returns error: true, explain briefly and suggest reconnecting OAuth if auth failed. "
        "After a successful change, confirm briefly—do not add a full insight-style plan unless asked. "
        "If required data is missing (e.g. user_id for Firestore), ask one concise question."
    ),
    tools=[
        create_task,
        complete_task,
        get_task,
        list_tasks,
        get_user_stats,
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
