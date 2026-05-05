"""Tests for Scorer Agent."""

import pytest
from src.agents.scorer_agent import ScorerAgent, ScoreResult


class TestScorerAgent:
    def test_score_document(self):
        agent = ScorerAgent()
        result = agent.score("doc1", "new novel useful invention", 2)
        assert result.document_id == "doc1"
        assert 0 <= result.novelty_score <= 1
        assert 0 <= result.non_obviousness_score <= 1
        assert 0 <= result.utility_score <= 1
        assert 0 <= result.prior_art_risk <= 1
        assert 0 <= result.total_score <= 1

    def test_score_stores_result(self):
        agent = ScorerAgent()
        agent.score("doc1", "test content", 0)
        retrieved = agent.get_score("doc1")
        assert retrieved is not None
        assert retrieved.document_id == "doc1"

    def test_get_score_nonexistent(self):
        agent = ScorerAgent()
        assert agent.get_score("nonexistent") is None

    def test_assess_novelty(self):
        agent = ScorerAgent()
        score = agent._assess_novelty("new novel unique original invention")
        assert score > 0
        assert score <= 1

    def test_assess_non_obviousness(self):
        agent = ScorerAgent()
        score = agent._assess_non_obviousness("complex advanced sophisticated")
        assert score > 0
        assert score <= 1

    def test_assess_utility(self):
        agent = ScorerAgent()
        score = agent._assess_utility("useful practical functional beneficial")
        assert score > 0
        assert score <= 1

    def test_assess_prior_art_risk(self):
        agent = ScorerAgent()
        risk = agent._assess_prior_art_risk(5)
        assert risk == 0.5

    def test_prior_art_risk_capped(self):
        agent = ScorerAgent()
        risk = agent._assess_prior_art_risk(20)
        assert risk == 1.0

    def test_total_score_calculation(self):
        agent = ScorerAgent()
        result = agent.score("doc1", "new novel useful", 0)
        expected = (result.novelty_score + result.non_obviousness_score + result.utility_score - result.prior_art_risk) / 3
        assert abs(result.total_score - expected) < 0.01

    def test_total_score_bounds(self):
        agent = ScorerAgent()
        result = agent.score("doc1", "test", 100)
        assert 0 <= result.total_score <= 1

    def test_guardrail_agt_g1_no_direct_imports(self):
        """Verify AGT-G1 guardrail: no direct imports of other agents."""
        import inspect
        from src.agents.scorer_agent import ScorerAgent

        source = inspect.getsource(ScorerAgent)
        assert "from src.agents" not in source
