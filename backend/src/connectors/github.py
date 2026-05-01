"""GitHub connector for OSS patent references.

Source: GitHub REST API
Jurisdiction: Multi-jurisdiction
API Type: REST JSON
Authentication: Personal Access Token
"""
from datetime import datetime
from typing import AsyncIterator, Optional

from httpx import AsyncClient, HTTPStatusError

from . import BaseConnector, ConnectorConfig


class GitHubConnector(BaseConnector):
    """Fetches patent-relevant GitHub repositories and issues."""

    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.client: Optional[AsyncClient] = None

    async def _get_client(self) -> AsyncClient:
        if not self.client:
            headers = {}
            if self.config.api_key:
                headers["Authorization"] = f"token {self.config.api_key}"
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
        """Yield GitHub repositories matching patent-related keywords."""
        client = await self._get_client()

        # Search for repositories with patent-related terms
        search_query = query or "patent OR invention OR intellectual property"
        params = {
            "q": search_query,
            "per_page": min(limit, 100),
            "sort": "updated",
            "order": "desc",
        }

        try:
            response = await client.get("/search/repositories", params=params)
            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                yield {
                    "id": item["id"],
                    "name": item["name"],
                    "full_name": item["full_name"],
                    "description": item.get("description", ""),
                    "html_url": item["html_url"],
                    "created_at": item["created_at"],
                    "updated_at": item["updated_at"],
                    "language": item.get("language"),
                    "stargazers_count": item["stargazers_count"],
                }
        except HTTPStatusError as e:
            print(f"GitHub API error: {e}")
            raise

    async def parse_document(self, raw_doc: dict) -> dict:
        """Parse GitHub repository into normalized prior_art schema."""
        return {
            "external_id": f"gh-{raw_doc['id']}",
            "patent_number": None,
            "title": raw_doc["full_name"],
            "inventors": [],
            "abstract": raw_doc.get("description", "")[:500],
            "description": raw_doc.get("description", ""),
            "filing_date": None,
            "publication_date": None,
            "claims": None,
            "jurisdiction": None,
            "source_url": raw_doc["html_url"],
        }

    def get_document_metadata(self, doc: dict) -> dict:
        """Extract metadata for prior_art table."""
        return {
            "source": "GitHub",
            "external_id": doc["external_id"],
            "relevance_score": 0.8,  # Default relevance for OSS references
        }

    async def close(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()
