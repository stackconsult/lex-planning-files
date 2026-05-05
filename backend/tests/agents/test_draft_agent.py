"""Tests for Draft Agent."""

import pytest
from src.agents.draft_agent import DraftAgent, DraftResult


class TestDraftAgent:
    def test_draft_section(self):
        agent = DraftAgent()
        result = agent.draft_section("abstract", "test analysis")
        assert result.section == "abstract"
        assert result.content is not None
        assert result.word_count > 0

    def test_draft_section_stores_result(self):
        agent = DraftAgent()
        agent.draft_section("abstract", "test analysis")
        retrieved = agent.get_draft("abstract")
        assert retrieved is not None
        assert retrieved.section == "abstract"

    def test_get_draft_nonexistent(self):
        agent = DraftAgent()
        assert agent.get_draft("nonexistent") is None

    def test_list_sections(self):
        agent = DraftAgent()
        agent.draft_section("abstract", "test")
        agent.draft_section("claims", "test")
        sections = agent.list_sections()
        assert len(sections) == 2
        assert "abstract" in sections
        assert "claims" in sections

    def test_generate_content_abstract(self):
        agent = DraftAgent()
        content = agent._generate_content("abstract", "test analysis")
        assert "Abstract:" in content
        assert "test analysis" in content

    def test_generate_content_claims(self):
        agent = DraftAgent()
        content = agent._generate_content("claims", "test analysis")
        assert "Claims:" in content
        assert "1. A method" in content

    def test_guardrail_agt_g1_no_direct_imports(self):
        """Verify AGT-G1 guardrail: no direct imports of other agents."""
        import inspect
        from src.agents.draft_agent import DraftAgent

        source = inspect.getsource(DraftAgent)
        assert "from src.agents" not in source
