#!/usr/bin/env bash
# Pull-style deploy for clusters GitHub Actions cannot reach (a laptop minikube, a lab cluster).
# Waits for the pipeline run of the current commit to finish, then rolls the cluster to the
# images the pipeline just published, tagged with that commit's SHA.
#
#   ./scripts/watch-and-deploy.sh              # minikube values (default)
#   ENV=prod ./scripts/watch-and-deploy.sh     # EKS values
set -euo pipefail
cd "$(dirname "$0")/.."
ENV="${ENV:-dev}"
NAMESPACE="${NAMESPACE:-fleetpulse}"
OWNER="${OWNER:-$(gh repo view --json owner --jq .owner.login | tr '[:upper:]' '[:lower:]')}"
SHA="$(git rev-parse HEAD)"

echo "==> commit ${SHA:0:7}: waiting for the GitHub Actions run"
for _ in $(seq 1 30); do
  RUN_ID="$(gh run list --commit "$SHA" --limit 1 --json databaseId --jq '.[0].databaseId' 2>/dev/null || true)"
  [ -n "$RUN_ID" ] && break
  sleep 5
done
[ -n "${RUN_ID:-}" ] || { echo "no pipeline run found for $SHA (did you push?)"; exit 1; }
echo "    https://github.com/$(gh repo view --json nameWithOwner --jq .nameWithOwner)/actions/runs/$RUN_ID"
gh run watch "$RUN_ID" --exit-status --interval 10 >/dev/null
echo "==> pipeline green: images ghcr.io/$OWNER/fleetpulse-{backend,frontend}:${SHA:0:7} are published"

echo "==> helm upgrade to the new SHA"
helm upgrade --install fleetpulse ./helm/fleetpulse -n "$NAMESPACE" --create-namespace \
  -f "helm/fleetpulse/values-${ENV}.yaml" \
  --set image.pullPolicy=IfNotPresent \
  --set backend.repository= --set frontend.repository= \
  --set image.owner="$OWNER" \
  --set backend.tag="$SHA" --set frontend.tag="$SHA" \
  --wait --timeout 10m
kubectl rollout status deployment/fleetpulse-backend -n "$NAMESPACE" --timeout=5m
kubectl rollout status deployment/fleetpulse-frontend -n "$NAMESPACE" --timeout=5m
echo "==> running images"
kubectl get deploy -n "$NAMESPACE" -o custom-columns='NAME:.metadata.name,READY:.status.readyReplicas,IMAGE:.spec.template.spec.containers[0].image'
helm history fleetpulse -n "$NAMESPACE" --max 3
