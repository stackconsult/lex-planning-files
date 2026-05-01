"""Alembic environment configuration for LexCore + LexRadar migrations.
Async PostgreSQL support using asyncpg driver.
"""

import os
import sys
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import configure_mappers

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import models if they exist (for autogenerate support)
# from src.models import Base

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate
# target_metadata = Base.metadata
target_metadata = None  # Set to your SQLAlchemy Base metadata when models are ready


def get_database_url():
    """Get database URL from environment or alembic config.
    Returns async PostgreSQL URL with asyncpg driver.
    """
    url = os.getenv("DATABASE_URL")
    if url:
        # Convert to async URL if not already
        if not url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://")
            url = url.replace("postgres://", "postgresql+asyncpg://")
        return url
    return config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Enable PostgreSQL-specific features
        include_schemas=True,
        # Compare type and server defaults
        compare_type=True,
        compare_server_default=True,
        # Render as batch for better performance
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def include_object(object, name, type_, reflected, compare_to):
    """Filter objects for autogenerate.

    Skip RLS policies and triggers which are managed via SQL scripts,
    not Alembic autogenerate.
    """
    if type_ == "table" and name == "audit_log":
        return False
    return True


def do_run_migrations(connection: Connection) -> None:
    """Execute migrations with the given connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,
        compare_type=True,
        compare_server_default=True,
        include_object=include_object,
        # Enable transaction per migration
        transaction_per_migration=True,
        # Render as batch for better performance
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async PostgreSQL."""
    url = get_database_url()
    
    # Override the sqlalchemy.url in the config
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = url

    connectable: AsyncEngine = create_async_engine(
        url,
        poolclass=None,  # Use default pool
        echo=False,
    )

    async with connectable.connect() as connection:
        # Set application name for monitoring
        await connection.execute("SET application_name = 'alembic_migration'")
        
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
