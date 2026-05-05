"""Monitor Agent - Monitors IP pipeline health and metrics."""

from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Metric:
    """Pipeline metric with value and timestamp."""
    name: str
    value: float
    timestamp: datetime
    metadata: Dict[str, str]


class MonitorAgent:
    """Monitors IP pipeline health and performance metrics."""

    def __init__(self):
        """Initialize monitor agent."""
        self._metrics: Dict[str, list] = {}

    def record_metric(self, name: str, value: float) -> Metric:
        """Record a pipeline metric.

        Args:
            name: Metric name
            value: Metric value

        Returns:
            Metric record

        Guardrail: AGT-G1 - No direct imports of other agents
        """
        metric = Metric(
            name=name,
            value=value,
            timestamp=datetime.utcnow(),
            metadata={}
        )

        if name not in self._metrics:
            self._metrics[name] = []
        self._metrics[name].append(metric)

        return metric

    def get_metric_history(self, name: str) -> list:
        """Get history of a metric.

        Args:
            name: Metric name

        Returns:
            List of metric records
        """
        return self._metrics.get(name, [])

    def get_latest_metric(self, name: str) -> Optional[Metric]:
        """Get latest value of a metric.

        Args:
            name: Metric name

        Returns:
            Latest metric or None if not found
        """
        history = self._metrics.get(name)
        if not history:
            return None
        return history[-1]

    def get_average_metric(self, name: str) -> Optional[float]:
        """Get average value of a metric.

        Args:
            name: Metric name

        Returns:
            Average value or None if not found
        """
        history = self._metrics.get(name)
        if not history:
            return None
        values = [m.value for m in history]
        return sum(values) / len(values)

    def list_metrics(self) -> list:
        """List all metric names.

        Returns:
            List of metric names
        """
        return list(self._metrics.keys())
