"""Discloser Agent - Manages disclosure requirements for patent applications."""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class DisclosureRequirement:
    """Disclosure requirement with status."""
    requirement_id: str
    name: str
    description: str
    status: str
    metadata: Dict[str, str]


class DiscloserAgent:
    """Manages disclosure requirements for patent applications."""

    def __init__(self):
        """Initialize discloser agent."""
        self._requirements: Dict[str, List[DisclosureRequirement]] = {}
        self._initialize_requirements()

    def _initialize_requirements(self):
        """Initialize standard disclosure requirements."""
        self._standard_requirements = [
            DisclosureRequirement(
                requirement_id="DISC001",
                name="Prior Art Disclosure",
                description="Disclose all known prior art references",
                status="pending",
                metadata={}
            ),
            DisclosureRequirement(
                requirement_id="DISC002",
                name="Inventorship Disclosure",
                description="Disclose all inventors and contributions",
                status="pending",
                metadata={}
            ),
            DisclosureRequirement(
                requirement_id="DISC003",
                name="Funding Disclosure",
                description="Disclose any government funding or grants",
                status="pending",
                metadata={}
            ),
        ]

    def get_requirements(self, document_id: str) -> List[DisclosureRequirement]:
        """Get disclosure requirements for a document.

        Args:
            document_id: Document identifier

        Returns:
            List of disclosure requirements

        Guardrail: AGT-G1 - No direct imports of other agents
        """
        if document_id not in self._requirements:
            self._requirements[document_id] = [req for req in self._standard_requirements]
        return self._requirements[document_id]

    def update_requirement_status(self, document_id: str, requirement_id: str, status: str) -> None:
        """Update status of a disclosure requirement.

        Args:
            document_id: Document identifier
            requirement_id: Requirement identifier
            status: New status (pending, completed, waived)
        """
        if document_id not in self._requirements:
            self.get_requirements(document_id)

        for req in self._requirements[document_id]:
            if req.requirement_id == requirement_id:
                req.status = status
                break

    def get_completion_status(self, document_id: str) -> float:
        """Get overall disclosure completion status.

        Args:
            document_id: Document identifier

        Returns:
            Completion percentage (0-1)
        """
        requirements = self.get_requirements(document_id)
        completed = sum(1 for req in requirements if req.status == "completed")
        return completed / len(requirements) if requirements else 0.0

    def get_missing_disclosures(self, document_id: str) -> List[DisclosureRequirement]:
        """Get list of missing disclosures.

        Args:
            document_id: Document identifier

        Returns:
            List of pending disclosure requirements
        """
        requirements = self.get_requirements(document_id)
        return [req for req in requirements if req.status == "pending"]
