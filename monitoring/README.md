# Observability — Prometheus + Grafana

```text
FastAPI /metrics  <-- scrape (15s) --  Prometheus  <-- query --  Grafana
     ^                                     ^
     |  prometheus-fastapi-instrumentator  |  ServiceMonitor (created by the FleetPulse Helm chart)
     |  + custom FleetCollector            |
```

## What the backend exposes

| Metric | Type | Source |
|---|---|---|
| `http_requests_total{handler,method,status}` | counter | instrumentator |
| `http_request_duration_seconds_bucket` | histogram | instrumentator |
| `http_request_size_bytes` / `http_response_size_bytes` | summary | instrumentator |
| `fleetpulse_vehicles{status}` | gauge | custom collector, computed from the DB at scrape time |
| `fleetpulse_vehicles_by_service_state{state}` | gauge | custom collector (OK / DUE_SOON / OVERDUE) |
| `fleetpulse_service_records_created_total{service_type}` | counter | incremented on POST .../services |

## Install

```bash
./monitoring/install.sh
```

The FleetPulse chart (`monitoring.serviceMonitor.enabled=true`, default) creates a `ServiceMonitor`
labelled `release: kube-prometheus-stack` and a dashboard `ConfigMap` labelled `grafana_dashboard: "1"`.
Nothing else is needed: Prometheus discovers the backend pods and Grafana loads "FleetPulse / Overview".

## Verify (screenshots for the rubric)

```bash
# 1. raw metrics
kubectl port-forward svc/fleetpulse-backend 8000:8000 -n fleetpulse
curl -s http://localhost:8000/metrics | grep -E "^(http_requests_total|fleetpulse_)"

# 2. Prometheus targets page -> serviceMonitor/fleetpulse/fleetpulse-backend/0  UP
kubectl port-forward svc/kube-prometheus-stack-prometheus 9090:9090 -n monitoring

# 3. Grafana -> Dashboards -> FleetPulse / Overview (generate traffic first)
kubectl port-forward svc/kube-prometheus-stack-grafana 3001:80 -n monitoring
URL=http://fleetpulse.local ./scripts/load-test.sh
```

Useful PromQL:

```promql
sum by (handler) (rate(http_requests_total{namespace="fleetpulse"}[2m]))
histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{namespace="fleetpulse"}[5m])))
max by (state) (fleetpulse_vehicles_by_service_state)
```
