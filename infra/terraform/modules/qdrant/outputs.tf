output "service_name" {
  value = kubernetes_service.qdrant.metadata[0].name
}

output "namespace" {
  value = var.namespace
}
