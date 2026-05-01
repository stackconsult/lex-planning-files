"""Tenant context middleware for LexCore + LexRadar API."""

from fastapi import Request


async def tenant_context_middleware(request: Request, call_next):
    """Middleware to set tenant context for RLS enforcement.
    
    Sets the PostgreSQL app.tenant_id session variable for Row-Level Security.
    Must run after jwt_auth_middleware (which sets request.state.tenant).
    """
    response = await call_next(request)
    
    # TODO: After request is processed, set tenant_id in DB session for RLS
    # This requires asyncpg or similar for async PostgreSQL
    # async with db_pool.acquire() as conn:
    #     await conn.execute("SELECT set_tenant_context($1)", tenant_id)
    
    return response
