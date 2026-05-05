# Neon Database Terraform Module

resource "neon_project" "main" {
  name = var.project_name
}

resource "neon_database" "main" {
  project_id = neon_project.main.id
  name       = var.database_name
}

resource "neon_branch" "main" {
  project_id = neon_project.main.id
  name       = "main"
}
