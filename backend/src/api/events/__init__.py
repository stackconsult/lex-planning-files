"""API event schemas and handlers.

Defines domain events emitted by the API layer for async processing
via Celery workers and event bus.
"""
from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from pydantic import BaseModel, Field


class EventMetadata(BaseModel):
    """Standard metadata attached to every API event."""
    event_id: UUID
    correlation_id: str
    tenant_id: UUID
    timestamp: datetime
    source: str = "api"


class DocumentIngestedEvent(BaseModel):
    """Emitted when a new legal document is ingested."""
    metadata: EventMetadata
    document_id: UUID
    jurisdiction: str
    doc_type: str


class MonitorRuleTriggeredEvent(BaseModel):
    """Emitted when a monitor rule detects a legislative change."""
    metadata: EventMetadata
    rule_id: UUID
    alert_id: UUID
    change_summary: str


class InventionDetectedEvent(BaseModel):
    """Emitted when a new invention candidate is detected."""
    metadata: EventMetadata
    invention_id: UUID
    source: str
    novelty_score: float = Field(..., ge=0, le=1)


class DisclosureDraftedEvent(BaseModel):
    """Emitted when a disclosure draft is generated."""
    metadata: EventMetadata
    disclosure_id: UUID
    invention_id: UUID
    grounding_score: float = Field(..., ge=0, le=1)


class FilingBundlePackagedEvent(BaseModel):
    """Emitted when a filing bundle is packaged."""
    metadata: EventMetadata
    bundle_id: UUID
    disclosure_id: UUID
    bundle_format: str


class LedgerAnchoredEvent(BaseModel):
    """Emitted when a bundle is anchored to the blockchain."""
    metadata: EventMetadata
    proof_id: UUID
    polygon_tx_hash: str
    block_number: str
