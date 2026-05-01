# ADR-003: Async Processing Strategy

> **Status:** Accepted  
> **Date:** 2026-04-29  
> **Deciders:** HORDE-ARCH  
> **Context:** C02 — Architecture + Contracts  

---

## Problem Statement

LexCore + LexRadar has multiple workloads with different latency and throughput requirements:

1. **LexCore Search Queries** — Must return in < 300ms (P95), synchronous, user-facing
2. **Legal Document Ingestion** — Background job, can take minutes per document, high throughput (1000s docs/day)
3. **LexRadar Invention Detection** — Triggered by GitHub webhooks, must process within seconds but can queue
4. **Prior Art Search** — Parallel searches across 7 sources, 10-30 seconds total, user-facing but can show progress
5. **Disclosure Draft Generation** — LLM-based generation, 2-5 minutes, async with progress tracking
6. **Blockchain Anchoring** — Transaction confirmation, 2-15 seconds (Polygon), must be reliable

The system needs a strategy that handles both synchronous API responses and background job processing with reliability guarantees.

---

## Decision

### Three-Tier Async Strategy

| Tier | Pattern | Use Case | Technology |
|------|---------|----------|------------|
| **T1: Synchronous** | Direct async/await | Search queries, document retrieval, auth | FastAPI + asyncpg + async Redis |
| **T2: Background Jobs** | Task queue with retries | Document ingestion, invention scanning, batch operations | Celery + Redis |
| **T3: Long-Running Pipelines** | Event-driven workflow | Disclosure generation, prior art search, blockchain anchoring | Celery chains + event bus |

### T1: Synchronous (API Hot Path)

**For:** Search, document fetch, citation graph, monitoring dashboard, auth

```python
# FastAPI async endpoint
@app.get("/v1/mcp/search_legal")
async def search_legal(request: SearchRequest) -> SearchResponse:
    # Synchronous from user perspective, async I/O under the hood
    tenant_id = await validate_jwt(request.token)
    
    # Parallel I/O: cache check + vector search + full-text search
    cache_task = check_cache(request.query_fingerprint)
    vector_task = qdrant.search(request.embedding, tenant_id)
    text_task = postgres.fulltext_search(request.query, tenant_id)
    
    cached, vector_results, text_results = await asyncio.gather(
        cache_task, vector_task, text_task
    )
    
    if cached:
        return cached
    
    # Combine and re-rank
    results = re_rank(vector_results, text_results)
    await store_cache(request.query_fingerprint, results)
    
    return SearchResponse(results=results, latency_ms=...)
```

**Timeout:** 30s hard limit (uvicorn), 5s soft limit for search (return partial results)

### T2: Background Jobs (Celery + Redis)

**For:** Document ingestion, scheduled scans, batch operations, cache warming

```python
# Celery task definition
@app.task(bind=True, max_retries=3, default_retry_delay=60)
def ingest_document(self, tenant_id: str, source: str, doc_id: str):
    try:
        connector = get_connector(source)
        raw_doc = connector.fetch_document(doc_id)
        
        # Pipeline stages
        parsed = DocumentParser().parse(raw_doc)
        chunks = HierarchicalChunker().chunk(parsed)
        embedded = EmbeddingService().embed_chunks(chunks)
        
        # Store
        doc = DocumentRepository().store(tenant_id, parsed)
        ChunkRepository().store_chunks(tenant_id, doc.id, embedded)
        QdrantStore().upsert_chunks(tenant_id, doc.id, embedded)
        
        return {"status": "success", "document_id": str(doc.id), "chunks": len(chunks)}
    
    except ConnectorRateLimit:
        # Retry with backoff
        raise self.retry(countdown=2 ** self.request.retries * 60)
    
    except Exception as exc:
        logger.error("ingest_failed", exc=str(exc), tenant_id=tenant_id, doc_id=doc_id)
        raise

# Scheduled tasks
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Every 6 hours: check all active monitor rules
    sender.add_periodic_task(
        crontab(hour="*/6"),
        check_legislative_changes.s(),
        name="legislative-monitor"
    )
    
    # Daily: scan connected code repos
    sender.add_periodic_task(
        crontab(hour=2, minute=0),
        scan_code_repos.s(),
        name="invention-scan"
    )
```

**Retry Policy:**
- Connector rate limit: exponential backoff (1min, 2min, 4min)
- Transient DB error: retry 3x with 5s backoff
- Permanent error (parse failure): dead letter queue, alert, manual intervention

### T3: Long-Running Pipelines (Event-Driven)

**For:** Prior art search, disclosure generation, blockchain anchoring

```python
# Celery chain: each step passes result to next
prior_art_pipeline = chain(
    search_uspto.s(invention_id, keywords),
    search_wipo.s(invention_id, keywords),
    search_epo.s(invention_id, keywords),
    # ... 7 sources in parallel group
    group(
        search_uspto.s(...),
        search_wipo.s(...),
        search_epo.s(...),
        search_lens.s(...),
        search_google_patents.s(...),
        search_patentscope.s(...),
        search_ipcom.s(...),
    ),
    merge_and_rank.s(invention_id),
    score_patentability.s(invention_id),
    generate_disclosure.s(invention_id),
    store_disclosure.s(invention_id),
    # Attorney notification (async, non-blocking)
    notify_attorney.s(invention_id),
)

# Execute
result = prior_art_pipeline.apply_async()
# Return task_id to client for polling / webhook
```

