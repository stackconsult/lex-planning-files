"""Tests for Router Agent."""

import pytest
from src.agents.router_agent import RouterAgent, AgentType


class TestRouterAgent:
    def test_route_search_query(self):
        router = RouterAgent()
        result = router.route("search for patents")
        assert result == AgentType.SEARCH

    def test_route_analysis_query(self):
        router = RouterAgent()
        result = router.route("analyze this document")
        assert result == AgentType.ANALYSIS

    def test_route_draft_query(self):
        router = RouterAgent()
        result = router.route("draft a patent application")
        assert result == AgentType.DRAFT

    def test_route_ingest_query(self):
        router = RouterAgent()
        result = router.route("ingest new documents")
        assert result == AgentType.INGEST

    def test_route_no_match(self):
        router = RouterAgent()
        result = router.route("unknown request")
        assert result is None

    def test_get_agent_priority(self):
        router = RouterAgent()
        assert router.get_agent_priority(AgentType.SEARCH) == 1
        assert router.get_agent_priority(AgentType.ANALYSIS) == 2
        assert router.get_agent_priority(AgentType.DRAFT) == 3

    def test_guardrail_agt_g1_no_direct_imports(self):
        """Verify AGT-G1 guardrail: no direct imports of other agents."""
        import inspect
        from src.agents.router_agent import RouterAgent

        source = inspect.getsource(RouterAgent)
        assert "from src.agents" not in source
        assert "import" not in source or "typing" in source or "enum" in source
