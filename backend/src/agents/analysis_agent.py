"""Analysis Agent - Analyzes IP documents for patentability."""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class AnalysisResult:
    """Analysis result with patentability assessment."""
    document_id: str
    patentability_score: float
    novelty: float
    non_obviousness: float
    utility: float
    metadata: Dict[str, str]


class AnalysisAgent:
    """Analyzes IP documents for patentability criteria."""

    def __init__(self):
        """Initialize analysis agent."""
        self._analyses: Dict[str, AnalysisResult] = {}

    def analyze(self, document_id: str, content: str) -> AnalysisResult:
        """Analyze document for patentability.

        Args:
            document_id: Document identifier
            content: Document content

        Returns:
            Analysis result with patentability scores

        Guardrail: AGT-G1 - No direct imports of other agents
        """
        novelty = self._assess_novelty(content)
        non_obviousness = self._assess_non_obviousness(content)
        utility = self._assess_utility(content)

        patentability_score = (novelty + non_obviousness + utility) / 3

        result = AnalysisResult(
            document_id=document_id,
            patentability_score=patentability_score,
            novelty=novelty,
            non_obviousness=non_obviousness,
            utility=utility,
            metadata={}
        )

        self._analyses[document_id] = result
        return result

    def _assess_novelty(self, content: str) -> float:
        """Assess novelty of invention.

        Args:
            content: Document content

        Returns:
            Novelty score (0-1)
        """
        content_lower = content.lower()
        novelty_indicators = ["new", "novel", "unique", "first", "original"]
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
        complexity_indicators = ["complex", "innovative", "advanced", "sophisticated"]
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
        utility_indicators = ["useful", "practical", "functional", "applicable"]
        matches = sum(1 for indicator in utility_indicators if indicator in content_lower)
        return min(matches / len(utility_indicators), 1.0)

    def get_analysis(self, document_id: str) -> Optional[AnalysisResult]:
        """Retrieve analysis by document ID.

        Args:
            document_id: Document identifier

        Returns:
            Analysis result or None if not found
        """
        return self._analyses.get(document_id)
