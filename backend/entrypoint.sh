#!/bin/sh
# Container entrypoint for the FleetPulse API.
#   RUN_MIGRATIONS=true   apply Alembic migrations before starting (serialized with a
#                         Postgres advisory lock, see app/migrate.py). docker compose sets
#                         this; in Kubernetes an init container runs `python -m app.migrate`.
#   SEED_DEMO_DATA=true   insert demo vehicles when the table is empty
set -eu

if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
  echo "[entrypoint] applying database migrations"
  python -m app.migrate
fi

if [ "${SEED_DEMO_DATA:-false}" = "true" ]; then
  echo "[entrypoint] seeding demo data (if the database is empty)"
  python -m app.seed
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers "${WEB_CONCURRENCY:-1}" --proxy-headers --forwarded-allow-ips="*"
