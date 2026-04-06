"""Execution sub-agent for task and calendar actions."""

import os

from google.adk.agents import LlmAgent

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
        "Until real tools are connected, clearly describe the intended action, "
        "required inputs, and expected result as a dry run."
    ),
)
