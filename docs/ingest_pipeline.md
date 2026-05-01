# HORDE-INGEST: Chunking and Embedding Pipeline

**Phase:** P1 — LexCore DB
**Horde:** HORDE-INGEST
**Status:** ⏳ PENDING (Schema + Infrastructure required)

---

## Pipeline Overview

```
Raw Document (HTML/XML/PDF)
    ↓
[Docling Parser] → Structured Document + Metadata
    ↓
[Hierarchical Chunker] → Sections → Paragraphs → Sentences
    ↓
[Token Counter] → Filter chunks by token count (max 512)
    ↓
[Deduplication] → Semantic dedup via embedding cache
    ↓
[Embedding Generator] → OpenAI text-embedding-3-large (1536-dim)
    ↓
[Vector Store] → Qdrant HNSW index
    ↓
[Relational Store] → PostgreSQL legal_chunks table
```

---

## Stage 1: Document Parsing

### Docling Document Converter

```python
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat

class DocumentParser:
    """Parse legal documents from various formats."""
    
    SUPPORTED_FORMATS = [
        InputFormat.HTML,
        InputFormat.PDF,
        InputFormat.MARKDOWN,
        InputFormat.TEXT,
    ]
    
    def __init__(self):
        self.converter = DocumentConverter(
            allowed_formats=self.SUPPORTED_FORMATS,
        )
    
    async def parse(
        self,
        content: str,
        content_type: InputFormat,
        source_url: str,
    ) -> ParsedDocument:
        """Parse document and extract structured content."""
        result = await self.converter.convert_async(
            content,
            input_format=content_type,
        )
        
        doc = result.document
        
        return ParsedDocument(
            title=doc.title or "Untitled",
            title_fr=self._extract_french_title(doc),
            full_text=doc.text,
            metadata={
                "source_url": source_url,
                "language": doc.language or "en",
                "page_count": len(doc.pages),
                "author": doc.author,
            },
            sections=self._extract_sections(doc),
        )
    
    def _extract_french_title(self, doc) -> Optional[str]:
        """Extract French title from bilingual documents."""
        # Check for alternate language titles
        for alt_title in doc.alternate_titles:
            if alt_title.language == "fr":
                return alt_title.text
        return None
    
    def _extract_sections(self, doc) -> list[DocumentSection]:
        """Extract hierarchical sections from document."""
        sections = []
        for heading in doc.headings:
            sections.append(DocumentSection(
                level=heading.level,
                title=heading.text,
                path=self._build_section_path(heading),
            ))
        return sections
```

---

## Stage 2: Hierarchical Chunking

### Chunking Strategy

Legal documents have deep hierarchical structure:
```
Title → Chapter → Part → Subpart → Section → Subsection → Paragraph
```

We chunk at multiple levels to support different query granularities:

1. **Section-level chunks** (~512 tokens) — For general search
2. **Paragraph-level chunks** (~128 tokens) — For precise citation
3. **Sentence-level chunks** (~32 tokens) — For exact phrase matching

### Chunking Algorithm

