# Qdrant Vector Store Terraform Module

resource "helm_release" "qdrant" {
  name       = var.cluster_name
  repository = "https://qdrant.github.io/qdrant-helm"
  chart      = "qdrant"
  namespace  = var.namespace

  set {
    name  = "replicas"
    value = var.replicas
  }

  set {
    name  = "persistence.enabled"
    value = var.persistence_enabled
  }

  set {
    name  = "persistence.size"
    value = var.storage_size
  }
}

resource "kubernetes_service" "qdrant" {
  metadata {
    name      = "qdrant"
    namespace = var.namespace
  }

  spec {
    selector = {
      app = "qdrant"
    }

    port {
      port        = 6333
      target_port = 6333
    }
  }
}
