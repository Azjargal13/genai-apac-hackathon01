#!/usr/bin/env python3
"""One-time OAuth login → saves user token for Google Tasks + Calendar.

See GOOGLE_TASKS_CALENDAR.md. Run from repo root: ``python scripts/google_oauth_login.py``
(needs ``GOOGLE_OAUTH_CLIENT_SECRETS_PATH`` in ``.env``; writes ``GOOGLE_OAUTH_TOKEN_PATH``).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Repo root: parent of scripts/
_ROOT = Path(__file__).resolve().parent.parent
_SRC = _ROOT / "src"
if _SRC.is_dir():
    sys.path.insert(0, str(_SRC))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(_ROOT / ".env")

from energy_task_manager.integrations.google_oauth import (  # noqa: E402
    GOOGLE_TASKS_CALENDAR_SCOPES,
)


def _is_codespace() -> bool:
    return bool(os.getenv("CODESPACE_NAME"))


def _open_browser() -> bool:
    if os.getenv("OAUTH_NO_BROWSER", "").strip().lower() in ("1", "true", "yes"):
        return False
    # Remote dev: browser on the server cannot show on your laptop; use printed URL + port forward.
    if _is_codespace():
        return False
    return True


def main() -> int:
    client_secrets = os.getenv("GOOGLE_OAUTH_CLIENT_SECRETS_PATH")
    if not client_secrets or not Path(client_secrets).is_file():
        print(
            "Set GOOGLE_OAUTH_CLIENT_SECRETS_PATH to your OAuth client JSON from Cloud Console.",
            file=sys.stderr,
        )
        return 1

    token_path = os.getenv("GOOGLE_OAUTH_TOKEN_PATH", "secrets/token.json")
    token_path = str(Path(token_path).expanduser())

    from google_auth_oauthlib.flow import InstalledAppFlow  # noqa: PLC0415

    flow = InstalledAppFlow.from_client_secrets_file(
        client_secrets,
        list(GOOGLE_TASKS_CALENDAR_SCOPES),
    )

    codespace = _is_codespace()
    if codespace:
        print(
            "\n=== GitHub Codespaces detected ===\n"
            "The Google sign-in page will NOT open automatically on your laptop.\n"
            "1. When the script prints 'Please visit this URL...', copy that full https:// URL "
            "and open it in your normal browser.\n"
            "2. In VS Code / Cursor: Ports tab → forward the port shown in "
            "'http://localhost:PORT' (the redirect server).\n"
            "3. After you approve Google, the browser redirects to http://127.0.0.1:PORT/ — "
            "that must hit the Codespace via the forwarded port.\n",
            file=sys.stderr,
        )
    else:
        print(
            "\nIf no browser tab opens: copy the 'Please visit this URL...' line from below, "
            "or set OAUTH_NO_BROWSER=1 and open that URL manually.\n",
            file=sys.stderr,
        )

    # Bind on all interfaces in Codespaces so forwarded ports reach the redirect server.
    run_kw: dict = {
        "port": 0,
        "open_browser": _open_browser(),
        "access_type": "offline",
        "prompt": "consent",
    }
    if codespace:
        run_kw["bind_addr"] = "0.0.0.0"

    creds = flow.run_local_server(**run_kw)

    parent = Path(token_path).resolve().parent
    if str(parent) not in ("", "."):
        parent.mkdir(parents=True, exist_ok=True)
    Path(token_path).write_text(creds.to_json(), encoding="utf-8")
    print(f"Saved credentials to {token_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
