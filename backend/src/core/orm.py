"""SQLAlchemy ORM models for LexCore + LexRadar.

Mapped to database schema defined in migrations (001_initial_schema.sql, 002_rls_policies.sql).
"""
from datetime import datetime
from typing import Optional, List
from uuid import uuid4, UUID

from sqlalchemy import (
    Column, String, DateTime, Boolean, Integer, Float, Text, JSON, ForeignKey,
    Index, UniqueConstraint, LargeBinary,
)
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# ============================================================================
# Tenant & User Models
# ============================================================================

class Tenant(Base):
    """Tenant model for multi-tenancy."""
    __tablename__ = "tenants"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    tier: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(default=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# LexCore Models
# ============================================================================

class LegalDocument(Base):
    """Legal document model."""
    __tablename__ = "legal_documents"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"))
    title: Mapped[str] = mapped_column(String(500))
    title_fr: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    citation: Mapped[str] = mapped_column(String(255))
    body_of_law: Mapped[str] = mapped_column(String(50))
    jurisdiction: Mapped[str] = mapped_column(String(20), index=True)
    doc_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    full_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    effective_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    data_quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(100))
    is_repealed: Mapped[bool] = mapped_column(default=False)
    overruled_by: Mapped[Optional[UUID]] = mapped_column(ForeignKey("legal_documents.id"), nullable=True)
    bam_compound: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_legal_documents_jurisdiction_body", "jurisdiction", "body_of_law"),
        Index("idx_legal_documents_tenant", "tenant_id"),
    )


class LegalChunk(Base):
    """Legal document chunk model for vector search."""
    __tablename__ = "legal_chunks"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    document_id: Mapped[UUID] = mapped_column(ForeignKey("legal_documents.id"))
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"))
    section_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    chunk_order: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    chunk_text: Mapped[str] = mapped_column(Text)
    token_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    chunk_quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    embedding: Mapped[Optional[List[float]]] = mapped_column(LargeBinary, nullable=True)  # pgvector
    bam_signal: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_legal_chunks_document", "document_id"),
        Index("idx_legal_chunks_tenant", "tenant_id"),
    )


class LegalCitation(Base):
    """Legal citation relationship model."""
    __tablename__ = "legal_citations"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    citing_chunk_id: Mapped[UUID] = mapped_column(ForeignKey("legal_chunks.id"))
    cited_document_id: Mapped[UUID] = mapped_column(ForeignKey("legal_documents.id"))
    citation_type: Mapped[str] = mapped_column(String(50))
    court: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    jurisdiction: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    decision_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    citation_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("citing_chunk_id", "cited_document_id", name="uq_legal_citations"),
    )


class QueryCache(Base):
    """Query cache model for agent queries."""
    __tablename__ = "query_cache"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"))
    agent_id: Mapped[str] = mapped_column(String(50))
    bam_compound: Mapped[dict] = mapped_column(JSON)
    query_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    query_normalized: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    query_fingerprint: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    result_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cache_hit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    query_params: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class MonitorRule(Base):
    """Monitor rule model for legal change tracking."""
    __tablename__ = "monitor_rules"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"))
    jurisdiction: Mapped[str] = mapped_column(String(20))
    body_of_law: Mapped[str] = mapped_column(String(50))
    alert_type: Mapped[str] = mapped_column(String(50))
    criteria: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    last_checked: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


class MonitorAlert(Base):
    """Monitor alert model."""
    __tablename__ = "monitor_alerts"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"))
    rule_id: Mapped[UUID] = mapped_column(ForeignKey("monitor_rules.id"))
    document_id: Mapped[UUID] = mapped_column(ForeignKey("legal_documents.id"))
    alert_type: Mapped[str] = mapped_column(String(50))
    alert_details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    acknowledged: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class ResearchTask(Base):
    """Research task model."""
    __tablename__ = "research_tasks"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"))
    query: Mapped[str] = mapped_column(Text)
    jurisdiction: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(50))
    result_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


class Jurisdiction(Base):
    """Jurisdiction metadata model."""
    __tablename__ = "jurisdictions"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"))
    code: Mapped[str] = mapped_column(String(20), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    coverage_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    doc_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# LexRadar Models
# ============================================================================

class Invention(Base):
    """Invention candidate model."""
    __tablename__ = "invention_candidates"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"))
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    inventors: Mapped[Optional[List[dict]]] = mapped_column(JSON, nullable=True)
    source: Mapped[str] = mapped_column(String(50))
    source_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bam_compound: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    signal_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    novelty_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    nonobviousness_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    enablement_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    written_description_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    definiteness_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    utility_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    composite_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50))
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    disclosed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    filed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


class PriorArt(Base):
    """Prior art model."""
    __tablename__ = "prior_art"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    invention_id: Mapped[UUID] = mapped_column(ForeignKey("invention_candidates.id"))
    source: Mapped[str] = mapped_column(String(50))
    external_id: Mapped[str] = mapped_column(String(255))
    patent_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    inventors: Mapped[Optional[List[dict]]] = mapped_column(JSON, nullable=True)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    filing_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    publication_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    claims: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    jurisdiction: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    relevance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bam_compound: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    embedding: Mapped[Optional[List[float]]] = mapped_column(LargeBinary, nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class Disclosure(Base):
    """Disclosure draft model."""
    __tablename__ = "disclosures"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    invention_id: Mapped[UUID] = mapped_column(ForeignKey("invention_candidates.id"))
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"))
    disclosure_type: Mapped[str] = mapped_column(String(50))
    sections: Mapped[dict] = mapped_column(JSON)
    claim_themes: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    grounding_score: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(50))
    attorney_feedback: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    attorney_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)
    drafted_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


class FilingBundle(Base):
    """Filing bundle model."""
    __tablename__ = "filing_bundles"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    disclosure_draft_id: Mapped[UUID] = mapped_column(ForeignKey("disclosures.id"))
    invention_id: Mapped[UUID] = mapped_column(ForeignKey("invention_candidates.id"))
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"))
    documents: Mapped[List[dict]] = mapped_column(JSON)
    bundle_format: Mapped[str] = mapped_column(String(50))
    bundle_path: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(50))
    packaged_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    downloaded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class ProofLedger(Base):
    """Blockchain proof ledger model."""
    __tablename__ = "blockchain_anchors"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"))
    invention_id: Mapped[UUID] = mapped_column(ForeignKey("invention_candidates.id"))
    filing_bundle_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("filing_bundles.id"), nullable=True)
    document_hash: Mapped[str] = mapped_column(String(64))
    bundle_hash: Mapped[str] = mapped_column(String(64))
    polygon_tx_hash: Mapped[str] = mapped_column(String(66))
    polygon_tx_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    polygon_block_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    encryption_key_id: Mapped[str] = mapped_column(String(255))
    encryption_algorithm: Mapped[str] = mapped_column(String(50))
    proof_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    anchored_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class AttorneyReview(Base):
    """Attorney review model."""
    __tablename__ = "attorney_reviews"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    disclosure_draft_id: Mapped[UUID] = mapped_column(ForeignKey("disclosures.id"))
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"))
    attorney_name: Mapped[str] = mapped_column(String(255))
    attorney_email: Mapped[str] = mapped_column(String(255))
    review_status: Mapped[str] = mapped_column(String(50))
    review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    requested_changes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    review_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    review_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
