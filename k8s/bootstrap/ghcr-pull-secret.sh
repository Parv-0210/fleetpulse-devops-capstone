#!/usr/bin/env bash
# Creates an image pull secret for GHCR. Only needed while the packages are private
# (GitHub makes them private by default - making them public is the simpler option for a demo).
#   GHCR_USER=<github-user> GHCR_TOKEN=<PAT with read:packages> ./k8s/bootstrap/ghcr-pull-secret.sh
# Then deploy with: --set 'image.pullSecrets[0].name=ghcr-pull'
set -euo pipefail
: "${GHCR_USER:?set GHCR_USER}"
: "${GHCR_TOKEN:?set GHCR_TOKEN (PAT with read:packages)}"
NAMESPACE="${NAMESPACE:-fleetpulse}"
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
kubectl create secret docker-registry ghcr-pull \
  --namespace "$NAMESPACE" \
  --docker-server=ghcr.io \
  --docker-username="$GHCR_USER" \
  --docker-password="$GHCR_TOKEN" \
  --dry-run=client -o yaml | kubectl apply -f -
echo "secret ghcr-pull ready in namespace $NAMESPACE"
