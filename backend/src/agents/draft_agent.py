"""Draft Agent - Drafts patent application sections."""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class DraftResult:
    """Draft result with generated content."""
    section: str
    content: str
    word_count: int
    metadata: Dict[str, str]


class DraftAgent:
    """Drafts patent application sections based on analysis."""

    def __init__(self):
        """Initialize draft agent."""
        self._drafts: Dict[str, DraftResult] = {}

    def draft_section(self, section: str, analysis_result: str) -> DraftResult:
        """Draft a patent application section.

        Args:
            section: Section name (e.g., "abstract", "claims", "description")
            analysis_result: Analysis result to base draft on

        Returns:
            Draft result with generated content

        Guardrail: AGT-G1 - No direct imports of other agents
        """
        content = self._generate_content(section, analysis_result)
        word_count = len(content.split())

        result = DraftResult(
            section=section,
            content=content,
            word_count=word_count,
            metadata={}
        )

        self._drafts[section] = result
        return result

    def _generate_content(self, section: str, analysis: str) -> str:
        """Generate content for a section.

        Args:
            section: Section name
            analysis: Analysis result

        Returns:
            Generated content
        """
        templates = {
            "abstract": f"Abstract: This invention relates to {analysis}. The invention provides novel and useful features.",
            "claims": f"Claims: 1. A method for {analysis}, comprising the steps of...",
            "description": f"Description: The present invention relates to {analysis}. The invention addresses the need for...",
            "summary": f"Summary: The invention provides {analysis} with improved functionality and efficiency.",
        }

        return templates.get(section, f"{section}: {analysis}")

    def get_draft(self, section: str) -> Optional[DraftResult]:
        """Retrieve draft by section name.

        Args:
            section: Section name

        Returns:
            Draft result or None if not found
        """
        return self._drafts.get(section)

    def list_sections(self) -> list:
        """List all drafted sections.

        Returns:
            List of section names
        """
        return list(self._drafts.keys())
