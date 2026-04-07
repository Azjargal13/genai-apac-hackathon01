"""ADK entrypoint expected by `adk run` (`root_agent` symbol)."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_ROOT / ".env", override=False)

from .agents.agent import root_agent
