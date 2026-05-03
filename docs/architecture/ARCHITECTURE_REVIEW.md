# Architecture Review — LexCore + LexRadar

> **Date:** 2026-05-02  
> **Reviewer:** Strategic Architecture Analysis  
> **Scope:** Full system architecture (L0-L7)  
> **Method:** Strength/Weakness/Opportunity/Threat (SWOT) + Strategic Prioritization

---

## Executive Summary

LexCore + LexRadar demonstrates a **well-architected, multi-layered system** with strong foundations in:
- **Defense-in-depth security** (RLS, JWT, BYOK, tenant isolation)
- **Hybrid search capability** (pgvector + full-text + re-rank)
- **Async-first design** (FastAPI + Celery + Redis)
- **Clear separation of concerns** (8-layer architecture)
- **Comprehensive observability** (Prometheus, Grafana, OpenTelemetry)

However, there are **strategic improvement opportunities** in:
- **Event-driven maturity** (Redis Streams → Kafka migration path)
- **Agent communication patterns** (direct imports vs. event bus)
- **Database scaling strategy** (single PostgreSQL vs. read replicas)
- **Circuit breaker implementation** (documented but not yet implemented)
- **Multi-region resilience** (single-region deployment risk)

**Overall Assessment:** **Strong foundation** (7.5/10) with clear enhancement path to production-grade architecture.

---

## Part 1: Architecture Strengths

### 1.1 Defense-in-Depth Tenant Isolation

**What It Is:**
Five-layer tenant isolation strategy across all data stores:
- **Database:** PostgreSQL RLS with session variable injection (`app.tenant_id`)
- **API:** JWT claims validation with middleware enforcement
- **Cache:** Redis key prefixing (`tenant:{tenant_id}:...`)
- **Vector DB:** Qdrant payload filtering on every search
- **Object Storage:** S3 path prefixing (`/{tenant_id}/...`)

**Why It's Good:**
- **Zero-trust assumption:** Even if one layer fails, others protect data
- **Database-level enforcement:** RLS prevents application bugs from leaking data
- **Performance-optimized:** Indexes still used with tenant_id filters
- **Audit-ready:** Every query automatically tagged with tenant context

**Evidence:**
```python
# db_session.py - RLS injection
async with get_db_session(tenant_uuid) as session:
    await session.execute(text("SET LOCAL app.tenant_id = :tenant_id"), ...)
    # All subsequent queries are RLS-filtered
```

**Strategic Value:** Critical for multi-tenant SaaS compliance (SOC 2, HIPAA, GDPR).

---

### 1.2 Hybrid Search Architecture

**What It Is:**
Three-tier search combining semantic, lexical, and re-ranking:
- **Tier 1:** HNSW vector similarity (pgvector, 1536-dim, cosine)
- **Tier 2:** GIN full-text search (PostgreSQL tsvector)
- **Tier 3:** Re-ranking algorithm (combine scores, boost recency)

**Why It's Good:**
- **Recall + Precision:** Vector search catches semantic matches; full-text catches exact terms
- **Performance:** HNSW provides sub-100ms search at 95% recall
- **Flexibility:** Re-ranking allows custom boosting (jurisdiction, recency, authority)
- **Cache-friendly:** Query fingerprinting enables Redis cache hits

**Evidence:**
```sql
-- pgvector HNSW index
CREATE INDEX legal_chunks_embedding_hnsw_cosine_idx
ON legal_chunks USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 100);

-- GIN full-text index
CREATE INDEX legal_chunks_content_gin_idx
ON legal_chunks USING gin (to_tsvector('english', content));
```

**Strategic Value:** Differentiates LexCore from competitors who rely on keyword-only search.

---

### 1.3 Three-Tier Async Strategy

**What It Is:**
Workload-appropriate async patterns:
- **T1 (Synchronous):** FastAPI async/await for hot path (search, auth, document fetch)
- **T2 (Background Jobs):** Celery + Redis for batch operations (ingest, scan)
- **T3 (Long-Running Pipelines):** Celery chains + event bus for complex workflows (prior art search, disclosure generation)

**Why It's Good:**
- **Right tool for the job:** No over-engineering simple queries; no blocking user requests on long jobs
- **Resilience built-in:** Retry policies, circuit breakers, dead letter queues
- **Progress tracking:** Pipeline state machine enables real-time status updates
- **Scalable:** Worker pools can be scaled independently per workload type

