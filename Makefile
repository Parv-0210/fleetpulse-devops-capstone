# FleetPulse developer entry points. Run `make help` to list targets.
SHELL := /bin/bash
.DEFAULT_GOAL := help

PY        := backend/.venv/bin
SHA       ?= $(shell git rev-parse --short HEAD)
PROFILE   ?= fleetpulse
NAMESPACE ?= fleetpulse

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ---------- local development ----------
venv: ## Create the backend virtualenv (Python 3.12 via uv) and install dev dependencies
	cd backend && uv venv --python 3.12 .venv && uv pip install -r requirements-dev.txt --python .venv/bin/python

test: ## Run backend tests (pytest -v)
	cd backend && .venv/bin/pytest -v

lint: ## Lint + format check (ruff)
	cd backend && .venv/bin/ruff check . && .venv/bin/ruff format --check .

fe-install: ## Install frontend dependencies
	cd frontend && npm ci --no-audit --no-fund

fe-test: ## Frontend unit tests (node --test)
	cd frontend && npm test

fe-build: ## Build the frontend bundle
	cd frontend && npm run build

check: lint test fe-test fe-build helm-lint tf-validate ## Everything CI runs, locally

# ---------- docker ----------
up: ## docker compose up --build (UI :3000, API :8000). Override: FRONTEND_PORT=3030 make up
	docker compose up --build

up-d: ## Same as `up`, detached
	docker compose up --build -d

down: ## Stop the compose stack (keeps the DB volume)
	docker compose down

down-v: ## Stop the compose stack and delete the DB volume
	docker compose down -v

build: ## Build both images (fleetpulse-backend:local, fleetpulse-frontend:local)
	docker compose build

scan: build ## Trivy scan both images with the same gate as CI (HIGH/CRITICAL, fixed only)
	trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 --scanners vuln fleetpulse-backend:local
	trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 --scanners vuln fleetpulse-frontend:local

# ---------- helm / kubernetes ----------
helm-lint: ## Lint and render the chart with every values overlay
	helm lint helm/fleetpulse
	helm lint helm/fleetpulse -f helm/fleetpulse/values-dev.yaml
	helm lint helm/fleetpulse -f helm/fleetpulse/values-prod.yaml
	helm template fleetpulse helm/fleetpulse -n $(NAMESPACE) -f helm/fleetpulse/values-prod.yaml --set backend.tag=$(SHA) --set frontend.tag=$(SHA) >/dev/null

k8s-up: ## Full local Kubernetes demo on minikube (profile $(PROFILE))
	PROFILE=$(PROFILE) ./scripts/minikube-up.sh

k8s-deploy-dev: ## helm upgrade --install with minikube values
	./scripts/deploy.sh dev

k8s-deploy-prod: ## helm upgrade --install with EKS values and the current git SHA
	./scripts/deploy.sh prod

k8s-status: ## Pods, services, ingress, HPA and Helm release
	kubectl get pods,svc,ingress,hpa -n $(NAMESPACE)
	helm list -n $(NAMESPACE)

k8s-test: ## Run the Helm test pod
	helm test fleetpulse -n $(NAMESPACE)

monitoring: ## Install Prometheus + Grafana (kube-prometheus-stack)
	./monitoring/install.sh

load-test: ## Generate traffic (URL=http://fleetpulse.local make load-test)
	./scripts/load-test.sh

k8s-down: ## Remove the Helm release and the minikube profile
	-helm uninstall fleetpulse -n $(NAMESPACE)
	-minikube delete -p $(PROFILE)

# ---------- terraform ----------
tf-validate: ## terraform fmt/init/validate without touching AWS
	cd terraform && terraform fmt -check -recursive && terraform init -backend=false -input=false >/dev/null && terraform validate

tf-plan: ## terraform plan (needs AWS credentials)
	cd terraform && terraform init -input=false && terraform plan -out=tfplan

tf-apply: ## terraform apply the saved plan
	cd terraform && terraform apply tfplan

tf-destroy: ## terraform destroy (remember to delete LoadBalancer services first)
	cd terraform && terraform destroy

.PHONY: help venv test lint fe-install fe-test fe-build check up up-d down down-v build scan helm-lint k8s-up k8s-deploy-dev k8s-deploy-prod k8s-status k8s-test monitoring load-test k8s-down tf-validate tf-plan tf-apply tf-destroy
