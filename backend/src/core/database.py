"""Database connection pool initialization.

Provides async connection pools for PostgreSQL (asyncpg), Redis, and Vault.
All pools are lazy-initialized on first use to support container startup without external dependencies.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
import asyncio
import threading
import asyncpg
import redis.asyncio as redis
import hvac
import structlog

from src.config.settings import settings

logger = structlog.get_logger(__name__)


# Global pool instances (lazy initialization)
_postgres_pool: Optional[asyncpg.Pool] = None
_redis_pool: Optional[redis.ConnectionPool] = None
_vault_client: Optional[hvac.Client] = None

# Locks for thread-safe lazy initialization
_postgres_lock = asyncio.Lock()
_redis_lock = asyncio.Lock()
_vault_lock = threading.Lock()


async def get_postgres_pool() -> asyncpg.Pool:
    """Get or create PostgreSQL async connection pool."""
    global _postgres_pool
    async with _postgres_lock:
        if _postgres_pool is None:
            logger.info("postgres_pool_init", pool_size=settings.DATABASE_POOL_SIZE)
            _postgres_pool = await asyncpg.create_pool(
                dsn=settings.DATABASE_URL,
                min_size=2,
                max_size=settings.DATABASE_POOL_SIZE,
                max_overflow=settings.DATABASE_MAX_OVERFLOW,
                command_timeout=30.0,
            )
            logger.info("postgres_pool_ready", pool_size=settings.DATABASE_POOL_SIZE)
    return _postgres_pool


async def get_redis_pool() -> redis.ConnectionPool:
    """Get or create Redis async connection pool."""
    global _redis_pool
    async with _redis_lock:
        if _redis_pool is None:
            logger.info("redis_pool_init", pool_size=settings.REDIS_POOL_SIZE)
            _redis_pool = redis.ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=settings.REDIS_POOL_SIZE,
                decode_responses=True,
            )
            logger.info("redis_pool_ready", pool_size=settings.REDIS_POOL_SIZE)
    return _redis_pool


def get_vault_client() -> hvac.Client:
    """Get or create Vault client (sync, for secret retrieval)."""
    global _vault_client
    with _vault_lock:
        if _vault_client is None:
            logger.info("vault_client_init", addr=settings.VAULT_ADDR)
            _vault_client = hvac.Client(
                url=settings.VAULT_ADDR,
                token=settings.VAULT_TOKEN,
                namespace=settings.VAULT_NAMESPACE or None,
            )
            if _vault_client.is_authenticated():
                logger.info("vault_client_ready", authenticated=True)
            else:
                logger.warning("vault_client_auth_failed")
    return _vault_client


async def close_all_pools():
    """Close all connection pools gracefully."""
    global _postgres_pool, _redis_pool, _vault_client

    if _postgres_pool:
        await _postgres_pool.close()
        _postgres_pool = None
        logger.info("postgres_pool_closed")

    if _redis_pool:
        await _redis_pool.aclose()
        _redis_pool = None
        logger.info("redis_pool_closed")

    _vault_client = None
    logger.info("vault_client_closed")


@asynccontextmanager
async def postgres_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """Context manager for PostgreSQL connection from pool."""
    pool = await get_postgres_pool()
    async with pool.acquire() as conn:
        yield conn


@asynccontextmanager
async def redis_connection() -> AsyncGenerator[redis.Redis, None]:
    """Context manager for Redis connection from pool."""
    pool = await get_redis_pool()
    async with redis.Redis(connection_pool=pool) as redis_conn:
        yield redis_conn


async def health_check() -> dict:
    """Health check for all connection pools."""
    health = {
        "postgres": "unknown",
        "redis": "unknown",
        "vault": "unknown",
    }

    # PostgreSQL health check
    try:
        pool = await get_postgres_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        health["postgres"] = "ok"
    except Exception as e:
        logger.error("postgres_health_check_failed", error=str(e))
        health["postgres"] = "error"

    # Redis health check
    try:
        pool = await get_redis_pool()
        async with redis.Redis(connection_pool=pool) as r:
            await r.ping()
        health["redis"] = "ok"
    except Exception as e:
        logger.error("redis_health_check_failed", error=str(e))
        health["redis"] = "error"

    # Vault health check
    try:
        client = get_vault_client()
        if client.is_authenticated():
            health["vault"] = "ok"
        else:
            health["vault"] = "unauthenticated"
    except Exception as e:
        logger.error("vault_health_check_failed", error=str(e))
        health["vault"] = "error"

    return health
