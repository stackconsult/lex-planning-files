"""LexCore legal intelligence routes."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query, HTTPException, status, Depends

from src.api.models import MonitorRuleCreate, MonitorRule
from src.api.schemas import DocumentResponse
from src.api.middleware.jwt_auth import get_current_tenant
from src.api.services.lexcore_service import LexCoreService

router = APIRouter()

lexcore_service = LexCoreService()


@router.get("/documents")
async def list_documents(
    jurisdiction: Optional[str] = Query(None),
    body_of_law: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    tenant: dict = Depends(get_current_tenant),
):
    """List legal documents with optional filtering."""
    return await lexcore_service.list_documents(
        tenant_id=tenant["tenant_id"],
        jurisdiction=jurisdiction,
        body_of_law=body_of_law,
        limit=limit,
        offset=offset,
    )


@router.get("/documents/{id}", response_model=DocumentResponse)
async def get_document_by_id(
    id: UUID,
    tenant: dict = Depends(get_current_tenant),
) -> DocumentResponse:
    """Get a specific legal document by ID."""
    return await lexcore_service.get_document_by_id(
        tenant_id=tenant["tenant_id"],
        doc_id=id,
    )


@router.get("/chunks")
async def list_chunks(
    document_id: Optional[UUID] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    tenant: dict = Depends(get_current_tenant),
):
    """List document chunks with optional document filter."""
    return await lexcore_service.list_chunks(
        tenant_id=tenant["tenant_id"],
        document_id=document_id,
        limit=limit,
    )


@router.post("/monitor-rules", response_model=MonitorRule, status_code=status.HTTP_201_CREATED)
async def create_monitor_rule(
    rule: MonitorRuleCreate,
    tenant: dict = Depends(get_current_tenant),
) -> MonitorRule:
    """Create a new monitor rule for legislative changes."""
    return await lexcore_service.create_monitor_rule(
        tenant_id=tenant["tenant_id"],
        rule=rule,
    )


@router.delete("/monitor-rules/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_monitor_rule(
    id: UUID,
    tenant: dict = Depends(get_current_tenant),
):
    """Delete a monitor rule."""
    await lexcore_service.delete_monitor_rule(
        tenant_id=tenant["tenant_id"],
        rule_id=id,
    )
