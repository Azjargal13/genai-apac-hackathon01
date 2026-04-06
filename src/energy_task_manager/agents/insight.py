"""Insight sub-agent for workload and overload reasoning."""

import os

from google.adk.agents import LlmAgent

MODEL = os.getenv("ADK_MODEL", "gemini-3-flash-preview")

insight_agent = LlmAgent(
    name="insight_agent",
    model=MODEL,
    description="Analyzes workload, available time, and overload risk.",
    instruction=(
        "You are the Insight Agent for an energy-aware task manager. "
        "Given task lists, completion history, and available hours, estimate "
        "time-per-task, total workload, and risk of overload. "
        "Provide concise recommendations such as reducing load or spreading "
        "tasks across days. Be explicit about assumptions."
    ),
)
