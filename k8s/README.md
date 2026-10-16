# Kubernetes bootstrap

Cluster-level prerequisites that live outside the Helm chart. Apply them once per cluster,
then deploy the application with Helm (`helm/fleetpulse`).

| File | Apply on | Purpose |
|---|---|---|
| `namespace.yaml` | all clusters | `fleetpulse` namespace with Pod Security Admission labels |
| `storageclass-gp3.yaml` | EKS only | default gp3 StorageClass backed by the EBS CSI add-on |
| `bootstrap/ingress-nginx.sh` | EKS / generic | NGINX Ingress Controller exposed through an AWS NLB |
| `bootstrap/metrics-server.sh` | generic | Metrics Server for HPA (EKS add-on and minikube addon already provide it) |
| `bootstrap/ghcr-pull-secret.sh` | any | pull secret if the GHCR packages are private |

## minikube (local)

```bash
minikube start -p fleetpulse --driver=docker --cpus=4 --memory=6144 --addons=ingress,metrics-server
kubectl apply -f k8s/namespace.yaml

# build the images locally and load them into the cluster
docker compose build
minikube -p fleetpulse image load fleetpulse-backend:local fleetpulse-frontend:local

helm upgrade --install fleetpulse ./helm/fleetpulse -n fleetpulse -f helm/fleetpulse/values-dev.yaml --wait
echo "$(minikube -p fleetpulse ip) fleetpulse.local" | sudo tee -a /etc/hosts   # Linux
# macOS with the docker driver: run `minikube -p fleetpulse tunnel` and map 127.0.0.1 instead
open http://fleetpulse.local
```

## EKS (after `terraform apply`)

```bash
$(cd terraform && terraform output -raw configure_kubectl)
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/storageclass-gp3.yaml
./k8s/bootstrap/ingress-nginx.sh

SHA=$(git rev-parse HEAD)
helm upgrade --install fleetpulse ./helm/fleetpulse -n fleetpulse \
  -f helm/fleetpulse/values-prod.yaml \
  --set backend.tag=$SHA --set frontend.tag=$SHA \
  --set ingress.host=fleetpulse.<nlb-ip>.nip.io --wait
```

## Verify

```bash
kubectl get pods -n fleetpulse          # all Running, backend/frontend 2 replicas each
kubectl get svc -n fleetpulse           # ClusterIP services for backend, frontend, postgres
kubectl get ingress,hpa -n fleetpulse
helm list -n fleetpulse
helm test fleetpulse -n fleetpulse
```
