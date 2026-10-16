#!/usr/bin/env bash
# One command from an empty AWS account to FleetPulse running on EKS.
#   AWS_PROFILE=fleetpulse ./scripts/aws-up.sh
# 1. terraform apply (VPC, EKS, node group, add-ons, GitHub OIDC deploy role)
# 2. point kubectl at the cluster
# 3. store the deploy role ARN as the repository variable AWS_ROLE_ARN
# 4. trigger the pipeline, whose deploy job bootstraps the cluster and installs the app
set -euo pipefail
cd "$(dirname "$0")/.."
: "${AWS_PROFILE:?set AWS_PROFILE to the AWS CLI profile to use}"
export AWS_PROFILE

echo "==> AWS identity"; aws sts get-caller-identity --query Arn --output text

cd terraform
[ -f terraform.tfvars ] || cp terraform.tfvars.example terraform.tfvars
terraform init -input=false
terraform plan -input=false -out=tfplan
read -r -p "Apply this plan? It creates billable resources (~0.25 USD/hour). [y/N] " ok
[ "$ok" = "y" ] || { echo "aborted"; exit 1; }
terraform apply -input=false tfplan
ROLE_ARN="$(terraform output -raw github_actions_role_arn)"
REGION="$(terraform output -raw aws_region)"
CLUSTER="$(terraform output -raw cluster_name)"
eval "$(terraform output -raw configure_kubectl)"
cd ..

echo "==> nodes"; kubectl get nodes -o wide

echo "==> enabling the EKS deploy job"
gh variable set AWS_ROLE_ARN --body "$ROLE_ARN"
gh variable set AWS_REGION --body "$REGION"
gh variable set EKS_CLUSTER_NAME --body "$CLUSTER"

echo "==> running the pipeline on main"
gh workflow run ci-cd.yml --ref main
sleep 8
gh run watch "$(gh run list --workflow ci-cd.yml -L 1 --json databaseId --jq '.[0].databaseId')" --exit-status
LB="$(kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')"
echo
echo "FleetPulse on AWS: http://$LB"
echo "Grafana:           kubectl port-forward svc/kube-prometheus-stack-grafana 3001:80 -n monitoring"