**Evidence:**
```python
# T1: Synchronous hot path
@app.get("/v1/mcp/search_legal")
async def search_legal(request: SearchRequest):
    cache, vector, text = await asyncio.gather(
        check_cache(...),
        qdrant.search(...),
        postgres.fulltext_search(...)
    )
    return re_rank(vector, text)

# T3: Long-running pipeline
prior_art_pipeline = chain(
    group(search_uspto.s(...), search_wipo.s(...), ...),
    merge_and_rank.s(...),
    generate_disclosure.s(...),
    anchor_to_blockchain.s(...)
)
```

**Strategic Value:** Enables SLA compliance (P95 < 300ms for search) while supporting complex workflows.

---

### 1.4 Clear Layer Boundaries (8-Layer Architecture)

**What It Is:**
Explicit separation across 8 layers with defined contracts:
- **L0:** External sources (9 legal + 7 patent + 3 code)
- **L1:** Connectors/ingestion workers
- **L2:** Storage (PostgreSQL, Redis, Qdrant, S3)
- **L3:** Services/workers/agents
- **L4:** API gateway + MCP boundary
- **L5:** Frontend/attorney portal
- **L6:** Observability
- **L7:** CI/CD + infrastructure

**Why It's Good:**
- **Independent scaling:** Each layer can scale horizontally
- **Clear ownership:** Teams can own specific layers without stepping on toes
- **Testability:** Layers can be mocked for unit/integration tests
- **Migration path:** Can replace a layer (e.g., Qdrant → Pinecone) without touching others

**Evidence:**
- Dependency graph shows **no cycles** (verified via topological sort)
- Event schema registry defines all cross-layer communication
- ADRs document technology choices with rationale

**Strategic Value:** Reduces technical debt, enables team autonomy, supports long-term maintainability.

---

### 1.5 Comprehensive Observability

**What It Is:**
Full-stack observability from day one:
- **Logging:** structlog (JSON, correlation_id propagation)
- **Metrics:** Prometheus + Grafana (15+ key metrics)
- **Tracing:** OpenTelemetry + Jaeger (distributed tracing)
- **Alerting:** Alertmanager + Slack + PagerDuty (6 critical alerts)

**Why It's Good:**
- **Debugging:** Correlation IDs trace requests across all layers
- **Proactive:** Alerts fire before users notice outages
- **Data-driven:** SLOs/SLIs backed by metrics, not guesses
- **Compliance:** Audit trail for all data access

**Evidence:**
```python
logger.info(
    "search_executed",
    correlation_id=correlation_id,
    tenant_id=tenant_id,
    latency_ms=latency_ms,
    cache_hit=cache_hit,
    result_count=result_count
)
```

**Strategic Value:** Enables rapid incident response, builds customer trust, supports compliance audits.

---

## Part 2: Architecture Weaknesses

### 2.1 Event-Driven Immaturity

**What It Is:**
Redis Streams chosen for MVP with Kafka deferred to "Enhancement Loop."

**Why It's Weak:**
- **Durability risk:** Redis Streams are in-memory by default; data loss on crash
- **Throughput ceiling:** Redis ~100K msg/s vs. Kafka 1M+ msg/s
- **Consumer group complexity:** Redis Streams have limited consumer group features
- **Operational risk:** Using Redis for both cache and queue creates resource contention

**Evidence:**
```json
// EVENT_SCHEMA_REGISTRY.json
"event_bus": "Redis Streams (MVP) / Kafka (Enhancement Loop)"
```

**Impact:** High — event bus is critical for agent coordination and pipeline orchestration.

---

### 2.2 Agent Communication Pattern

**What It Is:**
Architecture Law #3: "No agent imports another agent directly" — use router/bus for inter-agent communication.

**Why It's Weak:**
- **Tight coupling risk:** If law is violated, agents become tightly coupled
- **Testing difficulty:** Direct imports make unit testing agents in isolation harder
- **Scalability bottleneck:** Direct calls don't benefit from queue-based scaling
- **No enforcement:** Law is documented but not technically enforced

**Evidence:**
```python
// Architecture Law #3 (SYSTEM_LAYERS.md)
// "No agent imports another agent directly — Use router/bus"
// But no linter or runtime check enforces this
```

**Impact:** Medium — affects maintainability and testability of agent layer.

---

### 2.3 Single-Region Deployment

**What It Is:**
Infrastructure documentation shows single-region deployment (AWS us-east-1).

**Why It's Weak:**
- **Single point of failure:** AWS region outage takes down entire system
- **Latency for global users:** Non-US users experience higher latency
- **Compliance risk:** Some jurisdictions require data residency (e.g., EU GDPR)
- **No disaster recovery:** No active-active or hot-warm standby

