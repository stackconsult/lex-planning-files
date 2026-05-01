terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    neon = {
      source  = "neonhq/neon"
      version = "~> 0.1"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
    vault = {
      source  = "hashicorp/vault"
      version = "~> 3.20"
    }
  }

  backend "s3" {
    bucket         = "lexcore-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "LexCore"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# EKS Cluster (managed Kubernetes)
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "lexcore-${var.environment}"
  cluster_version = "1.28"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Managed node groups for different workloads
  eks_managed_node_groups = {
    general = {
      desired_size = var.node_group_general_desired
      min_size     = var.node_group_general_min
      max_size     = var.node_group_general_max

      instance_types = ["t3.large"]
      capacity_type  = "ON_DEMAND"

      labels = {
        workload = "general"
      }
    }

    compute = {
      desired_size = var.node_group_compute_desired
      min_size     = var.node_group_compute_min
      max_size     = var.node_group_compute_max

      instance_types = ["c5.2xlarge"]
      capacity_type  = "ON_DEMAND"

      labels = {
        workload = "compute"
      }

      taints = [{
        key    = "dedicated"
        value  = "compute"
        effect = "NO_SCHEDULE"
      }]
    }

    gpu = {
      desired_size = var.node_group_gpu_desired
      min_size     = var.node_group_gpu_min
      max_size     = var.node_group_gpu_max

      instance_types = ["p3.2xlarge"]
      capacity_type  = "ON_DEMAND"

      labels = {
        workload = "gpu"
      }

      taints = [{
        key    = "dedicated"
        value  = "gpu"
        effect = "NO_SCHEDULE"
      }]
    }
  }
}

# VPC for EKS
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "lexcore-${var.environment}"
  cidr = "10.0.0.0/16"

  azs             = data.aws_availability_zones.available.names
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = false
  single_nat_gateway = var.environment == "dev"

  tags = {
    "kubernetes.io/cluster/lexcore-${var.environment}" = "shared"
    "kubernetes.io/role/elb"                           = "1"
  }
}

data "aws_availability_zones" "available" {}

# Redis (ElastiCache)
module "redis" {
  source = "./modules/redis"

  cluster_name       = "lexcore-${var.environment}"
  node_type          = var.redis_node_type
  num_cache_nodes    = var.redis_num_nodes
  subnet_group_name  = aws_elasticache_subnet_group.redis.name
  security_group_ids = [aws_security_group.redis.id]
}

resource "aws_elasticache_subnet_group" "redis" {
  name       = "lexcore-${var.environment}-redis"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_security_group" "redis" {
  name_prefix = "lexcore-redis-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [module.eks.cluster_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# S3 buckets for document storage
resource "aws_s3_bucket" "legal_docs" {
  bucket = "lexcore-legal-docs-${var.environment}-${var.aws_account_id}"

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  lifecycle_rule {
    id      = "archive-old-versions"
    enabled = true

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 2555 # 7 years
    }

    noncurrent_version_expiration {
      days = 365
    }
  }
}

resource "aws_s3_bucket" "filing_bundles" {
  bucket = "lexradar-filing-bundles-${var.environment}-${var.aws_account_id}"

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  lifecycle_rule {
    id      = "archive-old-bundles"
    enabled = true

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 2555 # 7 years
    }
  }
}

resource "aws_s3_bucket" "terraform_state" {
  bucket = "lexcore-terraform-state"

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  lifecycle_rule {
    id      = "archive-old-state"
    enabled = true

    noncurrent_version_expiration {
      days = 30
    }
  }
}

# DynamoDB table for Terraform state locking
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}

# WAF for web traffic
resource "aws_wafv2_web_acl" "main" {
  name        = "lexcore-${var.environment}"
  description = "WAF for LexCore ${var.environment}"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 1

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesCommonRuleSetMetric"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "lexcore-waf"
    sampled_requests_enabled   = true
  }
}

# Security group for EKS (restrictive)
resource "aws_security_group" "eks_additional" {
  name_prefix = "lexcore-eks-additional-"
  vpc_id      = module.vpc.vpc_id
  description = "Additional security group for LexCore EKS cluster"

  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "HTTPS from ALB only"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [module.vpc.vpc_cidr_block]
    description = "Allow all egress within VPC"
  }

  tags = {
    Name = "lexcore-eks-additional"
  }
}

# ALB security group (allows public access to web)
resource "aws_security_group" "alb" {
  name_prefix = "lexcore-alb-"
  vpc_id      = module.vpc.vpc_id
  description = "Security group for LexCore ALB"

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS from anywhere (WAF protects)"
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP redirect to HTTPS"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "lexcore-alb"
  }
}

# IAM roles for service accounts (IRSA)
module "irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name = "lexcore-${var.environment}-irsa"

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["lexcore:*"]
    }
  }

  role_policy_arns = {
    s3           = aws_iam_policy.s3_access.arn
    dynamodb     = aws_iam_policy.dynamodb_access.arn
    secrets      = aws_iam_policy.secrets_access.arn
    cloudwatch   = aws_iam_policy.cloudwatch_access.arn
  }
}

resource "aws_iam_policy" "s3_access" {
  name = "lexcore-s3-access-${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.legal_docs.arn,
          "${aws_s3_bucket.legal_docs.arn}/*",
          aws_s3_bucket.filing_bundles.arn,
          "${aws_s3_bucket.filing_bundles.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_policy" "dynamodb_access" {
  name = "lexcore-dynamodb-access-${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = aws_dynamodb_table.terraform_locks.arn
      }
    ]
  })
}

resource "aws_iam_policy" "secrets_access" {
  name = "lexcore-secrets-access-${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = "arn:aws:secretsmanager:*:*:secret:lexcore/*"
      }
    ]
  })
}

resource "aws_iam_policy" "cloudwatch_access" {
  name = "lexcore-cloudwatch-access-${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# Outputs
output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}

output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "s3_legal_docs_bucket" {
  description = "S3 bucket for legal documents"
  value       = aws_s3_bucket.legal_docs.bucket
}

output "s3_filing_bundles_bucket" {
  description = "S3 bucket for filing bundles"
  value       = aws_s3_bucket.filing_bundles.bucket
}

output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = module.redis.endpoint
}

output "irsa_role_arn" {
  description = "IAM role ARN for service accounts"
  value       = module.irsa.iam_role_arn
}
