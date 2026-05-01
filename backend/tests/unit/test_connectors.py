"""Unit tests for document connectors."""
import pytest

from src.connectors.github import GitHubConnector
from src.connectors.uspto import USPTOConnector
from src.connectors import ConnectorConfig


@pytest.mark.unit
class TestGitHubConnector:
    """Test GitHub connector interface."""

    def test_initialization(self):
        """Test connector initialization."""
        config = ConnectorConfig(
            source_name="GitHub",
            base_url="https://api.github.com",
            api_key="test_key",
        )
        connector = GitHubConnector(config)
        assert connector.config.source_name == "GitHub"
        assert connector.config.api_key == "test_key"

    def test_get_document_metadata(self):
        """Test metadata extraction."""
        config = ConnectorConfig(source_name="GitHub", base_url="https://api.github.com")
        connector = GitHubConnector(config)
        
        doc = {
            "external_id": "gh-12345",
            "title": "test/repo",
        }
        metadata = connector.get_document_metadata(doc)
        assert metadata["source"] == "GitHub"
        assert metadata["external_id"] == "gh-12345"


@pytest.mark.unit
class TestUSPTOConnector:
    """Test USPTO connector interface."""

    def test_initialization(self):
        """Test USPTO connector initialization."""
        config = ConnectorConfig(
            source_name="USPTO",
            base_url="https://developer.uspto.gov",
            api_key="test_key",
        )
        connector = USPTOConnector(config)
        assert connector.config.source_name == "USPTO"
