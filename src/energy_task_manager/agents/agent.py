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
        "Route by intent. "
        "Use insight_agent for planning, workload, and overload questions. "
        "Use execution_agent for task/calendar operations. "
        "For casual follow-ups (acknowledgments, minor edits, small talk), answer directly and do not delegate. "
        "If user asks to recap/summarize recent discussion, prefer direct recap from conversation context "
        "without delegation or tools. "
        "Delegate to only one sub-agent per turn unless user explicitly asks for combined analysis + action. "
        "Default response style: max 2 sentences or up to 3 short bullets. "
        "Ask one concise clarification only when required data is missing. "
        "Never claim Google Tasks/Calendar changed unless execution_agent confirms a successful google_* tool result "
        "(no error flag). Firestore tools do not sync to Google."
    ),
    sub_agents=[insight_agent, execution_agent],
)
