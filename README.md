# FleetPulse — Fleet Maintenance Tracker · DevOps Capstone

[![CI/CD](https://github.com/Parv-0210/fleetpulse-devops-capstone/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/Parv-0210/fleetpulse-devops-capstone/actions/workflows/ci-cd.yml)

FleetPulse keeps a vehicle fleet road-worthy. Operators register vehicles, keep odometers current and
log maintenance (oil changes, tyres, brakes, inspections, repairs). The API computes, for every vehicle,
how many kilometres remain until its next service and classifies it as **OK**, **DUE SOON** or
**OVERDUE**; the dashboard surfaces the vehicles that need attention first and the 30-day maintenance spend.

The application is deliberately small so the DevOps path around it can be shown end to end:

```text
developer ──git push──▶ GitHub ──▶ GitHub Actions
                                    ├─ ruff + pytest (Postgres service) + Alembic round-trip
                                    ├─ frontend unit tests + Vite build
                                    ├─ helm lint / terraform validate
                                    ├─ docker buildx  ──▶ Trivy gate (HIGH/CRITICAL = fail)
                                    ├─ push ghcr.io/parv-0210/fleetpulse-{backend,frontend}:<git sha>
                                    └─ helm upgrade --install ──▶ EKS (Terraform-provisioned VPC + EKS)
                                                                    ├─ Ingress  /  → React (nginx)   / api → FastAPI
                                                                    ├─ HPA · PDB · probes · non-root pods
                                                                    └─ Prometheus (ServiceMonitor) → Grafana dashboard
```

## Stack

| Layer | Technology |
|---|---|
| Frontend | React 19 + Vite 7, served by `nginx-unprivileged` (multi-stage build, 31 MB image) |
| Backend | FastAPI, SQLAlchemy 2, Pydantic v2, Alembic migrations, `prometheus-fastapi-instrumentator` + custom collectors |
| Database | PostgreSQL 16 (compose volume / Kubernetes StatefulSet + PVC) |
| Tests & quality | pytest (19 tests, SQLite in-memory locally, Postgres in CI), ruff, `node --test` |
| Containers | Multi-stage Dockerfiles, non-root (uid 10001 / nginx 101), health checks, Trivy-clean |
| CI/CD | GitHub Actions → GHCR, image tag = commit SHA, SARIF + SBOM artifacts |
| Infrastructure | Terraform: VPC (2 public + 2 private subnets, NAT) + EKS 1.31 managed node group + EBS CSI |
| Kubernetes | Helm chart: Deployments (2 replicas), ClusterIP Services, Ingress, HPA, PDB, ServiceMonitor |
| Observability | kube-prometheus-stack; Grafana dashboard shipped inside the Helm chart |

## What makes it different from the course's TaskBoard reference

- **Own domain and data model** — two related tables (`vehicles`, `service_records`) with server-side derived
  maintenance state, plate normalisation, duplicate-plate conflicts and cascade deletes, evolved through
  two Alembic revisions.
- **Business metrics, not just HTTP metrics** — a custom Prometheus collector exposes
  `fleetpulse_vehicles{status}`, `fleetpulse_vehicles_by_service_state{state}` and
  `fleetpulse_service_records_created_total{service_type}`, computed at scrape time so every replica agrees.
- **Dashboard-as-code** — the Grafana dashboard is a ConfigMap in the Helm chart, discovered by the
  Grafana sidecar; `helm upgrade --install` is the only step.
- **Race-free migrations with multiple replicas** — an init container runs `python -m app.migrate`, which
  holds a PostgreSQL advisory lock around `alembic upgrade head`; `/ready` only succeeds once the schema exists.
- **Security by default** — runtime images contain no pip/setuptools, Alpine is patched at build time,
  pods run as non-root with a read-only root filesystem and all capabilities dropped, the namespace
  enforces Pod Security "baseline", and Trivy results feed the GitHub Security tab plus a CycloneDX SBOM.
- **Infra is tested too** — CI lints/renders the chart, runs `terraform validate` and an Alembic
  upgrade→downgrade→upgrade round-trip on a real PostgreSQL.

## API

| Method | Path | Description |
|---|---|---|
| GET | `/health`, `/ready`, `/metrics` | liveness, readiness (DB + schema), Prometheus |
| GET | `/api/vehicles?status=&q=` | list / filter / search |
| POST | `/api/vehicles` | register (201, 409 on duplicate plate) |
| GET / PUT / DELETE | `/api/vehicles/{id}` | read / update (incl. odometer) / remove |
| GET / POST | `/api/vehicles/{id}/services` | service history / log a service |
| DELETE | `/api/services/{id}` | remove a service record |
| GET | `/api/fleet/stats` | dashboard KPIs |

Swagger UI: `/docs`.

## Run it locally

```bash
git clone https://github.com/Parv-0210/fleetpulse-devops-capstone.git
cd fleetpulse-devops-capstone
docker compose up --build            # FRONTEND_PORT=3030 docker compose up --build  if 3000 is taken
```

- UI → http://localhost:3000 (demo data is seeded on first start)
- API → http://localhost:8000/docs · http://localhost:8000/health · http://localhost:8000/metrics

Without Docker (needs Python 3.12 via `uv`, Node 22, a PostgreSQL):

```bash
make venv && make test && make lint          # backend
make fe-install && make fe-test && make fe-build
cd backend && cp .env.example .env && .venv/bin/python -m app.migrate && .venv/bin/uvicorn app.main:app --reload
cd frontend && npm run dev                   # proxies /api to :8000
```

## Pipeline, infrastructure and cluster

| Step | Command / location |
|---|---|
| CI/CD | `.github/workflows/ci-cd.yml` — runs on every push to `main` and on PRs |
| Images | `ghcr.io/parv-0210/fleetpulse-backend:<sha>`, `ghcr.io/parv-0210/fleetpulse-frontend:<sha>` |
| AWS | `cd terraform && terraform init && terraform plan && terraform apply` → see `terraform/README.md` |
| Cluster prerequisites | `k8s/README.md` (namespace, gp3 StorageClass, ingress-nginx) |
| Deploy | `./scripts/deploy.sh prod` or `make k8s-deploy-prod` (Helm, SHA tags) |
| Local Kubernetes | `make k8s-up` (minikube profile `fleetpulse`) |
| Monitoring | `make monitoring` → `monitoring/README.md` |
| Troubleshooting lab | `troubleshooting/README.md` |
| Everything CI checks, locally | `make check` |

Enable automatic deploys from the pipeline by setting repository variable `DEPLOY_ENABLED=true`,
variables `AWS_REGION`, `EKS_CLUSTER_NAME`, `INGRESS_HOST` and secrets `AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY` (an IAM user with EKS access). No credentials are ever committed.

## Repository layout

```text
backend/            FastAPI app (app/), Alembic migrations, tests, Dockerfile
frontend/           React app (src/), nginx template, Dockerfile
docker-compose.yml  Local three-service stack
.github/workflows/  CI/CD pipeline
terraform/          AWS VPC + EKS
k8s/                Namespace, StorageClass, bootstrap scripts
helm/fleetpulse/    Helm chart (+ Grafana dashboard JSON)
monitoring/         kube-prometheus-stack values + installer
troubleshooting/    Deliberately broken manifests for the live demo
scripts/            load-test, deploy, minikube bring-up
docs/               PLAN.md, SUBMISSION.md (rubric → evidence), DEMO.md, TRIVY.md, screenshots/
```

## Documentation

- `docs/PLAN.md` — design and implementation plan
- `docs/SUBMISSION.md` — every rubric criterion mapped to files, commands and evidence
- `docs/DEMO.md` — the 15-step live demo script
- `docs/TRIVY.md` — what the scanner checks and how the images were made clean
