"""Pydantic models for LexCore + LexRadar API.

Generated from ERD_COMPLETE.dbml (Hash: 055cf61aecaf01e89b4b745adf1d8e06cbc47b28ee98a62fbdbdc2f128393027)
Schema Version: v0.1.0-foundation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Base Models
# ============================================================================

class TenantBase(BaseModel):
    """Base model for tenant data."""
    name: str = Field(..., max_length=255)
    tier: str = Field(..., pattern=r"^(SOLO|FIRM|ENTERPRISE)$")
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None


class TenantCreate(TenantBase):
    """Model for creating a new tenant."""
    pass


class Tenant(TenantBase):
    """Full tenant model with database fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    updated_at: datetime


# ============================================================================
# LexCore Models
# ============================================================================

class LegalDocumentBase(BaseModel):
    """Base model for legal document data."""
    title: str = Field(..., max_length=500)
    title_fr: Optional[str] = Field(None, max_length=500)
    citation: str = Field(..., max_length=255)
    body_of_law: str = Field(..., pattern=r"^(STATUTE|REGULATION|CASE)$")
    jurisdiction: str = Field(..., max_length=20)
    doc_type: Optional[str] = Field(None, max_length=50)
    full_text: Optional[str] = None
    effective_date: Optional[datetime] = None
    data_quality_score: Optional[float] = Field(None, ge=0, le=1)
    source: str = Field(..., max_length=100)
    is_repealed: bool = False
    bam_compound: Optional[Dict[str, Any]] = None


class LegalDocumentCreate(LegalDocumentBase):
    """Model for creating a new legal document."""
    tenant_id: UUID
    overruled_by: Optional[UUID] = None


class LegalDocument(LegalDocumentBase):
    """Full legal document model with database fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    tenant_id: UUID
    overruled_by: Optional[UUID] = None
    retrieved_at: datetime
    created_at: datetime
    updated_at: datetime


class LegalChunkBase(BaseModel):
    """Base model for legal chunk data."""
    section_path: Optional[str] = Field(None, max_length=500)
    chunk_order: Optional[int] = None
    chunk_text: str
    token_count: Optional[int] = None
    chunk_quality_score: Optional[float] = Field(None, ge=0, le=1)
    bam_signal: Optional[Dict[str, Any]] = None


class LegalChunkCreate(LegalChunkBase):
    """Model for creating a new legal chunk."""
    document_id: UUID
    tenant_id: UUID


class LegalChunk(LegalChunkBase):
    """Full legal chunk model with database fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    document_id: UUID
    tenant_id: UUID
    embedding: Optional[List[float]] = None  # 1536-dimensional vector
    created_at: datetime
    updated_at: datetime


class LegalCitationBase(BaseModel):
    """Base model for legal citation data."""
    citation_type: str = Field(..., pattern=r"^(DIRECT|IMPLIED|OVERRULING)$")
    court: Optional[str] = Field(None, max_length=255)
    jurisdiction: Optional[str] = Field(None, max_length=20)
    decision_date: Optional[datetime] = None
    citation_metadata: Optional[Dict[str, Any]] = None


class LegalCitationCreate(LegalCitationBase):
    """Model for creating a new legal citation."""
    citing_chunk_id: UUID
    cited_document_id: UUID


class LegalCitation(LegalCitationBase):
    """Full legal citation model with database fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    citing_chunk_id: UUID
    cited_document_id: UUID
    created_at: datetime


class AgentQueryBase(BaseModel):
    """Base model for agent query data."""
    agent_id: str = Field(..., max_length=50)
    bam_compound: Dict[str, Any]
    query_text: Optional[str] = None
    query_normalized: Optional[str] = None
    query_fingerprint: Optional[str] = Field(None, max_length=64)
    result_count: Optional[int] = None
    cache_hit: Optional[int] = Field(None, ge=0, le=1)
    latency_ms: Optional[float] = None
    query_params: Optional[Dict[str, Any]] = None


class AgentQueryCreate(AgentQueryBase):
    """Model for creating a new agent query."""
    tenant_id: UUID


class AgentQuery(AgentQueryBase):
    """Full agent query model with database fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    tenant_id: UUID
    created_at: datetime


