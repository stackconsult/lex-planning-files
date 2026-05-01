"""State patent database connector.

Source: Various state patent offices (CA, TX, NY, etc.)
Jurisdiction: US State
API Type: REST JSON
Authentication: API Key (varies by state)
"""
from datetime import datetime
from typing import AsyncIterator, Optional

from httpx import AsyncClient, HTTPStatusError

from . import BaseConnector, ConnectorConfig


class StateConnector(BaseConnector):
    """Fetches patent data from state patent databases."""

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
        """Yield state patents matching query."""
        client = await self._get_client()

        params = {
            "q": query or "",
            "limit": min(limit, 100),
        }

        try:
            response = await client.get("/api/v1/patents", params=params)
            response.raise_for_status()
            data = response.json()

            for patent in data.get("patents", []):
                yield patent
        except HTTPStatusError as e:
            print(f"State API error: {e}")
            raise

    async def parse_document(self, raw_doc: dict) -> dict:
        """Parse state patent into normalized prior_art schema."""
        return {
            "external_id": raw_doc.get("patent_id", ""),
            "patent_number": raw_doc.get("patent_number"),
            "title": raw_doc.get("title", ""),
            "inventors": raw_doc.get("inventors", []),
            "abstract": raw_doc.get("abstract", ""),
            "description": raw_doc.get("description", ""),
            "filing_date": raw_doc.get("filing_date"),
            "publication_date": raw_doc.get("grant_date"),
            "claims": raw_doc.get("claims"),
            "jurisdiction": f"J_US_{raw_doc.get('state', 'UNK').upper()}",
            "source_url": raw_doc.get("source_url"),
        }

    def get_document_metadata(self, doc: dict) -> dict:
        """Extract metadata for prior_art table."""
        return {
            "source": "State",
            "external_id": doc["external_id"],
            "relevance_score": 0.8,  # Medium-high relevance for state patents
        }

    async def close(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()
