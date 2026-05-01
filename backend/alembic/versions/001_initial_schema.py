"""Initial schema migration for LexCore + LexRadar
Revision ID: 001
Revises:
Create Date: 2026-04-30
Creates 24 tables across Platform, LexCore, and LexRadar.
"""
import os
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
revision: str = "001"
down_revision: Union[str, None] = None
def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"pgcrypto\"")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"vector\"")
    schema_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "migrations", "001_initial_schema.sql")
    with open(schema_file, "r") as f:
        op.execute(f.read())
def downgrade() -> None:
    tables = [
        "attorney_reviews","disclosures_filing_bundles","filing_bundles",
        "blockchain_anchors","prior_art","disclosures","invention_candidates",
        "jurisdictions","research_task_queries","research_task_citations",
        "research_task_documents","research_tasks","monitor_alerts","monitor_rules",
        "query_cache","legal_citations","legal_chunks","legal_documents",
        "audit_log","api_keys","workspaces","payment_plans","roles_permissions",
        "users","tenants"
    ]
    for table in tables:
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
    op.execute("DROP EXTENSION IF EXISTS \"vector\"")
    op.execute("DROP EXTENSION IF EXISTS \"pgcrypto\"")
    op.execute("DROP EXTENSION IF EXISTS \"uuid-ossp\"")
