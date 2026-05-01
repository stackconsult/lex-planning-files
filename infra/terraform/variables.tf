variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod"
  }
}

variable "aws_region" {
  description = "AWS region for infrastructure"
  type        = string
  default     = "us-east-1"
}

variable "aws_account_id" {
  description = "AWS account ID for S3 bucket naming"
  type        = string
}

variable "neon_project_name" {
  description = "Neon PostgreSQL project name"
  type        = string
  default     = "lexcore"
}

variable "neon_database_name" {
  description = "Neon database name"
  type        = string
  default     = "lexcore"
}

variable "neon_api_key" {
  description = "Neon API key for provisioning"
  type        = string
  sensitive   = true
}

variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.m6g.large"
}

variable "redis_num_nodes" {
  description = "Number of Redis cache nodes"
  type        = number
  default     = 3
}

variable "node_group_general_min" {
  description = "Minimum nodes in general purpose node group"
  type        = number
  default     = 3
}

variable "node_group_general_desired" {
  description = "Desired nodes in general purpose node group"
  type        = number
  default     = 3
}

variable "node_group_general_max" {
  description = "Maximum nodes in general purpose node group"
  type        = number
  default     = 10
}

variable "node_group_compute_min" {
  description = "Minimum nodes in compute-intensive node group"
  type        = number
  default     = 2
}

variable "node_group_compute_desired" {
  description = "Desired nodes in compute-intensive node group"
  type        = number
  default     = 2
}

variable "node_group_compute_max" {
  description = "Maximum nodes in compute-intensive node group"
  type        = number
  default     = 5
}

variable "node_group_gpu_min" {
  description = "Minimum nodes in GPU node group"
  type        = number
  default     = 1
}

variable "node_group_gpu_desired" {
  description = "Desired nodes in GPU node group"
  type        = number
  default     = 1
}

variable "node_group_gpu_max" {
  description = "Maximum nodes in GPU node group"
  type        = number
  default     = 3
}

variable "enable_gpu_nodes" {
  description = "Whether to create GPU node group (expensive, only for production)"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Additional tags for all resources"
  type        = map(string)
  default     = {}
}