```python
from dataclasses import dataclass
from typing import Iterator

@dataclass
class Chunk:
    text: str
    section_path: str  # "Title 1 > Chapter 2 > Part A > Section 3"
    chunk_order: int
    token_count: int
    level: int  # 0=title, 1=chapter, 2=section, 3=paragraph
    parent_id: Optional[UUID] = None


class HierarchicalChunker:
    """Chunk legal documents hierarchically."""
    
    def __init__(
        self,
        max_chunk_tokens: int = 512,
        overlap_tokens: int = 50,
        respect_page_breaks: bool = True,
    ):
        self.max_chunk_tokens = max_chunk_tokens
        self.overlap_tokens = overlap_tokens
        self.respect_page_breaks = respect_page_breaks
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def chunk(self, parsed_doc: ParsedDocument) -> Iterator[Chunk]:
        """Generate hierarchical chunks from parsed document."""
        sections = self._build_section_tree(parsed_doc.sections)
        
        for section in sections:
            # Generate section-level chunk
            section_text = self._extract_section_text(section)
            section_tokens = self._count_tokens(section_text)
            
            if section_tokens <= self.max_chunk_tokens:
                yield Chunk(
                    text=section_text,
                    section_path=section.path,
                    chunk_order=0,
                    token_count=section_tokens,
                    level=section.level,
                )
            else:
                # Split section into paragraph-level chunks
                yield from self._chunk_by_paragraphs(section)
    
    def _chunk_by_paragraphs(self, section) -> Iterator[Chunk]:
        """Split section into paragraph-level chunks."""
        paragraphs = section.paragraphs
        current_chunk = []
        current_tokens = 0
        chunk_order = 0
        
        for paragraph in paragraphs:
            para_tokens = self._count_tokens(paragraph.text)
            
            if current_tokens + para_tokens > self.max_chunk_tokens:
                # Yield current chunk
                if current_chunk:
                    yield Chunk(
                        text="\n\n".join(p.text for p in current_chunk),
                        section_path=section.path,
                        chunk_order=chunk_order,
                        token_count=current_tokens,
                        level=section.level + 1,
                    )
                    chunk_order += 1
                
                # Start new chunk with overlap
                overlap = self._get_overlap(current_chunk)
                current_chunk = overlap + [paragraph]
                current_tokens = sum(
                    self._count_tokens(p.text) for p in current_chunk
                )
            else:
                current_chunk.append(paragraph)
                current_tokens += para_tokens
        
        # Yield final chunk
        if current_chunk:
            yield Chunk(
                text="\n\n".join(p.text for p in current_chunk),
                section_path=section.path,
                chunk_order=chunk_order,
                token_count=current_tokens,
                level=section.level + 1,
            )
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens using cl100k_base encoding."""
        return len(self.tokenizer.encode(text))
    
    def _get_overlap(self, chunks: list) -> list:
        """Get overlapping paragraphs for continuity."""
        if not chunks or self.overlap_tokens == 0:
            return []
        
        overlap = []
        overlap_tokens = 0
        
        for chunk in reversed(chunks):
            chunk_tokens = self._count_tokens(chunk.text)
            if overlap_tokens + chunk_tokens <= self.overlap_tokens:
                overlap.insert(0, chunk)
                overlap_tokens += chunk_tokens
            else:
                break
        
        return overlap
```

---

## Stage 3: Embedding Generation

### OpenAI Embedding Service

```python
from openai import AsyncOpenAI
import asyncio
from typing import Iterator

class EmbeddingService:
    """Generate embeddings for text chunks."""
    
    MODEL = "text-embedding-3-large"
    DIMENSIONS = 1536
    MAX_BATCH_SIZE = 100  # OpenAI batch limit
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def embed_chunks(
        self,
        chunks: list[Chunk],
    ) -> list[EmbeddedChunk]:
        """Generate embeddings for chunks in batches."""
        results = []
        
        for batch in self._batch_chunks(chunks, self.MAX_BATCH_SIZE):
            texts = [chunk.text for chunk in batch]
            
            response = await self.client.embeddings.create(
                model=self.MODEL,
                input=texts,
                dimensions=self.DIMENSIONS,
                encoding_format="float",
            )
            
            for chunk, embedding_data in zip(batch, response.data):
                results.append(EmbeddedChunk(
                    chunk=chunk,
                    embedding=embedding_data.embedding,
                    model=self.MODEL,
                ))
        
        return results
    
    def _batch_chunks(
        self,
        chunks: list[Chunk],
        batch_size: int,
    ) -> Iterator[list[Chunk]]:
        """Yield chunks in batches."""
        for i in range(0, len(chunks), batch_size):
            yield chunks[i:i + batch_size]
```

### Embedding Cache

```python
import hashlib
from redis import Redis

class EmbeddingCache:
    """Cache embeddings to avoid re-computation."""
    
    def __init__(self, redis: Redis):
        self.redis = redis
        self.ttl = 86400 * 30  # 30 days
    
    def _make_key(self, text: str, model: str) -> str:
        """Create cache key from text hash and model."""
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        return f"embedding:{model}:{text_hash}"
    
    async def get(self, text: str, model: str) -> Optional[list[float]]:
        """Get cached embedding."""
        key = self._make_key(text, model)
        cached = await self.redis.get(key)
        if cached:
            import json
            return json.loads(cached)
        return None
    
    async def set(self, text: str, model: str, embedding: list[float]):
        """Cache embedding."""
        key = self._make_key(text, model)
        import json
        await self.redis.setex(
            key,
            self.ttl,
            json.dumps(embedding),
        )
```

