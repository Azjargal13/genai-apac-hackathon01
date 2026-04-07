#!/usr/bin/env bash
set -euo pipefail

# Quick smoke test for deployed API.
# Usage:
#   bash scripts/smoke_cloud_run.sh
#   bash scripts/smoke_cloud_run.sh --base-url "https://...run.app"
#   bash scripts/smoke_cloud_run.sh --user-id "beta-user-1" --session-id "local-session-1"

BASE_URL="https://energy-aware-ai-assistant-5736820628.asia-northeast3.run.app"
USER_ID="${DEFAULT_USER_ID:-beta-user-1}"
SESSION_ID="${DEFAULT_SESSION_ID:-local-session-1}"
AVAILABLE_MINUTES=360

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base-url)
      BASE_URL="$2"
      shift 2
      ;;
    --user-id)
      USER_ID="$2"
      shift 2
      ;;
    --session-id)
      SESSION_ID="$2"
      shift 2
      ;;
    --minutes)
      AVAILABLE_MINUTES="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

print_json() {
  if command -v jq >/dev/null 2>&1; then
    jq .
  else
    cat
  fi
}

req() {
  local method="$1"
  local path="$2"
  local body="${3:-}"

  if [[ -n "$body" ]]; then
    curl -sS -X "$method" "${BASE_URL}${path}" \
      -H "Content-Type: application/json" \
      -H "X-User-Id: ${USER_ID}" \
      -H "X-Session-Id: ${SESSION_ID}" \
      -d "$body"
  else
    curl -sS -X "$method" "${BASE_URL}${path}" \
      -H "X-User-Id: ${USER_ID}" \
      -H "X-Session-Id: ${SESSION_ID}"
  fi
}

echo "== Smoke test =="
echo "BASE_URL=${BASE_URL}"
echo "USER_ID=${USER_ID}"
echo "SESSION_ID=${SESSION_ID}"
echo

echo "== /health =="
req GET "/health" | print_json
echo

echo "== GET /task?limit=5 =="
req GET "/task?limit=5" | print_json
echo

echo "== POST /task =="
TASK_TITLE="Cloud Run smoke task $(date +%s)"
req POST "/task" "{\"title\":\"${TASK_TITLE}\",\"category\":\"admin\",\"priority\":\"medium\",\"estimated_minutes\":20}" | print_json
echo

echo "== POST /plan =="
req POST "/plan" "{\"total_available_time_minutes\":${AVAILABLE_MINUTES}}" | print_json
echo

echo "== GET /task/stats/me =="
req GET "/task/stats/me" | print_json
echo

echo "Smoke test completed."
