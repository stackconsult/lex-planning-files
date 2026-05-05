"""Tests for Ingest Agent."""

import pytest
from datetime import datetime
from src.agents.ingest_agent import IngestAgent, IngestResult


class TestIngestAgent:
    def test_ingest_document(self):
        agent = IngestAgent()
        result = agent.ingest("doc1", "test content for ingestion")
        assert result.document_id == "doc1"
        assert result.word_count > 0
        assert isinstance(result.processed_at, datetime)

    def test_ingest_stores_result(self):
        agent = IngestAgent()
        agent.ingest("doc1", "test content")
        retrieved = agent.get_ingest_result("doc1")
        assert retrieved is not None
        assert retrieved.document_id == "doc1"

    def test_get_ingest_result_nonexistent(self):
        agent = IngestAgent()
        assert agent.get_ingest_result("nonexistent") is None

    def test_list_documents(self):
        agent = IngestAgent()
        agent.ingest("doc1", "test")
        agent.ingest("doc2", "test")
        docs = agent.list_documents()
        assert len(docs) == 2
        assert "doc1" in docs
        assert "doc2" in docs

    def test_validate_content_valid(self):
        agent = IngestAgent()
        status = agent._validate_content("This is a valid document with enough content")
        assert status == "valid"

    def test_validate_content_empty(self):
        agent = IngestAgent()
        status = agent._validate_content("")
        assert status == "empty"

    def test_validate_content_invalid(self):
        agent = IngestAgent()
        status = agent._validate_content("short")
        assert status == "invalid"

    def test_guardrail_agt_g1_no_direct_imports(self):
        """Verify AGT-G1 guardrail: no direct imports of other agents."""
        import inspect
        from src.agents.ingest_agent import IngestAgent

        source = inspect.getsource(IngestAgent)
        assert "from src.agents" not in source
