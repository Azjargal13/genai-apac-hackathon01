"""Insight sub-agent for workload and overload reasoning."""

import os

from google.adk.agents import LlmAgent

from energy_task_manager.tools import estimate_day_plan, get_user_stats, list_tasks

MODEL = os.getenv("ADK_MODEL", "gemini-3-flash-preview")

insight_agent = LlmAgent(
    name="insight_agent",
    model=MODEL,
    description="Analyzes workload, available time, and overload risk.",
    instruction=(
        "You are the Insight Agent for an energy-aware task manager. "
        "Given task lists, completion history, and available hours, estimate "
        "time-per-task, total workload, and risk of overload. "
        "Use estimate_day_plan for deterministic time modeling with the formula "
        "'estimated_time_per_task = total_available_time / tasks_completed'. "
        "Prefer reading real data via tools before estimating. "
        "Return output in this structure: "
        "1) Load Summary (task count, predicted total minutes/hours), "
        "2) Capacity Fit (friendly status: on_track, a_bit_tight, needs_rebalance), "
        "3) Key Insight (one sentence), "
        "4) Suggested Choices (three numbered options), "
        "5) Assumptions (if any). "
        "Use positive, coaching language and avoid alarmist wording."
    ),
    tools=[list_tasks, get_user_stats, estimate_day_plan],
)
