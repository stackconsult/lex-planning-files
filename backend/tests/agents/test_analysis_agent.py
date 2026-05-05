"""Tests for Analysis Agent."""

import pytest
from src.agents.analysis_agent import AnalysisAgent, AnalysisResult


class TestAnalysisAgent:
    def test_analyze_document(self):
        agent = AnalysisAgent()
        result = agent.analyze("doc1", "new and useful invention")
        assert result.document_id == "doc1"
        assert 0 <= result.patentability_score <= 1
        assert 0 <= result.novelty <= 1
        assert 0 <= result.non_obviousness <= 1
        assert 0 <= result.utility <= 1

    def test_analyze_stores_result(self):
        agent = AnalysisAgent()
        agent.analyze("doc1", "test content")
        retrieved = agent.get_analysis("doc1")
        assert retrieved is not None
        assert retrieved.document_id == "doc1"

    def test_get_analysis_nonexistent(self):
        agent = AnalysisAgent()
        assert agent.get_analysis("nonexistent") is None

    def test_assess_novelty(self):
        agent = AnalysisAgent()
        score = agent._assess_novelty("new novel unique invention")
        assert score > 0
        assert score <= 1

    def test_assess_non_obviousness(self):
        agent = AnalysisAgent()
        score = agent._assess_non_obviousness("complex innovative advanced")
        assert score > 0
        assert score <= 1

    def test_assess_utility(self):
        agent = AnalysisAgent()
        score = agent._assess_utility("useful practical functional")
        assert score > 0
        assert score <= 1

    def test_patentability_score_average(self):
        agent = AnalysisAgent()
        result = agent.analyze("doc1", "new complex useful")
        expected = (result.novelty + result.non_obviousness + result.utility) / 3
        assert abs(result.patentability_score - expected) < 0.01

    def test_guardrail_agt_g1_no_direct_imports(self):
        """Verify AGT-G1 guardrail: no direct imports of other agents."""
        import inspect
        from src.agents.analysis_agent import AnalysisAgent

        source = inspect.getsource(AnalysisAgent)
        assert "from src.agents" not in source
