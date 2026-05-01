# Infrastructure Requirements — Phase 0
**HORDE-INFRA Specification for Chunks 7-8**

> **Schema Version:** v0.1.0-foundation
> **Created:** 2026-04-29
> **Horde:** HORDE-INFRA
> **Status:** ⏳ PENDING (requires cloud credentials)

---

## Core Services (Chunk 7)

### 1. Neon PostgreSQL
**Purpose:** Primary database for LexCore + LexRadar
**Requirements:**
- PostgreSQL 15+ with pgvector extension
- pgBouncer connection pooling
- Multi-region deployment (US East, EU West)
- Point-in-time recovery enabled
- Automated backups (daily, 7-day retention)
- Read replicas for analytics

**Configuration:**
- Instance: Large (4 vCPU, 16GB RAM minimum)
- Storage: 500GB SSD (auto-scaling to 2TB)
- Max connections: 100 (via pgBouncer)
- pgvector HNSW indexes for vector similarity search

**Tiers:**
- Development: Small (1 vCPU, 4GB RAM)
- Staging: Medium (2 vCPU, 8GB RAM)
- Production: Large (4 vCPU, 16GB RAM) with read replicas

---

### 2. Qdrant Vector Database
**Purpose:** Vector similarity search for legal chunks and prior art
**Requirements:**
- Qdrant 1.7+
- HNSW index support
- Multi-tenant isolation
- Real-time indexing
- Optimized for cosine similarity (1536-dimensional vectors)

**Configuration:**
- Instance: Medium (2 vCPU, 8GB RAM minimum)
- Storage: 200GB SSD (auto-scaling to 1TB)
- Collection: `legal_chunks` (LexCore)
- Collection: `prior_art` (LexRadar)
- Index parameters: M=16, ef_construction=100

**Tiers:**
- Development: Small (1 vCPU, 4GB RAM)
- Staging: Medium (2 vCPU, 8GB RAM)
- Production: Large (4 vCPU, 16GB RAM)

---

### 3. Redis (ElastiCache or self-hosted)
**Purpose:** Caching, job queue, session storage
**Requirements:**
- Redis 7+
- Cluster mode enabled for high availability
- AOF persistence enabled
- Multi-AZ deployment
- Pub/Sub for real-time updates

**Configuration:**
- Instance: Medium (cache.m6g.large)
- Redis Cluster: 3 nodes (1 primary, 2 replicas)
- Memory: 16GB per node
- Persistence: AOF with fsync every second
- Eviction policy: allkeys-lru

**Use Cases:**
- Query cache (TTL: 1 hour)
- Session storage (TTL: 24 hours)
- Job queue (Celery)
- Rate limiting (sliding window)

---

### 4. S3 Bucket
**Purpose:** Raw document archive, filing bundles
**Requirements:**
- Standard S3 with versioning enabled
- Lifecycle rules (cold storage after 90 days)
- Encryption: AES-256 server-side
- CORS configuration for web access
- Pre-signed URLs for attorney downloads

**Configuration:**
- Bucket: `lexcore-legal-docs`
- Bucket: `lexradar-filing-bundles`
- Lifecycle: Move to Glacier after 90 days, delete after 7 years
- Encryption: SSE-S3
- Access: IAM roles + pre-signed URLs

---

### 5. Polygon RPC Node
**Purpose:** Ledger anchoring for proof of existence
**Requirements:**
- Polygon mainnet RPC endpoint
- WebSocket support for real-time tx monitoring
- Infura or Alchemy (recommended)
- Fallback RPC endpoints

**Configuration:**
- Provider: Infura or Alchemy
- Network: Polygon mainnet
- Gas estimation: 30 gwei
- Confirmation requirement: 2 blocks
- Wallet: Hardware wallet (Ledger) for production

---

### 6. HashiCorp Vault
**Purpose:** BYOK encryption key storage, secrets management
**Requirements:**
- Vault Enterprise or Open Source
- HSM integration for key storage
- Transit encryption engine
- Audit logging enabled
- Multi-factor authentication

