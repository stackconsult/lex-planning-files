"""pgvector HNSW + GIN indexes for LexCore + LexRadar
Revision ID: 003
Revises: 002
Create Date: 2026-05-01
Creates HNSW cosine indexes on legal_chunks.embedding, GIN full-text
indexes, and composite query-performance indexes.
"""
import os
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    schema_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "migrations",
        "003_pgvector_indexes.sql",
    )
    with open(schema_file, "r") as f:
        op.execute(f.read())


def downgrade() -> None:
    indexes = [
        "legal_chunks_embedding_hnsw_cosine_idx",
        "legal_chunks_content_gin_idx",
        "legal_chunks_section_embedding_idx",
        "legal_chunks_tenant_doc_type_idx",
        "legal_chunks_tenant_embedding_idx",
        "legal_documents_metadata_gin_idx",
        "legal_documents_search_gin_idx",
        "query_cache_tenant_fingerprint_lookup_idx",
        "monitor_rules_active_tenant_idx",
        "invention_candidates_tenant_status_score_idx",
        "disclosures_tenant_status_created_idx",
        "attorney_reviews_expiring_idx",
    ]
    for idx in indexes:
        op.execute(f"DROP INDEX IF EXISTS {idx}")
