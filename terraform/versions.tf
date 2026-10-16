terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.100"
    }
  }

  # Remote state: copy backend.tf.example to backend.tf and fill in your bucket.
  # Local state is used when no backend block is present.
}
