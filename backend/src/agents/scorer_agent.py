"""Scorer Agent - Scores patent applications based on multiple criteria."""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class ScoreResult:
    """Score result with component scores and total."""
    document_id: str
    novelty_score: float
    non_obviousness_score: float
    utility_score: float
    prior_art_risk: float
    total_score: float
    metadata: Dict[str, str]


class ScorerAgent:
    """Scores patent applications based on patentability criteria."""

    def __init__(self):
        """Initialize scorer agent."""
        self._scores: Dict[str, ScoreResult] = {}

    def score(self, document_id: str, content: str, prior_art_count: int) -> ScoreResult:
        """Score document based on patentability criteria.

        Args:
            document_id: Document identifier
            content: Document content
            prior_art_count: Number of prior art references found

        Returns:
            Score result with component scores and total

        Guardrail: AGT-G1 - No direct imports of other agents
        """
        novelty_score = self._assess_novelty(content)
        non_obviousness_score = self._assess_non_obviousness(content)
        utility_score = self._assess_utility(content)
        prior_art_risk = self._assess_prior_art_risk(prior_art_count)

        total_score = (novelty_score + non_obviousness_score + utility_score - prior_art_risk) / 3
        total_score = max(0.0, min(1.0, total_score))

        result = ScoreResult(
            document_id=document_id,
            novelty_score=novelty_score,
            non_obviousness_score=non_obviousness_score,
            utility_score=utility_score,
            prior_art_risk=prior_art_risk,
            total_score=total_score,
            metadata={}
        )

        self._scores[document_id] = result
        return result

    def _assess_novelty(self, content: str) -> float:
        """Assess novelty of invention.

        Args:
            content: Document content

        Returns:
            Novelty score (0-1)
        """
        content_lower = content.lower()
        novelty_indicators = ["new", "novel", "unique", "first", "original", "innovative"]
        matches = sum(1 for indicator in novelty_indicators if indicator in content_lower)
        return min(matches / len(novelty_indicators), 1.0)

    def _assess_non_obviousness(self, content: str) -> float:
        """Assess non-obviousness of invention.

        Args:
            content: Document content

        Returns:
            Non-obviousness score (0-1)
        """
        content_lower = content.lower()
        complexity_indicators = ["complex", "advanced", "sophisticated", "non-obvious", "inventive"]
        matches = sum(1 for indicator in complexity_indicators if indicator in content_lower)
        return min(matches / len(complexity_indicators), 1.0)

    def _assess_utility(self, content: str) -> float:
        """Assess utility of invention.

        Args:
            content: Document content

        Returns:
            Utility score (0-1)
        """
        content_lower = content.lower()
        utility_indicators = ["useful", "practical", "functional", "applicable", "beneficial"]
        matches = sum(1 for indicator in utility_indicators if indicator in content_lower)
        return min(matches / len(utility_indicators), 1.0)

    def _assess_prior_art_risk(self, prior_art_count: int) -> float:
        """Assess prior art risk based on count.

        Args:
            prior_art_count: Number of prior art references

        Returns:
            Risk score (0-1, higher = more risk)
        """
        return min(prior_art_count / 10.0, 1.0)

    def get_score(self, document_id: str) -> Optional[ScoreResult]:
        """Retrieve score by document ID.

        Args:
            document_id: Document identifier

        Returns:
            Score result or None if not found
        """
        return self._scores.get(document_id)
