"""LexRadar IP detection routes."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query, HTTPException, status, Depends

from src.api.models import InventionCreate, Invention
from src.api.schemas import (
    DisclosureRequest,
    DisclosureResponse,
    FilingBundleResponse,
    LedgerProofResponse,
)
from src.api.middleware.jwt_auth import get_current_tenant
from src.api.services.lexradar_service import LexRadarService

router = APIRouter()

lexradar_service = LexRadarService()


@router.get("/inventions")
async def list_inventions(
    status: Optional[str] = Query(None, pattern=r"^(DETECTED|SCORING|DISCLOSED|FILED)$"),
    limit: int = Query(50, ge=1, le=1000),
    tenant: dict = Depends(get_current_tenant),
):
    """List inventions with optional status filter."""
    return await lexradar_service.list_inventions(
        tenant_id=tenant["tenant_id"],
        status=status,
        limit=limit,
    )


@router.post("/inventions", response_model=Invention, status_code=status.HTTP_201_CREATED)
async def create_invention(
    invention: InventionCreate,
    tenant: dict = Depends(get_current_tenant),
) -> Invention:
    """Create a new invention record."""
    return await lexradar_service.create_invention(
        tenant_id=tenant["tenant_id"],
        invention=invention,
    )


@router.post("/inventions/{id}/prior-art")
async def search_prior_art(
    id: UUID,
    sources: list[str] = Query(...),
    max_results: int = Query(50, ge=1, le=500),
    tenant: dict = Depends(get_current_tenant),
):
    """Search prior art for an invention across 7 sources."""
    return await lexradar_service.search_prior_art(
        tenant_id=tenant["tenant_id"],
        invention_id=id,
        sources=sources,
        max_results=max_results,
    )


@router.post("/inventions/{id}/disclosure", response_model=DisclosureResponse, status_code=status.HTTP_201_CREATED)
async def generate_disclosure(
    id: UUID,
    request: DisclosureRequest,
    tenant: dict = Depends(get_current_tenant),
) -> DisclosureResponse:
    """Generate a disclosure draft for an invention."""
    return await lexradar_service.generate_disclosure(
        tenant_id=tenant["tenant_id"],
        invention_id=id,
        request=request,
    )


@router.post("/inventions/{id}/filing-bundle", response_model=FilingBundleResponse, status_code=status.HTTP_201_CREATED)
async def package_filing_bundle(
    id: UUID,
    tenant: dict = Depends(get_current_tenant),
) -> FilingBundleResponse:
    """Package a filing bundle with 9 documents."""
    return await lexradar_service.package_filing_bundle(
        tenant_id=tenant["tenant_id"],
        invention_id=id,
    )


@router.get("/ledger/{id}", response_model=LedgerProofResponse)
async def get_ledger_proof(
    id: UUID,
    tenant: dict = Depends(get_current_tenant),
) -> LedgerProofResponse:
    """Get ledger proof for a filing bundle."""
    return await lexradar_service.get_ledger_proof(
        tenant_id=tenant["tenant_id"],
        bundle_id=id,
    )
