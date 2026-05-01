"""Row Level Security policies for LexCore + LexRadar
Revision ID: 002
Revises: 001
Create Date: 2026-05-01
Enables RLS on 24 tenant-scoped tables, creates tenant isolation function,
application role, and verification helper.
"""
import os
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    schema_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "migrations",
        "002_rls_policies.sql",
    )
    with open(schema_file, "r") as f:
        op.execute(f.read())


def downgrade() -> None:
    # Drop all RLS policies by forcing RLS off on every table.
    # The app_role is NOT dropped in downgrade to avoid accidental
    # privilege revocation; it can be cleaned up manually if needed.
    tables = [
        "tenants", "users", "roles_permissions", "payment_plans", "workspaces",
        "api_keys", "audit_log", "legal_documents", "legal_chunks",
        "legal_citations", "query_cache", "monitor_rules", "monitor_alerts",
        "research_tasks", "research_task_documents", "research_task_citations",
        "research_task_queries", "jurisdictions", "invention_candidates",
        "disclosures", "prior_art", "blockchain_anchors", "filing_bundles",
        "disclosures_filing_bundles", "attorney_reviews",
    ]
    for table in tables:
        op.execute(f'ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY')
        op.execute(f'ALTER TABLE {table} DISABLE ROW LEVEL SECURITY')

    op.execute("DROP FUNCTION IF EXISTS verify_rls_enabled()")
    op.execute("DROP FUNCTION IF EXISTS current_app_tenant_id()")
