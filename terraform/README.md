# Terraform — AWS VPC + EKS for FleetPulse

Provisions everything the Kubernetes layer needs, from code:

```text
AWS (ap-south-1)
└── VPC 10.40.0.0/16
    ├── public subnets  10.40.1.0/24, 10.40.2.0/24   (ELB, NAT gateway)
    ├── private subnets 10.40.101.0/24, 10.40.102.0/24 (EKS worker nodes)
    ├── Internet gateway + single NAT gateway
    └── EKS 1.31 "fleetpulse-dev-eks"
        ├── managed node group "general" (t3.medium, 2–3 nodes, private subnets)
        └── add-ons: vpc-cni, coredns, kube-proxy, aws-ebs-csi-driver (IRSA), metrics-server
```

## Usage

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # adjust if needed, never add credentials here
export AWS_PROFILE=<your-profile>              # or AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY env vars

terraform init
terraform fmt -check -recursive
terraform validate
terraform plan -out=tfplan
terraform apply tfplan                         # ~15 minutes

$(terraform output -raw configure_kubectl)     # writes kubeconfig for the new cluster
kubectl get nodes
```

Then continue with `k8s/README.md` (namespace, storage class, ingress controller) and the Helm chart.

## Tear down

```bash
# 1. Delete LoadBalancer-type Services first so AWS ELBs/ENIs are released:
helm uninstall ingress-nginx -n ingress-nginx || true
kubectl delete ns fleetpulse monitoring ingress-nginx --ignore-not-found
# 2. Destroy the infrastructure:
terraform destroy
```

## Cost notes

Roughly: EKS control plane ~0.10 USD/h, 2 × t3.medium ~0.09 USD/h, NAT gateway ~0.05 USD/h + data.
Run `terraform destroy` as soon as the demo/evaluation is done.

## Files

| File | Purpose |
|---|---|
| `versions.tf` | Terraform and provider version constraints |
| `providers.tf` | AWS provider, AZ lookup, shared locals/tags |
| `variables.tf` | Tunables with sane defaults |
| `vpc.tf` | VPC module: subnets, NAT, Kubernetes subnet tags |
| `eks.tf` | EKS module: control plane, node group, add-ons, EBS CSI IRSA role |
| `outputs.tf` | Cluster name/endpoint, subnet IDs, kubeconfig command |
| `terraform.tfvars.example` | Example variable values (no secrets) |
| `backend.tf.example` | Optional S3 remote state |