**Evidence:**
```yaml
// SYSTEM_LAYERS.md - Infrastructure section
// "Compute: AWS EKS (Kubernetes)" - no mention of multi-region
// "Database: Neon PostgreSQL (serverless)" - single region implied
```

**Impact:** High — affects availability, compliance, and global user experience.

---

### 2.4 Database Scaling Strategy

**What It Is:**
PostgreSQL as single primary with no documented read replica strategy.

**Why It's Weak:**
- **Read scalability bottleneck:** All reads hit primary (write-heavy workloads block reads)
- **No geographic distribution:** Can't place replicas closer to users
- **Backup only:** Cross-region replica mentioned for ENTERPRISE but not general read scaling
- **Vector search contention:** pgvector HNSW indexes are CPU-intensive on primary

**Evidence:**
```sql
// CONNECTION_POOL_CONFIG.md
// "PostgreSQL (Neon serverless)" - no read replica configuration
// "Cross-region replica for ENTERPRISE" - not for read scaling
```

**Impact:** Medium-High — affects performance and scalability as tenant count grows.

---

### 2.5 Circuit Breaker Not Implemented

**What It Is:**
Circuit breaker pattern documented in ADR-003 but not yet implemented in codebase.

**Why It's Weak:**
- **Cascading failure risk:** External API failures can propagate through system
- **No automatic recovery:** Manual intervention required to restart failed services
- **SLA breach risk:** No protection against degraded external dependencies
- **Operational burden:** Manual monitoring of external service health

**Evidence:**
```python
// ADR-003 documents circuit breaker pattern
from shared.resilience import circuit_breaker

@circuit_breaker(threshold=5, recovery_timeout=60)
async def call_uspto_api(query: str) -> dict:
    # But shared.resilience module doesn't exist yet
```

**Impact:** Medium — affects resilience and operational overhead.

---

### 2.6 JWT Secret Rotation Complexity

**What It Is:**
HS256 chosen for MVP with single shared secret; rotation requires coordinated restart.

**Why It's Weak:**
- **Downtime required:** All services must restart simultaneously during rotation
- **Rollout complexity:** Blue-green deployment doesn't work (both need same secret)
- **Secret exposure risk:** Single secret compromise affects all services
- **No key versioning:** Can't support multiple active keys during transition

**Evidence:**
```json
// ADR-002
// "HS256 requires secret rotation coordination (all services must update simultaneously)"
// "Migration to RS256 documented for microservices split in future"
```

**Impact:** Medium — affects security and operational complexity.

---

## Part 3: Improvement Opportunities

### 3.1 Kafka Migration Path (High Priority)

**Recommendation:**
Define and implement Kafka migration path before Redis Streams becomes a bottleneck.

**Implementation Plan:**
1. **Phase 1 (Immediate):** Enable Redis Streams persistence (AOF) to reduce data loss risk
2. **Phase 2 (1-2 months):** Implement dual-write pattern (write to both Redis and Kafka)
3. **Phase 3 (2-3 months):** Migrate consumers one-by-one to Kafka
4. **Phase 4 (3-4 months):** Decommission Redis Streams, use Redis for cache only

**Benefits:**
- **Durability:** Kafka persistent log guarantees no data loss
- **Throughput:** 10x higher message throughput
- **Consumer flexibility:** Better consumer group management and replay
- **Separation of concerns:** Cache and queue no longer share resources

**Estimated Effort:** 4-6 weeks (2 engineers)

---

### 3.2 Agent Communication Enforcement (High Priority)

**Recommendation:**
Technically enforce "no direct agent imports" via linter + runtime checks.

**Implementation Plan:**
1. **Linter rule:** Add flake8 or mypy plugin to detect agent-to-agent imports
2. **Runtime check:** Add startup validation to verify agent dependency graph
3. **Event bus mandatory:** Require all agent communication via event bus
4. **Agent registry:** Central registry of agent interfaces (contract enforcement)

**Benefits:**
- **Prevent coupling:** Linter prevents direct imports at commit time
- **Testability:** Agents can be tested in isolation with mock event bus
- **Scalability:** Event bus enables horizontal scaling of agents
- **Observability:** All agent communication visible in event logs

**Estimated Effort:** 2-3 weeks (1 engineer)

---

### 3.3 Read Replica Strategy (Medium Priority)

**Recommendation:**
Implement PostgreSQL read replicas for read-heavy workloads (search, document fetch).

**Implementation Plan:**
1. **Configure Neon read replicas:** 1-2 replicas per region
2. **ORM routing:** SQLAlchemy session routing (writes → primary, reads → replicas)
3. **Connection pool separation:** Separate pools for primary vs. replicas
4. **Replica lag monitoring:** Alert if replica lag > 1 second