---

## Stage 4: Vector Store (Qdrant)

### Qdrant Integration

```python
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    HnswConfigDiff,
)

class QdrantVectorStore:
    """Store and search vector embeddings in Qdrant."""
    
    COLLECTIONS = {
        "legal_chunks": VectorParams(size=1536, distance=Distance.COSINE),
        "prior_art": VectorParams(size=1536, distance=Distance.COSINE),
    }
    
    def __init__(self, url: str, api_key: Optional[str] = None):
        self.client = AsyncQdrantClient(url=url, api_key=api_key)
    
    async def initialize(self):
        """Create collections if they don't exist."""
        for name, params in self.COLLECTIONS.items():
            try:
                await self.client.create_collection(
                    collection_name=name,
                    vectors_config=params,
                    hnsw_config=HnswConfigDiff(
                        m=16,
                        ef_construct=100,
                    ),
                )
            except Exception as e:
                if "already exists" not in str(e):
                    raise
    
    async def upsert_chunks(
        self,
        tenant_id: UUID,
        document_id: UUID,
        chunks: list[EmbeddedChunk],
    ):
        """Store chunks in Qdrant with tenant isolation."""
        points = []
        for i, chunk in enumerate(chunks):
            points.append(PointStruct(
                id=f"{tenant_id}:{document_id}:{i}",
                vector=chunk.embedding,
                payload={
                    "tenant_id": str(tenant_id),
                    "document_id": str(document_id),
                    "section_path": chunk.chunk.section_path,
                    "chunk_order": chunk.chunk.chunk_order,
                    "token_count": chunk.chunk.token_count,
                    "text_preview": chunk.chunk.text[:200],
                },
            ))
        
        await self.client.upsert(
            collection_name="legal_chunks",
            points=points,
        )
    
    async def search(
        self,
        tenant_id: UUID,
        query_vector: list[float],
        limit: int = 10,
        filters: Optional[dict] = None,
    ) -> list[dict]:
        """Search chunks by vector similarity with tenant filter."""
        # Build tenant isolation filter
        must_filter = {
            "must": [
                {"key": "tenant_id", "match": {"value": str(tenant_id)}}
            ]
        }
        
        if filters:
            must_filter["must"].extend(filters)
        
        results = await self.client.search(
            collection_name="legal_chunks",
            query_vector=query_vector,
            limit=limit,
            query_filter=must_filter,
        )
        
        return [
            {
                "id": result.id,
                "score": result.score,
                "document_id": result.payload["document_id"],
                "section_path": result.payload["section_path"],
                "text_preview": result.payload["text_preview"],
            }
            for result in results
        ]
```

---

## Stage 5: Relational Store (PostgreSQL)

### Async Database Layer

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

class DatabaseStore:
    """Store documents and chunks in PostgreSQL."""
    
    def __init__(self, database_url: str):
        self.engine = create_async_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            echo=False,
        )
        self.session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    
    async def store_document(
        self,
        tenant_id: UUID,
        document: LegalDocumentCreate,
    ) -> LegalDocument:
        """Store document in PostgreSQL."""
        async with self.session_factory() as session:
            # Set tenant context for RLS
            await session.execute(
                text("SELECT set_tenant_context(:tenant_id)"),
                {"tenant_id": tenant_id},
            )
            
            # Insert document
            result = await session.execute(
                insert(LegalDocumentTable).values(
                    tenant_id=tenant_id,
                    **document.model_dump(),
                ).returning(LegalDocumentTable),
            )
            
            await session.commit()
            return LegalDocument.model_validate(result.scalar_one())
    
    async def store_chunks(
        self,
        tenant_id: UUID,
        document_id: UUID,
        chunks: list[EmbeddedChunk],
    ) -> list[LegalChunk]:
        """Store chunks in PostgreSQL."""
        async with self.session_factory() as session:
            await session.execute(
                text("SELECT set_tenant_context(:tenant_id)"),
                {"tenant_id": tenant_id},
            )
            
            chunk_data = [
                {
                    "tenant_id": tenant_id,
                    "document_id": document_id,
                    "section_path": chunk.chunk.section_path,
                    "chunk_order": chunk.chunk.chunk_order,
                    "chunk_text": chunk.chunk.text,
                    "embedding": chunk.embedding,
                    "token_count": chunk.chunk.token_count,
                    "chunk_quality_score": 1.0,  # Placeholder
                }
                for chunk in chunks
            ]
            
            result = await session.execute(
                insert(LegalChunkTable).values(chunk_data)
                .returning(LegalChunkTable),
            )
            
            await session.commit()
            return [LegalChunk.model_validate(row) for row in result.scalars().all()]
