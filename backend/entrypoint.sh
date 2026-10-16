#!/bin/sh
# Container entrypoint for the FleetPulse API.
#   RUN_MIGRATIONS=true   run `alembic upgrade head` before starting (docker compose / single replica)
#   SEED_DEMO_DATA=true   insert demo vehicles when the table is empty
# In Kubernetes migrations run once per release via a Helm hook Job instead,
# so the Deployment pods start with RUN_MIGRATIONS=false.
set -eu

if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
  echo "[entrypoint] applying database migrations"
  alembic upgrade head
fi

if [ "${SEED_DEMO_DATA:-false}" = "true" ]; then
  echo "[entrypoint] seeding demo data (if the database is empty)"
  python -m app.seed
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers "${WEB_CONCURRENCY:-1}" --proxy-headers --forwarded-allow-ips="*"
