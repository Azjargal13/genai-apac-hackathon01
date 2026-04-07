#!/usr/bin/env python3
"""Smoke test: Google Tasks + Calendar with saved OAuth token.

Run from repo root: ``PYTHONPATH=src python scripts/test_google_tokens.py``

``--write-smoke`` inserts one task then deletes it (proves write scope; check Google Tasks if needed).
"""

from __future__ import annotations

import argparse
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
    parser = argparse.ArgumentParser(description="Verify Google Tasks + Calendar OAuth token")
    parser.add_argument(
        "--write-smoke",
        action="store_true",
        help="Create then delete a test task on the default list (verifies write API)",
    )
    args = parser.parse_args()

    from energy_task_manager.integrations.google_oauth import google_oauth_configured

    if not google_oauth_configured():
        print("OAuth not configured. Set token path/env and run google_oauth_login.py.", file=sys.stderr)
        return 1

    from energy_task_manager.integrations.calendar import list_primary_calendar_events
    from energy_task_manager.integrations.tasks import delete_task, insert_task, list_task_lists, list_tasks

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

    if args.write_smoke:
        try:
            title = "[smoke test] energy_task_manager — safe to delete"
            created = insert_task(title)
            tid = created.get("id")
            print("\n=== Write smoke: created task ===")
            print(json.dumps(created, indent=2, default=str))
            if tid:
                delete_task(tid)
                print("\n=== Write smoke: deleted same task ===")
            else:
                print("WARN: no task id in response; delete skipped", file=sys.stderr)
        except Exception as e:
            print(f"Write smoke failed: {e}", file=sys.stderr)
            return 1

    print("\nOK — token works for Tasks + Calendar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
