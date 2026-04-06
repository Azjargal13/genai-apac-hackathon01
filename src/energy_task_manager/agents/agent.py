"""Root orchestrator agent definition for ADK runtime."""

import os

from google.adk.agents import LlmAgent

from .execution import execution_agent
from .insight import insight_agent

MODEL = os.getenv("ADK_MODEL", "gemini-3-flash-preview")

root_agent = LlmAgent(
    name="root_agent",
    model=MODEL,
    description=(
        "Orchestrates user task-management requests across insight and execution agents."
    ),
    instruction=(
        "You are the primary orchestrator for an energy-aware AI task manager. "
        "Classify user intent and delegate to sub-agents: "
        "use insight_agent for workload analysis and planning guidance, "
        "use execution_agent for operational actions and scheduling intent. "
        "If user input is ambiguous, ask one concise clarification. "
        "Return practical, user-friendly answers."
    ),
    sub_agents=[insight_agent, execution_agent],
)
