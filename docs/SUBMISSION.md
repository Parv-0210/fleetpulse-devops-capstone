# Submission map — rubric criterion → where to look

Repository: https://github.com/Parv-0210/fleetpulse-devops-capstone
Screenshots live in `docs/screenshots/` (file names below).

## M1 — Application (10)

| Criterion | Evidence |
|---|---|
| FastAPI starts, `/health` responds | `backend/app/routes/system.py`; `curl :8000/health` → `{"status":"UP"}` |
| ≥ 4 REST endpoints (GET/POST/PUT/DELETE) | `backend/app/routes/vehicles.py` (13 routes incl. GET/POST/PUT/DELETE `/api/vehicles`) |
| PostgreSQL + ≥ 1 Alembic-managed table | `backend/alembic/versions/0001_create_vehicles.py`, `0002_service_records.py`; `alembic_version` = `0002_service_records` |
| Frontend renders and calls the API | `frontend/src/App.jsx`, `frontend/src/api.js` → `/api/vehicles`, `/api/fleet/stats` |
| Responsive, usable UI | `frontend/src/styles.css` (breakpoints 900px / 560px) — `screenshots/01-app-desktop.png`, `02-app-mobile.png` |

## M2 — Testing (10)

| Criterion | Evidence |
|---|---|
| `pytest` runs without errors | `cd backend && pytest -v` → 19 passed — `screenshots/03-pytest.png` |
| ≥ 5 tests across ≥ 3 endpoints | `backend/tests/test_system.py` (4), `test_vehicles.py` (8), `test_services.py` (5), `test_fleet_and_metrics.py` (2) |
| Test DB / mock, not production | `backend/tests/conftest.py`: SQLite in-memory (local) or `TEST_DATABASE_URL` Postgres service (CI); `get_db` dependency override |
| `pytest.ini` / `conftest.py` configured | `backend/pytest.ini` (pythonpath, testpaths, strict markers), `backend/tests/conftest.py` |
| Code quality (bonus) | `ruff check` + `ruff format --check` in CI, config in `backend/pyproject.toml` |

## M3 — Git and GitHub (5)

| Criterion | Evidence |
|---|---|
| Public repository | link above |
| Meaningful commit messages | `git log --oneline` — conventional-commit style, one commit per module — `screenshots/04-git-log.png` |
| `.gitignore` | root `.gitignore` excludes `.env`, `__pycache__/`, `node_modules/`, `.venv/`, Terraform state |

## M4 — Docker (10)

| Criterion | Evidence |
|---|---|
| `backend/Dockerfile` builds | two-stage build (deps venv → slim runtime) |
| `frontend/Dockerfile` multi-stage | `node:22-alpine` build → `nginxinc/nginx-unprivileged:1.30-alpine-slim` runtime |
| Non-root users | backend `USER 10001`, frontend `USER nginx` (uid 101); `docker inspect --format '{{.Config.User}}'` |
| `docker compose up --build` starts 3 services | `docker-compose.yml` with Postgres health-gated startup — `screenshots/05-compose-up.png`, `06-compose-browser.png` |

## M5 — CI/CD (15)

| Criterion | Evidence |
|---|---|
| Workflow file | `.github/workflows/ci-cd.yml` (7 jobs) and `.github/workflows/security.yml` (6 jobs: CodeQL ×2, pip-audit, npm audit, secrets + IaC) |
| Triggers on push to `main` | `on.push.branches: [main]` (plus PRs and manual dispatch) |
| pytest job fails the build | job `backend-test` is a `needs:` of `build-scan-push`; a failing test stops image builds |
| Frontend built in pipeline | job `frontend-build` (`npm test`, `npm run build`, artifact `frontend-dist`) |
| Both images built | job `build-scan-push` matrix `[backend, frontend]` with buildx |
| Pushed to GHCR | `docker/login-action` + `docker/build-push-action` (multi-arch) → `ghcr.io/parv-0210/fleetpulse-*` |
| Deployment verified in CI | job `kind-smoke`: Helm install on a kind cluster with the pushed SHA images, `helm test`, curl `/health`, `/ready`, `/api/fleet/stats`, `/metrics` |
| SHA-based tags | `docker/metadata-action` tags `type=sha,format=long` and `sha-<short>`; never `latest` — `screenshots/07-actions-green.png`; tags visible on the GHCR package pages |

