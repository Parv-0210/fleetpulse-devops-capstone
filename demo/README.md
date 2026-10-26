# Demo

| File | What it is |
|---|---|
| [FleetPulse-Demo.mp4](FleetPulse-Demo.mp4) | Presentation video (about 7 minutes, 1080p, narrated) |
| [FleetPulse-Presentation.pdf](FleetPulse-Presentation.pdf) | Slide deck (PDF, 13 slides) |
| [FleetPulse-Presentation.pptx](FleetPulse-Presentation.pptx) | Same slide deck as PowerPoint, with speaker notes |

## What the video covers

| Time | Section |
|---|---|
| 0:00 | Introduction and the problem FleetPulse solves |
| 0:44 | Architecture on AWS EKS |
| 1:10 | Live app (`docker compose up`): dashboard, filters, search |
| 1:34 | Live: register a vehicle, log a service, the counter resets |
| 2:00 | Live: Swagger API, `/health`, `/metrics` with fleet gauges |
| 2:21 | Tests (pytest, 19 tests) and Docker (multi-stage, non-root) |
| 3:08 | CI/CD pipeline, then the run on GitHub Actions (3:42) |
| 4:02 | DevSecOps: Trivy gate and what it found |
| 4:35 | Terraform: VPC + EKS on AWS |
| 5:06 | Kubernetes and Helm on EKS |
| 5:36 | Observability: Prometheus and Grafana |
| 5:59 | Live delivery flow, lessons learned, summary |
