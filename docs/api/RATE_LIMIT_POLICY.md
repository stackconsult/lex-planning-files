# RATE_LIMIT_POLICY.md — LexCore + LexRadar API Rate Limiting

> **Build System:** Unified Build System v2  
> **Chunk:** C04 — API Contracts + MCP Tools  
> **Horde:** HORDE-API  
> **Control Plane:** ENGINEERING  

---

## Overview

Rate limiting is implemented at the API gateway layer using Redis sliding window counters. Every request is tagged with `tenant_id` + `endpoint` + `tier`, and the counter is checked before processing.

**Enforcement Point:** FastAPI middleware (after JWT validation, before route handler)  
**Storage:** Redis (DB 4: `REDIS_RATE_LIMIT_DB`)  
**Algorithm:** Sliding window with 60-second granularity  
**Fallback:** If Redis is unavailable, allow request (fail-open to prevent total outage)

---

## Rate Limit Tiers

### SOLO Tier (10,000 requests/month)

| Endpoint Category | Per-Minute Limit | Per-Day Limit | Per-Month Limit |
|-------------------|-----------------|---------------|----------------|
| MCP `search_legal` | 50 | 500 | 5,000 |
| MCP `research_task` | N/A | 10 | 50 |
| MCP `get_document` | 100 | 1,000 | 2,000 |
| MCP `get_citations` | 50 | 500 | 1,000 |
| MCP `check_updates` | 100 | 1,000 | 1,000 |
| MCP `jurisdiction_summary` | 100 | 1,000 | 500 |
| MCP `get_capabilities` | 100 | 2,000 | N/A |
| LexCore domain routes | 50 | 500 | N/A |
| LexRadar domain routes | 50 | 500 | N/A |
| Auth routes | 10 | 100 | N/A |
| Health routes | N/A | N/A | N/A (unlimited) |

### FIRM Tier (Unlimited)

| Endpoint Category | Per-Minute Limit | Per-Day Limit |
|-------------------|-----------------|---------------|
| MCP `search_legal` | 500 | 10,000 |
| MCP `research_task` | N/A | 100 |
| MCP `get_document` | 2,000 | 20,000 |
| MCP `get_citations` | 500 | 5,000 |
| MCP `check_updates` | 1,000 | 10,000 |
| MCP `jurisdiction_summary` | 1,000 | 10,000 |
| MCP `get_capabilities` | 1,000 | N/A |
| LexCore domain routes | 500 | 10,000 |
| LexRadar domain routes | 500 | 10,000 |
| Auth routes | 100 | 1,000 |
| Health routes | N/A | N/A |

### ENTERPRISE Tier (Unlimited + Self-Host Option)

| Endpoint Category | Per-Minute Limit | Per-Day Limit |
|-------------------|-----------------|---------------|
| MCP `search_legal` | 1,000 | 50,000 |
| MCP `research_task` | N/A | 500 |
| MCP `get_document` | 5,000 | 100,000 |
| MCP `get_citations` | 1,000 | 20,000 |
| MCP `check_updates` | 1,000 | 20,000 |
| MCP `jurisdiction_summary` | 1,000 | 20,000 |
| MCP `get_capabilities` | 1,000 | N/A |
| LexCore domain routes | 1,000 | 50,000 |
| LexRadar domain routes | 1,000 | 50,000 |
| Auth routes | 200 | 2,000 |
| Health routes | N/A | N/A |

---

## Rate Limit Response Headers

Every response includes rate limit headers (even for unlimited tiers, for transparency):

```http
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 47
X-RateLimit-Reset: 1714399200
X-RateLimit-Window: 60
X-RateLimit-Tier: SOLO
```

