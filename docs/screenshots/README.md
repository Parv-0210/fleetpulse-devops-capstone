# Screenshots for submission

Capture these while running the demo (names referenced from `docs/SUBMISSION.md`):

```text
01-app-desktop.png          UI at http://localhost:3000 (compose) or the Ingress host
02-app-mobile.png           same page at phone width (DevTools device toolbar)
03-pytest.png               `cd backend && pytest -v`
04-git-log.png              `git log --oneline` (≥ 10 commits)
05-compose-up.png           `docker compose up --build` output
06-compose-browser.png      browser at http://localhost:3000
07-actions-green.png        GitHub Actions run, all jobs green
08-ghcr-tags.png            GHCR package page with SHA tags
09-trivy.png                Trivy step output in the pipeline
10-terraform-plan.png       `terraform plan` summary
11-aws-vpc.png              AWS console: VPC + subnets
12-aws-eks.png              AWS console: EKS cluster + node group
13-terraform-destroy.png    `terraform destroy` completion
14-kubectl-pods.png         `kubectl get pods -n fleetpulse` (all Running)
15-kubectl-svc.png          `kubectl get svc -n fleetpulse`
16-helm-list.png            `helm list -n fleetpulse`
17-ingress-browser.png      browser at the Ingress hostname
18-metrics-curl.png         `curl http://<backend>/metrics`
19-prometheus-targets.png   Prometheus Targets page, app UP
20-grafana.png              Grafana "FleetPulse / Overview" with data
```
