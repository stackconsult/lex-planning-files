"""Tests for Search Agent."""

import pytest
from src.agents.search_agent import SearchAgent, SearchResult


class TestSearchAgent:
    def test_index_document(self):
        agent = SearchAgent()
        agent.index_document("doc1", "test content")
        assert agent.get_document("doc1") == "test content"

    def test_search_returns_results(self):
        agent = SearchAgent()
        agent.index_document("doc1", "patent invention")
        results = agent.search("patent")
        assert len(results) > 0
        assert results[0].document_id == "doc1"

    def test_search_respects_top_k(self):
        agent = SearchAgent()
        agent.index_document("doc1", "patent invention")
        agent.index_document("doc2", "patent application")
        results = agent.search("patent", top_k=1)
        assert len(results) == 1

    def test_search_no_results(self):
        agent = SearchAgent()
        agent.index_document("doc1", "test content")
        results = agent.search("nonexistent")
        assert len(results) == 0

    def test_get_document_nonexistent(self):
        agent = SearchAgent()
        assert agent.get_document("nonexistent") is None

    def test_relevance_calculation(self):
        agent = SearchAgent()
        score = agent._calculate_relevance("patent invention", "patent invention test")
        assert score > 0
        assert score <= 1

    def test_guardrail_agt_g1_no_direct_imports(self):
        """Verify AGT-G1 guardrail: no direct imports of other agents."""
        import inspect
        from src.agents.search_agent import SearchAgent

        source = inspect.getsource(SearchAgent)
        assert "from src.agents" not in source
