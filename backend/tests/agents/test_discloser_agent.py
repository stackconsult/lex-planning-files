"""Tests for Discloser Agent."""

import pytest
from src.agents.discloser_agent import DiscloserAgent, DisclosureRequirement


class TestDiscloserAgent:
    def test_get_requirements(self):
        agent = DiscloserAgent()
        requirements = agent.get_requirements("doc1")
        assert len(requirements) > 0
        assert all(isinstance(req, DisclosureRequirement) for req in requirements)

    def test_requirements_initialized(self):
        agent = DiscloserAgent()
        requirements = agent.get_requirements("doc1")
        assert any(req.name == "Prior Art Disclosure" for req in requirements)
        assert any(req.name == "Inventorship Disclosure" for req in requirements)
        assert any(req.name == "Funding Disclosure" for req in requirements)

    def test_update_requirement_status(self):
        agent = DiscloserAgent()
        agent.get_requirements("doc1")
        agent.update_requirement_status("doc1", "DISC001", "completed")
        requirements = agent.get_requirements("doc1")
        req = next(r for r in requirements if r.requirement_id == "DISC001")
        assert req.status == "completed"

    def test_get_completion_status(self):
        agent = DiscloserAgent()
        agent.get_requirements("doc1")
        agent.update_requirement_status("doc1", "DISC001", "completed")
        completion = agent.get_completion_status("doc1")
        assert completion > 0
        assert completion <= 1

    def test_get_completion_status_empty(self):
        agent = DiscloserAgent()
        completion = agent.get_completion_status("doc1")
        assert completion == 0.0

    def test_get_missing_disclosures(self):
        agent = DiscloserAgent()
        agent.get_requirements("doc1")
        agent.update_requirement_status("doc1", "DISC001", "completed")
        missing = agent.get_missing_disclosures("doc1")
        assert len(missing) > 0
        assert all(req.status == "pending" for req in missing)

    def test_get_missing_disclosures_all_completed(self):
        agent = DiscloserAgent()
        requirements = agent.get_requirements("doc1")
        for req in requirements:
            agent.update_requirement_status("doc1", req.requirement_id, "completed")
        missing = agent.get_missing_disclosures("doc1")
        assert len(missing) == 0

    def test_guardrail_agt_g1_no_direct_imports(self):
        """Verify AGT-G1 guardrail: no direct imports of other agents."""
        import inspect
        from src.agents.discloser_agent import DiscloserAgent

        source = inspect.getsource(DiscloserAgent)
        assert "from src.agents" not in source
