"""Document chunker for hierarchical text splitting.

Splits legal documents into chunks of ~512 tokens while preserving
section boundaries and citation context for vector search.
"""
from typing import List, Dict, Any, Optional
import re


class DocumentChunker:
    """Split documents into chunks for vector embedding and search."""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """Initialize chunker with size and overlap parameters."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    async def chunk_document(
        self,
        document: Dict[str, Any],
        preserve_hierarchy: bool = True,
    ) -> List[Dict[str, Any]]:
        """Chunk document into hierarchical sections."""
        if preserve_hierarchy:
            return await self._chunk_hierarchical(document)
        else:
            return await self._chunk_flat(document)

    async def _chunk_hierarchical(
        self, document: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Chunk document preserving section hierarchy."""
        chunks = []
        sections = document.get("sections", [])

        for i, section in enumerate(sections):
            section_chunks = await self._chunk_section(section, section_index=i)
            chunks.extend(section_chunks)

        return chunks

    async def _chunk_section(
        self, section: Dict[str, Any], section_index: int
    ) -> List[Dict[str, Any]]:
        """Chunk a single section into smaller pieces."""
        text = section.get("content", "")
        title = section.get("title", "")

        # Split text by paragraphs
        paragraphs = re.split(r"\n\s*\n", text)

        chunks = []
        current_chunk = ""
        chunk_order = 0

        for para in paragraphs:
            # Estimate tokens (rough approximation: 1 token ~ 4 characters)
            para_tokens = len(para) // 4
            current_tokens = len(current_chunk) // 4

            if current_tokens + para_tokens > self.chunk_size:
                if current_chunk:
                    chunks.append({
                        "section_path": f"{section.get('path', '')}",
                        "chunk_order": chunk_order,
                        "chunk_text": current_chunk,
                        "chunk_type": section.get("type", "BODY"),
                    })
                    chunk_order += 1
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para

        # Add final chunk
        if current_chunk:
            chunks.append({
                "section_path": f"{section.get('path', '')}",
                "chunk_order": chunk_order,
                "chunk_text": current_chunk,
                "chunk_type": section.get("type", "BODY"),
            })

        return chunks

    async def _chunk_flat(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Chunk document without preserving hierarchy."""
        text = document.get("full_text", "")
        chunks = []

        # Simple sliding window chunking
        for i in range(0, len(text), self.chunk_size * 4):
            chunk_text = text[i : i + self.chunk_size * 4]
            chunks.append({
                "section_path": "",
                "chunk_order": i // (self.chunk_size * 4),
                "chunk_text": chunk_text,
                "chunk_type": "FLAT",
            })

        return chunks

    def estimate_token_count(self, text: str) -> int:
        """Estimate token count (rough approximation)."""
        return len(text) // 4
