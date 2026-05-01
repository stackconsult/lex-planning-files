"""Global pytest fixtures for LexCore + LexRadar test suite."""

import asyncio
import os
import sys
from pathlib import Path

import pytest
import pytest_asyncio

# Ensure backend/src is on PYTHONPATH
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_pool():
    """Provide asyncpg connection pool for integration tests."""
    import asyncpg

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/lexcore_test",
    )
    pool = await asyncpg.create_pool(database_url, min_size=1, max_size=5)
    yield pool
    await pool.close()


@pytest.fixture
async def db_conn(db_pool):
    """Provide single database connection for a test."""
    async with db_pool.acquire() as conn:
        yield conn
