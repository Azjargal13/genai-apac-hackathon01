#!/usr/bin/env bash
# Quick smoke test for API + Firestore flow.
# Usage:
#   bash scripts/smoke_test.sh
#   BASE_URL=http://localhost:8080 USER_ID=beta-user-1 bash scripts/smoke_test.sh

set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8080}"
USER_ID="${USER_ID:-beta-user-1}"
SESSION_ID="${SESSION_ID:-smoke-session-1}"

echo "== Smoke test =="
echo "BASE_URL=${BASE_URL}"
echo "USER_ID=${USER_ID}"
echo "SESSION_ID=${SESSION_ID}"
echo

common_headers=(
  -H "Content-Type: application/json"
  -H "X-User-Id: ${USER_ID}"
  -H "X-Session-Id: ${SESSION_ID}"
)

echo "1) Health check"
curl -sS "${BASE_URL}/health"
echo
echo

echo "2) Create task A"
create_a_resp="$(
  curl -sS -X POST "${BASE_URL}/task" \
    "${common_headers[@]}" \
    -d '{"title":"Write architecture overview","estimated_minutes":90,"category":"deep_work","priority":"high"}'
)"
echo "${create_a_resp}"
echo
echo

echo "3) Create task B"
create_b_resp="$(
  curl -sS -X POST "${BASE_URL}/task" \
    "${common_headers[@]}" \
    -d '{"title":"Prepare grocery list","estimated_minutes":20,"category":"errand","priority":"medium"}'
)"
echo "${create_b_resp}"
echo
echo

task_id="$(python -c 'import json,sys; print(json.loads(sys.stdin.read()).get("task_id",""))' <<< "${create_a_resp}")"
if [[ -z "${task_id}" ]]; then
  echo "Could not extract task_id from create response."
  exit 1
fi
echo "Extracted task_id=${task_id}"
echo

echo "4) List tasks"
curl -sS "${BASE_URL}/task?limit=20" "${common_headers[@]}"
echo
echo

echo "5) Complete one task (${task_id})"
curl -sS -X POST "${BASE_URL}/task/${task_id}/complete" "${common_headers[@]}"
echo
echo

echo "6) User stats"
curl -sS "${BASE_URL}/task/stats/me" "${common_headers[@]}"
echo
echo

echo "7) Plan day (6h available)"
curl -sS -X POST "${BASE_URL}/plan" \
  "${common_headers[@]}" \
  -d '{"total_available_time_minutes":360}'
echo
echo

echo "Smoke test completed."
