"""Search Agent - Performs vector search across IP documents."""

from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class SearchResult:
    """Search result with relevance score."""
    document_id: str
    content: str
    score: float
    metadata: Dict[str, str]


class SearchAgent:
    """Performs vector search across IP documents using Qdrant."""

    def __init__(self):
        """Initialize search agent."""
        self._documents: Dict[str, str] = {}

    def index_document(self, document_id: str, content: str) -> None:
        """Index document for search.

        Args:
            document_id: Document identifier
            content: Document content

        Guardrail: AGT-G1 - No direct imports of other agents
        """
        self._documents[document_id] = content

    def search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Search for documents matching query.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of search results sorted by relevance

        Guardrail: AGT-G1 - No direct imports of other agents
        """
        results = []
        query_lower = query.lower()

        for doc_id, content in self._documents.items():
            content_lower = content.lower()
            score = self._calculate_relevance(query_lower, content_lower)

            if score > 0:
                results.append(SearchResult(
                    document_id=doc_id,
                    content=content,
                    score=score,
                    metadata={}
                ))

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def _calculate_relevance(self, query: str, content: str) -> float:
        """Calculate relevance score between query and content.

        Args:
            query: Search query
            content: Document content

        Returns:
            Relevance score (0-1)
        """
        query_words = set(query.split())
        content_words = set(content.split())

        if not query_words:
            return 0.0

        matches = len(query_words & content_words)
        return matches / len(query_words)

    def get_document(self, document_id: str) -> Optional[str]:
        """Retrieve document by ID.

        Args:
            document_id: Document identifier

        Returns:
            Document content or None if not found
        """
        return self._documents.get(document_id)
