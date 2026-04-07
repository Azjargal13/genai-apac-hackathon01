"""Root orchestrator agent definition for ADK runtime."""

import os

from google.adk.agents import LlmAgent

from .execution import execution_agent
from .insight import insight_agent
from .model_config import build_llm_generate_config

MODEL = os.getenv("ADK_MODEL", "gemini-3-flash-preview")

root_agent = LlmAgent(
    name="root_agent",
    model=MODEL,
    generate_content_config=build_llm_generate_config(),
    description=(
        "Orchestrates user task-management requests across insight and execution agents."
    ),
    instruction=(
        "You are the primary orchestrator for an energy-aware AI task manager. "
        "Classify user intent and delegate to sub-agents: "
        "use insight_agent for workload analysis and planning guidance, "
        "use execution_agent for operational task actions in the app (create, complete, lookup). "
        "If user input is ambiguous, ask one concise clarification. "
        "Conversation efficiency (important): do NOT repeat the same long structured answer "
        "(Load Summary, Capacity Fit, full assumptions, long option lists) on every turn. "
        "Use the full multi-section format only when the user clearly wants a fresh plan, "
        "a first-time analysis, or explicitly asks to recap or see the breakdown again. "
        "For acknowledgments, small additions, confirmations, or casual follow-ups, reply briefly "
        "(a few sentences or short bullets): confirm what changed, add only new information, "
        "and refer to prior context instead of reprinting it. "
        "This reduces token use and helps avoid model rate limits. "
        "Return practical, user-friendly answers."
    ),
    sub_agents=[insight_agent, execution_agent],
)
