"""Scanner Agent - Scans IP documents for compliance and issues."""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ScanResult:
    """Scan result with issues and compliance status."""
    document_id: str
    issues: List[str]
    compliance_score: float
    metadata: Dict[str, str]


class ScannerAgent:
    """Scans IP documents for compliance and issues."""

    def __init__(self):
        """Initialize scanner agent."""
        self._scans: Dict[str, ScanResult] = {}

    def scan(self, document_id: str, content: str) -> ScanResult:
        """Scan document for compliance issues.

        Args:
            document_id: Document identifier
            content: Document content

        Returns:
            Scan result with issues and compliance score

        Guardrail: AGT-G1 - No direct imports of other agents
        """
        issues = self._detect_issues(content)
        compliance_score = self._calculate_compliance(issues)

        result = ScanResult(
            document_id=document_id,
            issues=issues,
            compliance_score=compliance_score,
            metadata={}
        )

        self._scans[document_id] = result
        return result

    def _detect_issues(self, content: str) -> List[str]:
        """Detect issues in document content.

        Args:
            content: Document content

        Returns:
            List of detected issues
        """
        issues = []
        content_lower = content.lower()

        if len(content) < 100:
            issues.append("Document too short")

        if "confidential" not in content_lower and "proprietary" not in content_lower:
            issues.append("Missing confidentiality notice")

        if "abstract" not in content_lower:
            issues.append("Missing abstract section")

        return issues

    def _calculate_compliance(self, issues: List[str]) -> float:
        """Calculate compliance score based on issues.

        Args:
            issues: List of detected issues

        Returns:
            Compliance score (0-1)
        """
        if not issues:
            return 1.0
        return max(0.0, 1.0 - (len(issues) * 0.1))

    def get_scan_result(self, document_id: str) -> Optional[ScanResult]:
        """Retrieve scan result by document ID.

        Args:
            document_id: Document identifier

        Returns:
            Scan result or None if not found
        """
        return self._scans.get(document_id)
