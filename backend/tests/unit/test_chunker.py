"""Unit tests for DocumentChunker."""
import pytest

from src.core.chunker import DocumentChunker


@pytest.mark.unit
class TestDocumentChunker:
    """Test document chunking functionality."""

    @pytest.fixture
    def chunker(self):
        return DocumentChunker(chunk_size=512, chunk_overlap=50)

    async def test_chunk_flat(self, chunker):
        """Test flat chunking."""
        doc = {
            "full_text": "Test document content. " * 100,
            "sections": [],
        }
        chunks = await chunker._chunk_flat(doc)
        assert len(chunks) > 0
        assert all("chunk_text" in chunk for chunk in chunks)

    async def test_chunk_hierarchical(self, chunker):
        """Test hierarchical chunking."""
        doc = {
            "full_text": "",
            "sections": [
                {
                    "title": "Section 1",
                    "content": "Test content " * 50,
                    "type": "BODY",
                    "path": "1",
                }
            ],
        }
        chunks = await chunker._chunk_hierarchical(doc)
        assert len(chunks) > 0

    def test_estimate_token_count(self, chunker):
        """Test token count estimation."""
        text = "Test text"
        count = chunker.estimate_token_count(text)
        assert count >= 0