**Benefits:**
- **Read scalability:** Offload read queries from primary
- **Performance:** Lower latency for read-heavy operations
- **Availability:** Replicas can serve traffic if primary fails
- **Cost-effective:** Neon read replicas cheaper than scaling primary

**Estimated Effort:** 3-4 weeks (1 engineer + DBA)

---

### 3.4 Multi-Region Deployment (Medium Priority)

**Recommendation:**
Design multi-region deployment strategy for ENTERPRISE tier (US + EU).

**Implementation Plan:**
1. **Region selection:** us-east-1 (primary), eu-west-1 (secondary)
2. **Data replication:** PostgreSQL cross-region replicas, Qdrant replication
3. **DNS routing:** Route53 latency-based routing
4. **Tenant affinity:** EU tenants routed to EU region (data residency compliance)

**Benefits:**
- **Availability:** Region outage doesn't take down system
- **Latency:** Global users experience lower latency
- **Compliance:** EU data residency for GDPR
- **Disaster recovery:** Active-active or hot-warm standby

**Estimated Effort:** 8-12 weeks (2 engineers + DevOps)

---

### 3.5 Circuit Breaker Implementation (Medium Priority)

**Recommendation:**
Implement circuit breaker pattern for all external API calls (9 legal + 7 patent sources).

**Implementation Plan:**
1. **Library selection:** Use `circuitbreaker` or `hystrix-python` library
2. **Decorator pattern:** Apply to all connector methods
3. **Metrics integration:** Export circuit state to Prometheus
4. **Alerting:** Alert when circuit opens for critical services

**Benefits:**
- **Resilience:** Automatic degradation when external services fail
- **Operational simplicity:** No manual intervention required
- **SLA protection:** Prevents cascading failures
- **Observability:** Circuit state visible in dashboards

**Estimated Effort:** 2-3 weeks (1 engineer)

---

### 3.6 RS256 Migration (Low Priority)

**Recommendation:**
Migrate from HS256 to RS256 for JWT signing before microservices split.

**Implementation Plan:**
1. **Key generation:** Generate RSA key pair, store private key in Vault
2. **Dual validation:** Accept both HS256 and RS256 during transition
3. **Public key distribution:** JWKS endpoint for public key
4. **Rotation procedure:** Document key rotation without downtime

**Benefits:**
- **Security:** Asymmetric crypto more secure than shared secret
- **Scalability:** Public key distribution easier than secret coordination
- **Microservices ready:** No shared secret required across services
- **Rotation:** Can rotate keys without coordinated restart

**Estimated Effort:** 2-3 weeks (1 engineer)

---

### 3.7 GraphQL API Layer (Low Priority)

**Recommendation:**
Add GraphQL API layer for frontend to reduce over-fetching/under-fetching.

**Implementation Plan:**
1. **Schema design:** Define GraphQL schema for LexCore + LexRadar entities
2. **Resolver implementation:** Map resolvers to existing service layer
3. **Apollo Federation:** Consider if multiple GraphQL services needed
4. **Frontend migration:** Migrate from REST to GraphQL incrementally

**Benefits:**
- **Efficiency:** Frontend fetches exactly what it needs
- **Developer experience:** Strongly typed schema, auto-generated queries
- **Performance:** Single request instead of multiple REST calls
- **Flexibility:** Easy to add fields without backend changes

**Estimated Effort:** 6-8 weeks (1 engineer + 1 frontend dev)

---

## Part 4: Strategic Recommendations

### 4.1 Immediate Actions (Next 30 Days)

**Priority 1: Redis Streams Persistence**
- Enable AOF persistence to reduce data loss risk
- Estimated effort: 1 day
- Risk if not done: Data loss on Redis crash

**Priority 2: Agent Import Linter**
- Implement flake8 plugin to detect agent-to-agent imports
- Estimated effort: 3-5 days
- Risk if not done: Tight coupling, technical debt

**Priority 3: Circuit Breaker Library**
- Choose and integrate circuit breaker library
- Estimated effort: 3-5 days
- Risk if not done: Cascading failures from external APIs

---

### 4.2 Short-Term Actions (Next 90 Days)

**Priority 1: Kafka Migration**
- Begin dual-write pattern (Redis + Kafka)
- Estimated effort: 4-6 weeks
- Business value: Enables 10x throughput, better durability

**Priority 2: Read Replicas**
- Configure PostgreSQL read replicas
- Estimated effort: 3-4 weeks
- Business value: Better performance for read-heavy workloads

