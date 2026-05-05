"""Tests for Cite Agent."""

import pytest
from src.agents.cite_agent import CiteAgent, Citation


class TestCiteAgent:
    def test_add_citation(self):
        agent = CiteAgent()
        citation = agent.add_citation("doc1", "USPTO", "Patent #12345")
        assert citation.source == "USPTO"
        assert citation.reference == "Patent #12345"
        assert "cite_doc1" in citation.citation_id

    def test_add_citation_stores(self):
        agent = CiteAgent()
        agent.add_citation("doc1", "USPTO", "Patent #12345")
        citations = agent.get_citations("doc1")
        assert len(citations) == 1
        assert citations[0].source == "USPTO"

    def test_get_citations_nonexistent(self):
        agent = CiteAgent()
        citations = agent.get_citations("nonexistent")
        assert len(citations) == 0

    def test_get_citation_count(self):
        agent = CiteAgent()
        agent.add_citation("doc1", "USPTO", "Patent #1")
        agent.add_citation("doc1", "EPO", "Patent #2")
        count = agent.get_citation_count("doc1")
        assert count == 2

    def test_get_citation_count_nonexistent(self):
        agent = CiteAgent()
        count = agent.get_citation_count("nonexistent")
        assert count == 0

    def test_multiple_documents(self):
        agent = CiteAgent()
        agent.add_citation("doc1", "USPTO", "Patent #1")
        agent.add_citation("doc2", "EPO", "Patent #2")
        assert len(agent.get_citations("doc1")) == 1
        assert len(agent.get_citations("doc2")) == 1

    def test_guardrail_agt_g1_no_direct_imports(self):
        """Verify AGT-G1 guardrail: no direct imports of other agents."""
        import inspect
        from src.agents.cite_agent import CiteAgent

        source = inspect.getsource(CiteAgent)
        assert "from src.agents" not in source