## M6 — DevSecOps (5)

| Criterion | Evidence |
|---|---|
| Trivy on both images | `aquasecurity/trivy-action` step per matrix component, before the push step |
| Fails on HIGH/CRITICAL | `severity: HIGH,CRITICAL`, `exit-code: "1"`, `ignore-unfixed: true` |
| Explanation | `docs/TRIVY.md` — `screenshots/09-trivy.png` |
| Beyond the rubric | `security.yml`: CodeQL SAST, pip-audit and npm audit SCA, Trivy secret scan of full git history, Trivy IaC misconfiguration scan (CRITICAL blocks) |

## M7 — Terraform (15)

| Criterion | Evidence |
|---|---|
| `terraform/` valid HCL | `versions.tf`, `providers.tf`, `variables.tf`, `vpc.tf`, `eks.tf`, `outputs.tf` |
| `terraform init` | pinned modules vpc 5.21 / eks 20.37 / iam 5.60 resolve cleanly |
| `terraform plan` non-empty | `Plan: 72 to add` — `screenshots/10-terraform-plan.png` |
| VPC with ≥ 2 public subnets | `vpc.tf`: 2 AZs × (public + private), NAT, ELB tags — `screenshots/11-aws-vpc.png`, `11-aws-vpc-eks-cli.png` |
| EKS with ≥ 1 node group | `eks.tf`: EKS 1.36 ACTIVE, managed node group (t3.medium ×2) ACTIVE, OIDC deploy role — `screenshots/11-aws-vpc-eks-cli.png`, `14-kubectl-pods.png` |
| `terraform destroy` clean | `scripts/aws-down.sh` — screenshot `13-terraform-destroy.png` added after grading, when the cluster is torn down |
| `terraform.tfvars.example`, no secrets | present; `terraform.tfvars` and `backend.tf` are git-ignored |

## M8 — Kubernetes + Helm (15)

| Criterion | Evidence |
|---|---|
| `k8s/namespace.yaml` | present, with Pod Security labels |
| Helm chart | `helm/fleetpulse/{Chart.yaml,values.yaml,templates/}` (+ `values-dev.yaml`, `values-prod.yaml`) |
| `helm upgrade --install` works | pipeline job "Deploy · helm upgrade --install on EKS" (OIDC, SHA tags), `helm test` passes — `screenshots/16-helm-list.png` |
| 2 replicas each | `backend.replicaCount: 2`, `frontend.replicaCount: 2` — `screenshots/14-kubectl-pods.png` |
| ClusterIP Services | `templates/backend-service.yaml`, `frontend-service.yaml` — `screenshots/15-kubectl-svc.png` |
| Ingress `/` → frontend, `/api` → backend | `templates/ingress.yaml` — `screenshots/17-ingress-browser.png` |
| All pods Running | `screenshots/14-kubectl-pods.png`, `16-helm-list.png` |

## M9 — Observability (10)

| Criterion | Evidence |
|---|---|
| `/metrics` Prometheus format | `backend/app/metrics.py`, instrumentator — `screenshots/18-metrics-curl.png` |
| Prometheus scraping the app | `templates/servicemonitor.yaml` + `monitoring/kube-prometheus-stack-values.yaml` — `screenshots/19-prometheus-targets.png` |
| Grafana accessible | `monitoring/install.sh` port-forward — `screenshots/20-grafana.png` |
| Panel with live app metrics | `helm/fleetpulse/dashboards/fleetpulse.json` (request rate, p95 latency, error %, fleet gauges) |

## M10 — Presentation + docs (5)

| Criterion | Evidence |
|---|---|
| Root `README.md` | present |
| Live demo | `scripts/demo.sh`: commit → pipeline → new image tag → rollout |
