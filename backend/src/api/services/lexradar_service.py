"""LexRadar IP Detection Service Layer.

Business logic for LexRadar intellectual property detection:
- Invention management
- Prior art search
- Disclosure generation
- Filing bundle packaging
- Ledger proof anchoring
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from src.api.models import InventionCreate, Invention
from src.api.schemas import (
    DisclosureRequest,
    DisclosureResponse,
    FilingBundleResponse,
    LedgerProofResponse,
)
from src.core.db_session import get_db_session
from src.core.orm import Invention, ProofLedger


class LexRadarService:
    """Service layer for LexRadar operations."""

    def __init__(self):
        """Initialize LexRadar service."""
        pass

    async def list_inventions(
        self,
        tenant_id: str,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """List inventions with optional status filter.

        Queries the inventions table filtered by tenant and status.
        """
        tenant_uuid = UUID(tenant_id) if tenant_id else None

        async with get_db_session(tenant_uuid) as session:
            from sqlalchemy import select, func

            # Build base query
            query = select(Invention)

            # Apply status filter
            if status:
                query = query.where(Invention.status == status)

            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await session.execute(count_query)
            total = total_result.scalar() or 0

            # Apply limit
            query = query.limit(limit)

            # Execute query
            result = await session.execute(query)
            inventions = result.scalars().all()

            return {
                "inventions": [
                    {
                        "id": str(i.id),
                        "title": i.title,
                        "description": i.description,
                        "status": i.status,
                        "composite_score": i.composite_score,
                        "detected_at": i.detected_at.isoformat() if i.detected_at else None,
                    }
                    for i in inventions
                ],
                "total": total,
            }

    async def create_invention(
        self,
        tenant_id: str,
        invention: InventionCreate,
    ) -> Invention:
        """Create a new invention record.

        Inserts a new invention into the inventions table.
        """
        tenant_uuid = UUID(tenant_id) if tenant_id else None

        async with get_db_session(tenant_uuid) as session:
            from uuid import uuid4

            try:
                # Create ORM instance
                new_invention = Invention(
                    id=uuid4(),
                    tenant_id=tenant_uuid,
                    title=invention.title,
                    description=invention.description,
                    inventors=invention.inventors,
                    source=invention.source,
                    source_id=invention.source_id,
                    bam_compound=invention.bam_compound,
                    signal_type=invention.signal_type,
                    novelty_score=invention.novelty_score,
                    nonobviousness_score=invention.nonobviousness_score,
                    enablement_score=invention.enablement_score,
                    written_description_score=invention.written_description_score,
                    definiteness_score=invention.definiteness_score,
                    utility_score=invention.utility_score,
                    composite_score=invention.composite_score,
                    status=invention.status,
                    metadata=invention.metadata,
                    detected_at=datetime.utcnow(),
                    disclosed_at=None,
                    filed_at=None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )

                session.add(new_invention)
                await session.commit()
                await session.refresh(new_invention)

                return new_invention
            except Exception:
                await session.rollback()
                raise

    async def search_prior_art(
        self,
        tenant_id: str,
        invention_id: UUID,
        sources: List[str],
        max_results: int = 50,
    ) -> Dict[str, Any]:
        """Search prior art for an invention across 7 sources.
        
        Parallel search across connectors: GitHub, USPTO, WIPO, EPO, PACER, SEC, State.
        """
        # TODO: Implement parallel prior art search via Celery workers
        # 1. Trigger search_prior_art Celery task for each source
        # 2. Aggregate results
        # 3. Rank by relevance
        return {
            "prior_art": [],
            "total_found": 0,
        }

    async def generate_disclosure(
        self,
        tenant_id: str,
        invention_id: UUID,
        request: DisclosureRequest,
    ) -> DisclosureResponse:
        """Generate a disclosure draft for an invention.
        
        Uses LLM to generate disclosure draft with grounding check.
        """
        # TODO: Implement disclosure generation
        # 1. Retrieve invention details
        # 2. Generate disclosure draft via LLM
        # 3. Grounding check against prior art
        # 4. Store in disclosure_drafts table
        return DisclosureResponse(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            invention_id=invention_id,
            disclosure_type=request.disclosure_type,
            sections={},
            claim_themes=[],
            grounding_score=0.0,
            status="DRAFT",
        )

    async def package_filing_bundle(
        self,
        tenant_id: str,
        invention_id: UUID,
    ) -> FilingBundleResponse:
        """Package a filing bundle with 9 documents.
        
        Assembles all required documents for patent filing.
        """
        # TODO: Implement bundle packaging
        # 1. Retrieve disclosure draft
        # 2. Generate 9 required documents
        # 3. Package into ZIP/PDF bundle
        # 4. Store bundle metadata
        return FilingBundleResponse(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            disclosure_draft_id=UUID("00000000-0000-0000-0000-000000000000"),
            documents=[],
            bundle_path="",
            bundle_format="PDF",
            status="PACKAGED",
        )

    async def get_ledger_proof(
        self,
        tenant_id: str,
        bundle_id: UUID,
    ) -> LedgerProofResponse:
        """Get ledger proof for a filing bundle.

        Retrieves the blockchain anchoring proof from blockchain_anchors table.
        """
        tenant_uuid = UUID(tenant_id) if tenant_id else None

        async with get_db_session(tenant_uuid) as session:
            from sqlalchemy import select

            # Query blockchain_anchors for this bundle_id
            result = await session.execute(
                select(ProofLedger).where(ProofLedger.filing_bundle_id == bundle_id)
            )
            proof = result.scalar_one_or_none()

            if not proof:
                return LedgerProofResponse(
                    id=bundle_id,
                    document_hash="",
                    bundle_hash="",
                    polygon_tx_hash="",
                    polygon_block_number="",
                    anchored_at=datetime.utcnow(),
                )

            return LedgerProofResponse(
                id=proof.id,
                document_hash=proof.document_hash,
                bundle_hash=proof.bundle_hash,
                polygon_tx_hash=proof.polygon_tx_hash,
                polygon_block_number=proof.polygon_block_number or "",
                anchored_at=proof.anchored_at,
            )
