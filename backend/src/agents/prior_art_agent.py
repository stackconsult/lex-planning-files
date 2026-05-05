"""PriorArt Agent - Fetches and analyzes prior art references."""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PriorArtResult:
    """Prior art result with similarity score."""
    patent_id: str
    title: str
    similarity_score: float
    metadata: Dict[str, str]


class PriorArtAgent:
    """Fetches and analyzes prior art references for patent applications."""

    def __init__(self):
        """Initialize prior art agent."""
        self._prior_art_db: Dict[str, PriorArtResult] = {}
        self._initialize_sample_db()

    def _initialize_sample_db(self):
        """Initialize sample prior art database."""
        self._prior_art_db["US12345"] = PriorArtResult(
            patent_id="US12345",
            title="Method for data processing",
            similarity_score=0.0,
            metadata={}
        )
        self._prior_art_db["US67890"] = PriorArtResult(
            patent_id="US67890",
            title="System for content analysis",
            similarity_score=0.0,
            metadata={}
        )

    def search_prior_art(self, query: str) -> List[PriorArtResult]:
        """Search for prior art matching query.

        Args:
            query: Search query

        Returns:
            List of prior art results with similarity scores

        Guardrail: AGT-G1 - No direct imports of other agents
        """
        results = []
        query_lower = query.lower()

        for patent_id, result in self._prior_art_db.items():
            similarity = self._calculate_similarity(query_lower, result.title.lower())
            if similarity > 0.3:
                result.similarity_score = similarity
                results.append(result)

        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results

    def _calculate_similarity(self, query: str, title: str) -> float:
        """Calculate similarity between query and title.

        Args:
            query: Search query
            title: Patent title

        Returns:
            Similarity score (0-1)
        """
        query_words = set(query.split())
        title_words = set(title.split())

        if not query_words:
            return 0.0

        matches = len(query_words & title_words)
        return matches / len(query_words)

    def get_prior_art(self, patent_id: str) -> Optional[PriorArtResult]:
        """Retrieve prior art by patent ID.

        Args:
            patent_id: Patent identifier

        Returns:
            Prior art result or None if not found
        """
        return self._prior_art_db.get(patent_id)
