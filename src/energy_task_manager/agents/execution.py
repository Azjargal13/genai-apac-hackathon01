"""Execution sub-agent for task and calendar actions."""

import os

from google.adk.agents import LlmAgent

from energy_task_manager.tools import complete_task, create_task, get_task, list_tasks

MODEL = os.getenv("ADK_MODEL", "gemini-3-flash-preview")

execution_agent = LlmAgent(
    name="execution_agent",
    model=MODEL,
    description="Handles task updates and scheduling actions safely.",
    instruction=(
        "You are the Execution Agent for an energy-aware task manager. "
        "You prepare and validate task actions (create, update, complete) and "
        "calendar scheduling intents. "
        "When creating tasks, infer category from user text and use 'others' as "
        "the fallback if no category clearly applies. "
        "Use tools for CRUD operations whenever possible. "
        "If required data is missing (for example user_id), ask a concise question."
    ),
    tools=[create_task, complete_task, get_task, list_tasks],
)
