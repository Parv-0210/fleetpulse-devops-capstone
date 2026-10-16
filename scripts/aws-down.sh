#!/usr/bin/env bash
# Tear everything down so nothing keeps billing.
#   AWS_PROFILE=fleetpulse ./scripts/aws-down.sh
# Kubernetes-created load balancers and volumes are removed first; otherwise their ENIs keep
# the VPC alive and `terraform destroy` stalls on the subnets.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${AWS_PROFILE:?set AWS_PROFILE to the AWS CLI profile to use}"
export AWS_PROFILE

gh variable delete AWS_ROLE_ARN 2>/dev/null || true   # stop the pipeline from deploying to a dying cluster

if kubectl cluster-info >/dev/null 2>&1; then
  helm uninstall fleetpulse -n fleetpulse --wait || true
  helm uninstall kube-prometheus-stack -n monitoring --wait || true
  helm uninstall ingress-nginx -n ingress-nginx --wait || true
  kubectl delete pvc --all -n fleetpulse --wait=true || true
  kubectl delete namespace fleetpulse monitoring ingress-nginx --ignore-not-found --wait=true
  echo "waiting 60s for AWS to release the load balancer"; sleep 60
fi

cd terraform
terraform destroy -input=false
