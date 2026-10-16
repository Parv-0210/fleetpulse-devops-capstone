#!/usr/bin/env bash
# Deploys (or upgrades) FleetPulse with Helm using the current commit SHA as the image tag.
#   ./scripts/deploy.sh                # EKS values, images from GHCR
#   ./scripts/deploy.sh dev            # minikube values, local images
#   SHA=<sha> INGRESS_HOST=app.example.com ./scripts/deploy.sh
set -euo pipefail
cd "$(dirname "$0")/.."
ENV="${1:-prod}"
NAMESPACE="${NAMESPACE:-fleetpulse}"
SHA="${SHA:-$(git rev-parse HEAD)}"
OWNER="${OWNER:-parv-0210}"
EXTRA=()
if [ "$ENV" = "prod" ]; then
  EXTRA+=(--set backend.tag="$SHA" --set frontend.tag="$SHA" --set image.owner="$OWNER")
  [ -n "${INGRESS_HOST:-}" ] && EXTRA+=(--set ingress.host="$INGRESS_HOST")
fi
kubectl apply -f k8s/namespace.yaml
helm upgrade --install fleetpulse ./helm/fleetpulse \
  --namespace "$NAMESPACE" \
  -f "helm/fleetpulse/values-${ENV}.yaml" \
  "${EXTRA[@]}" \
  --wait --timeout 10m
kubectl get pods,svc,ingress,hpa -n "$NAMESPACE"
