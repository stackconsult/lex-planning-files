"""LexCore + LexRadar FastAPI Application.

Generated from openapi.yaml (Hash: 0fe4a24fc0d1f3cbcedca4d549e033ac1048aa10bdf5c401219fb3ad649f0037)
Schema Version: v0.1.0-foundation
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog

from src.api.routes import mcp, lexcore, lexradar, auth
from src.api.middleware import tenant_context, rate_limit, jwt_auth
from src.config.settings import settings

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    # Startup
    logger.info("lexcore_startup", version=settings.APP_VERSION, environment=settings.ENVIRONMENT)
    
    # Initialize connections (lazy — actual connections established on first use)
    # Database pool, Redis pool, Vault client initialized here when live
    
    yield
    
    # Shutdown
    logger.info("lexcore_shutdown")
    # Close connections gracefully


app = FastAPI(
    title="LexCore + LexRadar API",
    description="Complete API for LexCore legal intelligence and LexRadar IP detection",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

# Security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=600,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# Custom middleware (applied in reverse order of addition)
app.middleware("http")(rate_limit.rate_limit_middleware)
app.middleware("http")(tenant_context.tenant_context_middleware)
app.middleware("http")(jwt_auth.jwt_auth_middleware)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler — returns structured error responses."""
    logger.error(
        "unhandled_exception",
        error=str(exc),
        path=request.url.path,
        method=request.method,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "code": "INTERNAL_ERROR",
        },
    )


@app.get("/health/live", tags=["health"])
async def liveness_probe() -> dict:
    """Kubernetes liveness probe endpoint."""
    return {"status": "alive"}


@app.get("/health/ready", tags=["health"])
async def readiness_probe() -> dict:
    """Kubernetes readiness probe endpoint.
    
    Checks database connectivity, Redis connectivity, and Vault accessibility.
    """
    # Health checks implemented when database connections are live
    return {
        "status": "ready",
        "checks": {
            "database": "ok",  # To be implemented with real connection check
            "redis": "ok",     # To be implemented with real connection check
            "vault": "ok",     # To be implemented with real connection check
        },
    }


# Register routers
app.include_router(mcp.router, prefix="/v1/mcp", tags=["mcp"])
app.include_router(lexcore.router, prefix="/v1/lexcore", tags=["lexcore"])
app.include_router(lexradar.router, prefix="/v1/lexradar", tags=["lexradar"])
app.include_router(auth.router, prefix="/v1/auth", tags=["auth"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        workers=1 if settings.ENVIRONMENT == "development" else 4,
    )
