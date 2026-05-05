"""Tests for Detector Agent."""

import pytest
from src.agents.detector_agent import DetectorAgent, Detection


class TestDetectorAgent:
    def test_detect_patterns(self):
        agent = DetectorAgent()
        detections = agent.detect("doc1", "This is a novel inventive document")
        assert len(detections) > 0
        assert all(isinstance(d, Detection) for d in detections)

    def test_detect_novelty_indicator(self):
        agent = DetectorAgent()
        detections = agent.detect("doc1", "This is a novel invention")
        assert any(d.pattern == "novelty_indicator" for d in detections)

    def test_detect_inventiveness_indicator(self):
        agent = DetectorAgent()
        detections = agent.detect("doc1", "This is inventive")
        assert any(d.pattern == "inventiveness_indicator" for d in detections)

    def test_detect_prior_art_reference(self):
        agent = DetectorAgent()
        detections = agent.detect("doc1", "This references prior art")
        assert any(d.pattern == "prior_art_reference" for d in detections)

    def test_get_detections(self):
        agent = DetectorAgent()
        agent.detect("doc1", "novel content")
        detections = agent.get_detections("doc1")
        assert len(detections) > 0

    def test_get_detections_nonexistent(self):
        agent = DetectorAgent()
        detections = agent.get_detections("nonexistent")
        assert len(detections) == 0

    def test_get_detection_count(self):
        agent = DetectorAgent()
        agent.detect("doc1", "novel inventive prior art")
        count = agent.get_detection_count("doc1")
        assert count == 3

    def test_guardrail_agt_g1_no_direct_imports(self):
        """Verify AGT-G1 guardrail: no direct imports of other agents."""
        import inspect
        from src.agents.detector_agent import DetectorAgent

        source = inspect.getsource(DetectorAgent)
        assert "from src.agents" not in source
