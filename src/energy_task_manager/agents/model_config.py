"""Shared Gemini generation settings for ADK ``LlmAgent`` (caps output length, temperature)."""

from __future__ import annotations

import os

from google.genai import types


def _parse_int(name: str, default: int, *, lo: int = 64, hi: int = 8192) -> int:
    raw = os.getenv(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        return max(lo, min(int(str(raw).strip()), hi))
    except ValueError:
        return default


def _parse_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        return max(0.0, min(float(str(raw).strip()), 2.0))
    except ValueError:
        return default


def build_llm_generate_config() -> types.GenerateContentConfig:
    """Lower ``ADK_MAX_OUTPUT_TOKENS`` to keep replies short and reduce quota use.

    ``ADK_TEMPERATURE`` slightly lower = steadier routing and less rambling.
    """
    return types.GenerateContentConfig(
        max_output_tokens=_parse_int("ADK_MAX_OUTPUT_TOKENS", 1024),
        temperature=_parse_float("ADK_TEMPERATURE", 0.45),
    )
