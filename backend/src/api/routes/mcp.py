"""MCP (Model Context Protocol) Tool Routes.

7 MCP Tools:
1. get_capabilities — Returns jurisdiction + doc type manifest
2. search_legal — Hybrid search (pgvector + full-text)
3. research_task — Complex research with question decomposition
4. get_document — Retrieve full document with chunks and citations
5. get_citations — Citation graph retrieval
6. check_updates — Legislative changes since date
7. jurisdiction_summary — Coverage %, doc count, recent changes
"""

from typing import Optional
from datetime import date

from fastapi import APIRouter, Query, HTTPException, status, Depends
from pydantic import BaseModel, Field

from src.api.schemas import (
    CapabilitiesResponse,
    SearchLegalRequest,
    SearchLegalResponse,
    ResearchTaskRequest,
    ResearchTaskResponse,
    DocumentResponse,
    CitationGraphResponse,
    LegalUpdatesResponse,
    JurisdictionSummaryResponse,
)
from src.api.middleware.jwt_auth import get_current_tenant
from src.api.services.mcp_service import MCPService

router = APIRouter()

mcp_service = MCPService()


@router.get("/get_capabilities", response_model=CapabilitiesResponse)
async def get_capabilities(
    tenant: dict = Depends(get_current_tenant),
) -> CapabilitiesResponse:
    """Get system capabilities — full jurisdiction + doc type manifest.
    
    Returns all supported jurisdictions, document types, tools, and BAM tiers.
    """
    return await mcp_service.get_capabilities(tenant_id=tenant["tenant_id"])


@router.post("/search_legal", response_model=SearchLegalResponse)
async def search_legal(
    request: SearchLegalRequest,
    tenant: dict = Depends(get_current_tenant),
) -> SearchLegalResponse:
    """Search legal documents — hybrid pgvector + full-text search with BAM routing.
    
    Combines vector similarity search (HNSW index) with full-text search (GIN index)
    for optimal legal document retrieval.
    """
    return await mcp_service.search_legal(
        query=request.query,
        jurisdiction=request.jurisdiction,
        doc_type=request.doc_type,
        limit=request.limit,
        tenant_id=tenant["tenant_id"],
    )


@router.post("/research_task", response_model=ResearchTaskResponse)
async def research_task(
    request: ResearchTaskRequest,
    tenant: dict = Depends(get_current_tenant),
) -> ResearchTaskResponse:
    """Execute research task — complex research with question decomposition.
    
    Breaks down complex questions into sub-questions, runs parallel searches,
    and synthesizes a structured report with citation chain.
    """
    return await mcp_service.research_task(
        question=request.question,
        jurisdiction=request.jurisdiction,
        tenant_id=tenant["tenant_id"],
    )


@router.get("/get_document", response_model=DocumentResponse)
async def get_document(
    doc_id: Optional[str] = Query(None, description="Document UUID"),
    citation: Optional[str] = Query(None, description="Document citation"),
    tenant: dict = Depends(get_current_tenant),
) -> DocumentResponse:
    """Get document by ID or citation — retrieve full document with chunks and citations.
    
    Returns the complete document including all chunks, citation graph,
    and metadata. Requires either doc_id or citation parameter.
    """
    if not doc_id and not citation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either doc_id or citation must be provided",
        )
    
    return await mcp_service.get_document(
        doc_id=doc_id,
        citation=citation,
        tenant_id=tenant["tenant_id"],
    )


@router.get("/get_citations", response_model=CitationGraphResponse)
async def get_citations(
    doc_id: str = Query(..., description="Document UUID"),
    direction: str = Query("both", pattern=r"^(forward|backward|both)$"),
    depth: int = Query(3, ge=1, le=5),
    tenant: dict = Depends(get_current_tenant),
) -> CitationGraphResponse:
    """Get citation graph — retrieve citation graph up to specified depth.
    
    Traverses the legal_citations table to build a citation graph
    from the specified document, following forward (cited by),
    backward (cites), or both directions.
    """
    return await mcp_service.get_citations(
        doc_id=doc_id,
        direction=direction,
        depth=depth,
        tenant_id=tenant["tenant_id"],
    )


@router.get("/check_updates", response_model=LegalUpdatesResponse)
async def check_updates(
    jurisdiction: str = Query(..., description="Jurisdiction code"),
    since_date: date = Query(..., description="Date to check changes since"),
    tenant: dict = Depends(get_current_tenant),
) -> LegalUpdatesResponse:
    """Check for legal updates — all legislative changes since specified date.
    
    Queries the legal_updates table for changes detected by the
    monitor system since the given date for the specified jurisdiction.
    """
    return await mcp_service.check_updates(
        jurisdiction=jurisdiction,
        since_date=since_date,
        tenant_id=tenant["tenant_id"],
    )


@router.get("/jurisdiction_summary", response_model=JurisdictionSummaryResponse)
async def jurisdiction_summary(
    jurisdiction_code: str = Query(..., description="Jurisdiction code"),
    tenant: dict = Depends(get_current_tenant),
) -> JurisdictionSummaryResponse:
    """Get jurisdiction summary — coverage %, doc count, recent changes.
    
    Aggregates statistics from legal_documents and legal_updates tables
    for the specified jurisdiction.
    """
    return await mcp_service.jurisdiction_summary(
        jurisdiction_code=jurisdiction_code,
        tenant_id=tenant["tenant_id"],
    )