class MonitorRuleBase(BaseModel):
    """Base model for monitor rule data."""
    jurisdiction: str = Field(..., max_length=20)
    body_of_law: str = Field(..., max_length=50)
    alert_type: str = Field(..., pattern=r"^(CHANGE|REPEAL|NEW)$")
    criteria: Optional[Dict[str, Any]] = None
    is_active: bool = True


class MonitorRuleCreate(MonitorRuleBase):
    """Model for creating a new monitor rule."""
    tenant_id: UUID


class MonitorRule(MonitorRuleBase):
    """Full monitor rule model with database fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    tenant_id: UUID
    last_checked: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ============================================================================
# LexRadar Models
# ============================================================================

class InventionBase(BaseModel):
    """Base model for invention data."""
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    inventors: Optional[List[Dict[str, Any]]] = None
    source: str = Field(..., pattern=r"^(GitHub|Jira|Notion|Manual)$")
    source_id: Optional[str] = Field(None, max_length=255)
    bam_compound: Optional[Dict[str, Any]] = None
    signal_type: Optional[str] = Field(None, max_length=50)
    novelty_score: Optional[float] = Field(None, ge=0, le=1)
    nonobviousness_score: Optional[float] = Field(None, ge=0, le=1)
    enablement_score: Optional[float] = Field(None, ge=0, le=1)
    written_description_score: Optional[float] = Field(None, ge=0, le=1)
    definiteness_score: Optional[float] = Field(None, ge=0, le=1)
    utility_score: Optional[float] = Field(None, ge=0, le=1)
    composite_score: Optional[float] = Field(None, ge=0, le=1)
    status: str = Field(..., pattern=r"^(DETECTED|SCORING|DISCLOSED|FILED)$")
    metadata: Optional[Dict[str, Any]] = None


class InventionCreate(InventionBase):
    """Model for creating a new invention."""
    tenant_id: UUID


class Invention(InventionBase):
    """Full invention model with database fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    tenant_id: UUID
    detected_at: datetime
    disclosed_at: Optional[datetime] = None
    filed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class PriorArtBase(BaseModel):
    """Base model for prior art data."""
    source: str = Field(..., pattern=r"^(USPTO|WIPO|EPO|Lens|Google Patents|PatentScope|IP\.com)$")
    external_id: str = Field(..., max_length=255)
    patent_number: Optional[str] = Field(None, max_length=100)
    title: Optional[str] = Field(None, max_length=500)
    inventors: Optional[List[Dict[str, Any]]] = None
    abstract: Optional[str] = None
    description: Optional[str] = None
    filing_date: Optional[datetime] = None
    publication_date: Optional[datetime] = None
    claims: Optional[Dict[str, Any]] = None
    jurisdiction: Optional[str] = Field(None, max_length=20)
    relevance_score: Optional[float] = Field(None, ge=0, le=1)
    bam_compound: Optional[Dict[str, Any]] = None


class PriorArtCreate(PriorArtBase):
    """Model for creating a new prior art record."""
    invention_id: UUID


class PriorArt(PriorArtBase):
    """Full prior art model with database fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    invention_id: UUID
    embedding: Optional[List[float]] = None
    retrieved_at: datetime
    created_at: datetime


class PatentScoreBase(BaseModel):
    """Base model for patent score data."""
    novelty_score: Optional[float] = Field(None, ge=0, le=1)
    nonobviousness_score: Optional[float] = Field(None, ge=0, le=1)
    enablement_score: Optional[float] = Field(None, ge=0, le=1)
    written_description_score: Optional[float] = Field(None, ge=0, le=1)
    definiteness_score: Optional[float] = Field(None, ge=0, le=1)
    utility_score: Optional[float] = Field(None, ge=0, le=1)
    composite_score: Optional[float] = Field(None, ge=0, le=1)
    score_explanation: Optional[str] = None


class PatentScoreCreate(PatentScoreBase):
    """Model for creating a new patent score."""
    invention_id: UUID
    prior_art_id: Optional[UUID] = None


class PatentScore(PatentScoreBase):
    """Full patent score model with database fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    invention_id: UUID
    prior_art_id: Optional[UUID] = None
    scored_at: datetime
    created_at: datetime


