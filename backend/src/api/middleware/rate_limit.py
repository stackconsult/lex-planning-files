"""Rate limiting middleware for LexCore + LexRadar API."""

from fastapi import Request, HTTPException, status


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware using Redis sliding window.
    
    Limits are based on tenant tier:
    - SOLO: 10K requests/month (~0.23 req/min)
    - FIRM: Unlimited
    - ENTERPRISE: Unlimited + self-host option
    
    Uses Redis for distributed rate limit tracking.
    """
    # TODO: Implement Redis-based sliding window rate limiting
    # 1. Extract tenant_id from request state
    # 2. Look up tenant tier from cache/database
    # 3. Check current request count in Redis (window: 1 minute)
    # 4. If exceeded, return 429 Too Many Requests
    # 5. Increment counter in Redis with TTL
    
    response = await call_next(request)
    return response
