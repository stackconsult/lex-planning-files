"""Document connectors for LexRadar prior art ingestion.

Implements async HTTP clients for 7 patent/IP sources:
- GitHub (OSS patent references)
- USPTO (US Patent and Trademark Office)
- WIPO (World Intellectual Property Organization)
- EPO (European Patent Office)
- PACER (US Federal Court filings)
- SEC (EDGAR filings)
- State (State patent databases)
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import AsyncIterator, Optional

from pydantic import BaseModel


class ConnectorConfig(BaseModel):
    """Base configuration for all connectors."""
    source_name: str
    api_key: Optional[str] = None
    base_url: str
    rate_limit_per_minute: int = 60
    retry_attempts: int = 3
    timeout_seconds: int = 30
    tenant_id: Optional[str] = None


class BaseConnector(ABC):
    """Abstract base class for document connectors."""

    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.last_fetch: Optional[datetime] = None

    @abstractmethod
    async def fetch_documents(
        self,
        query: Optional[str] = None,
        since_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> AsyncIterator[dict]:
        """Yield raw documents from source."""
        pass

    @abstractmethod
    async def parse_document(self, raw_doc: dict) -> dict:
        """Parse raw document into normalized schema."""
        pass

    @abstractmethod
    def get_document_metadata(self, doc: dict) -> dict:
        """Extract metadata for prior_art table."""
        pass
