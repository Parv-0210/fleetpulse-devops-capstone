variable "aws_region" {
  description = "AWS region to deploy into."
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Short project identifier used in resource names and tags."
  type        = string
  default     = "fleetpulse"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)."
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.40.0.0/16"
}

variable "az_count" {
  description = "Number of availability zones to spread subnets across (minimum 2 for EKS)."
  type        = number
  default     = 2

  validation {
    condition     = var.az_count >= 2 && var.az_count <= 3
    error_message = "az_count must be 2 or 3."
  }
}

variable "single_nat_gateway" {
  description = "Use one NAT gateway for all private subnets (cheaper) instead of one per AZ (resilient)."
  type        = bool
  default     = true
}

variable "cluster_version" {
  description = "Kubernetes version for the EKS control plane (keep it in standard support; extended support costs 6x)."
  type        = string
  default     = "1.36"
}

variable "cluster_endpoint_public_access_cidrs" {
  description = "CIDRs allowed to reach the public EKS API endpoint. Narrow this to your IP for production."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "node_instance_types" {
  description = "Instance types for the managed node group."
  type        = list(string)
  default     = ["t3.medium"]
}

variable "node_group_min_size" {
  type    = number
  default = 2
}

variable "node_group_max_size" {
  type    = number
  default = 3
}

variable "node_group_desired_size" {
  type    = number
  default = 2
}

variable "node_disk_size_gb" {
  description = "Root volume size for worker nodes."
  type        = number
  default     = 20
}

variable "github_repo" {
  description = "GitHub owner/repo whose Actions may assume the deploy role via OIDC."
  type        = string
  default     = "Parv-0210/fleetpulse-devops-capstone"
}

variable "github_repo_immutable" {
  description = "Immutable OIDC subject form owner@ownerId/repo@repoId (see GET /repos/{owner}/{repo}/actions/oidc/customization/sub). Empty to skip."
  type        = string
  default     = "Parv-0210@177807718/fleetpulse-devops-capstone@1422312066"
}

variable "create_github_oidc_provider" {
  description = "Create the GitHub OIDC identity provider. Set false if the account already has one."
  type        = bool
  default     = true
}
