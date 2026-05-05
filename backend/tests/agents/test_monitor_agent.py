"""Tests for Monitor Agent."""

import pytest
from datetime import datetime
from src.agents.monitor_agent import MonitorAgent, Metric


class TestMonitorAgent:
    def test_record_metric(self):
        agent = MonitorAgent()
        metric = agent.record_metric("latency", 100.0)
        assert metric.name == "latency"
        assert metric.value == 100.0
        assert isinstance(metric.timestamp, datetime)

    def test_get_metric_history(self):
        agent = MonitorAgent()
        agent.record_metric("latency", 100.0)
        agent.record_metric("latency", 200.0)
        history = agent.get_metric_history("latency")
        assert len(history) == 2
        assert history[0].value == 100.0
        assert history[1].value == 200.0

    def test_get_latest_metric(self):
        agent = MonitorAgent()
        agent.record_metric("latency", 100.0)
        agent.record_metric("latency", 200.0)
        latest = agent.get_latest_metric("latency")
        assert latest is not None
        assert latest.value == 200.0

    def test_get_latest_metric_nonexistent(self):
        agent = MonitorAgent()
        assert agent.get_latest_metric("nonexistent") is None

    def test_get_average_metric(self):
        agent = MonitorAgent()
        agent.record_metric("latency", 100.0)
        agent.record_metric("latency", 200.0)
        avg = agent.get_average_metric("latency")
        assert avg == 150.0

    def test_get_average_metric_nonexistent(self):
        agent = MonitorAgent()
        assert agent.get_average_metric("nonexistent") is None

    def test_list_metrics(self):
        agent = MonitorAgent()
        agent.record_metric("latency", 100.0)
        agent.record_metric("throughput", 50.0)
        metrics = agent.list_metrics()
        assert len(metrics) == 2
        assert "latency" in metrics
        assert "throughput" in metrics

    def test_guardrail_agt_g1_no_direct_imports(self):
        """Verify AGT-G1 guardrail: no direct imports of other agents."""
        import inspect
        from src.agents.monitor_agent import MonitorAgent

        source = inspect.getsource(MonitorAgent)
        assert "from src.agents" not in source