class DisclosureDraftBase(BaseModel):
    """Base model for disclosure draft data."""
    disclosure_type: str = Field(..., pattern=r"^(PROVISIONAL|NON_PROVISIONAL|PCT)$")
    sections: Dict[str, Any]
    claim_themes: Optional[List[str]] = None
    grounding_score: float = Field(..., ge=0, le=1)
    status: str = Field(..., pattern=r"^(DRAFT|REVIEW|APPROVED)$")
    attorney_feedback: Optional[Dict[str, Any]] = None
    attorney_id: Optional[UUID] = None


class DisclosureDraftCreate(DisclosureDraftBase):
    """Model for creating a new disclosure draft."""
    invention_id: UUID
    tenant_id: UUID


class DisclosureDraft(DisclosureDraftBase):
    """Full disclosure draft model with database fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    invention_id: UUID
    tenant_id: UUID
    drafted_at: datetime
    reviewed_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class FilingBundleBase(BaseModel):
    """Base model for filing bundle data."""
    documents: List[Dict[str, Any]]
    bundle_format: str = Field(..., pattern=r"^(PDF|ZIP)$")
    bundle_path: str = Field(..., max_length=500)
    status: str = Field(..., pattern=r"^(PACKAGED|DOWNLOADED|SUBMITTED)$")


class FilingBundleCreate(FilingBundleBase):
    """Model for creating a new filing bundle."""
    disclosure_draft_id: UUID
    invention_id: UUID
    tenant_id: UUID


class FilingBundle(FilingBundleBase):
    """Full filing bundle model with database fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    disclosure_draft_id: UUID
    invention_id: UUID
    tenant_id: UUID
    packaged_at: datetime
    downloaded_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    created_at: datetime


class ProofLedgerBase(BaseModel):
    """Base model for proof ledger data."""
    document_hash: str = Field(..., max_length=64)
    bundle_hash: str = Field(..., max_length=64)
    polygon_tx_hash: str = Field(..., max_length=66)
    polygon_tx_timestamp: Optional[datetime] = None
    polygon_block_number: Optional[str] = Field(None, max_length=50)
    encryption_key_id: str = Field(..., max_length=255)
    encryption_algorithm: str = Field(default="AES-256", max_length=50)
    proof_metadata: Optional[Dict[str, Any]] = None


class ProofLedgerCreate(ProofLedgerBase):
    """Model for creating a new proof ledger entry."""
    tenant_id: UUID
    invention_id: UUID
    filing_bundle_id: Optional[UUID] = None


class ProofLedger(ProofLedgerBase):
    """Full proof ledger model with database fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    tenant_id: UUID
    invention_id: UUID
    filing_bundle_id: Optional[UUID] = None
    anchored_at: datetime
    created_at: datetime


class AttorneyReviewBase(BaseModel):
    """Base model for attorney review data."""
    attorney_name: str = Field(..., max_length=255)
    attorney_email: str = Field(..., max_length=255)
    review_status: str = Field(..., pattern=r"^(PENDING|IN_PROGRESS|APPROVED|REJECTED)$")
    review_notes: Optional[str] = None
    requested_changes: Optional[Dict[str, Any]] = None


class AttorneyReviewCreate(AttorneyReviewBase):
    """Model for creating a new attorney review."""
    disclosure_draft_id: UUID
    tenant_id: UUID


class AttorneyReview(AttorneyReviewBase):
    """Full attorney review model with database fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    disclosure_draft_id: UUID
    tenant_id: UUID
    review_started_at: Optional[datetime] = None
    review_completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
