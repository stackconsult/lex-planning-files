"""Text embedder using OpenAI text-embedding-3-large.

Generates 1536-dimensional embeddings for document chunks
to enable vector similarity search via pgvector/Qdrant.
"""
from typing import List, Optional
import os

from openai import AsyncOpenAI


class TextEmbedder:
    """Generate embeddings using OpenAI text-embedding-3-large."""

    def __init__(self, model: str = "text-embedding-3-large"):
        """Initialize OpenAI embedder."""
        self.model = model
        self.embedding_dim = 1536
        self.client: Optional[AsyncOpenAI] = None

    def _get_client(self) -> AsyncOpenAI:
        """Get or create OpenAI client."""
        if not self.client:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            self.client = AsyncOpenAI(api_key=api_key)
        return self.client

    async def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text chunk."""
        client = self._get_client()

        response = await client.embeddings.create(
            model=self.model,
            input=text,
            dimensions=self.embedding_dim,
        )

        return response.data[0].embedding

    async def embed_batch(
        self, texts: List[str], batch_size: int = 100
    ) -> List[List[float]]:
        """Generate embeddings for multiple text chunks in batches."""
        client = self._get_client()
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = await client.embeddings.create(
                model=self.model,
                input=batch,
                dimensions=self.embedding_dim,
            )
            batch_embeddings = [item.embedding for item in response.data]
            embeddings.extend(batch_embeddings)

        return embeddings

    async def close(self):
        """Close OpenAI client."""
        if self.client:
            await self.client.close()
