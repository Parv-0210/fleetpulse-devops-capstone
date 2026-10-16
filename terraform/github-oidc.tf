# GitHub Actions -> AWS without stored keys.
# The pipeline gets a short-lived OIDC token from GitHub and exchanges it for this role.
# Only pushes to main (and the "production" environment) of this repository can assume it.

resource "aws_iam_openid_connect_provider" "github" {
  count          = var.create_github_oidc_provider ? 1 : 0
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
  tags           = local.tags
}

# An AWS account can hold only one provider per URL; reuse it if it already exists.
data "aws_iam_openid_connect_provider" "github" {
  count = var.create_github_oidc_provider ? 0 : 1
  url   = "https://token.actions.githubusercontent.com"
}

locals {
  github_oidc_provider_arn = var.create_github_oidc_provider ? aws_iam_openid_connect_provider.github[0].arn : data.aws_iam_openid_connect_provider.github[0].arn
}

resource "aws_iam_role" "github_actions" {
  name        = "${local.name}-github-actions"
  description = "Assumed by GitHub Actions in ${var.github_repo} to deploy to EKS"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Federated = local.github_oidc_provider_arn }
      Action    = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = { "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com" }
        StringLike = {
          # GitHub sends either the classic subject (repo:owner/repo:...) or, for newer repositories,
          # the immutable one with numeric IDs (repo:owner@id/repo@id:...). Accept both.
          "token.actions.githubusercontent.com:sub" = flatten([
            for r in compact([var.github_repo, var.github_repo_immutable]) : [
              "repo:${r}:ref:refs/heads/main",
              "repo:${r}:environment:production",
            ]
          ])
        }
      }
    }]
  })

  tags = local.tags
}

# Enough to run `aws eks update-kubeconfig`; what it may do inside the cluster comes from the
# EKS access entry in eks.tf.
resource "aws_iam_role_policy" "github_actions_eks" {
  name = "eks-describe"
  role = aws_iam_role.github_actions.id
  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Action = ["eks:DescribeCluster"], Resource = module.eks.cluster_arn }]
  })
}
