#!/usr/bin/env bash
# Live demo: commit a visible change, watch the pipeline publish SHA-tagged images, see the cluster roll over.
#   ./scripts/demo.sh            (PAUSE=seconds between steps, default 3)
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="/opt/homebrew/bin:$PATH"
APP_URL="${APP_URL:-http://localhost:18080}"
say() { printf '\n\033[1;36m# %s\033[0m\n' "$*"; sleep "${PAUSE:-3}"; }
run() { printf '\033[1;33m$ %s\033[0m\n' "$*"; eval "$@"; }

say "FleetPulse live demo: commit a change -> pipeline -> new image -> cluster rollout"
run "git log --oneline -3"

say "Step 1. What is the cluster running right now?"
run "kubectl get deploy -n fleetpulse -o custom-columns='NAME:.metadata.name,READY:.status.readyReplicas,IMAGE:.spec.template.spec.containers[0].image'"
run "curl -s $APP_URL/ | grep -o 'maintenance control[^<]*' | head -1"

say "Step 2. Make a visible change: the sidebar tagline"
STAMP="$(date +%H:%M)"
run "sed -i '' 's|<small>maintenance control[^<]*</small>|<small>maintenance control · demo $STAMP</small>|' frontend/src/components/Sidebar.jsx"
run "git diff --stat"

say "Step 3. Commit and push to main"
run "git add -A && git commit -m 'feat(ui): tag the sidebar for the live demo ($STAMP)'"
run "git push origin main"

say "Step 4. GitHub Actions: tests, frontend build, infra checks, image build, Trivy gate, push to GHCR (tag = commit SHA)"
run "./scripts/watch-and-deploy.sh"

say "Step 5. The cluster now runs the image built from this commit"
run "kubectl get pods -n fleetpulse"
run "curl -s $APP_URL/ | grep -o 'maintenance control[^<]*' | head -1"
say "Done: same commit SHA in git, in GHCR and in the running pods."
[ -n "${DONE_FILE:-}" ] && touch "$DONE_FILE"
exit 0
