#!/usr/bin/env python3
"""Save a Google user token for Tasks + Calendar (Desktop OAuth client JSON in ``.env``).

We use **paste**: open the printed Google URL, sign in, then paste the full
``http://localhost:...?code=...`` line from the address bar (default in Codespaces).
Optional ``--server`` for a local redirect server. See COMMANDS.md."""

from __future__ import annotations

import argparse
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


def _env_truthy(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes")


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
        print(f"Listening on {listen_host}:{actual_port}. Open:", auth_url, file=sys.stderr)
        print(f"Please visit this URL to authorize this application: {auth_url}")
        local_server.timeout = None
        last_uri = None
        for _ in range(30):
            local_server.handle_request()
            last_uri = getattr(wsgi_app, "last_request_uri", None)
            if last_uri and "code=" in last_uri:
                break
        if not last_uri or "code=" not in last_uri:
            raise WSGITimeoutError("No callback with ?code= (try without --server / paste method)")
        if last_uri.startswith("http://"):
            authorization_response = "https://" + last_uri[len("http://") :]
        else:
            authorization_response = last_uri
        flow.fetch_token(authorization_response=authorization_response)
    finally:
        local_server.server_close()
    return flow.credentials


def _oauth_via_pasted_redirect(
    flow,
    *,
    redirect_port: int,
    access_type: str,
    prompt: str,
):
    """No local server: user pastes the full ``http://localhost:...?code=...`` from the address bar."""
    print(
        "\n--paste mode: no HTTP server in this process. Your browser may show a localhost "
        "error after consent; copy the full URL from the address bar anyway.\n",
        file=sys.stderr,
    )
    flow.redirect_uri = f"http://localhost:{redirect_port}/"
    auth_url, _ = flow.authorization_url(access_type=access_type, prompt=prompt)
    print(f"Please visit this URL to authorize this application: {auth_url}")
    print(
        "\nAfter you approve, Google **will** send the browser to "
        f"http://localhost:{redirect_port}/?code=... — that is correct "
        "(the `code` must reach this project, not stay on google.com).\n"
        "If the tab shows an error, copy the **entire** URL from the address bar anyway.\n"
        "Paste it here and press Enter:\n",
        file=sys.stderr,
    )
    pasted = input().strip()
    if not pasted:
        print("No URL pasted.", file=sys.stderr)
        raise SystemExit(1)
    pasted = pasted.replace("127.0.0.1", "localhost")
    if pasted.startswith("http://"):
        authorization_response = "https://" + pasted[len("http://") :]
    else:
        authorization_response = pasted
    flow.fetch_token(authorization_response=authorization_response)
    return flow.credentials


def main() -> int:
    parser = argparse.ArgumentParser(description="Google OAuth token for Tasks + Calendar")
    parser.add_argument(
        "--paste",
        action="store_true",
        help="Force paste mode: paste redirect URL after browser consent",
    )
    parser.add_argument(
        "--server",
        action="store_true",
        help="Use loopback HTTP server (Codespaces: only if port forward works)",
    )
    args = parser.parse_args()
    force_server = args.server or _env_truthy("OAUTH_LOCAL_SERVER")
    explicit_paste = args.paste or _env_truthy("OAUTH_PASTE_REDIRECT")

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

    if force_server:
        use_paste = False
    elif codespace:
        use_paste = True
    else:
        use_paste = explicit_paste

    if codespace:
        print(
            "\nCodespaces: using **paste** (copy redirect URL from the browser). "
            "Optional: `--server` + port forward on "
            f"{redirect_port}.\n",
            file=sys.stderr,
        )
    else:
        print(
            "\nIf no browser tab opens: copy the 'Please visit this URL...' line from below, "
            "or set OAUTH_NO_BROWSER=1 and open that URL manually.\n",
            file=sys.stderr,
        )

    bind_addr = "0.0.0.0" if codespace else None

    if use_paste:
        print(
            "\n>>> Paste mode: open the Google URL below, sign in, click Allow — then paste the "
            "full localhost URL from the address bar (same run; do not reuse an old URL).\n",
            file=sys.stderr,
        )
        creds = _oauth_via_pasted_redirect(
            flow,
            redirect_port=redirect_port,
            access_type="offline",
            prompt="consent",
        )
    else:
        print(
            "\nServer mode: keep this terminal open until you see Saved credentials.\n",
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
