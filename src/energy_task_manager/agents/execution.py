"""Execution sub-agent for Firestore-backed task CRUD (Google Calendar/Tasks tools not wired yet)."""

import os

from google.adk.agents import LlmAgent

from energy_task_manager.tools import complete_task, create_task, get_task, get_user_stats, list_tasks

MODEL = os.getenv("ADK_MODEL", "gemini-3-flash-preview")

execution_agent = LlmAgent(
    name="execution_agent",
    model=MODEL,
    description="Handles task create/complete and lookups in the app datastore.",
    instruction=(
        "You are the Execution Agent for an energy-aware task manager. "
        "You prepare and validate task actions (create, complete, get, list) in the "
        "app's Firestore-backed task store using the available tools only. "
        "When creating tasks, you must decide category and estimated_minutes from user intent "
        "and context. Before estimating minutes, check historical behavior via get_user_stats "
        "and keep estimates personalized. "
        "Category MUST be one of this schema enum only: "
        "deep_work, errand, personal, admin, meeting, learning, health, others. "
        "Never invent new category labels. Use 'others' only when no category clearly applies. "
        "Use tools for CRUD operations whenever possible. "
        "If required data is missing (for example user_id), ask a concise question."
    ),
    tools=[create_task, complete_task, get_task, list_tasks, get_user_stats],
)
