#!/usr/bin/env python3
"""Smoke test: Google Tasks + Calendar with saved OAuth token.

Run from repo root: ``PYTHONPATH=src python scripts/test_google_tokens.py``
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SRC = _ROOT / "src"
if _SRC.is_dir():
    sys.path.insert(0, str(_SRC))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(_ROOT / ".env")


def main() -> int:
    from energy_task_manager.integrations.google_oauth import google_oauth_configured

    if not google_oauth_configured():
        print("OAuth not configured. Set token path/env and run google_oauth_login.py.", file=sys.stderr)
        return 1

    from energy_task_manager.integrations.calendar import list_primary_calendar_events
    from energy_task_manager.integrations.tasks import list_task_lists, list_tasks

    try:
        print("=== Task lists ===")
        print(json.dumps(list_task_lists(), indent=2, default=str))
        print("\n=== Tasks (default list) ===")
        print(json.dumps(list_tasks(), indent=2, default=str))
        print("\n=== Calendar (primary, ~7 days) ===")
        print(json.dumps(list_primary_calendar_events(), indent=2, default=str))
    except Exception as e:
        print(f"API error: {e}", file=sys.stderr)
        return 1

    print("\nOK — token works for Tasks + Calendar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