**Progress Tracking:**
```python
# Store progress in Redis
redis.hset(f"pipeline:{task_id}", mapping={
    "status": "running",
    "current_step": "search_uspto",
    "total_steps": 9,
    "completed_steps": 2,
    "started_at": datetime.utcnow().isoformat(),
})

# Client polls or receives webhook
@app.get("/v1/lexradar/pipeline/{task_id}/status")
async def get_pipeline_status(task_id: str):
    return redis.hgetall(f"pipeline:{task_id}")
```

---

## Alternatives Considered

### Celery vs RQ (Redis Queue) vs asyncio-only

| Factor | Celery | RQ | asyncio-only |
|--------|--------|-----|-------------|
| Maturity | Very high (12+ years) | High | N/A (pattern, not framework) |
| Monitoring | Flower dashboard | rq-dashboard | Custom |
| Scheduling | Built-in (beat) | Requires rq-scheduler | APScheduler |
| Chains/groups | Built-in (canvas) | Limited | Manual orchestration |
| Result backend | Redis, PostgreSQL, etc. | Redis only | Custom |
| Learning curve | Moderate | Low | High |

**Decision:** Celery for T2/T3 — battle-tested, extensive ecosystem, chains/groups for complex pipelines.

### Kafka vs Redis for Event Bus

| Factor | Kafka | Redis (Pub/Sub / Streams) |
|--------|-------|---------------------------|
| Durability | Persistent (disk) | In-memory (configurable) |
| Throughput | 1M+ msg/s | 100K+ msg/s |
| Consumer groups | Native | Redis Streams |
| Operational complexity | High (ZooKeeper/KRaft) | Low |
| Cost | Significant infra | Minimal (ElastiCache) |

**Decision:** Redis for MVP (Celery backend + Streams for events). Kafka deferred to Enhancement Loop for high-throughput streaming (e.g., real-time webhook ingestion).

### WebSockets vs Polling vs SSE

| Factor | WebSockets | Polling | SSE (Server-Sent Events) |
|--------|-----------|---------|-------------------------|
| Real-time | Yes | No | Yes (one-way) |
| Complexity | High (connection mgmt) | Low | Medium |
| Firewall friendly | Sometimes blocked | Yes | Yes |
| Use case | Bi-directional chat | Simple status checks | Progress streams |

**Decision:**
- **Polling** for T2/T3 job status (simple, reliable, cacheable)
- **SSE** for real-time legislative alerts (server push, one-way)
- **WebSockets** deferred to Enhancement Loop (collaborative editing, real-time notifications)

---

## Consequences

### Positive
- Three-tier strategy matches workload characteristics exactly
- Celery chains enable complex pipeline orchestration with built-in retry
- Redis serves triple duty: cache, queue backend, event stream — operational simplicity
- FastAPI native async handles hot path without additional infrastructure

### Negative
- Celery adds operational complexity (Flower dashboard, worker monitoring)
- Redis as both cache and queue creates resource contention risk
- Long-running pipelines (disclosure generation) can block workers — requires dedicated worker pools

### Risks
- **Redis memory exhaustion:** Mitigation — memory limits, eviction policies, separate ElastiCache instances for cache vs queue
- **Celery worker crash mid-pipeline:** Mitigation — task idempotency, pipeline checkpointing in PostgreSQL
- **Pipeline never completes:** Mitigation — task time limits (1h), visibility timeout alerts, manual intervention runbook

---

## Implementation Details

### Worker Pool Configuration

```python
# Celery config
celery_app.conf.update(
    task_default_queue='default',
    task_routes={
        'tasks.ingest.*': {'queue': 'ingest'},
        'tasks.scan.*': {'queue': 'scan'},
        'tasks.search_prior_art.*': {'queue': 'prior_art'},
        'tasks.generate_disclosure.*': {'queue': 'generation'},
        'tasks.anchor_blockchain.*': {'queue': 'blockchain'},
    },
    worker_prefetch_multiplier=1,  # Don't prefetch — allow task prioritization
    task_acks_late=True,  # Acknowledge after task completes (retry on worker crash)
    task_reject_on_worker_lost=True,
    result_backend='redis://redis:6379/1',
    broker_url='redis://redis:6379/0',
)
```

### Pipeline State Machine

```python
class PipelineStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING = "waiting"  # Waiting for external (blockchain confirmation)
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# State transitions
PENDING → RUNNING → COMPLETED
PENDING → RUNNING → WAITING → COMPLETED
PENDING → RUNNING → FAILED
RUNNING → CANCELLED (by user)
```

### Circuit Breaker Pattern

```python
from shared.resilience import circuit_breaker

@circuit_breaker(threshold=5, recovery_timeout=60)
async def call_uspto_api(query: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(USPTO_API_URL, json={"q": query})
        return response.json()
```

---

## Related Decisions

- ADR-001: Technology Stack Choice (Celery + Redis selected)
- ADR-002: Authentication Strategy (affects async task authorization)

---

## References

- Celery: https://docs.celeryproject.org/
- Redis Streams: https://redis.io/docs/data-types/streams/
- FastAPI Background Tasks: https://fastapi.tiangolo.com/tutorial/background-tasks/
- Circuit Breaker Pattern: https://martinfowler.com/bliki/CircuitBreaker.html