**Configuration:**
- Instance: Medium (2 vCPU, 8GB RAM)
- Storage: 100GB SSD
- Backend: Consul for HA
- Encryption: Transit secrets engine
- BYOK: Tenant-specific keys (AES-256-GCM)

**Key Management:**
- Master key stored in HSM
- Tenant keys: Auto-generated per tenant
- Key rotation: Every 90 days
- Access: IAM roles + Vault policies

---

## Compute Infrastructure (Chunk 8)

### Kubernetes Cluster
**Purpose:** Container orchestration for all services
**Requirements:**
- Kubernetes 1.28+
- Managed service (EKS, GKE, or AKS)
- Node autoscaling
- Horizontal Pod Autoscaling
- Network policies enabled

**Configuration:**
- Control plane: Managed by cloud provider
- Node pools:
  - General purpose: 3 nodes (t3.large, auto-scale to 10)
  - Compute-intensive: 2 nodes (c5.2xlarge, auto-scale to 5)
  - GPU nodes: 1 node (p3.2xlarge, for embedding generation)
- Storage: EBS CSI driver
- Networking: VPC with private subnets

**Namespaces:**
- `lexcore-dev`
- `lexcore-staging`
- `lexcore-prod`
- `monitoring`
- `security`

---

### CI/CD Pipeline (GitHub Actions)
**Purpose:** Automated testing and deployment
**Requirements:**
- GitHub Actions workflows
- Docker container registry (ECR)
- Environment-specific deployments
- Rollback capability
- Approval gates for production

**Workflows:**
1. `ci.yml`: Run tests on every PR
2. `build.yml`: Build Docker images
3. `deploy-dev.yml`: Deploy to dev on merge to main
4. `deploy-staging.yml`: Deploy to staging (manual trigger)
5. `deploy-prod.yml`: Deploy to production (approval required)

**Stages:**
- Lint (flake8, black, mypy)
- Unit tests (pytest)
- Integration tests (testcontainers)
- Security scan (Snyk, Trivy)
- Build Docker image
- Deploy to environment
- Smoke tests

---

### Observability Stack
**Purpose:** Metrics, logging, and alerting
**Requirements:**
- Prometheus for metrics collection
- Grafana for visualization
- Loki for log aggregation
- AlertManager for alert routing
- PagerDuty or Slack for notifications

**Configuration:**
- Prometheus: Scrape every 15 seconds
- Retention: 30 days
- Grafana: Pre-built dashboards
- Loki: 7-day log retention
- AlertManager: Route to Slack + PagerDuty

**SLOs:**
- API latency P95: < 300ms
- API latency P99: < 1s
- Error rate: < 0.1%
- Availability: > 99.9%

---

## Security Requirements

### Network Security
- VPC with private subnets
- Security groups with least privilege
- WAF for web traffic
- DDoS protection (CloudFlare or AWS Shield)

### Access Control
- IAM roles for service-to-service communication
- OIDC for GitHub Actions
- SSO for human access (Okta)
- MFA required for production access

### Data Encryption
- At rest: AES-256 (S3, EBS, RDS)
- In transit: TLS 1.3
- BYOK: Vault Transit engine for tenant data

### Compliance
- SOC 2 Type II controls
- GDPR compliance
- HIPAA compliance (for healthcare tenants)

---

## Cost Estimates (Monthly)

| Service | Development | Staging | Production |
|---------|-------------|---------|------------|
| Neon PostgreSQL | $50 | $200 | $800 |
| Qdrant | $30 | $100 | $400 |
| Redis | $40 | $150 | $600 |
| S3 | $10 | $50 | $200 |
| Polygon RPC | $0 | $0 | $50 |
| Vault | $50 | $100 | $300 |
| Kubernetes | $100 | $300 | $1,200 |
| Observability | $50 | $150 | $500 |
| **Total** | **$330** | **$1,050** | **$4,050** |

---

## Next Steps

1. Obtain cloud credentials (AWS/GCP/Azure)
2. Set up Terraform workspace
3. Create Terraform configurations
4. Run `terraform plan` for review
5. Run `terraform apply` to provision
6. Configure DNS and SSL certificates
7. Set up monitoring and alerting
8. Run smoke tests (Chunk 10)
