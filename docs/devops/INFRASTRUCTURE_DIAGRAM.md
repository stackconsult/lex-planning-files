# INFRASTRUCTURE_DIAGRAM.md — LexCore + LexRadar System Architecture Diagram

> **Build System:** Unified Build System v2 | **Chunk:** C07 — DevOps + CI/CD | **Horde:** HORDE-DEVOPS

---

## High-Level System Architecture

```
                              ┌─────────────────────────────────────────────┐
                              │           Cloudflare Edge                     │
                              │  ┌──────────────────────────────────────┐   │
                              │  │ DNS / CDN / WAF / DDoS Protection   │   │
                              │  └──────────────────────────────────────┘   │
                              │           │                                   │
                              │  ┌──────────────────────────────────────┐   │
                              │  │ R2 Object Storage                      │   │
                              │  │ • documents (90d temp)                 │   │
                              │  │ • bundles (7yr retention)              │   │
                              │  │ • backups (30d)                        │   │
                              │  │ • logs (90d)                           │   │
                              │  └──────────────────────────────────────┘   │
                              └──────────────────┬──────────────────────────┘
                                                 │ HTTPS (TLS 1.3)
                              ┌──────────────────┴──────────────────────────┐
                              │           AWS Region (us-east-1)              │
                              │  ┌──────────────────────────────────────┐   │
                              │  │ Application Load Balancer (ALB)       │   │
                              │  │ • TLS termination                     │   │
                              │  │ • HTTP → HTTPS redirect               │   │
                              │  │ • Health checks                       │   │
                              │  └──────────────────┬───────────────────┘   │
                              │                     │                       │
                              │  ┌──────────────────┴───────────────────┐  │
                              │  │ EKS Cluster (Kubernetes 1.29)          │  │
                              │  │  ┌─────────────────────────────────┐  │  │
                              │  │  │ Namespace: production           │  │  │
                              │  │  │                                 │  │  │
                              │  │  │  ┌──────────────┐              │  │  │
                              │  │  │  │ API Pods     │  (FastAPI)   │  │  │
                              │  │  │  │ • 3-10 replicas│             │  │  │
                              │  │  │  │ • HPA: CPU 70% │             │  │  │
                              │  │  │  │ • PDB: min 1   │             │  │  │
                              │  │  │  └──────┬───────┘              │  │  │
                              │  │  │         │                       │  │  │
                              │  │  │  ┌──────┴───────┐              │  │  │
                              │  │  │  │ Frontend Pods│  (Next.js)   │  │  │
                              │  │  │  │ • 3-10 replicas│             │  │  │
                              │  │  │  │ • HPA: CPU 70% │             │  │  │
                              │  │  │  └──────────────┘              │  │  │
                              │  │  │                                 │  │  │
                              │  │  │  ┌──────────────────────────┐  │  │  │
                              │  │  │  │ Worker Pods (Celery)      │  │  │
                              │  │  │  │ • ingestion: 8 workers   │  │  │
                              │  │  │  │ • patent: 8 workers       │  │  │
                              │  │  │  │ • monitor: 2 workers      │  │  │
                              │  │  │  │ • email: 2 workers        │  │  │
                              │  │  │  │ • evaluation: 4 workers   │  │  │
                              │  │  │  │ • blockchain: 2 workers │  │  │
                              │  │  │  │ • research: 4 workers     │  │  │
                              │  │  │  │ • search: 4 workers       │  │  │
                              │  │  │  └──────────────────────────┘  │  │  │
                              │  │  │                                 │  │  │
                              │  │  │  ┌──────────────────────────┐  │  │  │
                              │  │  │  │ Flower Dashboard           │  │  │
                              │  │  │  │ (Celery monitoring)        │  │  │
                              │  │  │  └──────────────────────────┘  │  │  │
                              │  │  └─────────────────────────────────┘  │  │
                              │  └─────────────────────────────────────────┘  │
                              │                                                 │
                              │  ┌──────────────────────────────────────┐   │
                              │  │ CloudWatch                           │   │
                              │  │ • Logs (Fluent Bit → CloudWatch)     │   │
                              │  │ • Metrics (Prometheus → AMP)         │   │
                              │  │ • Alarms (PagerDuty, Slack)          │   │
                              │  └──────────────────────────────────────┘   │
                              │                                                 │
                              │  ┌──────────────────────────────────────┐   │
                              │  │ VPC (10.2.0.0/16)                    │   │
                              │  │ • 3 AZs, public + private subnets    │   │
                              │  │ • NAT Gateways (3, HA)               │   │
                              │  │ • Security Groups (least privilege) │   │
                              │  └──────────────────────────────────────┘   │
                              └─────────────────────────────────────────────────┘
                                                 │
            ┌────────────────────────────────────┼────────────────────────────────────┐
            │                                    │                                    │
            ▼                                    ▼                                    ▼
   ┌────────────────────┐          ┌────────────────────┐          ┌────────────────────┐
   │  Neon PostgreSQL     │          │  Upstash Redis     │          │  Qdrant Cloud      │
   │  + pgvector          │          │  (Multi-DB)        │          │  Vector Database   │
   │                     │          │                     │          │                     │
   │  • Primary: us-east-1│          │  • Primary: us-east-1│          │  • Cluster: us-east-1│
   │  • Read replicas:    │          │  • Replica: us-west-2│          │  • Collections:     │
   │    us-west-2,        │          │  • DB 0: Celery     │          │    legal_chunks   │
   │    eu-west-1        │          │  • DB 1: Results    │          │    prior_art_emb   │
   │  • PgBouncer pooler  │          │  • DB 2: Cache      │          │  • HNSW indexes   │
   │  • PITR: 14 days     │          │  • DB 3: Sessions   │          │                     │
   │                     │          │  • DB 4: Rate limit │          │                     │
   │  Tables: tenants,    │          │  • DB 5: Pipeline   │          │                     │
   │  users, documents,   │          │                     │          │                     │
   │  chunks, inventions,│          │                     │          │                     │
   │  disclosures, etc.   │          │                     │          │                     │
   └────────────────────┘          └────────────────────┘          └────────────────────┘
            │                                    │
            └────────────────────────────────────┘
                              │
                              ▼
                   ┌────────────────────┐
                   │  Polygon (L2)      │
                   │  Blockchain        │
                   │                     │
                   │  • Proof of        │
                   │    existence      │
                   │  • SHA-256 hashes │
                   │    only (no raw   │
                   │    IP content)    │
                   └────────────────────┘
```

