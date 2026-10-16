# FleetPulse — DevOps Capstone Implementation Plan

> Session 21 Final Capstone (Python track). This plan maps every rubric criterion in
> `GRADING.md` to a concrete file, command, and piece of evidence, and defines the
> order in which the work is built and verified.

---

## 0. Decisions at a glance

| Topic | Decision | Why |
|---|---|---|
| Domain | **FleetPulse** — vehicle fleet maintenance tracker | Own domain (rubric requires it); not in the suggested list; two related tables give a richer API than a single CRUD board |
| Backend | FastAPI + SQLAlchemy 2 + Alembic + PostgreSQL 16 | Course stack; rubric M1 |
| Frontend | React 19 + Vite 8, plain CSS, served by **nginx-unprivileged** | Multi-stage build + non-root runtime (M4) |
| Tests | pytest, isolated test DB (SQLite in-memory locally, Postgres service container in CI), ruff for code quality | M2 |
| CI/CD | GitHub Actions: test → build → Trivy → push to GHCR (SHA tags) → optional Helm deploy | M5, M6 |
| Infra | Terraform: VPC (2 public + 2 private subnets, NAT) + EKS managed node group + EBS CSI addon (IRSA) | M7 |
| K8s | `k8s/` bootstrap + Helm chart `helm/fleetpulse` with Deployments (2 replicas), ClusterIP Services, Ingress, HPA, PDB, migration hook Job, ServiceMonitor, Grafana dashboard ConfigMap | M8, M9 |
| Observability | kube-prometheus-stack values in `monitoring/`; backend exposes HTTP metrics **plus custom business metrics** | M9 |
| Docs | Root README, `docs/PLAN.md`, `docs/SUBMISSION.md` (rubric→evidence map), `docs/DEMO.md` runbook, `docs/TRIVY.md` | M10 |

### What makes this submission unique (beyond the rubric minimum)

1. **Domain-specific metrics**: a custom Prometheus collector exports `fleetpulse_vehicles{status}`,
   `fleetpulse_vehicles_service_due`, and `fleetpulse_service_records_created_total{service_type}` next to the
   standard HTTP metrics — the Grafana dashboard shows business health, not just request counts.
2. **Grafana dashboard ships inside the Helm chart** as a ConfigMap discovered by the Grafana sidecar —
   `helm upgrade --install` is the only step needed to get a populated dashboard.
3. **Schema migrations run as a Helm pre-install/pre-upgrade hook Job**, not inside every replica's
   container start — avoids concurrent migration races with 2+ replicas.
4. **Pipeline validates infrastructure too**: `helm lint` + `helm template`, `terraform fmt/validate`,
   and `ruff` run as quality gates in addition to pytest; Trivy results are uploaded as SARIF to the
   GitHub Security tab and an SBOM is published as a build artifact.
5. **Derived maintenance logic**: `km_until_service` / `service_state` (OK, DUE_SOON, OVERDUE) is computed
   server-side and surfaced as KPI cards, so the UI is a real dashboard rather than a table.
6. **Two Alembic revisions** (vehicles, then service records) to demonstrate schema evolution.
7. **Reproducible local loop**: `Makefile` targets wrap compose, tests, lint, helm, terraform and
   minikube so the live demo is a sequence of one-liners.

---

## 1. Application design (M1)

### 1.1 Data model

```text
vehicles
  id                  PK
  name                varchar(100)   "Van 12"
  plate               varchar(20)    unique
  vehicle_type        VAN | TRUCK | CAR | BIKE
  status              ACTIVE | IN_SHOP | RETIRED
  odometer_km         int  >= 0
  service_interval_km int  > 0 (default 10000)
  last_service_km     int  >= 0 (default 0)
  last_service_at     timestamptz nullable
  created_at / updated_at timestamptz

service_records
  id            PK
  vehicle_id    FK -> vehicles.id  ON DELETE CASCADE
  service_type  OIL_CHANGE | TIRES | BRAKES | INSPECTION | REPAIR | OTHER
  odometer_km   int
  cost          numeric(10,2)
  notes         text
  performed_at  timestamptz
  created_at    timestamptz
```

Derived per vehicle: `km_until_service = last_service_km + service_interval_km - odometer_km`,
`service_state = OVERDUE (<=0) | DUE_SOON (<=500) | OK`.

