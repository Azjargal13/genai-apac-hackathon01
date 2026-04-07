"""Insight sub-agent for workload and overload reasoning."""

import os

from google.adk.agents import LlmAgent

from .model_config import build_llm_generate_config
from energy_task_manager.tools import (
    estimate_day_plan,
    get_user_stats,
    list_google_calendar_events,
    list_google_tasks,
    list_tasks,
)

MODEL = os.getenv("ADK_MODEL", "gemini-3-flash-preview")

insight_agent = LlmAgent(
    name="insight_agent",
    model=MODEL,
    generate_content_config=build_llm_generate_config(),
    description="Analyzes workload, available time, and overload risk.",
    instruction=(
        "Analyze workload and overload risk from user context and tools. "
        "Use Firestore tools (list_tasks, get_user_stats, estimate_day_plan) for in-app planning; "
        "use Google read tools only when user asks about real Google tasks/calendar or external commitments. "
        "Use minimal tools (default max 2 per turn) and avoid re-reading unchanged context on follow-ups. "
        "Default response style: max 2 sentences or up to 3 short bullets. "
        "Only provide full structured analysis when user explicitly asks for a fresh plan/estimate/recap. "
        "When detailed format is requested, provide: Load Summary, Capacity Fit, Key Insight, Suggested Choices, Assumptions. "
        "Keep tone positive, practical, and non-alarmist."
    ),
    tools=[
        list_tasks,
        get_user_stats,
        list_google_tasks,
        list_google_calendar_events,
        estimate_day_plan,
    ],
)
