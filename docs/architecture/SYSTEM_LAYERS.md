# SYSTEM_LAYERS.md — LexCore + LexRadar Architecture

> **Build System:** Unified Build System v2  
> **Chunk:** C02 — Architecture + Contracts  
> **Horde:** HORDE-ARCH  
> **Control Plane:** ENGINEERING  

---

## Overview

LexCore + LexRadar is built on 8 system layers (L0-L7) with clear boundaries, contracts, and data flow. Every layer has defined interfaces, resilience requirements, and observability hooks.

```
┌─────────────────────────────────────────────────────────────┐
│  L6: Observability — logs, metrics, traces, dashboards     │
│  L7: CI/CD + Infrastructure — deploy, promote, rollback  │
├─────────────────────────────────────────────────────────────┤
│  L5: Frontend / UI / Attorney Portal — Next.js 14 App Router │
├─────────────────────────────────────────────────────────────┤
│  L4: API Gateway + MCP Boundary — FastAPI, JWT, rate limits │
├─────────────────────────────────────────────────────────────┤
│  L3: Services / Workers / Agents — Python async services   │
├─────────────────────────────────────────────────────────────┤
│  L2: Storage — PostgreSQL + pgvector, Redis, Qdrant, S3/R2   │
├─────────────────────────────────────────────────────────────┤
│  L1: Connectors / Ingestion Workers — 9 legal + 7 patent   │
├─────────────────────────────────────────────────────────────┤
│  L0: External Sources — APIs, scrapes, webhooks, uploads     │
└─────────────────────────────────────────────────────────────┘
```

---

## L0 — External Sources

### LexCore Sources (9 Connectors)
| Source | Type | Auth | Rate Limit | Jurisdiction |
|--------|------|------|------------|--------------|
| eCFR | REST JSON | None | 120/min | US Federal |
| CanLII | REST JSON | API Key | 30/min | CA Federal + Provincial |
| CourtListener | REST JSON | API Key | 60/min | US Federal |
| US Congress API | REST JSON | API Key | 30/min | US Federal |
| EUR-Lex | REST JSON | None | 20/min | EU |
| UK Legislation | REST XML/JSON | None | 60/min | UK |
| AustLII | REST | API Key | 30/min | AU |
| NZ Legislation | REST XML | None | 60/min | NZ |
| US State APIs | REST/HTML | Varies | Varies | US States |

### LexRadar Sources (7 Prior Art Fetchers)
| Source | Type | Auth | Rate Limit | Jurisdiction |
|--------|------|------|------------|--------------|
| USPTO PatentsView | REST JSON | API Key | 45/min | US |
| WIPO | REST JSON | OAuth 2.0 | 30/min | International |
| EPO OPS | REST XML | OAuth 1.0a | 30/min | EP |
| Lens | REST JSON | API Key | 10/min | Global |
| Google Patents | Scraping/API | None | N/A | Global |
| PatentScope | REST | None | N/A | Global |
| IP.com | REST | API Key | Varies | Global |

### LexRadar Code Sources (Invention Detection)
| Source | Type | Auth | Trigger |
|--------|------|------|---------|
| GitHub | REST JSON + Webhooks | OAuth | Commit push, PR merge |
| Jira | REST JSON | OAuth/API Token | Ticket created/updated |
| Notion | REST JSON | OAuth | Page created/updated |

---

## L1 — Connectors / Ingestion Workers

### Architecture
- **Connector Base Class:** `BaseConnector` with `fetch()`, `parse()`, `transform()`, `chunk()`, `embed()`, `store()` methods
- **Docling Parser:** Unified parsing for HTML, PDF, Markdown, Word → structured document
- **Hierarchical Chunker:** Section-level (~512 tokens), paragraph-level (~128 tokens), sentence-level (~32 tokens)
- **Embedding Service:** OpenAI `text-embedding-3-large` (1536-dim) with Redis caching
- **Batch Ingestion:** Celery tasks with exponential backoff, circuit breakers, DLQ for failures

### Resilience Requirements
- Every source connector: timeout=30s, retry=3, circuit breaker (5 failures → 60s open)
- Rate limit pacing per source (configurable)
- Schema validation on fetch (alert on parse failure)
- Dead letter queue for unprocessable documents
- Idempotency: document fingerprint prevents duplicates

### Data Flow
```
L0 Source API → L1 Connector.fetch() → Docling.parse() → Chunker.chunk()
→ EmbeddingService.embed() → PostgreSQL (legal_documents + legal_chunks)
→ Qdrant (vector index) → Redis (cache invalidation)
```

---

## L2 — Storage Layer