### 1.2 REST API

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | service banner |
| GET | `/health` | liveness |
| GET | `/ready` | readiness (runs a DB query) |
| GET | `/metrics` | Prometheus exposition |
| GET | `/api/vehicles?status=&q=` | list / filter |
| POST | `/api/vehicles` | create (201) |
| GET | `/api/vehicles/{id}` | read |
| PUT | `/api/vehicles/{id}` | partial update (incl. odometer) |
| DELETE | `/api/vehicles/{id}` | delete (204) |
| GET | `/api/vehicles/{id}/services` | service history |
| POST | `/api/vehicles/{id}/services` | log service (updates last_service_*) |
| DELETE | `/api/services/{id}` | remove a record |
| GET | `/api/fleet/stats` | KPIs for the dashboard |

### 1.3 Frontend

Single-page dashboard: sidebar, KPI cards (vehicles, active, due soon, overdue, 30-day spend),
vehicle grid with filters and search, service-log drawer, create/edit modal, loading/error/empty states,
responsive at phone width. All API calls go to relative `/api/...` (nginx / Ingress route them).

---

## 2. Repository layout

```text
fleetpulse/
├── backend/
│   ├── app/            main.py, config.py, db.py, models.py, schemas.py, routes/, metrics.py, services.py
│   ├── alembic/        env.py, versions/0001_vehicles.py, 0002_service_records.py
│   ├── tests/          conftest.py, test_health.py, test_vehicles.py, test_services.py, test_stats.py, test_metrics.py
│   ├── Dockerfile, entrypoint.sh, requirements.txt, requirements-dev.txt, pytest.ini, pyproject.toml (ruff), alembic.ini, .env.example
├── frontend/
│   ├── src/            main.jsx, App.jsx, api.js, lib/service.js (+ test), components/, styles.css
│   ├── Dockerfile, nginx/default.conf.template, package.json, vite.config.js, index.html
├── docker-compose.yml
├── .github/workflows/ci-cd.yml
├── terraform/          versions.tf, providers.tf, variables.tf, vpc.tf, eks.tf, outputs.tf, terraform.tfvars.example, README.md
├── k8s/                namespace.yaml, storageclass-gp3.yaml, README.md, bootstrap scripts (ingress-nginx, metrics-server)
├── helm/fleetpulse/    Chart.yaml, values.yaml, values-dev.yaml, values-prod.yaml, templates/
├── monitoring/         kube-prometheus-stack-values.yaml, install.sh, README.md
├── troubleshooting/    broken-image.yaml, broken-service.yaml
├── scripts/            load-test.sh, deploy.sh, ghcr-pull-secret.sh
├── docs/               PLAN.md, SUBMISSION.md, DEMO.md, TRIVY.md, screenshots/
├── Makefile, .gitignore, .dockerignore, README.md
```

---

## 3. Rubric mapping and implementation order

Build order follows the pipeline order so each layer is verified before the next depends on it.

### Step 1 — Backend (M1: 7 pts of 10)
- Files: `backend/app/*`, `backend/alembic/*`, `backend/requirements.txt`.
- Verify: `uvicorn` boots, `/health` → `{"status":"UP"}`, Swagger lists 13 routes, `alembic upgrade head` creates 2 tables on Postgres.

### Step 2 — Tests + quality (M2: 10 pts)
- `conftest.py` builds an isolated engine (`TEST_DATABASE_URL` or SQLite in-memory with `StaticPool`), overrides `get_db`, creates schema, truncates between tests.
- ≥ 12 tests across ≥ 6 endpoints incl. validation and 404 paths. `pytest.ini` sets `pythonpath` and `-v` defaults.
- `ruff check` configured in `pyproject.toml`.
- Verify: `pytest -v` green locally; screenshot for submission.

### Step 3 — Frontend (M1: 3 pts)
- React dashboard; `node --test` unit test for `lib/service.js`.
- Verify: `npm run build` produces `dist/`.

### Step 4 — Docker + Compose (M4: 10 pts)
- Backend: `python:3.12-slim`, non-root uid 10001, `HEALTHCHECK`, entrypoint runs `alembic upgrade head` when `RUN_MIGRATIONS=true`.
- Frontend: stage 1 `node:22-alpine` build, stage 2 `nginxinc/nginx-unprivileged:1.27-alpine` (uid 101, port 8080); backend upstream injected via nginx template env var.
- Compose: postgres (healthcheck) → backend (depends_on healthy) → frontend; port 3000 → 8080.
- Verify: `docker compose up --build`, browser on :3000, `docker inspect` shows non-root.

