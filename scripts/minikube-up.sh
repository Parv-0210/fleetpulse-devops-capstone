#!/usr/bin/env bash
# One-shot local Kubernetes demo: minikube profile + local images + Helm release + monitoring.
#   ./scripts/minikube-up.sh            # app only
#   WITH_MONITORING=1 ./scripts/minikube-up.sh
set -euo pipefail
cd "$(dirname "$0")/.."
PROFILE="${PROFILE:-fleetpulse}"
minikube status -p "$PROFILE" >/dev/null 2>&1 || \
  minikube start -p "$PROFILE" --driver=docker --cpus=4 --memory=6144 --addons=ingress,metrics-server
kubectl config use-context "$PROFILE" >/dev/null
docker compose build
minikube -p "$PROFILE" image load fleetpulse-backend:local
minikube -p "$PROFILE" image load fleetpulse-frontend:local
./scripts/deploy.sh dev
if [ "${WITH_MONITORING:-0}" = "1" ]; then ./monitoring/install.sh; fi
cat <<MSG

Ingress host: fleetpulse.local
  Linux : echo "$(minikube -p "$PROFILE" ip) fleetpulse.local" | sudo tee -a /etc/hosts
  macOS : add "127.0.0.1 fleetpulse.local" to /etc/hosts and run: minikube -p $PROFILE tunnel
MSG
