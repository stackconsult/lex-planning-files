# HORDE-INGEST: Connector Specifications
**9 Legal Document Connectors for LexCore**

> **Schema Version:** v0.1.0-foundation
> **Horde:** HORDE-INGEST
> **Status:** ⏳ PENDING (Schema + Infrastructure required)

---

## Connector Architecture

All connectors implement the `BaseConnector` interface and follow the same pipeline:

```
1. FETCH → HTTP request to source API
2. PARSE → Extract structured data (Docling parser)
3. TRANSFORM → Normalize to legal_documents schema
4. CHUNK → Split into legal_chunks (hierarchical)
5. EMBED → Generate 1536-dim OpenAI embeddings
6. STORE → Insert into PostgreSQL with tenant_id
7. INDEX → Add to Qdrant vector index
```

## Base Connector Interface

```python
from abc import ABC, abstractmethod
from datetime import datetime
from typing import AsyncIterator, Optional
from pydantic import BaseModel

class ConnectorConfig(BaseModel):
    source_name: str
    api_key: Optional[str] = None
    base_url: str
    rate_limit_per_minute: int = 60
    retry_attempts: int = 3
    timeout_seconds: int = 30
    tenant_id: Optional[str] = None  # For multi-tenant connectors

class BaseConnector(ABC):
    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.last_fetch: Optional[datetime] = None
    
    @abstractmethod
    async def fetch_documents(
        self,
        jurisdiction: Optional[str] = None,
        body_of_law: Optional[str] = None,
        since_date: Optional[datetime] = None,
    ) -> AsyncIterator[dict]:
        """Yield raw documents from source."""
        pass
    
    @abstractmethod
    async def parse_document(self, raw_doc: dict) -> dict:
        """Parse raw document into normalized schema."""
        pass
    
    @abstractmethod
    def get_document_metadata(self, doc: dict) -> dict:
        """Extract metadata for legal_documents table."""
        pass
```

---

## Connector 1: eCFR (US Code of Federal Regulations)

**Source:** `https://www.ecfr.gov/api/`
**Jurisdiction:** J_US_FED
**Body of Law:** REGULATION
**API Type:** REST JSON
**Authentication:** None (public)

### Configuration
```python
ecfr_config = ConnectorConfig(
    source_name="eCFR",
    base_url="https://www.ecfr.gov/api",
    rate_limit_per_minute=120,
)
```

### Endpoints
- `GET /api/versioner/v1/full/{date}/title-{title}.json` — Full title content
- `GET /api/search/v1/results` — Search by query
- `GET /api/admin/v1/agencies.json` — Agency listing

### Document Structure
- **Title:** eCFR Title number + subtitle
- **Citation:** `CFR {title}.{part}.{section}`
- **Body:** HTML content (strip tags for full_text)
- **Effective Date:** Available in metadata
- **Source URL:** eCFR permalink

### Parsing Rules
1. Strip HTML tags from body text
2. Extract hierarchical structure: Title → Chapter → Part → Subpart → Section
3. Citation format: `CFR {title} {part}.{section}`
4. Jurisdiction: `J_US_FED`

### Rate Limiting
- Max 120 requests/minute (eCFR public limit)
- Batch processing: 1 title per request
- Retry: Exponential backoff on 429

---

## Connector 2: CanLII (Canadian Legal Information Institute)

**Source:** `https://api.canlii.org/v1/`
**Jurisdiction:** J_CA_FED, J_CA_PROV
**Body of Law:** STATUTE, REGULATION, CASE
**API Type:** REST JSON
**Authentication:** API Key required

### Configuration
```python
canlii_config = ConnectorConfig(
    source_name="CanLII",
    base_url="https://api.canlii.org/v1",
    api_key="${CANLII_API_KEY}",
    rate_limit_per_minute=30,
)
```

### Endpoints
- `GET /caseBrowse/en/{database}/` — Browse cases
- `GET /legislationBrowse/en/{database}/` — Browse legislation
- `GET /caseBrowse/en/{database}/{caseId}` — Case details
- `GET /legislationBrowse/en/{database}/{legislationId}` — Legislation details

### Document Structure
- **Title:** Case name or statute title (bilingual: EN + FR)
- **Citation:** CanLII citation format
- **Body:** HTML or plain text
- **Effective Date:** Decision date (cases) or enactment date (statutes)
- **Bilingual:** Store both `title` and `title_fr`

### Parsing Rules
1. Extract both English and French titles when available
2. Case citations: `[Year] CanLII {id} ({court})`
3. Statute citations: `{short_title}, {chapter}, {jurisdiction}`
4. Jurisdiction mapping: `ca` → J_CA_FED, `{prov_code}` → J_CA_{PROV}

### Rate Limiting
- Max 30 requests/minute (CanLII limit)
- Requires valid API key

---

## Connector 3: CourtListener (US Federal Courts)

**Source:** `https://www.courtlistener.com/api/rest/v3/`
**Jurisdiction:** J_US_FED
**Body of Law:** CASE
**API Type:** REST JSON (Django REST Framework)
**Authentication:** API Key (optional, higher rate limits)