### PostgreSQL (Primary Database)
- **Server:** Neon PostgreSQL (serverless, auto-scaling)
- **Extensions:** `uuid-ossp`, `pgcrypto`, `pgvector`
- **Tables:** 18 tables (10 LexCore + 8 LexRadar)
- **RLS:** `FORCE ROW LEVEL SECURITY` on all tenant-scoped tables
- **Indexes:** 40+ indexes including HNSW (pgvector), GIN (full-text), composite
- **Migrations:** Alembic with upgrade/downgrade symmetry
- **Backups:** Neon automated (PITR), cross-region replica for ENTERPRISE

### Redis (Cache + Sessions + Queue)
- **Server:** AWS ElastiCache Redis (cluster mode disabled for MVP)
- **Uses:**
  - Query cache (`query_cache` table + Redis hot cache)
  - JWT session store (refresh tokens, blacklists)
  - Celery task queue backend
  - Rate limit counters (sliding window)
  - Embedding cache (SHA-256 key → vector)
- **TTL Policies:**
  - Query results: 24h default, configurable per tenant
  - JWT refresh tokens: 7 days
  - Embeddings: 30 days
  - Rate limit windows: 1 minute

### Qdrant (Vector Database)
- **Collections:** `legal_chunks` (1536-dim, cosine), `prior_art` (1536-dim, cosine)
- **Index:** HNSW (M=16, ef_construction=100)
- **Tenant Isolation:** Filter by `tenant_id` payload field on every search
- **Replication:** Single node for MVP; cluster for ENTERPRISE tier

### S3 / R2 (Object Storage)
- **Buckets:**
  - `lexcore-legal-docs` — Raw source documents (HTML, PDF)
  - `lexradar-filing-bundles` — Packaged patent disclosures (PDF, ZIP)
- **Encryption:** AES-256-S3 (server-side), BYOK for ENTERPRISE
- **Retention:** Legal docs indefinite; filing bundles 7 years (patent lifecycle)

---

## L3 — Services / Workers / Agents

### Service Layer Architecture
```
┌─────────────────────────────────────────────┐
│  API Routes (L4)                            │
├─────────────────────────────────────────────┤
│  Service Layer (bounded contexts)           │
│  ├── LexCore: Search, Monitor, Ingest       │
│  ├── LexRadar: Detect, Score, Disclose      │
│  ├── Shared: Auth, Tenant, Audit            │
├─────────────────────────────────────────────┤
│  Repository Layer (one per entity)          │
│  ├── DocumentRepository                     │
│  ├── ChunkRepository                        │
│  ├── InventionRepository                    │
│  ├── PriorArtRepository                     │
│  └── ...                                    │
├─────────────────────────────────────────────┤
│  Workers (Celery background tasks)          │
│  ├── ingest_document                        │
│  ├── batch_ingest                           │
│  ├── scheduled_ingest                       │
│  ├── detect_inventions                      │
│  ├── search_prior_art                       │
│  ├── generate_disclosure                    │
│  └── anchor_to_blockchain                   │
└─────────────────────────────────────────────┘
```

### Agent Directory (14 Agents)

**LexCore Agents:**
1. **AGT_ROUTER** — BAM compound parsing, dispatch to correct agent lane
2. **AGT_SEARCH** — Hybrid search orchestration (vector + full-text + re-rank)
3. **AGT_ANALYSIS** — Legal analysis, research task decomposition, synthesis
4. **AGT_DRAFT** — Document drafting assistance, template filling
5. **AGT_INGEST** — Document ingestion pipeline, connector management
6. **AGT_MONITOR** — Legislative change detection, monitor rule evaluation
7. **AGT_CITE** — Citation graph traversal, authority scoring, overruled detection

**LexRadar Agents:**
8. **AGT_SCANNER** — Code/repo scanning for invention signals
9. **AGT_SIGNAL_CLASSIFIER** — Classify invention signals by type
10. **AGT_PRIORART** — Parallel prior art search across 7 sources
11. **AGT_SCORER** — 6-dimension patentability scoring
12. **AGT_DISCLOSER** — Generate 10-section LHP disclosure drafts
13. **AGT_LEDGER** — Blockchain proof anchoring (Polygon mainnet)
14. **AGT_ATTYFLOW** — Attorney portal handoff, scoped JWT management

### Resilience Requirements (ALL services/agents)
- **Timeout:** `asyncio.wait_for(op, timeout=30.0)`
- **Retry:** max_attempts=3, exponential backoff + jitter, skip on 4xx
- **Circuit Breaker:** CLOSED → 5 failures → OPEN(60s) → HALF_OPEN → CLOSED
- **Typed Exceptions:** `AppException > ValidationError | ExternalServiceError | TenantIsolationError`
- **Logging:** `structlog.info(..., correlation_id=..., duration_ms=...)`
- **Health Check:** `/health` returns 200 or 503 with diagnostics
- **Graceful Shutdown:** SIGTERM/SIGINT handlers flush queues, close DB pools