---

## Data Flow: Legal Search Request

```
User (Browser)
    │
    ▼ HTTPS
Cloudflare (DNS + CDN + WAF)
    │
    ▼
AWS ALB (TLS termination, health check)
    │
    ▼
EKS → Frontend Pod (Next.js)
    │
    ▼ API call (Bearer JWT)
EKS → API Pod (FastAPI)
    │
    ├──► Clerk (validate JWT)
    │
    ├──► Redis (check rate limit counter)
    │
    ├──► Redis (check search cache)
    │         ├── Cache HIT → Return cached results
    │         └── Cache MISS → Continue
    │
    ├──► PostgreSQL (full-text search via GIN index)
    │
    ├──► Qdrant (vector search via HNSW index)
    │
    ├──► OpenAI (embedding generation, if needed)
    │
    ├──► PostgreSQL (fetch citation chains)
    │
    └──► Redis (cache results, 24h TTL)
    │
    ▼ JSON
Frontend Pod (render results)
    │
    ▼ HTML/JSON
User (Browser)
```

---

## Data Flow: Patent Pipeline (Invention to Filing)

```
Developer (GitHub / Jira / Notion)
    │
    ▼ Webhook / Scheduled scan
EKS → Worker Pod (AGT_SCANNER)
    │
    ├──► GitHub API (fetch commits/PRs)
    ├──► Jira API (fetch tickets)
    └──► Notion API (fetch pages)
    │
    ▼ Invention signals detected
PostgreSQL (invention_candidates table)
    │
    ▼ User triggers scoring
EKS → Worker Pod (AGT_PRIORART)
    │
    ├──► USPTO API (parallel search)
    ├──► WIPO API (parallel search)
    ├──► EPO API (parallel search)
    ├──► Lens API (parallel search)
    ├──► Google Patents API (parallel search)
    ├──► PatentScope API (parallel search)
    └──► IPcom API (parallel search)
    │
    ▼ Prior art results stored
PostgreSQL (prior_art_results table)
    │
    ▼ Patentability scores computed
PostgreSQL (invention_candidates.scores updated)
    │
    ▼ User triggers disclosure draft
EKS → Worker Pod (AGT_DISCLOSER)
    │
    ├──► OpenAI (LLM generation, 10 LHP sections)
    ├──► PostgreSQL (store draft)
    └──► Qdrant (verify grounding sources)
    │
    ▼ User approves disclosure
PostgreSQL (disclosure.status = APPROVED)
    │
    ▼ User triggers handoff
EKS → Worker Pod (AGT_ATTYFLOW)
    │
    ├──► PostgreSQL (create handoff record)
    ├──► Vault (generate scoped JWT, 48h expiry)
    ├──► SendGrid (email attorney with portal link)
    └──► Redis (cache handoff metadata)
    │
    ▼ Attorney reviews via portal
Attorney Portal (Next.js, scoped JWT)
    │
    ├──► PostgreSQL (fetch handoff package)
    ├──► PostgreSQL (save edits to 3 sections)
    └──► PostgreSQL (submit review: APPROVE/REJECT/REQUEST_CHANGES)
    │
    ▼ If APPROVED
PostgreSQL (disclosure.status = FILED)
    │
    ▼ Blockchain anchoring
EKS → Worker Pod (AGT_BLOCKCHAIN)
    │
    └──► Polygon (store SHA-256 hash of bundle)
    │
    ▼ Filing bundle created
PostgreSQL (filing_bundles table)
R2 (ZIP package of all disclosures)
```

