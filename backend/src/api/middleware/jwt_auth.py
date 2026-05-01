"""JWT authentication middleware for LexCore + LexRadar API."""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()


async def jwt_auth_middleware(request: Request, call_next):
    """Middleware to validate JWT tokens on protected routes.
    
    Skips validation for public paths (/health/*, /docs, /openapi.json, /auth/token).
    Extracts tenant_id from JWT claims and sets it in request state.
    """
    public_paths = {
        "/health/live",
        "/health/ready",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/v1/auth/token",
    }
    
    if any(request.url.path.startswith(path) for path in public_paths):
        return await call_next(request)
    
    # TODO: Implement JWT validation
    # 1. Extract Authorization header
    # 2. Verify JWT signature
    # 3. Check expiry
    # 4. Extract tenant_id from claims
    # 5. Set request.state.tenant_id
    
    response = await call_next(request)
    return response


async def get_current_tenant(request: Request) -> dict:
    """Extract tenant from request state (set by jwt_auth_middleware)."""
    tenant = getattr(request.state, "tenant", None)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return tenant