**Priority 3: Multi-Region Design**
- Design multi-region architecture document
- Estimated effort: 2-3 weeks
- Business value: Compliance, availability, global latency

---

### 4.3 Medium-Term Actions (Next 6 Months)

**Priority 1: Complete Kafka Migration**
- Migrate all consumers to Kafka
- Decommission Redis Streams for event bus
- Estimated effort: 4-6 weeks
- Business value: Production-grade event bus

**Priority 2: Multi-Region Implementation**
- Deploy secondary region (EU)
- Implement DNS routing and tenant affinity
- Estimated effort: 8-12 weeks
- Business value: ENTERPRISE tier feature, compliance

**Priority 3: RS256 Migration**
- Migrate JWT signing to RS256
- Estimated effort: 2-3 weeks
- Business value: Security, microservices readiness

---

### 4.4 Long-Term Vision (12+ Months)

**Priority 1: GraphQL API Layer**
- Add GraphQL for frontend efficiency
- Estimated effort: 6-8 weeks
- Business value: Better developer experience, performance

**Priority 2: Agent Marketplace**
- Enable third-party agent development
- Estimated effort: 12-16 weeks
- Business value: Ecosystem expansion, revenue

**Priority 3: Self-Hosting Option**
- Enable ENTERPRISE customers to self-host
- Estimated effort: 16-24 weeks
- Business value: ENTERPRISE sales, data sovereignty

---

## Part 5: Architecture Scorecard

| Dimension | Score (1-10) | Rationale |
|-----------|--------------|-----------|
| **Security** | 9/10 | Defense-in-depth tenant isolation, RLS, BYOK, audit trail |
| **Performance** | 8/10 | Hybrid search fast, but single DB primary limits read scaling |
| **Scalability** | 7/10 | Horizontal scaling possible, but single-region, single-DB primary |
| **Reliability** | 7/10 | Circuit breakers documented but not implemented, single-region risk |
| **Maintainability** | 8/10 | Clear layer boundaries, ADRs, observability, but agent coupling risk |
| **Observability** | 9/10 | Comprehensive logging, metrics, tracing, alerting from day one |
| **Compliance** | 8/10 | Strong tenant isolation, audit trail, but no multi-region for data residency |
| **Developer Experience** | 8/10 | FastAPI auto-docs, Pydantic validation, but no GraphQL yet |

**Overall Score:** **7.5/10** — Strong foundation with clear enhancement path.

---

## Part 6: Conclusion

LexCore + LexRadar demonstrates a **thoughtfully architected system** with strong foundations in security, search capability, and observability. The 8-layer architecture provides clear boundaries, and the ADR process documents key decisions with rationale.

**Key Strengths:**
- Defense-in-depth tenant isolation (RLS + JWT + cache prefixing)
- Hybrid search architecture (vector + full-text + re-rank)
- Three-tier async strategy (synchronous, background jobs, long-running pipelines)
- Comprehensive observability (logging, metrics, tracing, alerting)

**Key Weaknesses:**
- Event-driven immaturity (Redis Streams → Kafka migration needed)
- Single-region deployment risk
- Database scaling strategy (no read replicas)
- Circuit breaker not implemented (cascading failure risk)

**Strategic Path Forward:**
1. **Immediate:** Enable Redis persistence, implement agent import linter, add circuit breaker library
2. **Short-term:** Begin Kafka migration, configure read replicas, design multi-region architecture
3. **Medium-term:** Complete Kafka migration, implement multi-region deployment, migrate to RS256
4. **Long-term:** Add GraphQL API layer, enable agent marketplace, offer self-hosting option

**Recommendation:** Proceed with current architecture while prioritizing Kafka migration and multi-region design. The foundation is solid; enhancements are incremental and well-defined.

---

## Appendix: Reference Documents

- `docs/architecture/SYSTEM_LAYERS.md` — 8-layer architecture definition
- `docs/architecture/ADR/001_stack_choice.md` — Technology stack decisions
- `docs/architecture/ADR/002_auth.md` — Authentication strategy
- `docs/architecture/ADR/003_async_strategy.md` — Async processing strategy
- `docs/architecture/DEPENDENCY_GRAPH.json` — Component dependencies
- `docs/architecture/EVENT_SCHEMA_REGISTRY.json` — Event schemas
- `docs/03-data/ERD.md` — Database schema (24 tables)
- `docs/03-data/CONNECTION_POOL_CONFIG.md` — Database configuration
- `docs/api/API_SPEC.md` — API specification
