"""WIPO connector for international patents.

Source: WIPO Patentscope
Jurisdiction: International
API Type: REST JSON
Authentication: API Key
"""
from datetime import datetime
from typing import AsyncIterator, Optional

from httpx import AsyncClient, HTTPStatusError

from . import BaseConnector, ConnectorConfig


class WIPOConnector(BaseConnector):
    """Fetches patent data from WIPO Patentscope."""

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
        """Yield WIPO patents matching query."""
        client = await self._get_client()

        params = {
            "q": query or "",
            "ps": min(limit, 100),
            "fmt": "json",
        }

        try:
            response = await client.get("/search/patents", params=params)
            response.raise_for_status()
            data = response.json()

            for patent in data.get("results", []):
                yield patent
        except HTTPStatusError as e:
            print(f"WIPO API error: {e}")
            raise

    async def parse_document(self, raw_doc: dict) -> dict:
        """Parse WIPO patent into normalized prior_art schema."""
        return {
            "external_id": raw_doc.get("docdb", {}).get("docId", ""),
            "patent_number": raw_doc.get("docdb", {}).get("docId"),
            "title": raw_doc.get("biblio", {}).get("title", ""),
            "inventors": raw_doc.get("biblio", {}).get("inventors", []),
            "abstract": raw_doc.get("abstract", ""),
            "description": raw_doc.get("description", ""),
            "filing_date": raw_doc.get("biblio", {}).get("date"),
            "publication_date": raw_doc.get("biblio", {}).get("pubDate"),
            "claims": raw_doc.get("claims"),
            "jurisdiction": raw_doc.get("biblio", {}).get("country"),
            "source_url": raw_doc.get("link"),
        }

    def get_document_metadata(self, doc: dict) -> dict:
        """Extract metadata for prior_art table."""
        return {
            "source": "WIPO",
            "external_id": doc["external_id"],
            "relevance_score": 0.95,  # High relevance for international patents
        }

    async def close(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()
