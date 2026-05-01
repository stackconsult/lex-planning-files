"""SEC connector for EDGAR filings.

Source: SEC EDGAR (Electronic Data Gathering, Analysis, and Retrieval)
Jurisdiction: J_US_FED
API Type: REST JSON
Authentication: API Key
"""
from datetime import datetime
from typing import AsyncIterator, Optional

from httpx import AsyncClient, HTTPStatusError

from . import BaseConnector, ConnectorConfig


class SECConnector(BaseConnector):
    """Fetches SEC filings from EDGAR."""

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
        """Yield SEC filings matching query."""
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
            print(f"SEC API error: {e}")
            raise

    async def parse_document(self, raw_doc: dict) -> dict:
        """Parse SEC filing into normalized prior_art schema."""
        return {
            "external_id": raw_doc.get("accession_number", ""),
            "patent_number": None,
            "title": raw_doc.get("company_name", ""),
            "inventors": [],
            "abstract": raw_doc.get("filing_description", "")[:500],
            "description": raw_doc.get("filing_description", ""),
            "filing_date": raw_doc.get("filing_date"),
            "publication_date": None,
            "claims": None,
            "jurisdiction": "J_US_FED",
            "source_url": f"https://www.sec.gov/Archives/edgar/data/{raw_doc.get('cik')}/{raw_doc.get('accession_number')}",
        }

    def get_document_metadata(self, doc: dict) -> dict:
        """Extract metadata for prior_art table."""
        return {
            "source": "SEC",
            "external_id": doc["external_id"],
            "relevance_score": 0.6,  # Lower relevance for SEC filings
        }

    async def close(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()
