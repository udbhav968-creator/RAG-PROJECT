variable "aws_region" {
  default = "us-east-1"
}

variable "eks_role_arn" {
  description = "IAM Role ARN for AWS EKS Cluster"
  default     = "arn:aws:iam::123456789012:role/EKSClusterRole"
}

variable "subnet_ids" {
  type    = list(string)
  default = ["subnet-12345678", "subnet-87654321"]
}
