# RESILIENCE_RULES.md — LexCore + LexRadar Reliability & Resilience

> **Build System:** Unified Build System v2  
> **Chunk:** C05 — Services + Workers + Agents  
> **Horde:** HORDE-AGENTS  
> **Control Plane:** ENGINEERING  

---

## Overview

This document defines resilience patterns, circuit breakers, retry policies, and failure modes for all services, agents, and workers. All resilience rules derive from C02 architecture laws and HORDE-AUDIT L3 security requirements.

**Principles:**
1. **Fail-open for auth, fail-closed for data** (C02 Law #3)
2. **All idempotent operations are replay-safe** (C02 Law #4)
3. **Every critical state change writes an audit row** (C02 Law #5)
4. **Circuit breakers protect upstream services** (C02 Law #7)
5. **Dead-letter queues catch unhandled failures** (C02 Law #8)
6. **Rate limit counters never block auth** (C02 Law #9)
7. **Correlation IDs trace every request end-to-end** (C02 Law #11)

---

## Circuit Breaker Configuration

### Circuit Breaker Registry

```python
from pybreaker import CircuitBreaker

# Registry of circuit breakers per dependency
CIRCUIT_BREAKERS = {
    "openai": CircuitBreaker(
        fail_max=5,
        timeout_duration=60,
        expected_exception=openai.APITimeoutError,
    ),
    "qdrant": CircuitBreaker(
        fail_max=10,
        timeout_duration=30,
        expected_exception=QdrantException,
    ),
    "postgres": CircuitBreaker(
        fail_max=5,
        timeout_duration=30,
        expected_exception=asyncpg.PostgresError,
    ),
    "redis": CircuitBreaker(
        fail_max=10,
        timeout_duration=10,
        expected_exception=redis.ConnectionError,
    ),
    "uspto": CircuitBreaker(
        fail_max=10,
        timeout_duration=300,
        expected_exception=USPTOAPIError,
    ),
    "wipo": CircuitBreaker(
        fail_max=10,
        timeout_duration=300,
        expected_exception=WIPOAPIError,
    ),
    "epo": CircuitBreaker(
        fail_max=10,
        timeout_duration=300,
        expected_exception=EPOAPIError,
    ),
    "github_api": CircuitBreaker(
        fail_max=10,
        timeout_duration=60,
        expected_exception=GithubAPIError,
    ),
    "polygon": CircuitBreaker(
        fail_max=10,
        timeout_duration=60,
        expected_exception=PolygonError,
    ),
    "clerk": CircuitBreaker(
        fail_max=5,
        timeout_duration=30,
        expected_exception=ClerkError,
    ),
}
```

### Circuit Breaker States

| State | Behavior | Trigger |
|-------|----------|---------|
| **CLOSED** | Normal operation, requests pass through | Default state |
| **OPEN** | All requests fail immediately, return cached or degraded response | `fail_max` failures within `timeout_duration` |
| **HALF-OPEN** | Allow 1 probe request; if success → CLOSED, if fail → OPEN | After `timeout_duration` in OPEN |

### Circuit Breaker Response (OPEN State)

| Dependency | OPEN State Response | Degraded UX |
|-----------|---------------------|-------------|
| OpenAI | Return `503 LLM_UNAVAILABLE` | Research tasks queued, search uses cached embeddings |
| Qdrant | Fall back to PostgreSQL GIN search only | Semantic search disabled, text search only |
| PostgreSQL | Return `500 DATABASE_ERROR` | API unavailable (fail-closed for data) |
| Redis | Allow request (fail-open for cache) | No caching, no rate limiting, degraded performance |
| USPTO/WIPO/EPO | Return empty prior art + warning | Prior art search partial results |
| GitHub API | Return empty scan results | Scan pending manual retry |
| Polygon | Queue for retry | Blockchain anchoring deferred |
| Clerk | Return `503 SERVICE_UNAVAILABLE` | Frontend auth unavailable |

---

## Retry Policies

### Retry Configuration by Operation

| Operation | Max Retries | Base Delay | Max Delay | Backoff Strategy | Jitter |
|-----------|-------------|------------|-----------|-----------------|--------|
| OpenAI API call | 3 | 2s | 30s | Exponential (2^n) | ±20% |
| Qdrant search | 3 | 1s | 10s | Exponential | ±10% |
| PostgreSQL query | 3 | 100ms | 2s | Linear (100ms, 500ms, 1s) | None |
| Redis operation | 5 | 50ms | 2s | Exponential | ±10% |
| USPTO API | 5 | 5s | 60s | Exponential | ±30% |
| WIPO API | 5 | 5s | 60s | Exponential | ±30% |
| EPO API | 5 | 5s | 60s | Exponential | ±30% |
| GitHub API | 3 | 1s | 10s | Exponential | ±20% |
| Polygon transaction | 5 | 10s | 300s | Exponential | ±50% |
| Email send | 3 | 5s | 30s | Exponential | ±20% |
| Clerk session validation | 2 | 100ms | 1s | Linear | None |

### Retry Implementation (Async)

```python
import asyncio
import random
from functools import wraps
from typing import Callable, TypeVar

T = TypeVar("T")

class RetryPolicy:
    """Configurable retry policy for async operations."""
    
    def __init__(
        self,
        max_retries: int,
        base_delay: float,
        max_delay: float,
        backoff_strategy: str = "exponential",
        jitter: float = 0.0,
        exceptions: tuple = (Exception,),
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_strategy = backoff_strategy
        self.jitter = jitter
        self.exceptions = exceptions
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for attempt N (0-indexed)."""
        if self.backoff_strategy == "exponential":
            delay = self.base_delay * (2 ** attempt)
        elif self.backoff_strategy == "linear":
            delay = self.base_delay * (attempt + 1)
        else:  # fixed
            delay = self.base_delay
        
        # Apply max delay cap
        delay = min(delay, self.max_delay)
        
        # Apply jitter
        if self.jitter > 0:
            jitter_amount = delay * self.jitter
            delay = delay + random.uniform(-jitter_amount, jitter_amount)
        
        return max(0, delay)
    
    async def execute(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with retries."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except self.exceptions as exc:
                last_exception = exc
                
                if attempt < self.max_retries:
                    delay = self.calculate_delay(attempt)
                    await asyncio.sleep(delay)
        
        raise last_exception


# Pre-configured retry policies
RETRY_POLICIES = {
    "openai": RetryPolicy(
        max_retries=3,
        base_delay=2.0,
        max_delay=30.0,
        backoff_strategy="exponential",
        jitter=0.2,
        exceptions=(openai.APITimeoutError, openai.RateLimitError),
    ),
    "postgres": RetryPolicy(
        max_retries=3,
        base_delay=0.1,
        max_delay=2.0,
        backoff_strategy="linear",
        jitter=0.0,
        exceptions=(asyncpg.PostgresError, asyncpg.ConnectionError),
    ),
    "redis": RetryPolicy(
        max_retries=5,
        base_delay=0.05,
        max_delay=2.0,
        backoff_strategy="exponential",
        jitter=0.1,
        exceptions=(redis.ConnectionError, redis.TimeoutError),
    ),
    "uspto": RetryPolicy(
        max_retries=5,
        base_delay=5.0,
        max_delay=60.0,
        backoff_strategy="exponential",
        jitter=0.3,
        exceptions=(USPTOAPIError, aiohttp.ClientError),
    ),
    "polygon": RetryPolicy(
        max_retries=5,
        base_delay=10.0,
        max_delay=300.0,
        backoff_strategy="exponential",
        jitter=0.5,
        exceptions=(PolygonError, ConnectionError),
    ),
}


def with_retry(policy_name: str):
    """Decorator to apply retry policy to a function."""
    policy = RETRY_POLICIES[policy_name]
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await policy.execute(func, *args, **kwargs)
        return wrapper
    return decorator
```

---

## Database Resilience

### Connection Pool Recovery

```python
class ResilientDBPool:
    """Database connection pool with automatic recovery."""
    
    def __init__(self, dsn: str, min_size: int = 2, max_size: int = 20):
        self.dsn = dsn
        self.min_size = min_size
        self.max_size = max_size
        self._pool = None
        self._lock = asyncio.Lock()
    
    async def _create_pool(self) -> asyncpg.Pool:
        """Create new connection pool."""
        return await asyncpg.create_pool(
            dsn=self.dsn,
            min_size=self.min_size,
            max_size=self.max_size,
            command_timeout=30,
            server_settings={"jit": "off"},
        )
    
    async def get_pool(self) -> asyncpg.Pool:
        """Get pool, creating if necessary."""
        if self._pool is None or self._pool._closed:
            async with self._lock:
                if self._pool is None or self._pool._closed:
                    self._pool = await self._create_pool()
        return self._pool
    
    async def acquire(self):
        """Acquire connection with retry."""
        pool = await self.get_pool()
        
        try:
            return await pool.acquire()
        except asyncpg.ConnectionError:
            # Pool may be stale, recreate
            self._pool = None
            pool = await self.get_pool()
            return await pool.acquire()
```

### PostgreSQL Query Timeouts

```python
# Query timeout enforced at multiple layers
LAYER_1_APP = 30   # FastAPI request timeout
LAYER_2_POOL = 30  # asyncpg pool command_timeout
LAYER_3_DB = 30    # PostgreSQL statement_timeout (SET statement_timeout = '30s')

# Long-running queries (research, ingestion) use separate pool
LONG_QUERY_POOL = {
    "command_timeout": 300,  # 5 minutes
    "max_size": 5,  # Smaller pool for long queries
}
```

---

## External API Resilience

### OpenAI API Resilience

```python
@with_retry("openai")
async def generate_embedding(text: str) -> list[float]:
    """Generate embedding with retry and circuit breaker."""
    cb = CIRCUIT_BREAKERS["openai"]
    
    @cb
    async def _call():
        return await openai.embeddings.create(
            input=text,
            model="text-embedding-3-large",
        )
    
    try:
        result = await _call()
        return result.data[0].embedding
    except CircuitBreakerError:
        # Fallback: return cached embedding or raise
        raise LLMUnavailable("OpenAI circuit breaker OPEN")
```

### Qdrant Search Resilience

```python
async def search_vectors(
    tenant_id: UUID,
    vector: list[float],
    top_k: int = 10,
) -> list[dict]:
    """Search Qdrant with fallback to PostgreSQL GIN."""
    cb = CIRCUIT_BREAKERS["qdrant"]
    
    @cb
    async def _qdrant_search():
        return await qdrant_client.search(
            collection_name="legal_chunks",
            query_vector=vector,
            limit=top_k,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="tenant_id",
                        match=models.MatchValue(value=str(tenant_id)),
                    )
                ]
            ),
        )
    
    try:
        return await _qdrant_search()
    except CircuitBreakerError:
        # Degraded: fall back to PostgreSQL GIN full-text search
        logger.warning("Qdrant circuit breaker OPEN — falling back to GIN search")
        return await fallback_gin_search(tenant_id, vector, top_k)
```

---

## Celery Worker Resilience

### Worker Crash Recovery

```python
# Celery configuration for resilience
celery_app.conf.update(
    task_acks_late=True,  # Acknowledge AFTER completion
    task_reject_on_worker_lost=True,  # Re-queue if worker dies mid-task
    worker_prefetch_multiplier=1,  # Don't prefetch (fair task distribution)
    worker_max_tasks_per_child=1000,  # Restart worker after N tasks (memory leaks)
    worker_max_memory_per_child=256000,  # Kill worker if memory > 256MB (in KiB)
    
    # Task visibility timeout (Redis only)
    visibility_timeout=43200,  # 12 hours (for long-running tasks)
    
    # Result backend
    result_backend="redis://localhost:6379/1",
    result_expires=86400,  # 24 hours
    result_extended=True,  # Keep extended result info
    
    # Retries
    task_default_retry_delay=60,
    task_max_retries=3,
    task_default_rate_limit=None,
)
```

### Memory Leak Prevention

```python
# Kill worker if memory exceeds threshold
# 256000 KiB = 256 MB
# This prevents memory leaks from accumulating over long-running workers

# Monitor memory usage
import psutil

def check_worker_memory():
    """Check current worker memory usage."""
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    
    if memory_mb > 200:  # 200 MB warning
        logger.warning(f"Worker memory usage: {memory_mb:.1f}MB — approaching limit")
    
    return memory_mb
```

---

## Correlation ID & Distributed Tracing

### Correlation ID Propagation

```python
import uuid
from contextvars import ContextVar

correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default=None)

class CorrelationIDMiddleware:
    """Attach correlation ID to every request."""
    
    async def __call__(self, request, call_next):
        # Get from header or generate new
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        correlation_id_var.set(correlation_id)
        
        # Add to request state
        request.state.correlation_id = correlation_id
        
        # Propagate to all downstream calls
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response


def get_correlation_id() -> str:
    """Get current correlation ID from context."""
    return correlation_id_var.get() or str(uuid.uuid4())
```

### Structured Logging with Correlation ID

```python
import structlog

logger = structlog.get_logger()

def bind_correlation_id():
    """Bind correlation ID to logger context."""
    correlation_id = get_correlation_id()
    return logger.bind(correlation_id=correlation_id)

# Usage in services
async def search_documents(tenant_id: UUID, query: str):
    log = bind_correlation_id()
    log.info("search_started", tenant_id=str(tenant_id), query=query)
    
    try:
        results = await search_service.search(tenant_id, query)
        log.info("search_completed", result_count=len(results))
        return results
    except Exception as exc:
        log.error("search_failed", error=str(exc))
        raise
```

---

## Graceful Degradation

### Degradation Strategies by Feature

| Feature | Degraded Mode | Trigger |
|---------|--------------|---------|
| Semantic search | GIN full-text only | Qdrant unavailable |
| Citation graph | Direct citations only (no traversal) | Depth=1 only |
| Research task | Cached template response | OpenAI unavailable |
| Prior art search | Partial results (working sources only) | Some APIs unavailable |
| Blockchain anchoring | Queue for retry | Polygon unavailable |
| Email notifications | In-app notification only | Email service unavailable |
| Real-time updates | Manual refresh | WebSocket unavailable |
| Dashboard analytics | Last known values | Analytics DB unavailable |

### Degradation Implementation

```python
class DegradationController:
    """Central controller for graceful degradation."""
    
    DEGRADATION_RULES = {
        "semantic_search": {
            "check": lambda: CIRCUIT_BREAKERS["qdrant"].current_state != "closed",
            "fallback": "gin_search",
        },
        "research_task": {
            "check": lambda: CIRCUIT_BREAKERS["openai"].current_state != "closed",
            "fallback": "cached_template",
        },
        "prior_art_search": {
            "check": lambda: any(
                CIRCUIT_BREAKERS[f].current_state != "closed"
                for f in ["uspto", "wipo", "epo"]
            ),
            "fallback": "partial_results",
        },
    }
    
    @classmethod
    def is_degraded(cls, feature: str) -> bool:
        rule = cls.DEGRADATION_RULES.get(feature)
        if not rule:
            return False
        return rule["check"]()
    
    @classmethod
    def get_fallback(cls, feature: str) -> str | None:
        rule = cls.DEGRADATION_RULES.get(feature)
        return rule["fallback"] if rule else None
```

---

## Failure Mode Summary

| Failure | Impact | Detection | Recovery | SLA |
|---------|--------|-----------|----------|-----|
| PostgreSQL unavailable | All data operations fail | Health check 30s | Auto-reconnect, alert on-call | RTO: 5 min |
| Redis unavailable | No cache, no rate limits, no sessions | Health check 10s | Auto-reconnect, degraded mode | RTO: 2 min |
| Qdrant unavailable | Semantic search disabled | Health check 10s | Fallback to GIN search | RTO: 2 min |
| OpenAI unavailable | Research tasks queued, no new embeddings | Circuit breaker | Retry queue, cached results | RTO: 10 min |
| Clerk unavailable | Frontend auth fails | Circuit breaker | SSO fallback (if configured) | RTO: 5 min |
| USPTO/WIPO/EPO down | Prior art partial results | Retry failures | Partial results, retry later | RTO: N/A |
| GitHub API down | No new code scans | Retry failures | Manual retry button | RTO: N/A |
| Polygon RPC down | Blockchain anchoring queued | Retry failures | Deferred anchoring | RTO: N/A |
| Email service down | No email notifications | Retry failures | In-app notifications only | RTO: N/A |
| Celery worker crash | Tasks re-queued | Worker monitoring | Auto-restart via Kubernetes | RTO: 1 min |

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-29 | Initial resilience rules | C05 resilience definition |
