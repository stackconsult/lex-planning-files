"""Tests for PriorArt Agent."""

import pytest
from src.agents.prior_art_agent import PriorArtAgent, PriorArtResult


class TestPriorArtAgent:
    def test_search_prior_art(self):
        agent = PriorArtAgent()
        results = agent.search_prior_art("data processing")
        assert len(results) > 0
        assert all(isinstance(r, PriorArtResult) for r in results)

    def test_search_prior_art_no_results(self):
        agent = PriorArtAgent()
        results = agent.search_prior_art("nonexistent query")
        assert len(results) == 0

    def test_search_prior_art_similarity_threshold(self):
        agent = PriorArtAgent()
        results = agent.search_prior_art("data")
        assert all(r.similarity_score > 0.3 for r in results)

    def test_get_prior_art(self):
        agent = PriorArtAgent()
        result = agent.get_prior_art("US12345")
        assert result is not None
        assert result.patent_id == "US12345"

    def test_get_prior_art_nonexistent(self):
        agent = PriorArtAgent()
        result = agent.get_prior_art("nonexistent")
        assert result is None

    def test_calculate_similarity(self):
        agent = PriorArtAgent()
        score = agent._calculate_similarity("data processing", "method for data processing")
        assert score > 0
        assert score <= 1

    def test_search_results_sorted_by_similarity(self):
        agent = PriorArtAgent()
        results = agent.search_prior_art("data")
        if len(results) > 1:
            assert results[0].similarity_score >= results[1].similarity_score

    def test_guardrail_agt_g1_no_direct_imports(self):
        """Verify AGT-G1 guardrail: no direct imports of other agents."""
        import inspect
        from src.agents.prior_art_agent import PriorArtAgent

        source = inspect.getsource(PriorArtAgent)
        assert "from src.agents" not in source
