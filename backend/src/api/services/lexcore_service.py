"""LexCore Service Layer.

Business logic for LexCore legal intelligence routes:
- Document listing and retrieval
- Chunk retrieval
- Monitor rule management
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from src.api.models import MonitorRuleCreate, MonitorRule
from src.api.schemas import DocumentResponse
from src.core.db_session import get_db_session
from src.core.orm import LegalDocument, LegalChunk, MonitorRule, LegalCitation


class LexCoreService:
    """Service layer for LexCore operations."""

    def __init__(self):
        """Initialize LexCore service."""
        # In production, inject database session
        self.documents_cache: Dict[str, Any] = {}
        self.monitor_rules: Dict[str, List[Dict]] = {}

    async def list_documents(
        self,
        tenant_id: str,
        jurisdiction: Optional[str] = None,
        body_of_law: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """List legal documents with optional filtering.

        Queries the legal_documents table filtered by tenant,
        jurisdiction, and body of law.
        """
        tenant_uuid = UUID(tenant_id) if tenant_id else None

        async with get_db_session(tenant_uuid) as session:
            from sqlalchemy import select, func

            # Build base query
            query = select(LegalDocument)

            # Apply filters
            if jurisdiction:
                query = query.where(LegalDocument.jurisdiction == jurisdiction)
            if body_of_law:
                query = query.where(LegalDocument.body_of_law == body_of_law)

            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await session.execute(count_query)
            total = total_result.scalar() or 0

            # Apply pagination
            query = query.limit(limit).offset(offset)

            # Execute query
            result = await session.execute(query)
            documents = result.scalars().all()

            return {
                "documents": [
                    {
                        "id": str(d.id),
                        "title": d.title,
                        "citation": d.citation,
                        "jurisdiction": d.jurisdiction,
                        "body_of_law": d.body_of_law,
                        "effective_date": d.effective_date.isoformat() if d.effective_date else None,
                    }
                    for d in documents
                ],
                "total": total,
                "limit": limit,
                "offset": offset,
            }

    async def get_document_by_id(
        self,
        tenant_id: str,
        doc_id: UUID,
    ) -> DocumentResponse:
        """Get a specific legal document by ID.

        Returns the complete document including all chunks and citation graph.
        """
        tenant_uuid = UUID(tenant_id) if tenant_id else None

        async with get_db_session(tenant_uuid) as session:
            from sqlalchemy import select

            # Query document by ID
            result = await session.execute(
                select(LegalDocument).where(LegalDocument.id == doc_id)
            )
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

    async def list_chunks(
        self,
        tenant_id: str,
        document_id: Optional[UUID] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """List document chunks with optional document filter.

        Queries the legal_chunks table filtered by tenant and document.
        """
        tenant_uuid = UUID(tenant_id) if tenant_id else None

        async with get_db_session(tenant_uuid) as session:
            from sqlalchemy import select, func

            # Build base query
            query = select(LegalChunk)

            # Apply document filter
            if document_id:
                query = query.where(LegalChunk.document_id == document_id)

            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await session.execute(count_query)
            total = total_result.scalar() or 0

            # Apply limit
            query = query.limit(limit)

            # Execute query
            result = await session.execute(query)
            chunks = result.scalars().all()

            return {
                "chunks": [
                    {
                        "id": str(c.id),
                        "document_id": str(c.document_id),
                        "section_path": c.section_path,
                        "chunk_order": c.chunk_order,
                        "chunk_text": c.chunk_text,
                    }
                    for c in chunks
                ],
                "total": total,
            }

    async def create_monitor_rule(
        self,
        tenant_id: str,
        rule: MonitorRuleCreate,
    ) -> MonitorRule:
        """Create a new monitor rule for legislative changes.

        Inserts a new monitor_rule record for the tenant.
        """
        tenant_uuid = UUID(tenant_id) if tenant_id else None

        async with get_db_session(tenant_uuid) as session:
            from sqlalchemy import select
            from uuid import uuid4

            # Check if MonitorRuleCreate has the correct fields from the Pydantic model
            # Create ORM instance
            new_rule = MonitorRule(
                id=uuid4(),
                tenant_id=tenant_uuid,
                jurisdiction=rule.jurisdiction,
                body_of_law=rule.body_of_law,
                alert_type=rule.alert_type,
                criteria=rule.criteria,
                is_active=rule.is_active,
                last_checked=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            session.add(new_rule)
            await session.commit()
            await session.refresh(new_rule)

            return new_rule

    async def delete_monitor_rule(
        self,
        tenant_id: str,
        rule_id: UUID,
    ) -> None:
        """Delete a monitor rule.

        Removes the monitor rule from the database. RLS ensures
        only the tenant's own rules can be deleted.
        """
        tenant_uuid = UUID(tenant_id) if tenant_id else None

        async with get_db_session(tenant_uuid) as session:
            from sqlalchemy import select, delete

            # Query the rule first to ensure it exists
            result = await session.execute(
                select(MonitorRule).where(MonitorRule.id == rule_id)
            )
            rule = result.scalar_one_or_none()

            if not rule:
                return

            # Delete the rule (RLS will enforce tenant isolation)
            await session.execute(
                delete(MonitorRule).where(MonitorRule.id == rule_id)
            )
            await session.commit()
