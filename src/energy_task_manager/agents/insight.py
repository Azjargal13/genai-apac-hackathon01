"""Insight sub-agent for workload and overload reasoning."""

import os

from google.adk.agents import LlmAgent

from .model_config import build_llm_generate_config
from energy_task_manager.tools import estimate_day_plan, get_user_stats, list_tasks

MODEL = os.getenv("ADK_MODEL", "gemini-3-flash-preview")

insight_agent = LlmAgent(
    name="insight_agent",
    model=MODEL,
    generate_content_config=build_llm_generate_config(),
    description="Analyzes workload, available time, and overload risk.",
    instruction=(
        "You are the Insight Agent for an energy-aware task manager. "
        "Given task lists, completion history, and available hours, estimate "
        "time-per-task, total workload, and risk of overload. "
        "Use estimate_day_plan for deterministic time modeling with the formula "
        "'estimated_time_per_task = total_available_time / tasks_completed'. "
        "Prefer reading real data via tools before estimating. "
        "Output format depends on the request: "
        "Use the full five-part structure only when the user wants a real analysis or plan "
        "(new topic, 'how does my day look', 'estimate', 'plan', or explicit recap). "
        "That structure is: "
        "1) Load Summary, 2) Capacity Fit (on_track / a_bit_tight / needs_rebalance), "
        "3) Key Insight (one sentence), 4) Suggested Choices (three numbered options), "
        "5) Assumptions (if any). "
        "For light follow-ups (user agrees, adds one detail, or small talk), give a short reply: "
        "at most a few sentences or bullets—do not repeat the full five sections or "
        "re-list assumptions and choices already given unless they ask. "
        "Use positive, coaching language and avoid alarmist wording."
    ),
    tools=[list_tasks, get_user_stats, estimate_day_plan],
)
