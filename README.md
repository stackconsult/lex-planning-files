# LexCore + LexRadar

Legal intelligence platform for patent detection, prior art search, and regulatory monitoring.

## Architecture

- **Backend**: Python FastAPI with async service layer
- **Workers**: Celery for ingest, LexRadar IP detection, and monitoring
- **Database**: PostgreSQL + pgvector for embeddings, with RLS-enforced tenant isolation
- **Blockchain**: Polygon for IP anchoring (SHA-256 hashed bundles)
- **ML**: Hyper-efficient data flow with token efficiency tracking and pattern forensic consistency

## Technical Mapping

### System Layers

```
┌─────────────────────────────────────────────────────────────────┐
│ L5: Frontend (React)                                             │
│    - MCP tool invocation                                         │
│    - LexRadar dashboard                                          │
│    - LexCore document viewer                                     │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST + JWT
┌────────────────────────────▼────────────────────────────────────┐
│ L4: API Layer (FastAPI)                                         │
│    - /v1/mcp/* (7 tools)                                         │
│    - /v1/lexcore/* (5 routes)                                   │
│    - /v1/lexradar/* (6 routes)                                  │
│    - /v1/auth/* (token exchange)                                │
└────────────────────────────┬────────────────────────────────────┘
                             │ Service method calls
┌────────────────────────────▼────────────────────────────────────┐
│ L3: Service Layer (Business Logic)                              │
│    - MCPService (7 tools)                                        │
│    - LexCoreService (5 operations)                               │
│    - LexRadarService (6 IP operations)                           │
└────────────────────────────┬────────────────────────────────────┘
                             │ ORM queries + asyncpg
┌────────────────────────────▼────────────────────────────────────┐
│ L2: Data Access Layer (SQLAlchemy ORM)                          │
│    - Session management with tenant context                     │
│    - RLS enforcement (app.tenant_id)                             │
│    - Connection pooling (asyncpg)                               │
└────────────────────────────┬────────────────────────────────────┘
                             │ SQL + pgvector
┌────────────────────────────▼────────────────────────────────────┐
│ L1: Database Layer (PostgreSQL)                                 │
│    - 24 tables (LexCore 10, LexRadar 8, Platform 6)              │
│    - HNSW vector indexes (pgvector)                              │
│    - Row-Level Security (RLS) policies                          │
│    - Composite B-tree indexes                                    │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Examples

#### 1. Legal Document Search (MCP Tool)

```
User Query → /v1/mcp/search_legal
  ↓
MCPService.search_legal()
  ↓
Query cache check (Redis fingerprint)
  ↓ (cache miss)
Hybrid search:
  - Vector similarity: HNSW index on legal_chunks.embedding (1536-dim)
  - Full-text search: GIN index on legal_chunks.content (tsvector)
  - Re-rank: Combine scores
  ↓
Return results with citation chains
```

#### 2. Invention Candidate Detection (LexRadar)

```
GitHub/Jira webhook → /v1/lexradar/inventions
  ↓
LexRadarService.create_invention()
  ↓
Insert into invention_candidates table
  ↓
Celery task: AGT_SCANNER (scoring)
  ↓
Update novelty_score, nonobviousness_score, etc.
  ↓
Status transition: DETECTED → SCORING → SCORED
```

#### 3. Tenant Isolation (RLS)

```
Request with JWT → TenantContextMiddleware
  ↓
SET app.tenant_id = 'uuid' (PostgreSQL session variable)
  ↓
RLS policy: WHERE tenant_id = current_app_tenant_id()
  ↓
Query automatically filtered to tenant's data
```

## Database Efficiency

### Connection Pool Configuration

**PostgreSQL (asyncpg)**
- Min size: 2 connections (warm pool)
- Max size: 20 connections per worker
- Max inactive time: 300 seconds
- Max queries per connection: 50,000
- Command timeout: 30 seconds
- SSL: Required (TLS 1.3)

**Redis (Celery + Cache)**
- Max connections: 50
- Health check interval: 30 seconds
- Multi-DB allocation:
  - DB 0: Celery broker
  - DB 1: Celery results
  - DB 2: Application cache
  - DB 3: Session blacklist
  - DB 4: Rate limit counters
  - DB 5: Pipeline tracking

### Index Strategy

#### Vector Search (pgvector)
```sql
-- HNSW index for approximate nearest neighbor
CREATE INDEX legal_chunks_embedding_hnsw_cosine_idx
ON legal_chunks USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 100);
-- Tuning: ef_search = 40 (95% recall at < 100ms)
```

#### Full-Text Search (GIN)
```sql
-- GIN index for tsvector search
CREATE INDEX legal_chunks_content_gin_idx
ON legal_chunks USING gin (to_tsvector('english', content));
```

#### Composite Indexes (Tenant-Scoped)
```sql
-- Tenant + document + chunk type
CREATE INDEX legal_chunks_tenant_doc_type_idx
ON legal_chunks(tenant_id, document_id, chunk_type);

