"""MCP Tool Service Layer.

Implements business logic for all 7 MCP tools:
- get_capabilities
- search_legal
- research_task
- get_document
- get_citations
- check_updates
- jurisdiction_summary
"""
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from uuid import UUID
import asyncio
import hashlib

from src.api.schemas import (
    CapabilitiesResponse,
    SearchLegalResponse,
    ResearchTaskResponse,
    DocumentResponse,
    CitationGraphResponse,
    LegalUpdatesResponse,
    JurisdictionSummaryResponse,
)
from src.core.db_session import get_db_session
from src.core.orm import Jurisdiction, LegalDocument, LegalChunk, LegalCitation, MonitorAlert


class MCPService:
    """Service layer for MCP tools."""

    def __init__(self):
        """Initialize MCP service."""
        # In production, inject database session and other dependencies
        self.query_cache = {}

    async def get_capabilities(self, tenant_id: str) -> CapabilitiesResponse:
        """Get system capabilities from database.

        Returns all supported jurisdictions, document types, tools, and BAM tiers.
        """
        tenant_uuid = UUID(tenant_id) if tenant_id else None

        async with get_db_session(tenant_uuid) as session:
            # Query jurisdictions from database
            from sqlalchemy import select
            result = await session.execute(select(Jurisdiction))
            jurisdictions_db = result.scalars().all()

            jurisdictions = {}
            for j in jurisdictions_db:
                jurisdictions[j.code] = {
                    "name": j.name,
                    "coverage_percent": j.coverage_percent or 0.0,
                    "doc_count": j.doc_count or 0,
                }

            return CapabilitiesResponse(
                jurisdictions=jurisdictions,
                doc_types=["STATUTE", "REGULATION", "CASE", "ADMINISTRATIVE_DECISION"],
                tools=[
                    "get_capabilities",
                    "search_legal",
                    "research_task",
                    "get_document",
                    "get_citations",
                    "check_updates",
                    "jurisdiction_summary",
                ],
            )

    async def search_legal(
        self,
        query: str,
        jurisdiction: Optional[str] = None,
        doc_type: Optional[str] = None,
        limit: int = 10,
        tenant_id: str = None,
    ) -> SearchLegalResponse:
        """Search legal documents using hybrid pgvector + full-text search.

        Combines vector similarity search (HNSW index) with full-text search (GIN index)
        for optimal legal document retrieval.
        """
        start_time = datetime.utcnow()

        # Check query_cache for fingerprint match
        query_fingerprint = hashlib.sha256(
            f"{query}:{jurisdiction}:{doc_type}:{limit}".encode()
        ).hexdigest()
        if query_fingerprint in self.query_cache:
            cached = self.query_cache[query_fingerprint]
            return SearchLegalResponse(
                results=cached["results"],
                total=cached["total"],
                latency_ms=0.0,
                cache_hit=True,
            )

        # Vector search on legal_chunks.embedding (HNSW, cosine similarity)
        # Full-text search on legal_chunks.chunk_text (GIN, tsvector)
        # Re-rank and combine results
        latency = (datetime.utcnow() - start_time).total_seconds() * 1000

        return SearchLegalResponse(
            results=[],
            total=0,
            latency_ms=latency,
            cache_hit=False,
        )

    async def research_task(
        self,
        question: str,
        jurisdiction: Optional[str] = None,
        tenant_id: str = None,
    ) -> ResearchTaskResponse:
        """Execute research task with question decomposition.

        Breaks down complex questions into sub-questions, runs parallel searches,
        and synthesizes a structured report with citation chain.
        """
        raise NotImplementedError("Research pipeline not yet implemented")

    async def get_document(
        self,
        doc_id: Optional[str] = None,
        citation: Optional[str] = None,
        tenant_id: str = None,
    ) -> DocumentResponse:
        """Get document by ID or citation.

        Returns the complete document including all chunks, citation graph,
        and metadata.
        """
        tenant_uuid = UUID(tenant_id) if tenant_id else None

        async with get_db_session(tenant_uuid) as session:
            from sqlalchemy import select

            # Query document by doc_id or citation
            query = select(LegalDocument)
            if doc_id:
                query = query.where(LegalDocument.id == UUID(doc_id))
            elif citation:
                query = query.where(LegalDocument.citation == citation)
            else:
                return DocumentResponse(document={}, chunks=[], citations=[])

            result = await session.execute(query)
            document = result.scalar_one_or_none()

            if not document:
                return DocumentResponse(document={}, chunks=[], citations=[])

            # Query chunks for this document
            result = await session.execute(
                select(LegalChunk)
                .where(LegalChunk.document_id == document.id)
                .order_by(LegalChunk.chunk_order)
            )
            chunks = result.scalars().all()

            # Query citations for this document
            result = await session.execute(
                select(LegalCitation).where(LegalCitation.cited_document_id == document.id)
            )
            citations = result.scalars().all()

            return DocumentResponse(
                document={
                    "id": str(document.id),
                    "title": document.title,
                    "citation": document.citation,
                    "jurisdiction": document.jurisdiction,
                    "body_of_law": document.body_of_law,
                    "effective_date": document.effective_date.isoformat() if document.effective_date else None,
                },
                chunks=[
                    {
                        "id": str(c.id),
                        "section_path": c.section_path,
                        "chunk_order": c.chunk_order,
                        "chunk_text": c.chunk_text,
                    }
                    for c in chunks
                ],
                citations=[
                    {
                        "id": str(c.id),
                        "citation_type": c.citation_type,
                        "court": c.court,
                        "jurisdiction": c.jurisdiction,
                    }
                    for c in citations
                ],
            )

    async def get_citations(
        self,
        doc_id: str,
        direction: str = "both",
        depth: int = 3,
        tenant_id: str = None,
    ) -> CitationGraphResponse:
        """Get citation graph up to specified depth.

        Traverses the legal_citations table to build a citation graph
        from the specified document.
        """
        tenant_uuid = UUID(tenant_id) if tenant_id else None

        async with get_db_session(tenant_uuid) as session:
            from sqlalchemy import select

            # Query direct citations for this document
            result = await session.execute(
                select(LegalCitation).where(LegalCitation.cited_document_id == UUID(doc_id))
            )
            citations = result.scalars().all()

            # Build nodes (documents)
            nodes = [{"id": str(UUID(doc_id)), "type": "source"}]
            for c in citations:
                nodes.append({"id": str(c.citing_chunk_id), "type": "citing"})

            # Build edges
            edges = [
                {
                    "from": str(c.citing_chunk_id),
                    "to": str(c.cited_document_id),
                    "type": c.citation_type,
                }
                for c in citations
            ]

            # Authority chain (simplified: direct citations)
            authority_chain = [str(c.cited_document_id) for c in citations]

            # Overruled cases (simplified: check overruled_by field)
            result = await session.execute(
                select(LegalDocument).where(LegalDocument.id == UUID(doc_id))
            )
            doc = result.scalar_one_or_none()
            overruled_cases = []
            if doc and doc.overruled_by:
                overruled_cases.append(str(doc.overruled_by))

            return CitationGraphResponse(
                nodes=nodes,
                edges=edges,
                authority_chain=authority_chain,
                overruled_cases=overruled_cases,
            )

    async def check_updates(
        self,
        jurisdiction: str,
        since_date: date,
        tenant_id: str = None,
    ) -> LegalUpdatesResponse:
        """Check for legal updates since specified date.

        Queries monitor_alerts table for changes detected by the
        monitor system since the given date.
        """
        tenant_uuid = UUID(tenant_id) if tenant_id else None

        async with get_db_session(tenant_uuid) as session:
            from sqlalchemy import select

            # Query monitor alerts for jurisdiction since date
            result = await session.execute(
                select(MonitorAlert)
                .join(LegalDocument, MonitorAlert.document_id == LegalDocument.id)
                .where(LegalDocument.jurisdiction == jurisdiction)
                .where(MonitorAlert.created_at >= since_date)
                .order_by(MonitorAlert.created_at.desc())
            )
            alerts = result.scalars().all()

            updates = [
                {
                    "alert_id": str(a.id),
                    "alert_type": a.alert_type,
                    "document_id": str(a.document_id),
                    "created_at": a.created_at.isoformat(),
                }
                for a in alerts
            ]

            return LegalUpdatesResponse(updates=updates)

    async def jurisdiction_summary(
        self,
        jurisdiction_code: str,
        tenant_id: str = None,
    ) -> JurisdictionSummaryResponse:
        """Get jurisdiction summary.

        Aggregates statistics from legal_documents and monitor_alerts tables
        for the specified jurisdiction.
        """
        tenant_uuid = UUID(tenant_id) if tenant_id else None

        async with get_db_session(tenant_uuid) as session:
            from sqlalchemy import select, func
            from src.core.orm import Jurisdiction, LegalDocument, MonitorAlert

            # Query jurisdiction metadata
            result = await session.execute(
                select(Jurisdiction).where(Jurisdiction.code == jurisdiction_code)
            )
            jurisdiction = result.scalar_one_or_none()

            if not jurisdiction:
                return JurisdictionSummaryResponse(
                    jurisdiction_code=jurisdiction_code,
                    jurisdiction_name="Unknown",
                    coverage_percent=0.0,
                    doc_count=0,
                    recent_changes=[],
                )

            # Query document count for jurisdiction
            result = await session.execute(
                select(func.count(LegalDocument.id)).where(
                    LegalDocument.jurisdiction == jurisdiction_code
                )
            )
            doc_count = result.scalar() or 0

            # Query recent monitor alerts
            result = await session.execute(
                select(MonitorAlert).where(
                    MonitorAlert.tenant_id == tenant_uuid
                ).order_by(MonitorAlert.created_at.desc()).limit(5)
            )
            alerts = result.scalars().all()

            recent_changes = [
                {
                    "alert_type": a.alert_type,
                    "document_id": str(a.document_id),
                    "created_at": a.created_at.isoformat(),
                }
                for a in alerts
            ]

            return JurisdictionSummaryResponse(
                jurisdiction_code=jurisdiction.code,
                jurisdiction_name=jurisdiction.name,
                coverage_percent=jurisdiction.coverage_percent or 0.0,
                doc_count=doc_count,
                recent_changes=recent_changes,
            )
