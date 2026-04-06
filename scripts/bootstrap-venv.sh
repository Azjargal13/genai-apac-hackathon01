#!/usr/bin/env bash
# Optional: use a project venv in Codespaces or Linux instead of pip install --user
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python3 -m venv .venv
# shellcheck source=/dev/null
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt
echo "Activate with: source .venv/bin/activate"
