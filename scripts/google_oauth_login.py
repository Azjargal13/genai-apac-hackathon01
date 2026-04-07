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


def _run_oauth_local_server(
    flow,
    *,
    host: str,
    bind_addr: str | None,
    port: int,
    open_browser: bool,
    access_type: str,
    prompt: str,
):
    """Same as InstalledAppFlow.run_local_server but fixes Google's ``iss=https://...`` callback.

    Upstream ``run_local_server`` does ``uri.replace("http", "https")`` on the full redirect URL,
    which corrupts query params and triggers ``MismatchingStateError``. We only rewrite the scheme
    once (``http://`` at the start of the callback URL).
    """
    import webbrowser
    import wsgiref.simple_server

    from google_auth_oauthlib.flow import (  # noqa: PLC2701
        WSGITimeoutError,
        _RedirectWSGIApp,
        _WSGIRequestHandler,
    )

    success_message = (
        "The authentication flow has completed. You may close this window."
    )
    wsgi_app = _RedirectWSGIApp(success_message)
    wsgiref.simple_server.WSGIServer.allow_reuse_address = False
    listen_host = bind_addr if bind_addr else host
    local_server = wsgiref.simple_server.make_server(
        listen_host, port, wsgi_app, handler_class=_WSGIRequestHandler
    )
    try:
        actual_port = local_server.server_port
        flow.redirect_uri = f"http://{host}:{actual_port}/"
        auth_url, _ = flow.authorization_url(
            access_type=access_type,
            prompt=prompt,
        )
        if open_browser:
            webbrowser.open(auth_url, new=1, autoraise=True)
        print(f"Please visit this URL to authorize this application: {auth_url}")
        local_server.timeout = None
        local_server.handle_request()
        last_uri = getattr(wsgi_app, "last_request_uri", None)
        if not last_uri:
            raise WSGITimeoutError(
                "Timed out waiting for response from authorization server"
            )
        if last_uri.startswith("http://"):
            authorization_response = "https://" + last_uri[len("http://") :]
        else:
            authorization_response = last_uri
        flow.fetch_token(authorization_response=authorization_response)
    finally:
        local_server.server_close()
    return flow.credentials


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

    bind_addr = "0.0.0.0" if codespace else None

    print(
        "\n>>> Leave this command RUNNING until you see 'Saved credentials' below.\n"
        ">>> Google's redirect goes to a tiny server inside this Python process — if you\n"
        "    Ctrl+C or close the terminal first, you get ERR_CONNECTION_REFUSED on localhost.\n"
        ">>> (Using a venv or not does not matter; the process must stay alive.)\n",
        file=sys.stderr,
    )

    creds = _run_oauth_local_server(
        flow,
        host="localhost",
        bind_addr=bind_addr,
        port=redirect_port,
        open_browser=_open_browser(),
        access_type="offline",
        prompt="consent",
    )

    parent = Path(token_path).resolve().parent
    if str(parent) not in ("", "."):
        parent.mkdir(parents=True, exist_ok=True)
    Path(token_path).write_text(creds.to_json(), encoding="utf-8")
    print(f"Saved credentials to {token_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
