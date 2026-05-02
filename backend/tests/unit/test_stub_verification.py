"""Test verification for NotImplementedError in stub methods."""
import pytest
from uuid import UUID
from src.api.services.lexradar_service import LexRadarService
from src.api.services.mcp_service import MCPService
from src.api.schemas import DisclosureRequest


def test_lexradar_search_prior_art_raises_not_implemented():
    """Verify search_prior_art raises NotImplementedError."""
    service = LexRadarService()
    with pytest.raises(NotImplementedError, match="Parallel prior art search"):
        service.search_prior_art(
            tenant_id="test-tenant",
            invention_id=UUID("00000000-0000-0000-0000-000000000001"),
            sources=["github"],
            max_results=10,
        )


def test_lexradar_generate_disclosure_raises_not_implemented():
    """Verify generate_disclosure raises NotImplementedError."""
    service = LexRadarService()
    with pytest.raises(NotImplementedError, match="Disclosure generation"):
        service.generate_disclosure(
            tenant_id="test-tenant",
            invention_id=UUID("00000000-0000-0000-0000-000000000001"),
            request=DisclosureRequest(
                disclosure_type="provisional",
                sections=[],
            ),
        )


def test_lexradar_package_filing_bundle_raises_not_implemented():
    """Verify package_filing_bundle raises NotImplementedError."""
    service = LexRadarService()
    with pytest.raises(NotImplementedError, match="Filing bundle packaging"):
        service.package_filing_bundle(
            tenant_id="test-tenant",
            invention_id=UUID("00000000-0000-0000-0000-000000000001"),
        )


def test_mcp_research_task_raises_not_implemented():
    """Verify research_task raises NotImplementedError."""
    service = MCPService()
    with pytest.raises(NotImplementedError, match="Research pipeline"):
        service.research_task(
            question="test question",
            jurisdiction="US",
            tenant_id="test-tenant",
        )