### Configuration
```python
courtlistener_config = ConnectorConfig(
    source_name="CourtListener",
    base_url="https://www.courtlistener.com/api/rest/v3",
    api_key="${COURTLISTENER_API_KEY}",
    rate_limit_per_minute=60,
)
```

### Endpoints
- `GET /opinions/` — Search opinions
- `GET /clusters/{id}/` — Opinion cluster details
- `GET /dockets/{id}/` — Docket details
- `GET /citations/` — Citation search

### Document Structure
- **Title:** Case name
- **Citation:** Standard legal citation (e.g., `410 U.S. 113`)
- **Body:** Plain text opinion content
- **Effective Date:** Date filed
- **Court:** Court name (map to jurisdiction)

### Parsing Rules
1. Extract opinion text from `plain_text` or `html` field
2. Citation from `citations` array
3. Court mapping: Extract circuit/district for jurisdiction
4. Docket number for cross-reference

### Rate Limiting
- Anonymous: 1000 requests/hour
- Authenticated: 10000 requests/hour
- Paginate with `?offset=` and `?limit=`

---

## Connector 4: US Congress API (Legislation)

**Source:** `https://api.congress.gov/v3/`
**Jurisdiction:** J_US_FED
**Body of Law:** STATUTE
**API Type:** REST JSON
**Authentication:** API Key required

### Configuration
```python
congress_config = ConnectorConfig(
    source_name="USCongress",
    base_url="https://api.congress.gov/v3",
    api_key="${CONGRESS_API_KEY}",
    rate_limit_per_minute=30,
)
```

### Endpoints
- `GET /bill/{congress}/{billType}/{billNumber}` — Bill details
- `GET /law/{congress}` — Public laws
- `GET /amendment/{congress}/{amendmentType}/{amendmentNumber}` — Amendments

### Document Structure
- **Title:** Bill short title
- **Citation:** `Pub. L. {congress}-{law_number}`
- **Body:** Bill text (XML or plain text)
- **Effective Date:** Enactment date
- **Status:** Introduced, Passed, Enacted, Vetoed

### Parsing Rules
1. Convert XML bill text to plain text
2. Extract sponsor, cosponsors, committees
3. Track bill status changes
4. Link to enacted public law when passed

---

## Connector 5: EUR-Lex (European Union)

**Source:** `https://eur-lex.europa.eu/europa-webservices/rs/`
**Jurisdiction:** J_EU
**Body of Law:** REGULATION, DIRECTIVE, DECISION
**API Type:** REST JSON / SOAP
**Authentication:** None (public)

### Configuration
```python
eurlex_config = ConnectorConfig(
    source_name="EUR-Lex",
    base_url="https://eur-lex.europa.eu/europa-webservices/rs",
    rate_limit_per_minute=20,
)
```

### Endpoints
- `GET /search` — Search by criteria
- `GET /download/{celex}` — Download document by CELEX number
- `GET /do/{celex}` — Document metadata

### Document Structure
- **Title:** Document title (multilingual)
- **Citation:** CELEX number (e.g., `32016R0679`)
- **Body:** HTML / PDF (extract text)
- **Effective Date:** Publication date in Official Journal
- **Languages:** EN, FR, DE, etc.

### Parsing Rules
1. CELEX format: `{type}{year}{number}` (e.g., 32016R0679 = Regulation 2016/679)
2. Extract text from HTML or use OCR for PDFs
3. Map document type to body_of_law: R→REGULATION, D→DIRECTIVE, L→DECISION
4. Store multilingual titles

### Rate Limiting
- Max 20 requests/minute (EUR-Lex limit)
- Use `format=JSON` for structured data

---

## Connector 6: UK Legislation API

**Source:** `https://www.legislation.gov.uk/`
**Jurisdiction:** J_UK
**Body of Law:** STATUTE, REGULATION
**API Type:** REST XML / JSON
**Authentication:** None (public)

### Configuration
```python
uk_legislation_config = ConnectorConfig(
    source_name="UKLegislation",
    base_url="https://www.legislation.gov.uk",
    rate_limit_per_minute=60,
)
```

### Endpoints
- `GET /id/{type}/{year}/{number}` — Act / SI details
- `GET /search` — Search legislation
- `GET /changes` — Changes feed (for monitoring)

### Document Structure
- **Title:** Short title
- **Citation:** `{year} c. {number}` (Acts) or `{year} No. {number}` (SIs)
- **Body:** XML / HTML legislation text
- **Effective Date:** Royal Assent date (Acts) or made date (SIs)
- **Status:** Current, Repealed, Amended

### Parsing Rules
1. Parse UK Legislation XML schema
2. Extract hierarchical structure: Part → Chapter → Section → Schedule
3. Track amendment history from changes feed
4. Map to body_of_law: ukpga → STATUTE, uksi → REGULATION

---

## Connector 7: AustLII (Australian Legal Information Institute)

