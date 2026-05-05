"""Detector Agent - Detects patterns and anomalies in IP documents."""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Detection:
    """Detection result with pattern and confidence."""
    pattern: str
    confidence: float
    location: str
    metadata: Dict[str, str]


class DetectorAgent:
    """Detects patterns and anomalies in IP documents."""

    def __init__(self):
        """Initialize detector agent."""
        self._detections: Dict[str, List[Detection]] = {}

    def detect(self, document_id: str, content: str) -> List[Detection]:
        """Detect patterns in document content.

        Args:
            document_id: Document identifier
            content: Document content

        Returns:
            List of detections

        Guardrail: AGT-G1 - No direct imports of other agents
        """
        detections = []
        content_lower = content.lower()

        if "novel" in content_lower:
            detections.append(Detection(
                pattern="novelty_indicator",
                confidence=0.8,
                location="content",
                metadata={}
            ))

        if "inventive" in content_lower:
            detections.append(Detection(
                pattern="inventiveness_indicator",
                confidence=0.75,
                location="content",
                metadata={}
            ))

        if "prior art" in content_lower:
            detections.append(Detection(
                pattern="prior_art_reference",
                confidence=0.9,
                location="content",
                metadata={}
            ))

        self._detections[document_id] = detections
        return detections

    def get_detections(self, document_id: str) -> List[Detection]:
        """Get detections for a document.

        Args:
            document_id: Document identifier

        Returns:
            List of detections
        """
        return self._detections.get(document_id, [])

    def get_detection_count(self, document_id: str) -> int:
        """Get detection count for a document.

        Args:
            document_id: Document identifier

        Returns:
            Number of detections
        """
        return len(self._detections.get(document_id, []))