---

## Network Security Zones

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Public Zone (Internet)                             │
│  Users, Attorneys (Portal), External APIs (USPTO, WIPO, etc.)             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                              Cloudflare WAF
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                        Edge Zone (Cloudflare)                             │
│  DNS, CDN, DDoS, R2 Object Storage                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                              AWS ALB (TLS 1.3)
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                        DMZ / Public Subnet                                │
│  ALB, NAT Gateways, Bastion Host (staging/prod only)                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                        Application Zone (Private Subnet)                    │
│  EKS Cluster (API, Frontend, Worker Pods)                               │
│  Security Groups:                                                         │
│    - API pods: ingress from ALB only (port 8000)                          │
│    - Frontend pods: ingress from ALB only (port 3000)                     │
│    - Worker pods: no ingress (outbound only)                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                        Data Zone (Private Subnet)                           │
│  Neon PostgreSQL (managed, TLS)                                           │
│  Upstash Redis (managed, TLS)                                           │
│  Qdrant Cloud (managed, TLS)                                            │
│  AWS Secrets Manager                                                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                        External Zone (Internet, API-only)                 │
│  OpenAI, Clerk, USPTO, WIPO, EPO, GitHub, Polygon                        │
│  Outbound HTTPS only (port 443)                                           │
│  VPC Endpoints for AWS services (S3, ECR, CloudWatch)                   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## CI/CD Flow

```
Developer
    │
    ▼ git push feature/branch
GitHub (Source Control)
    │
    ├──► PR opened
    │    └──► GitHub Actions: Build & Test
    │         ├── Lint, type check
    │         ├── Unit tests (api + frontend)
    │         ├── Integration tests (Docker Compose)
    │         ├── Security scan (Trivy, Bandit, npm audit)
    │         └── Coverage report (> 80%)
    │
    ├──► PR approved → merge to main
    │    └──► GitHub Actions: Deploy to Staging
    │         ├── Build images (API, Frontend, Worker)
    │         ├── Scan images (Trivy + SBOM)
    │         ├── Push to ECR (SHA tag)
    │         ├── Deploy to EKS staging (Helm)
    │         ├── Smoke tests
    │         └── HORDE-AUDIT quick gate (L1 + L3)
    │
    └──► Create Release (vX.Y.Z)
         └──► GitHub Actions: Deploy to Production
              ├── Promote staging image to prod tag
              ├── Blue-green deployment
              ├── Canary rollout (10% → 50% → 100%)
              ├── Smoke tests + synthetic monitoring
              ├── Verify and switch traffic
              ├── Notify Slack
              └── Automatic rollback on failure
```

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-30 | Initial infrastructure diagram | C07 DevOps definition |