---

## L4 — API Gateway + MCP Boundary

### FastAPI Application
- **Framework:** FastAPI 0.110+ with Pydantic v2
- **Server:** Uvicorn with 4 workers (production), 1 worker (dev)
- **Routing:**
  - `/v1/mcp/*` — MCP tool endpoints (7 tools)
  - `/v1/lexcore/*` — LexCore domain routes
  - `/v1/lexradar/*` — LexRadar domain routes
  - `/v1/auth/*` — Authentication routes
  - `/health/*` — Kubernetes probes

### MCP Tool Contracts (7 Tools)
1. `get_capabilities` — Returns jurisdiction + doc type manifest
2. `search_legal` — Hybrid search (pgvector + full-text) with BAM routing
3. `research_task` — Complex research with question decomposition
4. `get_document` — Retrieve full document with chunks and citations
5. `get_citations` — Citation graph traversal (forward/backward/both)
6. `check_updates` — Legislative changes since date
7. `jurisdiction_summary` — Coverage %, doc count, recent changes

### Authentication
- **Primary:** Clerk (OAuth, SAML-ready) — decision locked in C02
- **Fallback:** JWT with refresh tokens (for API-only integrations)
- **JWT Claims:** `tenant_id`, `tier`, `role`, `scopes`, `exp`, `iat`
- **Rate Limiting:**
  - SOLO: 10K requests/month (~0.23 req/min)
  - FIRM: Unlimited
  - ENTERPRISE: Unlimited + self-host option

### Middleware Stack
1. CORS (`CORSMiddleware`)
2. Trusted Host (`TrustedHostMiddleware`)
3. Rate Limit (Redis sliding window)
4. Tenant Context (set `app.tenant_id` for RLS)
5. JWT Auth (validate token, extract claims)

---

## L5 — Frontend / UI / Attorney Portal

### Technology Stack
- **Framework:** Next.js 14+ App Router
- **Language:** TypeScript strict mode
- **Styling:** Tailwind CSS + Shadcn/UI component library
- **State:** React Query (TanStack Query) for server state, Zustand for client state
- **Validation:** Zod schemas for all API responses
- **API Client:** `lib/api-client.ts` — ONLY place raw fetch/axios lives

### LexCore UI
- **Search Interface:** Query input, jurisdiction filter, results list, document viewer
- **Monitor Dashboard:** Rule list, change alerts, coverage statistics
- **Research Workspace:** Query decomposition, sub-result panels, synthesis export
- **Jurisdiction Browser:** Tree view of jurisdictions, coverage indicators

### LexRadar UI (Attorney Portal)
- **Handoff Package Viewer:** 10 sections, 3 editable (claims, detailed description, abstract)
- **Claim Theme Editor:** Syntax highlighting, claim validation
- **Evidence Chain Viewer:** Read-only, links to source commits/PRs
- **Prior Art Comparison Table:** Side-by-side prior art vs. invention
- **Filing Bundle Download:** Secure link, PDF/ZIP format
- **Action Buttons:** Approve / Reject / Request Changes

### Onboarding Flow
- **LexCore:** 5-step wizard (welcome → workspace → sources → first search → monitor setup)
- **LexRadar Engineering:** 7-step wizard (welcome → connectors → scan config → first scan → review queue → disclosure preview → handoff simulation)
- **LexRadar Attorney:** Email link → portal load → review → action

---

## L6 — Observability

### Logging
- **Tool:** structlog (JSON output)
- **Fields:** `timestamp`, `level`, `event`, `correlation_id`, `tenant_id`, `duration_ms`, `source`, `message`
- **Rules:** No PII, no passwords, no encryption keys ever logged

### Metrics
- **Tool:** Prometheus + Grafana
- **Key Metrics:**
  - `http_requests_total` (by method, status, route)
  - `http_request_duration_seconds` (histogram, P50/P95/P99)
  - `search_latency_seconds` (hybrid search breakdown)
  - `cache_hit_rate` (Redis cache metrics)
  - `ingest_documents_total` (by source, jurisdiction)
  - `invention_detection_total` (by source, signal_type)
  - `prior_art_search_duration_seconds` (by source)
  - `disclosure_grounding_score` (distribution)
  - `blockchain_anchor_latency_seconds` (Polygon tx)

