"""API request/response schemas for LexCore + LexRadar.

Generated from API_SPEC.md (Hash: 0fe4a24fc0d1f3cbcedca4d549e033ac1048aa10bdf5c401219fb3ad649f0037)
Schema Version: v0.1.0-foundation
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================================================
# MCP Tool Schemas
# ============================================================================

class CapabilitiesResponse(BaseModel):
    """Response for get_capabilities MCP tool."""
    jurisdictions: Dict[str, Any]
    doc_types: List[str]
    tools: List[str]


class SearchLegalRequest(BaseModel):
    """Request for search_legal MCP tool."""
    query: str = Field(..., min_length=1, max_length=2000)
    jurisdiction: Optional[str] = Field(None, max_length=20)
    doc_type: Optional[str] = Field(None, max_length=50)
    limit: int = Field(50, ge=1, le=1000)


class SearchLegalResponse(BaseModel):
    """Response for search_legal MCP tool."""
    results: List[Dict[str, Any]]
    total: int
    latency_ms: float
    cache_hit: bool


class ResearchTaskRequest(BaseModel):
    """Request for research_task MCP tool."""
    question: str = Field(..., min_length=1, max_length=5000)
    jurisdiction: Optional[str] = Field(None, max_length=20)
    depth: int = Field(3, ge=1, le=5)


class ResearchTaskResponse(BaseModel):
    """Response for research_task MCP tool."""
    report: str
    citation_chain: List[Dict[str, Any]]
    confidence: float = Field(..., ge=0, le=1)
    gap_detected: bool


class DocumentResponse(BaseModel):
    """Response for get_document MCP tool and /documents/{id} route."""
    document: Dict[str, Any]
    chunks: List[Dict[str, Any]]
    citations: List[Dict[str, Any]]


class CitationGraphResponse(BaseModel):
    """Response for get_citations MCP tool."""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    authority_chain: List[str]
    overruled_cases: List[str]


class LegalUpdatesResponse(BaseModel):
    """Response for check_updates MCP tool."""
    updates: List[Dict[str, Any]]


class JurisdictionSummaryResponse(BaseModel):
    """Response for jurisdiction_summary MCP tool."""
    jurisdiction_code: str
    jurisdiction_name: str
    coverage_percent: float = Field(..., ge=0, le=1)
    doc_count: int
    recent_changes: List[Dict[str, Any]]


# ============================================================================
# LexRadar Schemas
# ============================================================================

class DisclosureRequest(BaseModel):
    """Request to generate a disclosure draft for an invention."""
    disclosure_type: str = Field(..., pattern=r"^(PROVISIONAL|NON_PROVISIONAL|PCT)$")
    sections: Dict[str, Any]
    claim_themes: Optional[List[str]] = None


class DisclosureResponse(BaseModel):
    """Response containing a generated disclosure draft."""
    id: UUID
    invention_id: UUID
    disclosure_type: str
    sections: Dict[str, Any]
    claim_themes: List[str]
    grounding_score: float = Field(..., ge=0, le=1)
    status: str


class FilingBundleResponse(BaseModel):
    """Response containing a packaged filing bundle."""
    id: UUID
    disclosure_draft_id: UUID
    documents: List[Dict[str, Any]]
    bundle_path: str
    bundle_format: str
    status: str


class LedgerProofResponse(BaseModel):
    """Response containing a ledger proof for a filing bundle."""
    id: UUID
    document_hash: str
    bundle_hash: str
    polygon_tx_hash: str
    polygon_block_number: str
    anchored_at: datetime