```

---

## Stage 6: Full Pipeline Orchestration

### Celery Task Definitions

```python
from celery import Celery
from celery.signals import task_failure

app = Celery("lexcore_ingest")
app.config_from_object({
    "broker_url": "redis://redis:6379/0",
    "result_backend": "redis://redis:6379/0",
    "task_serializer": "json",
    "accept_content": ["json"],
    "result_serializer": "json",
    "timezone": "UTC",
    "enable_utc": True,
    "task_track_started": True,
    "task_time_limit": 3600,  # 1 hour max
    "worker_prefetch_multiplier": 1,
    "task_acks_late": True,
})

@app.task(bind=True, max_retries=3)
def ingest_document(self, tenant_id: str, source: str, doc_id: str):
    """Ingest a single document through the full pipeline."""
    try:
        # 1. Fetch from source
        connector = get_connector(source)
        raw_doc = connector.fetch_document(doc_id)
        
        # 2. Parse with Docling
        parsed = DocumentParser().parse(raw_doc.content, raw_doc.format, raw_doc.url)
        
        # 3. Chunk hierarchically
        chunks = list(HierarchicalChunker().chunk(parsed))
        
        # 4. Generate embeddings
        embedded = asyncio.run(EmbeddingService().embed_chunks(chunks))
        
        # 5. Store in PostgreSQL
        doc = asyncio.run(DatabaseStore().store_document(
            UUID(tenant_id),
            LegalDocumentCreate(**parsed.to_dict()),
        ))
        
        # 6. Store chunks in PostgreSQL + Qdrant
        stored_chunks = asyncio.run(DatabaseStore().store_chunks(
            UUID(tenant_id), doc.id, embedded,
        ))
        
        asyncio.run(QdrantVectorStore().upsert_chunks(
            UUID(tenant_id), doc.id, embedded,
        ))
        
        return {
            "document_id": str(doc.id),
            "chunks_count": len(stored_chunks),
            "status": "success",
        }
    
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 60)


@app.task
def batch_ingest(tenant_id: str, source: str, doc_ids: list[str]):
    """Ingest multiple documents in parallel."""
    job = group(
        ingest_document.s(tenant_id, source, doc_id)
        for doc_id in doc_ids
    )
    result = job.apply_async()
    return result.id


@app.task
def scheduled_ingest():
    """Scheduled ingestion for all active connectors."""
    for connector_name in get_active_connectors():
        connector = get_connector(connector_name)
        new_docs = connector.check_for_updates()
        for doc in new_docs:
            ingest_document.delay(
                tenant_id=doc.tenant_id,
                source=connector_name,
                doc_id=doc.external_id,
            )
```

---

## Monitoring & Quality Metrics

### Ingestion Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|----------------|
| `ingest_duration_seconds` | Time per document | P95 > 300s |
| `ingest_errors_total` | Failed ingestions | > 5% error rate |
| `chunks_per_document` | Average chunks | < 1 (parsing failure) |
| `embedding_latency_seconds` | Embedding generation | P95 > 10s |
| `tokens_per_chunk` | Average chunk size | > 512 (truncation risk) |

### Quality Checks

1. **Parsing Quality:**
   - Title extracted (not "Untitled")
   - At least 1 chunk generated
   - Chunk text is meaningful (> 20 chars)

2. **Embedding Quality:**
   - Embedding vector has exactly 1536 dimensions
   - Vector is not all zeros (indicates failure)
   - Vector L2 norm is reasonable (~1.0 for normalized)

3. **Storage Quality:**
   - Document exists in PostgreSQL
   - All chunks exist in PostgreSQL
   - All chunks exist in Qdrant
   - RLS policies enforce tenant isolation