### Tracing
- **Tool:** OpenTelemetry + Jaeger
- **Propagation:** `correlation_id` across all service boundaries
- **Spans:** API request → service call → DB query → external API → cache access

### Alerting
- **Tool:** Prometheus Alertmanager + Slack + PagerDuty
- **Critical Alerts:**
  - Error rate > 1% for 2 minutes
  - P95 latency > 500ms for 3 minutes
  - API down (health check fails)
  - Tenant isolation breach detected
  - BYOK test failure
  - Ingestion pipeline stalled (no docs in 24h)

### Dashboards
1. **LexCore API Overview:** Request rate, error rate, latency (P50/P95/P99)
2. **Database & Cache:** PostgreSQL connections, Redis memory, Qdrant search latency
3. **Security & Compliance:** BYOK status, RLS audit, failed login attempts, CVE count
4. **SLOs & SLIs:** Availability (30d), P95 latency (7d), error budget
5. **LexRadar Pipeline:** Invention detection rate, prior art search coverage, disclosure quality scores
6. **Ingestion Health:** Connector status, documents ingested per day, parse failure rate

---

## L7 — CI/CD + Infrastructure

### CI/CD Pipeline (13 Stages)
1. Code quality: black, isort, flake8, pylint, mypy
2. Secret scan: gitleaks
3. Dependency audit: pip-audit, npm audit
4. Unit tests: pytest --cov --fail-under=80
5. Integration tests: real DB/Redis, mock external APIs
6. Frontend build: tsc, eslint, next build
7. E2E tests: Playwright
8. Security scan: bandit, semgrep, trivy
9. Build + push: Docker build, push to ECR
10. Deploy staging: alembic upgrade head, k8s rollout
11. Smoke test: curl /health, run smoke suite
12. Canary prod: 10% traffic, 5 min observation
13. Promote or rollback: auto-promote on fitness | rollback on breach

### Infrastructure
- **Compute:** AWS EKS (Kubernetes)
- **Database:** Neon PostgreSQL (serverless)
- **Cache:** AWS ElastiCache Redis
- **Vector:** Qdrant (self-managed or Qdrant Cloud)
- **Object Storage:** AWS S3
- **Secrets:** HashiCorp Vault (or AWS Secrets Manager)
- **CDN:** CloudFront (static assets)
- **DNS:** Route 53
- **TLS:** Let's Encrypt (staging), ACM (production)

### Auto-Rollback Triggers
- Error rate > 1%
- P95 latency > 500ms
- Health check failures > 2
- Canary fitness score < 0.90

---

## Cross-Cutting Concerns

### Multi-Tenancy
- **Database:** RLS policies on all tenant-scoped tables
- **API:** JWT claims enforce tenant scope; middleware sets DB session variable
- **Cache:** All Redis keys prefixed with `tenant:{tenant_id}:`
- **Vector Search:** Qdrant payload filter `tenant_id` on every query
- **Object Storage:** S3 bucket paths prefixed with `/{tenant_id}/`

### Security
- **Encryption at Rest:** PostgreSQL (Neon), Redis (ElastiCache), S3 (AES-256)
- **Encryption in Transit:** TLS 1.3 for all external communication
- **Secrets Management:** Vault for API keys, JWT secrets, DB credentials
- **BYOK:** Enterprise tenants supply own Vault encryption keys
- **Audit Trail:** Every data access logged to `audit_log` table

### BAM (Binary Action Matrix) Routing
- **Every agent query** carries a BAM compound signal
- **Router (AGT_ROUTER)** parses BAM compound, dispatches to correct agent lane
- **BAM Genesis Hash:** `a96893482a3e79e75437ed19c21be1c9f618633c88cd5102f1e2d020035ade96`
- **Traceability:** Every action logged with BAM signal for audit and debugging

---

## Architecture Laws (Enforced)

1. **No business logic in route handlers** — Routes delegate to service layer
2. **No raw DB access outside repository layer** — All DB operations through repositories
3. **No agent imports another agent directly** — Use router/bus for inter-agent communication
4. **Agents receive typed inputs, return typed outputs** — Pydantic models for all agent contracts
5. **Every critical state change writes an audit row** — `audit_log` table tracks all mutations
6. **Workers must handle restart without duplicate side effects** — Idempotency keys, deduplication
7. **Never hard-code secrets** — All secrets from Vault or environment
8. **Never use `Any` type** — Strict typing in Pydantic and TypeScript
9. **Never skip error handling** — Bare `except: pass` is a critical finding
10. **Observability before scale** — Dashboards and alerts must exist before traffic increases

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-29 | Initial system layers definition | C02 architecture specification |
