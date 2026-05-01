# CONNECTION_POOL_CONFIG.md — LexCore + LexRadar Database Configuration

> **Build System:** Unified Build System v2  
> **Chunk:** C03 — Data Model + Storage  
> **Horde:** HORDE-SCHEMA  
> **Control Plane:** ENGINEERING  

---

## Primary Database: Neon PostgreSQL (Serverless)

### Connection Details
- **Provider:** Neon (serverless PostgreSQL with auto-scaling)
- **Minimum compute:** 0.25 vCPU, 1 GB RAM
- **Maximum compute:** 4 vCPU, 16 GB RAM (FIRM tier), 8 vCPU, 32 GB RAM (ENTERPRISE)
- **Storage:** 10 GB base + auto-scaling
- **Extensions:** `uuid-ossp`, `pgcrypto`, `pgvector`
- **SSL Mode:** Require (TLS 1.3)

### Connection Pool Settings (asyncpg)

```python
DB_POOL_CONFIG = {
    "min_size": 2,        # Keep 2 connections warm
    "max_size": 20,       # Max 20 concurrent connections per worker
    "max_inactive_time": 300,  # 5 min idle timeout
    "max_queries": 50000,  # Refresh connection after 50K queries
    "max_inactive_lifetime": 1800,  # 30 min max connection lifetime
    "ssl": "require",     # TLS mandatory
    "server_settings": {
        "application_name": "lexcore-api",
        "jit": "off",       # Disable JIT for small queries (overhead)
        "search_path": "public",
    },
    "command_timeout": 30,  # 30s query timeout (matches FastAPI timeout)
}
```

### Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/lexcore?sslmode=require
DB_POOL_MIN_SIZE=2
DB_POOL_MAX_SIZE=20
DB_COMMAND_TIMEOUT=30
```

### RLS Session Setup
Every database connection must set the tenant_id context variable before any query:

```python
async def set_tenant_context(conn, tenant_id: UUID):
    """Set RLS tenant context on connection. Must be called on every acquired connection."""
    await conn.execute("SET app.tenant_id = $1", tenant_id)
```

---

## Cache Database: Redis (ElastiCache)

### Connection Details
- **Provider:** AWS ElastiCache for Redis (cluster mode disabled for MVP)
- **Engine:** Redis 7.x
- **Node Type:** cache.t4g.medium (2 vCPU, 3.09 GB memory)
- **Multi-AZ:** Enabled for FIRM/ENTERPRISE tiers
- **Encryption:** In-transit (TLS 1.2), at-rest (AES-256)

### Connection Pool Settings (redis-py async)

```python
REDIS_CONFIG = {
    "host": "redis.elasti-cache.amazonaws.com",
    "port": 6379,
    "db": 0,              # Celery broker
    "decode_responses": True,
    "max_connections": 50,
    "health_check_interval": 30,
    "socket_connect_timeout": 5,
    "socket_keepalive": True,
    "retry_on_timeout": True,
    "ssl": True,
    "ssl_cert_reqs": "required",
}
```

### Multi-DB Usage
```python
# Redis DB allocation
REDIS_BROKER_DB = 0        # Celery task broker
REDIS_RESULT_DB = 1        # Celery result backend
REDIS_CACHE_DB = 2         # Application cache (query results, embeddings)
REDIS_SESSION_DB = 3       # JWT refresh token blacklist
REDIS_RATE_LIMIT_DB = 4    # Rate limit counters
REDIS_PIPELINE_DB = 5    # Pipeline progress tracking (LexRadar)
```

---

## Vector Database: Qdrant

### Connection Details
- **Provider:** Qdrant Cloud (managed) or self-hosted on EKS
- **Version:** Qdrant 1.7+
- **Collections:** `legal_chunks` (1536-dim), `prior_art` (1536-dim)
- **Distance:** Cosine similarity

### Client Configuration
```python
QDRANT_CONFIG = {
    "url": "https://qdrant.example.com",
    "api_key": "qdrant-api-key-from-vault",
    "prefer_grpc": False,    # REST for MVP (gRPC in Enhancement Loop)
    "timeout": 10,           # 10s search timeout
    "grpc_port": 6334,
    "https": True,
}
```

### Collection Settings
```python
LEGAL_CHUNKS_COLLECTION = {
    "vectors_config": {
        "size": 1536,
        "distance": "Cosine",
        "hnsw_config": {
            "m": 16,
            "ef_construct": 100,
            "full_scan_threshold": 10000,
        }
    },
    "optimizers_config": {
        "indexing_threshold": 20000,  # Build HNSW after 20K points
    },
    "payload_schema": {
        "tenant_id": {"type": "keyword", "index": True},
        "document_id": {"type": "keyword", "index": True},
        "chunk_type": {"type": "keyword", "index": True},
        "jurisdiction_code": {"type": "keyword", "index": True},
    }
}
```

---

## Object Storage: S3 / R2

### Bucket Configuration
```python
S3_CONFIG = {
    "legal_documents_bucket": "lexcore-legal-docs",
    "filing_bundles_bucket": "lexradar-filing-bundles",
    "region": "us-east-1",
    "encryption": "AES256",  # Server-side encryption
    "versioning": "Enabled",  # Immutable document history
    "lifecycle": {
        "legal_documents": "Retain indefinitely",
        "filing_bundles": "7 years (patent lifecycle)"
    }
}
```

### Object Key Structure
```python
# Legal documents
s3://lexcore-legal-docs/{tenant_id}/{jurisdiction_code}/{doc_id}/{version}/document.html

