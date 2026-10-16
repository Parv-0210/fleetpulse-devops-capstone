# Live demo runbook (≈ 15 minutes)

Pre-flight (do before the session): `terraform apply` finished, `k8s/README.md` EKS steps done,
monitoring installed, repository variable `DEPLOY_ENABLED=true`, `/etc/hosts` or DNS points the
Ingress host at the NLB. Have three terminals open: repo, `kubectl`, browser.

| # | Step | Command / action | What to say |
|---|---|---|---|
| 1 | Application | open `http://<ingress-host>/`; register a vehicle, bump its odometer, log a service | derived OK / DUE SOON / OVERDUE state, KPI cards update |
| 2 | API | open `/docs`; run GET, POST, PUT, DELETE on `/api/vehicles` | 13 routes, validation (422), conflict (409) |
| 3 | Database | `kubectl exec -n fleetpulse fleetpulse-postgres-0 -- psql -U fleetpulse -c '\dt' -c 'select version_num from alembic_version'` | two Alembic revisions manage the schema |
| 4 | Git | edit `frontend/src/components/Sidebar.jsx` (e.g. the tagline), `git commit -m "feat(ui): ..."`, `git push` | meaningful commits, `.gitignore` |
| 5 | CI | GitHub → Actions → watch `backend-test`, `frontend-build`, `infra-validate` run in parallel | tests are the first gate |
| 6 | Docker | show `backend/Dockerfile` (two stages, uid 10001) and `frontend/Dockerfile` (node → nginx-unprivileged) | non-root, small images |
| 7 | Security | expand the Trivy step in `build-scan-push`; show the Security tab (SARIF) and the SBOM artifact | HIGH/CRITICAL would stop the push |
| 8 | Registry | GitHub → Packages → `fleetpulse-backend` → tags = the commit SHA you just pushed | commit ↔ image traceability |
| 9 | Terraform | `terraform/vpc.tf`, `eks.tf`; AWS console VPC + EKS pages | infra as code, `terraform destroy` later |
| 10 | Kubernetes | `kubectl get pods,svc -n fleetpulse` | 2 backend + 2 frontend replicas, ClusterIP services |
| 11 | Helm | `helm list -n fleetpulse`, `helm history fleetpulse -n fleetpulse` | the deploy job created a new revision with the new SHA |
| 12 | Ingress | reload the browser → the UI change from step 4 is live | `/` → frontend, `/api` → backend |
| 13 | HPA | `URL=http://<ingress-host> REQUESTS=3000 CONCURRENCY=40 ./scripts/load-test.sh`; `kubectl get hpa -n fleetpulse -w` | CPU target 60 %, 2 → N replicas |
| 14 | Monitoring | Prometheus Targets (UP), Grafana "FleetPulse / Overview" | request rate, p95, error %, fleet gauges |
| 15 | Troubleshooting | `kubectl apply -f troubleshooting/broken-image.yaml` → `describe`; `broken-service.yaml` → `get endpoints` | ImagePullBackOff; selector mismatch |

Wrap-up: `kubectl delete -f troubleshooting/`, and after grading: `helm uninstall ingress-nginx -n ingress-nginx`
then `terraform destroy`.

## Recorded-walkthrough variant

Record steps 1–15 with `minikube` (`make k8s-up`, `make monitoring`) when AWS is not available during the
session; the only differences are the Ingress host (`fleetpulse.local`) and the absence of the AWS console step.
