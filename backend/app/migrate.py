"""Apply Alembic migrations safely from any number of concurrently starting pods.

Run with: python -m app.migrate

* Waits for the database to accept connections (fresh Postgres pods need a few seconds).
* On PostgreSQL, takes a session-level advisory lock so that when two backend replicas
  start at the same time only one of them runs `alembic upgrade head`; the other waits
  and then finds the schema already current. SQLite (tests/dev) skips the lock.

This is what the Kubernetes init container and the docker-compose entrypoint execute,
so there is exactly one migration code path across environments.
"""

import logging
import sys
import time
from pathlib import Path

from alembic.config import Config
from sqlalchemy import create_engine, text

from alembic import command

from .config import settings

log = logging.getLogger("fleetpulse.migrate")
ADVISORY_LOCK_ID = 742_801  # arbitrary, app-wide constant
MAX_WAIT_SECONDS = 120


def wait_for_database(engine) -> None:
    deadline = time.monotonic() + MAX_WAIT_SECONDS
    attempt = 0
    while True:
        attempt += 1
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            log.info("database reachable (attempt %d)", attempt)
            return
        except Exception as exc:
            if time.monotonic() > deadline:
                log.error("database not reachable after %ss: %s", MAX_WAIT_SECONDS, exc)
                raise
            log.warning("database not ready yet (attempt %d): %s", attempt, exc.__class__.__name__)
            time.sleep(min(2 * attempt, 10))


def run() -> None:
    root = Path(__file__).resolve().parent.parent
    cfg = Config(str(root / "alembic.ini"))
    cfg.set_main_option("script_location", str(root / "alembic"))

    engine = create_engine(settings.database_url, pool_pre_ping=True)
    wait_for_database(engine)

    if engine.dialect.name == "postgresql":
        with engine.connect() as conn:
            log.info("acquiring migration lock %d", ADVISORY_LOCK_ID)
            conn.execute(text("SELECT pg_advisory_lock(:id)"), {"id": ADVISORY_LOCK_ID})
            try:
                command.upgrade(cfg, "head")
            finally:
                conn.execute(text("SELECT pg_advisory_unlock(:id)"), {"id": ADVISORY_LOCK_ID})
                log.info("released migration lock")
    else:
        command.upgrade(cfg, "head")
    log.info("schema is at head")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    try:
        run()
    except Exception:
        log.exception("migration failed")
        sys.exit(1)
