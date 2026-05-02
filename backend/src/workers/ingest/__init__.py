"""Ingest worker for document ingestion pipeline.

Processes document fetch, parse, chunk, embed, and store tasks
from the connector outputs.
"""
import logging
from typing import Dict, Any

from src.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="src.workers.ingest.fetch_and_parse",
    queue="ingest",
    bind=True,
    max_retries=3,
)
def fetch_and_parse(self, connector_config: Dict[str, Any], query: str) -> Dict[str, Any]:
    """Fetch and parse documents from connector."""
    import asyncio
    from src.connectors import ConnectorConfig
    from src.core.parser import DocumentParser

    config = ConnectorConfig(**connector_config)
    connector_class = _get_connector_class(config.source_name)
    if not connector_class:
        raise ValueError(f"Unknown connector source: {config.source_name}")

    connector = connector_class(config)
    parser = DocumentParser()
    documents_processed = 0

    async def _run():
        nonlocal documents_processed
        try:
            async for raw_doc in connector.fetch_documents(query=query):
                parsed = await connector.parse_document(raw_doc)
                metadata = connector.get_document_metadata(parsed)
                documents_processed += 1
            return {"status": "completed", "documents_processed": documents_processed}
        except Exception as e:
            logger.error(f"Fetch and parse failed: {e}")
            raise self.retry(exc=e, countdown=60)
        finally:
            await connector.close()

    try:
        return asyncio.run(_run())
    except Exception as e:
        logger.error(f"Fetch and parse failed: {e}")
        raise


@celery_app.task(
    name="src.workers.ingest.chunk_and_embed",
    queue="ingest",
    bind=True,
    max_retries=3,
)
def chunk_and_embed(self, document: Dict[str, Any]) -> Dict[str, Any]:
    """Chunk document and generate embeddings."""
    import asyncio
    from src.core.chunker import DocumentChunker
    from src.core.embedder import TextEmbedder

    chunker = DocumentChunker(chunk_size=512, chunk_overlap=50)
    embedder = TextEmbedder()

    async def _run():
        try:
            chunks = await chunker.chunk_document(document, strategy="hierarchical")
            embeddings = await embedder.embed_batch(chunks)
            return {"status": "completed", "chunks_created": len(chunks)}
        except Exception as e:
            logger.error(f"Chunk and embed failed: {e}")
            raise self.retry(exc=e, countdown=60)

    try:
        return asyncio.run(_run())
    except Exception as e:
        logger.error(f"Chunk and embed failed: {e}")
        raise


def _get_connector_class(source_name: str):
    """Get connector class by source name."""
    from src.connectors.github import GitHubConnector
    from src.connectors.uspto import USPTOConnector
    from src.connectors.wipo import WIPOConnector
    from src.connectors.epo import EPOConnector
    from src.connectors.pacer import PACERConnector
    from src.connectors.sec import SECConnector
    from src.connectors.state import StateConnector

    mapping = {
        "GitHub": GitHubConnector,
        "USPTO": USPTOConnector,
        "WIPO": WIPOConnector,
        "EPO": EPOConnector,
        "PACER": PACERConnector,
        "SEC": SECConnector,
        "State": StateConnector,
    }
    return mapping.get(source_name)
