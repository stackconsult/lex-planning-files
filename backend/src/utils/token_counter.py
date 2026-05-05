"""Token Counter - Measures token usage for operations."""

from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TokenCount:
    """Token count record."""
    operation: str
    tokens: int
    timestamp: datetime
    metadata: Dict[str, str]


class TokenCounter:
    """Counts tokens for various operations."""

    def __init__(self):
        """Initialize token counter."""
        self._counts: Dict[str, list] = {}
        self._baselines: Dict[str, int] = {
            "api_search": 2500,
            "api_analysis": 3200,
            "api_draft": 4500,
            "agent_router": 800,
            "agent_search": 1500,
            "agent_analysis": 2000,
            "db_simple": 300,
            "db_complex": 800,
            "ml_inference": 5000,
        }

    def count_tokens(self, operation: str, content: str) -> TokenCount:
        """Count tokens for an operation.

        Args:
            operation: Operation name
            content: Content to count

        Returns:
            Token count record
        """
        # Simple token counting: split by whitespace
        tokens = len(content.split())

        count = TokenCount(
            operation=operation,
            tokens=tokens,
            timestamp=datetime.utcnow(),
            metadata={}
        )

        if operation not in self._counts:
            self._counts[operation] = []
        self._counts[operation].append(count)

        return count

    def get_baseline(self, operation: str) -> Optional[int]:
        """Get baseline token count for operation.

        Args:
            operation: Operation name

        Returns:
            Baseline token count or None
        """
        return self._baselines.get(operation)

    def get_average_tokens(self, operation: str) -> Optional[float]:
        """Get average token count for operation.

        Args:
            operation: Operation name

        Returns:
            Average token count or None
        """
        counts = self._counts.get(operation)
        if not counts:
            return None
        return sum(c.tokens for c in counts) / len(counts)

    def calculate_efficiency(self, operation: str) -> Optional[float]:
        """Calculate token efficiency for operation.

        Args:
            operation: Operation name

        Returns:
            Efficiency ratio (0-1) or None
        """
        baseline = self.get_baseline(operation)
        average = self.get_average_tokens(operation)

        if baseline is None or average is None:
            return None

        if baseline == 0:
            return 0.0

        reduction = (baseline - average) / baseline
        return max(0.0, min(1.0, reduction))
