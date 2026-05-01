"""PACER connector for US Federal Court filings.

Source: PACER (Public Access to Court Electronic Records)
Jurisdiction: J_US_FED
API Type: REST JSON
Authentication: API Key
"""
from datetime import datetime
from typing import AsyncIterator, Optional

from httpx import AsyncClient, HTTPStatusError

from . import BaseConnector, ConnectorConfig


class PACERConnector(BaseConnector):
    """Fetches court filings from PACER."""

    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.client: Optional[AsyncClient] = None

    async def _get_client(self) -> AsyncClient:
        if not self.client:
            headers = {}
            if self.config.api_key:
                headers["Authorization"] = f"Bearer {self.config.api_key}"
            self.client = AsyncClient(
                base_url=self.config.base_url,
                headers=headers,
                timeout=self.config.timeout_seconds,
            )
        return self.client

    async def fetch_documents(
        self,
        query: Optional[str] = None,
        since_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> AsyncIterator[dict]:
        """Yield PACER court filings matching query."""
        client = await self._get_client()

        params = {
            "q": query or "",
            "limit": min(limit, 100),
        }

        try:
            response = await client.get("/api/v1/filings", params=params)
            response.raise_for_status()
            data = response.json()

            for filing in data.get("filings", []):
                yield filing
        except HTTPStatusError as e:
            print(f"PACER API error: {e}")
            raise

    async def parse_document(self, raw_doc: dict) -> dict:
        """Parse PACER filing into normalized prior_art schema."""
        return {
            "external_id": raw_doc.get("case_id", ""),
            "patent_number": None,
            "title": raw_doc.get("case_title", ""),
            "inventors": [],
            "abstract": raw_doc.get("summary", "")[:500],
            "description": raw_doc.get("summary", ""),
            "filing_date": raw_doc.get("filed_date"),
            "publication_date": None,
            "claims": None,
            "jurisdiction": "J_US_FED",
            "source_url": raw_doc.get("pacer_url"),
        }

    def get_document_metadata(self, doc: dict) -> dict:
        """Extract metadata for prior_art table."""
        return {
            "source": "PACER",
            "external_id": doc["external_id"],
            "relevance_score": 0.7,  # Medium relevance for court filings
        }

    async def close(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()
