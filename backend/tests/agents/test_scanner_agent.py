"""Tests for Scanner Agent."""

import pytest
from src.agents.scanner_agent import ScannerAgent, ScanResult


class TestScannerAgent:
    def test_scan_document(self):
        agent = ScannerAgent()
        result = agent.scan("doc1", "test content with abstract and confidential")
        assert result.document_id == "doc1"
        assert isinstance(result.issues, list)
        assert 0 <= result.compliance_score <= 1

    def test_scan_stores_result(self):
        agent = ScannerAgent()
        agent.scan("doc1", "test content")
        retrieved = agent.get_scan_result("doc1")
        assert retrieved is not None
        assert retrieved.document_id == "doc1"

    def test_get_scan_result_nonexistent(self):
        agent = ScannerAgent()
        assert agent.get_scan_result("nonexistent") is None

    def test_detect_issues_short_document(self):
        agent = ScannerAgent()
        issues = agent._detect_issues("short")
        assert "Document too short" in issues

    def test_detect_issues_missing_confidentiality(self):
        agent = ScannerAgent()
        issues = agent._detect_issues("This is a test document without confidentiality")
        assert "Missing confidentiality notice" in issues

    def test_detect_issues_missing_abstract(self):
        agent = ScannerAgent()
        issues = agent._detect_issues("This is a test document without abstract section")
        assert "Missing abstract section" in issues

    def test_calculate_compliance_no_issues(self):
        agent = ScannerAgent()
        score = agent._calculate_compliance([])
        assert score == 1.0

    def test_calculate_compliance_with_issues(self):
        agent = ScannerAgent()
        score = agent._calculate_compliance(["issue1", "issue2"])
        assert score == 0.8

    def test_guardrail_agt_g1_no_direct_imports(self):
        """Verify AGT-G1 guardrail: no direct imports of other agents."""
        import inspect
        from src.agents.scanner_agent import ScannerAgent

        source = inspect.getsource(ScannerAgent)
        assert "from src.agents" not in source
