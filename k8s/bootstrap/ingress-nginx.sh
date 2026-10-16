#!/usr/bin/env bash
# Installs the NGINX Ingress Controller. On EKS its Service becomes an AWS Network Load Balancer;
# on minikube use `minikube addons enable ingress` instead (see k8s/README.md).
set -euo pipefail
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx >/dev/null
helm repo update >/dev/null
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --set controller.service.type=LoadBalancer \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/aws-load-balancer-type"=nlb \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/aws-load-balancer-scheme"=internet-facing \
  --set controller.metrics.enabled=true \
  --wait --timeout 5m
echo
echo "Ingress controller address (may take ~2 minutes to appear):"
kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].hostname}{.status.loadBalancer.ingress[0].ip}{"\n"}'
