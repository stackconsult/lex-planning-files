# CLOUD_PROVISIONING.md — LexCore + LexRadar Infrastructure

> **Build System:** Unified Build System v2 | **Chunk:** C07 — DevOps + CI/CD | **Horde:** HORDE-DEVOPS

---

## Overview

Cloud infrastructure is provisioned via Terraform with a multi-environment strategy (dev/staging/production). Primary cloud is AWS (EKS, ALB, VPC, CloudWatch). Managed services: Neon (PostgreSQL), Upstash (Redis), Qdrant Cloud (vector DB), Cloudflare (CDN/DNS/R2).

**IaC:** Terraform 1.7+ with Terraform Cloud remote state  
**Environments:** dev, staging, production  
**Model:** Immutable infrastructure, blue-green deployments

---

## Architecture

```
Cloudflare Edge (DNS/CDN/WAF/DDoS)
  → AWS ALB (TLS termination)
    → EKS Cluster (VPC private subnets)
      → API Pods (FastAPI)
      → Worker Pods (Celery)
      → Frontend Pods (Next.js)
    → CloudWatch (logs/metrics/alarms)
  → Neon PostgreSQL + pgvector
  → Upstash Redis (multi-DB)
  → Qdrant Cloud (vector search)
  → Cloudflare R2 (S3-compatible object storage)
  → Polygon (blockchain anchoring)
```

---

## Terraform Structure

```
terraform/
  modules/
    vpc/          — VPC, subnets, NAT, flow logs
    eks/          — EKS cluster, node groups (general/api/workers/gpu)
    alb/          — ALB, target groups, health checks, ACM certs
    monitoring/   — CloudWatch, Prometheus, Grafana
    security/     — WAF, security groups, IAM roles
  environments/
    dev/          — dev.tfvars, small footprint
    staging/      — staging.tfvars, mirror prod at 1/3 scale
    production/   — prod.tfvars, full HA
  shared/
    providers.tf, backend.tf, versions.tf
```

---

## VPC

| Env | CIDR | AZs | Public Subnets | Private Subnets | NAT |
|-----|------|-----|----------------|-----------------|-----|
| dev | 10.0.0.0/16 | 3 | /24 × 3 | /24 × 3 | 1 |
| staging | 10.1.0.0/16 | 3 | /24 × 3 | /24 × 3 | 1 |
| production | 10.2.0.0/16 | 3 | /24 × 3 | /24 × 3 | 3 |

Flow logs enabled → CloudWatch Logs. VPC endpoints for S3, ECR, CloudWatch (no NAT traversal).

---

## EKS Node Groups

| Group | Instance | vCPU | RAM | GPU | Purpose | Min-Max (dev) | Min-Max (prod) |
|-------|----------|------|-----|-----|---------|---------------|----------------|
| general | m6i.xlarge | 4 | 16 GB | — | Frontend, general | 1-3 | 3-10 |
| api | m6i.2xlarge | 8 | 32 GB | — | FastAPI servers | 1-2 | 2-8 |
| workers | m6i.2xlarge | 8 | 32 GB | — | Celery workers | 1-2 | 2-6 |
| gpu | g5.xlarge | 4 | 16 GB | A10G | LLM inference | 0-1 | 0-4 |

Taints: `dedicated=api`, `dedicated=workers`, `nvidia.com/gpu=true`.  
Fargate profiles for spot workloads (prod only).  
Cluster version: 1.29. Endpoint: public (dev), private (staging/prod) + bastion.

---

## ALB

- HTTPS:443 → TLS 1.3 (ACM cert), HTTP:80 → 301 redirect to HTTPS
- Health check: `GET /health`, interval 30s, threshold 2/2
- Target type: IP (pod-level routing via AWS Load Balancer Controller)
- WAF association: rate limiting, geo-blocking, SQLi/XSS rule sets

---

## External Services

### Neon PostgreSQL

| Param | Dev | Staging | Production |
|-------|-----|---------|------------|
| Plan | Free | Scale | Business |
| vCPU | Shared | 4 | 8 |
| RAM | Shared | 8 GB | 16 GB |
| Storage | 500 MB | 100 GB | 500 GB |
| Read replicas | 0 | 1 | 2 |
| PITR | 1 day | 7 days | 14 days |
| Connection pooler | PgBouncer | PgBouncer | PgBouncer |

Connection string stored in AWS Secrets Manager; injected via External Secrets Operator.

### Upstash Redis

| Param | Dev | Staging | Production |
|-------|-----|---------|------------|
| Plan | Free | Pro | Pro |
| Max memory | 256 MB | 2 GB | 10 GB |
| Max connections | 100 | 1,000 | 5,000 |
| Multi-DB | 16 | 16 | 16 |
| Replication | — | Yes | Yes |
| Multi-AZ | — | Yes | Yes |

### Qdrant Cloud

| Param | Dev | Staging | Production |
|-------|-----|---------|------------|
| Plan | Free | Small | Medium |
| Storage | 1 GB | 20 GB | 100 GB |
| RAM | 1 GB | 4 GB | 16 GB |
| vCPU | 0.5 | 2 | 4 |
| Collections | 2 | 5 | 10 |

### Cloudflare

- **DNS:** apex, api, app, flower → ALB
- **CDN:** static assets cached 24h, API bypass cache
- **WAF:** block admin paths, challenge threat score > 50
- **R2 buckets:** documents (90d temp), bundles (7yr), backups (30d), logs (90d)
- **DDoS:** Always On + Advanced (Enterprise)

---

## Secret Management

All secrets in AWS Secrets Manager. Kubernetes External Secrets Operator syncs to pods:

```yaml
# ExternalSecret example (abbreviated)
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: lexcore-api-secrets
spec:
  refreshInterval: 1h
  secretStoreRef:
    kind: SecretStore
    name: aws-secrets-manager
  target:
    name: lexcore-api-secrets
  data:
    - secretKey: NEON_DATABASE_URL
      remoteRef:
        key: "{env}/neon/database_url"
        property: connection_string
    - secretKey: REDIS_URL
      remoteRef:
        key: "{env}/upstash/redis_url"
    - secretKey: QDRANT_API_KEY
      remoteRef:
        key: "{env}/qdrant/api_key"
    - secretKey: OPENAI_API_KEY
      remoteRef:
        key: "{env}/openai/api_key"
    - secretKey: CLERK_SECRET_KEY
      remoteRef:
        key: "{env}/clerk/secret_key"
    - secretKey: POLYGON_PRIVATE_KEY
      remoteRef:
        key: "{env}/polygon/private_key"
```

---

## Cost Estimate (Monthly)

| Environment | Approximate Cost |
|-------------|-----------------|
| dev | ~$200 |
| staging | ~$1,500 |
| production | ~$5,000–$8,000 |

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-29 | Initial cloud provisioning spec | C07 DevOps definition |
