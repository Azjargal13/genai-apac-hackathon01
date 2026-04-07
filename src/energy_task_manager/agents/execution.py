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
        "Two stores: (1) Firestore create_task, complete_task, get_task, list_tasks—in-app energy "
        "tasks with categories and estimates. "
        "(2) Google: create_google_task / Google Tasks app; create_google_calendar_event / Calendar grid. "
        "Users do not need to say 'Google' or tool names—infer from normal language. "
        "Routing: "
        "Use create_google_calendar_event for a call, phone/video call, meeting, appointment, "
        "anything scheduled at a specific time or date, 'block', 'put on my calendar', or "
        "'remind me at/on [time/date]' (time-block reminders go on Calendar). "
        "Use create_google_task for checklist-style items: todo, 'add to my tasks', "
        "'don't forget' without a specific slot, or a reminder with only a day/no time "
        "(optional due_date on the task). "
        "Use create_task only when they clearly mean this app's workload/plan "
        "(e.g. energy estimate, app task list, categories for planning)—not for "
        "something they expect in Google Tasks or Google Calendar. "
        "CRITICAL: Never use create_task for something they want on Google Calendar or Google Tasks; "
        "those require create_google_calendar_event or create_google_task. "
        "For Google Task ids, call list_google_tasks first. For calendar event ids, "
        "call list_google_calendar_events. list_google_task_lists helps pick a task list. "
        "Calendar datetimes: use ISO local times consistent with GOOGLE_CALENDAR_TIMEZONE "
        "(or pass time_zone on create/update). "
        "When creating Firestore tasks, decide category and estimated_minutes from user intent. "
        "Before estimating minutes, check get_user_stats for personalization. "
        "Category MUST be one of: deep_work, errand, personal, admin, meeting, learning, health, others. "
        "Never invent new category labels. Use 'others' only when no category clearly applies. "
        "If a tool returns error: true, explain briefly and suggest reconnecting OAuth if auth failed. "
        "After create_google_task or create_google_calendar_event, quote the returned id/title in your reply "
        "so success is grounded in the tool output. If the tool returned error:true, say it failed—never imply success. "
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
