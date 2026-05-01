"""USPTO connector for US patents.

Source: USPTO Patent Examination Research System
Jurisdiction: J_US_FED
API Type: REST JSON
Authentication: API Key
"""
from datetime import datetime
from typing import AsyncIterator, Optional

from httpx import AsyncClient, HTTPStatusError

from . import BaseConnector, ConnectorConfig


class USPTOConnector(BaseConnector):
    """Fetches patent data from USPTO database."""

    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.client: Optional[AsyncClient] = None

    async def _get_client(self) -> AsyncClient:
        if not self.client:
            headers = {}
            if self.config.api_key:
                headers["X-Api-Key"] = self.config.api_key
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
        """Yield US patents matching query."""
        client = await self._get_client()

        params = {
            "q": query or "",
            "f": "patentNumber,patentTitle,inventors,applicationDate,grantDate",
            "rows": min(limit, 100),
        }

        try:
            response = await client.get("/api/v1/patent", params=params)
            response.raise_for_status()
            data = response.json()

            for patent in data.get("results", []):
                yield patent
        except HTTPStatusError as e:
            print(f"USPTO API error: {e}")
            raise

    async def parse_document(self, raw_doc: dict) -> dict:
        """Parse USPTO patent into normalized prior_art schema."""
        return {
            "external_id": raw_doc.get("patentNumber", ""),
            "patent_number": raw_doc.get("patentNumber"),
            "title": raw_doc.get("patentTitle", ""),
            "inventors": raw_doc.get("inventors", []),
            "abstract": raw_doc.get("abstract", ""),
            "description": raw_doc.get("description", ""),
            "filing_date": raw_doc.get("applicationDate"),
            "publication_date": raw_doc.get("grantDate"),
            "claims": raw_doc.get("claims"),
            "jurisdiction": "J_US_FED",
            "source_url": f"https://patents.google.com/patent/{raw_doc.get('patentNumber')}",
        }

    def get_document_metadata(self, doc: dict) -> dict:
        """Extract metadata for prior_art table."""
        return {
            "source": "USPTO",
            "external_id": doc["external_id"],
            "relevance_score": 1.0,  # High relevance for direct patent matches
        }

    async def close(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()