-- Tenant + status + created_at (time-series queries)
CREATE INDEX disclosures_tenant_status_created_idx
ON disclosures(tenant_id, status, created_at DESC);
```

#### Partial Indexes (Conditional)
```sql
-- Only index active monitor rules
CREATE INDEX monitor_rules_active_tenant_idx
ON monitor_rules(tenant_id, status)
WHERE status = 'ACTIVE';

-- Only index expiring attorney reviews
CREATE INDEX attorney_reviews_expiring_idx
ON attorney_reviews(tenant_id, expires_at)
WHERE status IN ('PENDING', 'IN_PROGRESS')
  AND expires_at < now() + interval '24 hours';
```

### Query Optimization Patterns

#### 1. Pagination with Count
```python
# Efficient: Single query with subquery
query = select(LegalDocument)
count_query = select(func.count()).select_from(query.subquery())
total = await session.execute(count_query)
query = query.limit(limit).offset(offset)
```

#### 2. Tenant-Scoped Search
```python
# RLS automatically filters by tenant_id
# No WHERE tenant_id = :tenant_id needed in application code
async with get_db_session(tenant_uuid) as session:
    result = await session.execute(select(LegalDocument))
    # RLS policy: USING (tenant_id = current_app_tenant_id())
```

#### 3. Hybrid Search (Vector + Full-Text)
```python
# Combine HNSW (semantic) + GIN (lexical) + re-rank
vector_results = await session.execute(
    select(LegalChunk)
    .order_by(LegalChunk.embedding <=> query_embedding)
    .limit(100)
)
text_results = await session.execute(
    select(LegalChunk)
    .where(LegalChunk.content.match(query_text))
    .limit(100)
)
# Re-rank and combine top 10
```

### Row-Level Security (RLS)

**Architecture**
- All tenant-scoped tables have RLS enabled
- Session variable `app.tenant_id` set on connection acquire
- RLS policy: `USING (tenant_id = current_app_tenant_id())`
- Audit log: SELECT only (no UPDATE/DELETE)

**Performance Impact**
- Minimal: Policy evaluation at query planning time
- Indexes still used with tenant_id filter
- Connection reuse maintains tenant context

### Caching Strategy

**Query Cache (Redis)**
- Key: SHA-256 fingerprint of (query, jurisdiction, doc_type, limit)
- TTL: 5 minutes (300 seconds)
- Hit rate: Target 60%+ for repetitive queries
- Invalidation: Manual on document updates

**Embedding Cache (Qdrant)**
- Stored separately from PostgreSQL
- Async sync after document ingestion
- HNSW index rebuilt at 20K points threshold

## Quick Start

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run build validation
python scripts/validate_build.py

# Run predictability validation
python scripts/validate_predictability.py

# Run HORDE-AUDIT
python scripts/horde_audit.py
```

## Service Layer

| Domain | Routes | Service | Methods |
|---|---|---|---|
| MCP | 7 | `mcp_service.py` | 7 tools |
| LexCore | 5 | `lexcore_service.py` | 5 operations |
| LexRadar | 6 | `lexradar_service.py` | 6 IP operations |

## Validation

- **Token efficiency**: 41.9% reduction (target 40%)
- **Pattern forensic consistency**: 100%
- **Predictability curve R²**: 0.9449

## Documentation

- `docs/teams/` — 17 team execution plans
- `docs/execution/BUILD_JOURNAL.md` — incremental build log
- `docs/execution/HORDE_AUDIT_REPORT.md` — latest audit gate
- `docs/03-data/ERD.md` — Entity relationship diagram (24 tables)
- `docs/03-data/CONNECTION_POOL_CONFIG.md` — Database configuration
- `docs/api/API_SPEC.md` — Complete API specification
