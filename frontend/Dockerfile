# ---------- Stage 1: build the static bundle ----------
FROM node:22-alpine AS build
WORKDIR /app
ENV CI=true
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm test && npm run build

# ---------- Stage 2: serve with an unprivileged nginx ----------
# nginx-unprivileged runs as uid 101 ("nginx"), listens on 8080 and keeps its
# pid/cache under /tmp, so no root is needed at runtime.
FROM nginxinc/nginx-unprivileged:1.30-alpine-slim
LABEL org.opencontainers.image.title="fleetpulse-frontend" \
      org.opencontainers.image.description="FleetPulse dashboard served by nginx" \
      org.opencontainers.image.source="https://github.com/Parv-0210/fleetpulse-devops-capstone"

# Pull in Alpine security updates so the Trivy HIGH/CRITICAL gate stays green.
USER root
RUN apk upgrade --no-cache
USER nginx

ENV BACKEND_UPSTREAM=backend:8000
COPY --chown=nginx:nginx nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build --chown=nginx:nginx /app/dist /usr/share/nginx/html

USER nginx
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8080/healthz >/dev/null || exit 1
