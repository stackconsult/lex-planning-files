"""SQLAlchemy async session factory with RLS tenant injection.

Provides async session factory that injects tenant_id into PostgreSQL session context
to enable Row Level Security (RLS) enforcement per tenant.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
import structlog

from src.config.settings import settings

logger = structlog.get_logger(__name__)

Base = declarative_base()


# Global engine and session factory (lazy initialization)
_engine: Optional[object] = None
_async_session_factory: Optional[async_sessionmaker] = None


def get_async_engine():
    """Get or create async SQLAlchemy engine."""
    global _engine
    if _engine is None:
        logger.info("sqlalchemy_engine_init", database_url=settings.DATABASE_URL)
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.ENVIRONMENT == "development",
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=True,
        )
        logger.info("sqlalchemy_engine_ready")
    return _engine


def get_async_session_factory() -> async_sessionmaker:
    """Get or create async session factory."""
    global _async_session_factory
    if _async_session_factory is None:
        engine = get_async_engine()
        _async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info("sqlalchemy_session_factory_ready")
    return _async_session_factory


@asynccontextmanager
async def get_db_session(tenant_id: Optional[UUID] = None) -> AsyncGenerator[AsyncSession, None]:
    """Get async database session with RLS tenant injection.

    Args:
        tenant_id: Tenant UUID to inject into PostgreSQL session context for RLS.

    Yields:
        AsyncSession: SQLAlchemy async session.
    """
    async with get_async_session_factory()() as session:
        # Inject tenant_id into PostgreSQL session context for RLS
        if tenant_id is not None:
            await session.execute(f"SET LOCAL app.tenant_id = '{tenant_id}'")
            logger.debug("tenant_context_injected", tenant_id=str(tenant_id))
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database connection and create tables if needed."""
    engine = get_async_engine()
    # In production, use Alembic migrations instead of create_all
    # Base.metadata.create_all(bind=engine)
    logger.info("database_initialized")


async def close_db():
    """Close database connections."""
    global _engine, _async_session_factory
    if _engine:
        await _engine.dispose()
        _engine = None
        logger.info("sqlalchemy_engine_closed")
    _async_session_factory = None