**Source:** `https://api.austlii.edu.au/`
**Jurisdiction:** J_AU_FED, J_AU_STATE
**Body of Law:** STATUTE, REGULATION, CASE
**API Type:** REST (limited public API)
**Authentication:** API Key (research access)

### Configuration
```python
austlii_config = ConnectorConfig(
    source_name="AustLII",
    base_url="https://api.austlii.edu.au",
    api_key="${AUSTLII_API_KEY}",
    rate_limit_per_minute=30,
)
```

### Endpoints
- `GET /api/v1/cases/{database}/` — Browse cases
- `GET /api/v1/legislation/{database}/` — Browse legislation
- `GET /api/v1/search` — Full-text search

### Document Structure
- **Title:** Case name or Act title
- **Citation:** Standard Australian citation (e.g., `[2023] HCA 1`)
- **Body:** HTML content
- **Effective Date:** Decision date (cases) or assent date (Acts)

---

## Connector 8: New Zealand Legislation API

**Source:** `https://www.legislation.govt.nz/`
**Jurisdiction:** J_NZ
**Body of Law:** STATUTE, REGULATION
**API Type:** REST XML
**Authentication:** None (public)

### Configuration
```python
nz_legislation_config = ConnectorConfig(
    source_name="NZLegislation",
    base_url="https://www.legislation.govt.nz",
    rate_limit_per_minute=60,
)
```

### Endpoints
- `GET /act/public/{year}/{number}` — Public Act
- `GET /regulation/public/{year}/{number}` — Regulation
- `GET /search` — Search

### Document Structure
- **Title:** Act / Regulation title
- **Citation:** `{year} No. {number}`
- **Body:** XML / HTML
- **Effective Date:** Assent date

---

## Connector 9: State Legislative APIs (US States)

**Sources:** 
- California: `https://leginfo.legislature.ca.gov/`
- New York: `https://legislation.nysenate.gov/`
- Texas: `https://capitol.texas.gov/`
- Florida: `https://www.flsenate.gov/`
- Illinois: `https://www.ilga.gov/`

**Jurisdiction:** J_US_STATE
**Body of Law:** STATUTE, REGULATION
**API Type:** REST / HTML scraping (varies by state)
**Authentication:** Varies (most public)

### Configuration
```python
# Example: California

ca_legislation_config = ConnectorConfig(
    source_name="CaliforniaLegislation",
    base_url="https://leginfo.legislature.ca.gov",
    rate_limit_per_minute=60,
)
```

### Challenges
- No uniform API across states
- Some require HTML scraping
- Rate limits vary significantly
- Document formats vary (HTML, PDF, Word)

### Mitigation Strategy
1. Use LegiScan API (aggregates state data)
2. Implement per-state adapter classes
3. Use Docling parser for format normalization
4. Fallback to web scraping with Scrapy

---

## Connector Pipeline: Docling Parser

All connectors use Docling for document parsing and chunking:

```python
from docling.document_converter import DocumentConverter
from docling.chunking import HierarchicalChunker

class DoclingParser:
    def __init__(self):
        self.converter = DocumentConverter()
        self.chunker = HierarchicalChunker(
            max_chunk_size=512,
            overlap=50,
            respect_page_breaks=True,
        )
    
    async def parse(self, content: str, content_type: str) -> dict:
        """Parse content and extract structured chunks."""
        # Convert to Docling document
        doc = await self.converter.convert(content, content_type)
        
        # Extract metadata
        metadata = {
            "title": doc.title,
            "authors": doc.authors,
            "date": doc.date,
            "language": doc.language,
        }
        
        # Chunk hierarchically
        chunks = []
        for chunk in self.chunker.chunk(doc):
            chunks.append({
                "text": chunk.text,
                "section_path": chunk.metadata.headings,
                "page_number": chunk.metadata.page_number,
                "level": chunk.metadata.level,
            })
        
        return {
            "metadata": metadata,
            "chunks": chunks,
            "full_text": doc.text,
        }
```

---

## Connector Pipeline: Embedding Generation

```python
from openai import AsyncOpenAI

class EmbeddingService:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "text-embedding-3-large"
        self.dimensions = 1536
    
    async def embed(self, text: str) -> list[float]:
        """Generate embedding for text chunk."""
        response = await self.client.embeddings.create(
            model=self.model,
            input=text,
            dimensions=self.dimensions,
        )
        return response.data[0].embedding
```

---

## Monitoring & Error Handling

### Retry Policy
- Exponential backoff: `2^attempt * base_delay`
- Max retries: 3
- Retry on: 429, 500, 502, 503, 504
- Circuit breaker: Open after 5 consecutive failures

### Monitoring Metrics
- `connector_fetch_duration_seconds` — Histogram
- `connector_fetch_errors_total` — Counter (by source, error_type)
- `connector_documents_ingested_total` — Counter (by source, jurisdiction)
- `connector_chunks_embedded_total` — Counter (by source)

### Alerting
- Alert if `connector_fetch_errors_total` > 10/min for any source
- Alert if `connector_fetch_duration_seconds` p95 > 30s
- Alert if no documents ingested in 24h for active connector
