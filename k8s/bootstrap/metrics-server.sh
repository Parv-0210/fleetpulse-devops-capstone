#!/usr/bin/env bash
# Metrics Server powers `kubectl top` and the HorizontalPodAutoscaler.
# EKS: already installed as an add-on by Terraform. minikube: `minikube addons enable metrics-server`.
# Use this only for other clusters (kind, k3s, bare metal).
set -euo pipefail
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/ >/dev/null
helm repo update >/dev/null
helm upgrade --install metrics-server metrics-server/metrics-server \
  --namespace kube-system \
  --set args="{--kubelet-insecure-tls}" \
  --wait
kubectl top nodes
