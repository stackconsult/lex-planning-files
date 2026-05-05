variable "cluster_name" {
  type        = string
  description = "Qdrant cluster name"
}

variable "namespace" {
  type        = string
  description = "Kubernetes namespace"
}

variable "replicas" {
  type        = number
  description = "Number of replicas"
  default     = 1
}

variable "persistence_enabled" {
  type        = bool
  description = "Enable persistent storage"
  default     = true
}

variable "storage_size" {
  type        = string
  description = "Storage size"
  default     = "10Gi"
}
