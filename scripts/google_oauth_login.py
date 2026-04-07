#!/usr/bin/env python3
"""One-time OAuth login → saves user token for Google Tasks + Calendar.

See COMMANDS.md / GOOGLE_TASKS_CALENDAR.md. For a solo demo, set OAuth consent screen
to **Testing** and add your Gmail under **Test users** in Cloud Console.

Run from repo root: ``python scripts/google_oauth_login.py``
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


def _redirect_server_port(*, codespace: bool) -> int:
    """Fixed port in Codespaces so devcontainer can pre-forward; 0 = random (local desktop)."""
    raw = os.getenv("OAUTH_REDIRECT_PORT", "").strip()
    if raw:
        try:
            p = int(raw)
            if 1024 <= p <= 65535:
                return p
        except ValueError:
            pass
    if codespace:
        return 55555
    return 0


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
    redirect_port = _redirect_server_port(codespace=codespace)

    if codespace:
        print(
            "\n=== GitHub Codespaces / remote container ===\n"
            f"The redirect server will use port **{redirect_port}** on localhost.\n"
            "Do this ORDER:\n"
            f"  1) Ports tab → ensure port {redirect_port} is forwarded (this repo's devcontainer "
            "lists it; or add it manually *before* you finish Google).\n"
            "  2) Copy the 'Please visit this URL...' https://accounts.google.com/... line below "
            "and open it in your **normal laptop browser**.\n"
            f"  3) After you click Allow, Google sends you to http://localhost:{redirect_port}/?code=...\n"
            "     That only works if step (1) is done — otherwise you get a blank / connection error.\n"
            "  Alternative: run this same script on your **local PC** once, then copy secrets/token.json "
            "into the container.\n",
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
        "port": redirect_port,
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
