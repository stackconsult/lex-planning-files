"""Test migration upgrade/downgrade for schema-01.

Tests:
1. upgrade() creates all 24 tables
2. downgrade() drops all tables
3. upgrade() after downgrade() recreates tables
"""
import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import asyncpg
from alembic.config import Config
from alembic import command


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/lexcore_test"
)


async def get_connection():
    """Get async PostgreSQL connection."""
    url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    return await asyncpg.connect(url)


async def test_upgrade():
    """Test upgrade creates all tables."""
    conn = await get_connection()
    try:
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        table_names = [row['table_name'] for row in tables]
        expected = {
            'api_keys', 'attorney_reviews', 'audit_log', 'blockchain_anchors',
            'disclosures', 'disclosures_filing_bundles', 'filing_bundles',
            'invention_candidates', 'jurisdictions', 'legal_citations',
            'legal_chunks', 'legal_documents', 'monitor_alerts', 'monitor_rules',
            'payment_plans', 'prior_art', 'query_cache', 'research_task_citations',
            'research_task_documents', 'research_task_queries', 'research_tasks',
            'roles_permissions', 'tenants', 'users', 'workspaces'
        }
        missing = expected - set(table_names)
        extra = set(table_names) - expected
        if missing or extra:
            print(f"FAIL: Missing tables: {missing}")
            print(f"FAIL: Extra tables: {extra}")
            return False
        print("PASS: All 24 tables created")
        return True
    finally:
        await conn.close()


async def test_downgrade():
    """Test downgrade drops all tables."""
    conn = await get_connection()
    try:
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        if tables:
            print(f"FAIL: Tables still exist: {[r['table_name'] for r in tables]}")
            return False
        print("PASS: All tables dropped")
        return True
    finally:
        await conn.close()


async def run_alembic_upgrade():
    """Run alembic upgrade."""
    config = Config("../../alembic.ini")
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    command.upgrade(config, "head")


async def run_alembic_downgrade():
    """Run alembic downgrade."""
    config = Config("../../alembic.ini")
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    command.downgrade(config, "base")


async def main():
    """Run all migration tests."""
    print("=== Migration Tests for schema-01 ===")
    
    print("\n1. Running upgrade...")
    await run_alembic_upgrade()
    
    print("\n2. Testing upgrade...")
    upgrade_pass = await test_upgrade()
    
    print("\n3. Running downgrade...")
    await run_alembic_downgrade()
    
    print("\n4. Testing downgrade...")
    downgrade_pass = await test_downgrade()
    
    print("\n5. Running upgrade again...")
    await run_alembic_upgrade()
    
    print("\n6. Testing re-upgrade...")
    reupgrade_pass = await test_upgrade()
    
    print("\n=== Results ===")
    all_pass = upgrade_pass and downgrade_pass and reupgrade_pass
    if all_pass:
        print("PASS: All migration tests passed")
        sys.exit(0)
    else:
        print("FAIL: Some migration tests failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