On rate limit exceeded (429):

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 45
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1714399260
X-RateLimit-Window: 60

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded for search_legal. Retry after 45 seconds.",
    "status": 429,
    "retry_after": 45,
    "rate_limit": {
      "limit": 50,
      "remaining": 0,
      "reset_at": "2024-04-29T10:01:00Z",
      "window": "60s"
    }
  }
}
```

---

## Redis Key Structure

```
rate_limit:{tenant_id}:{endpoint}:{window_start_timestamp}
```

Where `window_start_timestamp` is the Unix timestamp rounded down to the window boundary (60-second windows).

**Example:**
```
rate_limit:550e8400-e29b-41d4-a716-446655440000:search_legal:1714399140
value: 47  (47 requests in this 60s window, limit 50)
TTL: 120s (expire after 2 windows to clean up)
```

---

## Sliding Window Algorithm

```python
async def check_rate_limit(tenant_id: str, endpoint: str, tier: str) -> dict:
    """Check if request is within rate limit using sliding window."""
    now = time.time()
    window = 60  # seconds
    current_window = int(now // window) * window
    previous_window = current_window - window
    
    # Get counts from current and previous windows
    current_key = f"rate_limit:{tenant_id}:{endpoint}:{current_window}"
    previous_key = f"rate_limit:{tenant_id}:{endpoint}:{previous_window}"
    
    current_count = await redis.get(current_key) or 0
    previous_count = await redis.get(previous_key) or 0
    
    # Sliding window: weighted average
    # Previous window contributes less as time progresses
    time_into_window = now - current_window
    previous_weight = 1 - (time_into_window / window)
    
    estimated_count = (previous_count * previous_weight) + current_count
    
    limit = get_limit(tier, endpoint)
    
    if estimated_count >= limit:
        # Calculate retry_after
        retry_after = window - time_into_window
        raise RateLimitExceeded(retry_after=int(retry_after))
    
    # Increment current window counter
    pipe = redis.pipeline()
    pipe.incr(current_key)
    pipe.expire(current_key, window * 2)  # TTL = 2 windows
    await pipe.execute()
    
    remaining = limit - estimated_count - 1
    
    return {
        "limit": limit,
        "remaining": max(0, int(remaining)),
        "reset_at": current_window + window,
        "window": window,
    }
```

---

## Burst Handling

SOLO tier: Allow 1 burst of 2x the per-minute limit per hour (emergency use).  
FIRM tier: Allow 1 burst of 3x the per-minute limit per hour.  
ENTERPRISE tier: Allow configurable burst multiplier (default 5x).

Burst tracking key:
```
rate_limit_burst:{tenant_id}:{endpoint}:{hour_timestamp}
```

---

## Monitoring & Alerting

### Metrics
| Metric | Type | Alert Threshold |
|--------|------|----------------|
| `rate_limit_hits_total` | Counter | > 100/hour for any tenant |
| `rate_limit_remaining_avg` | Gauge | < 10% for any SOLO tenant |
| `rate_limit_redis_latency_ms` | Histogram | P95 > 10ms |

### Alerts
- **High rate limit rate:** > 5% of requests return 429 for any tenant (suggests need tier upgrade)
- **Redis rate limit failure:** > 1% of rate limit checks fail (fail-open — alert on security risk)

---

## Implementation (FastAPI Middleware)

```python
class RateLimitMiddleware:
    async def __call__(self, request: Request, call_next):
        # Skip health endpoints
        if request.url.path.startswith("/health"):
            return await call_next(request)
        
        # Extract tenant and endpoint
        tenant_id = request.state.tenant_id  # Set by TenantContextMiddleware
        endpoint = self.get_endpoint_category(request.url.path)
        
        # Check rate limit
        try:
            result = await check_rate_limit(tenant_id, endpoint, request.state.tier)
        except RateLimitExceeded as exc:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Rate limit exceeded for {endpoint}. Retry after {exc.retry_after} seconds.",
                        "status": 429,
                        "retry_after": exc.retry_after,
                    }
                },
                headers={
                    "Retry-After": str(exc.retry_after),
                    "X-RateLimit-Limit": str(result["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(result["reset_at"]),
                }
            )
        
        # Proceed with request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(result["limit"])
        response.headers["X-RateLimit-Remaining"] = str(result["remaining"])
        response.headers["X-RateLimit-Reset"] = str(result["reset_at"])
        response.headers["X-RateLimit-Window"] = str(result["window"])
        response.headers["X-RateLimit-Tier"] = request.state.tier
        
        return response
```

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-29 | Initial rate limit policy | C04 API contracts definition |
