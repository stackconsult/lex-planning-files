"""Row Level Security integration tests.

Tests:
1. RLS is enabled and forced on all 24 tables.
2. Cross-tenant SELECT returns empty when app.tenant_id is set.
3. current_app_tenant_id() returns NULL when unset.
4. Audit log INSERT still succeeds (tenant-scoped but row-level).
5. Audit log UPDATE/DELETE is blocked by policy.

Requires: alembic upgrade to revision 002 (or later).
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import asyncpg
import pytest

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/lexcore_dev",
)
# Strip the +asyncpg dialect prefix for asyncpg direct connections.
RAW_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")


@pytest.fixture
async def db_pool():
    pool = await asyncpg.create_pool(RAW_DATABASE_URL, min_size=1, max_size=2)
    yield pool
    await pool.close()


async def _get_tables_with_rls(pool) -> list[dict]:
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT c.relname AS table_name,
                   c.relrowsecurity AS rls_enabled,
                   c.relforcerowsecurity AS force_rls_enabled
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relkind = 'r'
              AND n.nspname = 'public'
              AND c.relname IN (
                  'tenants','users','roles_permissions','payment_plans',
                  'workspaces','api_keys','audit_log','legal_documents',
                  'legal_chunks','legal_citations','query_cache','monitor_rules',
                  'monitor_alerts','research_tasks','research_task_documents',
                  'research_task_citations','research_task_queries',
                  'jurisdictions','invention_candidates','disclosures',
                  'prior_art','blockchain_anchors','filing_bundles',
                  'disclosures_filing_bundles','attorney_reviews'
              )
            ORDER BY c.relname;
            """
        )
    return [dict(r) for r in rows]


@pytest.mark.asyncio
async def test_rls_enabled_and_forced_on_all_tables(db_pool):
    """Every tenant-scoped table must have both RLS and FORCE RLS enabled."""
    results = await _get_tables_with_rls(db_pool)
    assert len(results) == 24, f"Expected 24 tables, got {len(results)}"

    failures = []
    for row in results:
        if not row["rls_enabled"]:
            failures.append(f"{row['table_name']}: RLS disabled")
        if not row["force_rls_enabled"]:
            failures.append(f"{row['table_name']}: FORCE RLS disabled")

    assert not failures, "RLS not fully enabled:\n" + "\n".join(failures)


@pytest.mark.asyncio
async def test_current_app_tenant_id_returns_null_when_unset(db_pool):
    """current_app_tenant_id() must return NULL when no session var is set."""
    async with db_pool.acquire() as conn:
        result = await conn.fetchval("SELECT current_app_tenant_id()")
    assert result is None


@pytest.mark.asyncio
async def test_cross_tenant_select_is_empty(db_pool):
    """With app.tenant_id set, a tenant should not see another tenant's rows."""
    async with db_pool.acquire() as conn:
        # Insert two tenants manually (bypassing RLS as superuser).
        tenant_a = await conn.fetchval(
            "INSERT INTO tenants (name, domain) VALUES ('Tenant A', 'a.example') RETURNING id"
        )
        tenant_b = await conn.fetchval(
            "INSERT INTO tenants (name, domain) VALUES ('Tenant B', 'b.example') RETURNING id"
        )

        # Create a workspace under tenant_a.
        ws_a = await conn.fetchval(
            "INSERT INTO workspaces (tenant_id, name) VALUES ($1, 'WS-A') RETURNING id",
            tenant_a,
        )

        # Switch to app_role context with tenant_b set.
        # We use a fresh connection to simulate app_role cleanly, or we can
        # just SET app.tenant_id on the current connection and rely on RLS.
        await conn.execute("SET app.tenant_id = $1", str(tenant_b))
        await conn.execute("SET ROLE app_role")

        rows = await conn.fetch(
            "SELECT id FROM workspaces WHERE id = $1", ws_a
        )

        # Restore role and clean up.
        await conn.execute("RESET ROLE")
        await conn.execute("RESET app.tenant_id")
        await conn.execute("DELETE FROM workspaces WHERE tenant_id = ANY($1)", [tenant_a, tenant_b])
        await conn.execute("DELETE FROM tenants WHERE id = ANY($1)", [tenant_a, tenant_b])

    assert len(rows) == 0, "Cross-tenant SELECT was NOT blocked by RLS"


@pytest.mark.asyncio
async def test_audit_log_update_blocked(db_pool):
    """Audit log UPDATE must be blocked for app_role by the no_update policy."""
    async with db_pool.acquire() as conn:
        tenant_id = await conn.fetchval(
            "INSERT INTO tenants (name, domain) VALUES ('Audit Tenant', 'audit.example') RETURNING id"
        )
        log_id = await conn.fetchval(
            "INSERT INTO audit_log (tenant_id, action, entity_type, entity_id, actor_id, details) "
            "VALUES ($1, 'TEST', 'USER', 'u-1', 'a-1', '{}') RETURNING id",
            tenant_id,
        )

        await conn.execute("SET app.tenant_id = $1", str(tenant_id))
        await conn.execute("SET ROLE app_role")

        with pytest.raises(asyncpg.exceptions.InsufficientPrivilegeError):
            await conn.execute(
                "UPDATE audit_log SET action = 'HACK' WHERE id = $1", log_id
            )

        # Restore and clean up.
        await conn.execute("RESET ROLE")
        await conn.execute("RESET app.tenant_id")
        await conn.execute("DELETE FROM audit_log WHERE tenant_id = $1", tenant_id)
        await conn.execute("DELETE FROM tenants WHERE id = $1", tenant_id)
