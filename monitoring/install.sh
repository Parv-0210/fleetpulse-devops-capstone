#!/usr/bin/env bash
# Installs Prometheus Operator + Prometheus + Grafana (kube-prometheus-stack) into the "monitoring" namespace.
set -euo pipefail
cd "$(dirname "$0")"
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts >/dev/null
helm repo update >/dev/null
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  -f kube-prometheus-stack-values.yaml \
  --wait --timeout 10m
cat <<MSG

Prometheus : kubectl port-forward svc/kube-prometheus-stack-prometheus 9090:9090 -n monitoring
             -> http://localhost:9090/targets   (look for serviceMonitor/fleetpulse/fleetpulse-backend = UP)
Grafana    : kubectl port-forward svc/kube-prometheus-stack-grafana 3001:80 -n monitoring
             -> http://localhost:3001  (admin / fleetpulse-admin)  -> Dashboards -> "FleetPulse / Overview"
MSG
