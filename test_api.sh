#!/usr/bin/env bash
set -euo pipefail

# Config
BASE_URL="${BASE_URL:-http://192.168.30.150:8000}"
USER_ID="${USER_ID:-test_user}"
MSG="${MSG:-Hello, what can you do?}"

JSON_HDR=(-H "Content-Type: application/json")

request() {
  local method="$1"
  local path="$2"
  local data="${3-}"
  echo ">> ${method} ${BASE_URL}${path}"
  if [[ -n "${data}" ]]; then
    # Print body then status code on a new line
    resp=$(curl -sS -w "\n%{http_code}" -X "${method}" "${BASE_URL}${path}" "${JSON_HDR[@]}" -d "${data}")
  else
    resp=$(curl -sS -w "\n%{http_code}" -X "${method}" "${BASE_URL}${path}")
  fi
  body="${resp%$'\n'*}"
  code="${resp##*$'\n'}"
  echo "${body}"
  echo "HTTP ${code}"
  # Fail fast on non-2xx
  if [[ "${code}" -lt 200 || "${code}" -ge 300 ]]; then
    echo "Request failed: ${method} ${path} -> ${code}" >&2
    exit 1
  fi
}

echo "=== Health ==="
request GET "/api/v1/health"

echo "=== Chat ==="
chat_payload=$(printf '{"user_id":"%s","message":"%s"}' "${USER_ID}" "${MSG}")
request POST "/api/v1/chat" "${chat_payload}"

echo "=== Summary ==="
request GET "/api/v1/summary/${USER_ID}"

echo "=== Conversation ==="
request GET "/api/v1/conversation/${USER_ID}"

echo "=== Conversations (list) ==="
request GET "/api/v1/conversations"

echo "=== Reset conversation ==="
request POST "/api/v1/conversation/${USER_ID}/reset"

echo "=== Delete conversation ==="
request DELETE "/api/v1/conversation/${USER_ID}"

echo "All tests passed."
