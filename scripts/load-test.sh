#!/usr/bin/env bash
# Generates realistic traffic against the API so Grafana panels fill up and the HPA has CPU to react to.
#   URL=http://fleetpulse.local REQUESTS=600 CONCURRENCY=20 ./scripts/load-test.sh
set -euo pipefail
URL="${URL:-http://localhost:8000}"
REQUESTS="${REQUESTS:-500}"
CONCURRENCY="${CONCURRENCY:-10}"

echo "load test -> $URL  ($REQUESTS requests, concurrency $CONCURRENCY)"
curl -fsS "$URL/health" >/dev/null || { echo "backend not reachable at $URL"; exit 1; }

hit() {
  local i="$1"
  case $((i % 6)) in
    0|1) curl -s -o /dev/null "$URL/api/vehicles" ;;
    2)   curl -s -o /dev/null "$URL/api/fleet/stats" ;;
    3)   curl -s -o /dev/null "$URL/api/vehicles?q=van" ;;
    4)   id=$(curl -s -X POST "$URL/api/vehicles" -H 'content-type: application/json' \
               -d "{\"name\":\"Load Van $i\",\"plate\":\"LT $$ $i\",\"odometer_km\":$((RANDOM % 50000))}" \
               | sed -n 's/.*"id":\([0-9]*\).*/\1/p')
         [ -n "$id" ] && curl -s -o /dev/null -X DELETE "$URL/api/vehicles/$id" ;;
    5)   curl -s -o /dev/null "$URL/api/vehicles/999999" ;;   # a 404 so the status-code panel has colour
  esac
}
export -f hit; export URL
seq 1 "$REQUESTS" | xargs -P "$CONCURRENCY" -I{} bash -c 'hit {}'
echo "done. check: $URL/metrics | grep http_requests_total, and the Grafana dashboard."