# Filing bundles
s3://lexradar-filing-bundles/{tenant_id}/{filing_bundle_id}/{disclosure_id}/bundle.zip
```

---

## Connection Pool Sizing Guide

### Sizing Formula
```
max_connections = (web_workers × async concurrency) + (celery_workers × tasks_per_worker) + buffer

Where:
  web_workers = 4 (uvicorn workers)
  async concurrency = 20 (asyncpg pool max_size)
  celery_workers = 8 (Celery worker count)
  tasks_per_worker = 2 (Celery worker prefetches)
  buffer = 10 (admin queries, monitoring)

Max PostgreSQL connections = (4 × 20) + (8 × 2) + 10 = 80 + 16 + 10 = ~106

Neon free tier: 100 concurrent connections (sufficient)
Neon paid tier: 500+ concurrent connections (comfortable margin)
```

### Per-Environment Configuration

| Environment | PG Pool Min | PG Pool Max | Redis Max | Qdrant Timeout |
|-------------|-------------|-------------|-----------|----------------|
| Development | 1 | 5 | 10 | 30s |
| CI / Testing | 1 | 3 | 5 | 10s |
| Staging | 2 | 10 | 20 | 10s |
| Production (SOLO) | 2 | 10 | 30 | 10s |
| Production (FIRM) | 2 | 20 | 50 | 10s |
| Production (ENTERPRISE) | 5 | 50 | 100 | 10s |

---

## Health Checks

### Database Health Check
```python
async def db_health_check() -> dict:
    """Return database connectivity and latency."""
    try:
        async with db_pool.acquire() as conn:
            start = time.time()
            await conn.execute("SELECT 1")
            latency_ms = (time.time() - start) * 1000
            return {
                "status": "healthy",
                "latency_ms": round(latency_ms, 2),
                "connections": len(db_pool._holders),
            }
    except Exception as exc:
        return {"status": "unhealthy", "error": str(exc)}
```

### Redis Health Check
```python
async def redis_health_check() -> dict:
    """Return Redis connectivity and latency."""
    try:
        start = time.time()
        await redis.ping()
        latency_ms = (time.time() - start) * 1000
        info = await redis.info("memory")
        return {
            "status": "healthy",
            "latency_ms": round(latency_ms, 2),
            "memory_used_human": info.get("used_memory_human", "unknown"),
        }
    except Exception as exc:
        return {"status": "unhealthy", "error": str(exc)}
```

### Qdrant Health Check
```python
async def qdrant_health_check() -> dict:
    """Return Qdrant connectivity and collection status."""
    try:
        start = time.time()
        collections = await qdrant_client.get_collections()
        latency_ms = (time.time() - start) * 1000
        return {
            "status": "healthy",
            "latency_ms": round(latency_ms, 2),
            "collections": [c.name for c in collections.collections],
        }
    except Exception as exc:
        return {"status": "unhealthy", "error": str(exc)}
```

---

## Monitoring

### Key Metrics
| Metric | Alert Threshold | Tool |
|--------|----------------|------|
| PG active connections | > 80% of max | Prometheus |
| PG connection wait time | > 100ms (P95) | Prometheus |
| PG slow queries | > 1s, count > 5/min | PostgreSQL logs + Loki |
| Redis memory usage | > 80% of max | CloudWatch / Prometheus |
| Redis eviction rate | > 10/min | CloudWatch / Prometheus |
| Qdrant search latency | > 200ms (P95) | Prometheus |
| Qdrant collection size | > 1M points (trigger reindex) | Prometheus |

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-29 | Initial pool configuration | C03 data model definition |
