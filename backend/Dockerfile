# ---------- Stage 1: resolve and install dependencies ----------
FROM python:3.12-slim AS deps
WORKDIR /app
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt \
    # pip is only needed at build time; dropping it (and its vendored urllib3/msgpack)
    # removes a whole class of CVEs from the runtime image.
    && /opt/venv/bin/pip uninstall -y pip setuptools wheel || true

# ---------- Stage 2: minimal runtime, non-root ----------
FROM python:3.12-slim
LABEL org.opencontainers.image.title="fleetpulse-backend" \
      org.opencontainers.image.description="FleetPulse FastAPI service" \
      org.opencontainers.image.source="https://github.com/Parv-0210/fleetpulse-devops-capstone"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_ENV=production \
    PORT=8000

# Keep the OS patched inside the image so Trivy's gate stays green.
RUN apt-get update && apt-get upgrade -y --no-install-recommends && rm -rf /var/lib/apt/lists/* \
    && rm -rf /usr/local/lib/python3.12/site-packages/pip* /usr/local/lib/python3.12/site-packages/setuptools* \
              /usr/local/lib/python3.12/site-packages/wheel* /usr/local/bin/pip* /usr/local/lib/python3.12/ensurepip \
    && groupadd --gid 10001 app && useradd --uid 10001 --gid app --home-dir /app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app
COPY --from=deps /opt/venv /opt/venv
COPY --chown=app:app alembic.ini entrypoint.sh ./
COPY --chown=app:app alembic ./alembic
COPY --chown=app:app app ./app

USER 10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).status == 200 else 1)"
ENTRYPOINT ["./entrypoint.sh"]
