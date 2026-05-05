"""Ingest Agent - Ingests and processes IP documents."""

from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class IngestResult:
    """Ingest result with document metadata."""
    document_id: str
    status: str
    word_count: int
    processed_at: datetime
    metadata: Dict[str, str]


class IngestAgent:
    """Ingests and processes IP documents for analysis."""

    def __init__(self):
        """Initialize ingest agent."""
        self._documents: Dict[str, IngestResult] = {}

    def ingest(self, document_id: str, content: str) -> IngestResult:
        """Ingest document for processing.

        Args:
            document_id: Document identifier
            content: Document content

        Returns:
            Ingest result with processing status

        Guardrail: AGT-G1 - No direct imports of other agents
        """
        word_count = len(content.split())
        status = self._validate_content(content)

        result = IngestResult(
            document_id=document_id,
            status=status,
            word_count=word_count,
            processed_at=datetime.utcnow(),
            metadata={}
        )

        self._documents[document_id] = result
        return result

    def _validate_content(self, content: str) -> str:
        """Validate document content.

        Args:
            content: Document content

        Returns:
            Status string ("valid", "invalid", "empty")
        """
        if not content or not content.strip():
            return "empty"
        if len(content) < 50:
            return "invalid"
        return "valid"

    def get_ingest_result(self, document_id: str) -> Optional[IngestResult]:
        """Retrieve ingest result by document ID.

        Args:
            document_id: Document identifier

        Returns:
            Ingest result or None if not found
        """
        return self._documents.get(document_id)

    def list_documents(self) -> list:
        """List all ingested documents.

        Returns:
            List of document IDs
        """
        return list(self._documents.keys())