### Step 5 — Git (M3: 5 pts)
- Conventional-commit style messages, one commit per logical module (≥ 10 commits).
- `.gitignore` covers `.env`, `__pycache__`, `node_modules`, `.venv`, `.terraform`, `*.tfstate`.

### Step 6 — CI/CD + Trivy (M5: 15 pts, M6: 5 pts)
- Jobs: `backend-test` (ruff + pytest vs Postgres service), `frontend-build`, `infra-validate` (helm lint/template, terraform fmt/validate), `build-scan-push` (buildx, Trivy HIGH/CRITICAL exit 1 on both images, SARIF upload, SBOM artifact, push `ghcr.io/<owner>/fleetpulse-{backend,frontend}:<sha>`), `deploy` (main only, gated by repo variable `DEPLOY_ENABLED`).
- Verify locally: `trivy image` on both images; YAML validated; first push on GitHub turns the pipeline green.

### Step 7 — Terraform (M7: 15 pts)
- Modules `terraform-aws-modules/vpc` and `/eks` pinned; VPC `10.40.0.0/16`, 2 AZs, 2 public + 2 private subnets, single NAT; EKS 1.31 with managed node group (t3.medium, 2–3 nodes); addons incl. EBS CSI with IRSA; kubernetes-required subnet tags for ELB discovery.
- `terraform.tfvars.example`, `backend.tf.example` (S3 state), outputs incl. `aws eks update-kubeconfig` command.
- Verify locally: `terraform init -backend=false`, `terraform fmt -check`, `terraform validate`. `plan/apply/destroy` require AWS credentials (student runs; evidence screenshots).

### Step 8 — Kubernetes + Helm (M8: 15 pts)
- `k8s/namespace.yaml`, `k8s/storageclass-gp3.yaml`, bootstrap scripts for ingress-nginx + metrics-server.
- Chart templates: configmap, secret, postgres (Deployment + PVC + Service), migrate-job (hook), backend/frontend Deployments (2 replicas, probes, resources, securityContext), ClusterIP Services, Ingress (`/api` → backend, `/` → frontend), HPA, PDB, ServiceMonitor, Grafana dashboard ConfigMap, NOTES.txt.
- Verify: `helm lint`, `helm template`, then on minikube: `helm upgrade --install`, pods Running, Ingress reachable.

### Step 9 — Observability (M9: 10 pts)
- `monitoring/kube-prometheus-stack-values.yaml`: Grafana enabled, sidecar dashboards on, ServiceMonitor selectors opened.
- Verify: Prometheus Targets `UP`, Grafana dashboard panels populated after `scripts/load-test.sh`.

### Step 10 — Documentation (M10: 5 pts)
- Root `README.md` (what/why/how to run/architecture), `docs/SUBMISSION.md` (criterion → file → evidence table), `docs/DEMO.md` (15-step live demo script), `docs/TRIVY.md`.

---

## 4. Verification matrix

| Check | Command | Expected |
|---|---|---|
| Unit/API tests | `make test` | all pass |
| Lint | `make lint` | ruff clean |
| Frontend build | `make fe-build` | `dist/` produced |
| Compose | `make up` | 3 services healthy; UI on :3000 |
| Non-root | `docker inspect --format '{{.Config.User}}'` | `10001` / `nginx` |
| Trivy | `make scan` | 0 HIGH/CRITICAL (fixed) |
| Helm | `make helm-lint` | 0 errors |
| Terraform | `make tf-validate` | Success |
| K8s (minikube) | `make k8s-up` | pods Running, Ingress serves UI |

---

## 5. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Base image CVEs fail the Trivy gate | `ignore-unfixed: true`; pin recent slim/alpine bases; `.trivyignore` documented if a justified exception is needed |
| GHCR packages are private by default → ImagePullBackOff | README documents making packages public or `scripts/ghcr-pull-secret.sh` |
| PVC pending on EKS | EBS CSI addon + gp3 StorageClass in `k8s/` |
| Migrations race with 2 replicas | Helm hook Job runs migrations once per release |
| AWS cost | `terraform destroy` step in demo runbook; single NAT; small node group |
