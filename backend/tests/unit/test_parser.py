"""Unit tests for DocumentParser."""
import pytest

from src.core.parser import DocumentParser


@pytest.mark.unit
class TestDocumentParser:
    """Test document parsing functionality."""

    @pytest.fixture
    def parser(self):
        return DocumentParser()

    async def test_parse_text(self, parser):
        """Test plain text parsing."""
        text = "Test document content"
        result = await parser.parse_text(text)
        assert result["full_text"] == text

    async def test_parse_html(self, parser):
        """Test HTML parsing."""
        html = "<html><body>Test content</body></html>"
        result = await parser.parse_html(html)
        assert "sections" in result

    @pytest.mark.skip(reason="Docling integration pending")
    async def test_parse_pdf(self, parser):
        """Test PDF parsing."""
        # TODO: Implement with actual PDF file
        pass
