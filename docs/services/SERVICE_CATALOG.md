# SERVICE_CATALOG.md — LexCore + LexRadar Service Layer

> **Build System:** Unified Build System v2  
> **Chunk:** C05 — Services + Workers + Agents  
> **Horde:** HORDE-AGENTS  
> **Control Plane:** ENGINEERING  

---

## Overview

The service layer implements business logic for all domain operations. It sits between the API routes (L4) and the repository layer (L2), enforcing:
- **No business logic in route handlers** (C02 Law #1)
- **No raw DB access outside repositories** (C02 Law #2)
- **All critical state changes write audit rows** (C02 Law #5)

---

## Service Architecture

```
┌─────────────────────────────────────────────┐
│  API Routes (L4)                            │
│  ├── MCP Tools                              │
│  ├── LexCore Domain                         │
│  ├── LexRadar Domain                        │
│  └── Auth                                   │
├─────────────────────────────────────────────┤
│  SERVICE LAYER (Bounded Contexts)            │
│  ├── LexCoreServices                        │
│  │   ├── SearchService                      │
│  │   ├── DocumentService                   │
│  │   ├── MonitorService                    │
│  │   ├── ResearchService                   │
│  │   └── CitationService                   │
│  ├── LexRadarServices                       │
│  │   ├── ScanService                       │
│  │   ├── InventionService                  │
│  │   ├── PriorArtService                   │
│  │   ├── DisclosureService                 │
│  │   ├── FilingBundleService               │
│  │   └── HandoffService                    │
│  ├── SharedServices                         │
│  │   ├── AuthService                       │
│  │   ├── TenantService                     │
│  │   ├── AuditService                      │
│  │   └── CacheService                      │
│  └── PipelineServices                       │
│      ├── IngestPipelineService              │
│      ├── SearchPipelineService              │
│      └── PatentPipelineService              │
├─────────────────────────────────────────────┤
│  REPOSITORY LAYER                           │
│  ├── DocumentRepository                   │
│  ├── ChunkRepository                      │
│  ├── InventionRepository                  │
│  ├── PriorArtRepository                   │
│  ├── DisclosureRepository                 │
│  ├── FilingBundleRepository               │
│  ├── AttorneyReviewRepository             │
│  ├── MonitorRuleRepository                │
│  ├── ResearchTaskRepository               │
│  ├── JurisdictionRepository               │
│  └── ...                                  │
├─────────────────────────────────────────────┤
│  STORAGE (L2)                               │
│  ├── PostgreSQL + pgvector                  │
│  ├── Redis                                  │
│  ├── Qdrant                                 │
│  └── S3 / R2                                │
└─────────────────────────────────────────────┘
```

---

## LexCore Services

### SearchService

**Responsibility:** Hybrid search orchestration (vector + full-text + re-rank)  
**Agent:** `AGT_SEARCH` delegates to this service  
**Dependencies:** `ChunkRepository`, `QdrantClient`, `CacheService`, `EmbeddingService`

**Public Methods:**
```python
class SearchService:
    async def search(
        self,
        tenant_id: UUID,
        query: str,
        jurisdiction: str | None,
        body_of_law: str | None,
        top_k: int = 10,
        include_citations: bool = True,
    ) -> SearchResult:
        """
        1. Check cache (query fingerprint)
        2. Generate embedding (or use cached)
        3. Parallel: vector search (Qdrant) + full-text search (PostgreSQL)
        4. Combine and re-rank (cross-encoder)
        5. Fetch citation chains (if requested)
        6. Cache results
        7. Return ranked results
        """

    async def get_document_with_chunks(
        self,
        tenant_id: UUID,
        doc_id: UUID | None,
        citation: str | None,
    ) -> DocumentWithChunks:
        """Retrieve document with all chunks and citations."""

    async def get_citation_graph(
        self,
        tenant_id: UUID,
        doc_id: UUID,
        direction: str,
        depth: int,
    ) -> CitationGraph:
        """Traverse citation graph with authority scoring."""
```

**SLA:**
- P95 latency: 500ms (cache miss), 5ms (cache hit)
- P99 latency: 1000ms (cache miss)
- Availability: 99.9%

---

### DocumentService

**Responsibility:** Document lifecycle management (CRUD, version tracking, deprecation)  
**Dependencies:** `DocumentRepository`, `ChunkRepository`, `AuditService`

**Public Methods:**
```python
class DocumentService:
    async def list_documents(
        self,
        tenant_id: UUID,
        filters: DocumentFilters,
        pagination: Pagination,
    ) -> PaginatedResult[LegalDocument]:
        """List documents with filters and pagination."""

    async def get_document(
        self,
        tenant_id: UUID,
        doc_id: UUID | None,
        citation: str | None,
    ) -> LegalDocument:
        """Get single document by ID or citation."""

    async def mark_deprecated(
        self,
        tenant_id: UUID,
        doc_id: UUID,
        reason: str,
        superseded_by: UUID | None,
    ) -> LegalDocument:
        """Mark document as deprecated (repealed/overruled). Writes audit row."""

    async def get_document_versions(
        self,
        tenant_id: UUID,
        doc_id: UUID,
    ) -> list[DocumentVersion]:
        """Get version history of a document."""
```

---

### MonitorService

**Responsibility:** Monitor rule CRUD and evaluation  
**Agent:** `AGT_MONITOR` delegates to this service  
**Dependencies:** `MonitorRuleRepository`, `MonitorAlertRepository`, `DocumentRepository`

**Public Methods:**
```python
class MonitorService:
    async def create_rule(
        self,
        tenant_id: UUID,
        rule: MonitorRuleCreate,
    ) -> MonitorRule:
        """Create monitor rule. Writes audit row."""

    async def update_rule(
        self,
        tenant_id: UUID,
        rule_id: UUID,
        updates: MonitorRuleUpdate,
    ) -> MonitorRule:
        """Update monitor rule. Writes audit row."""

    async def delete_rule(
        self,
        tenant_id: UUID,
        rule_id: UUID,
    ) -> None:
        """Delete (archive) monitor rule. Writes audit row."""

    async def evaluate_rules(
        self,
        tenant_id: UUID | None = None,  # None = all tenants
    ) -> list[MonitorAlert]:
        """
        Evaluate all active monitor rules against recent document changes.
        Called by scheduled Celery task every 6 hours.
        Returns list of generated alerts.
        """

    async def get_alerts(
        self,
        tenant_id: UUID,
        filters: AlertFilters,
        pagination: Pagination,
    ) -> PaginatedResult[MonitorAlert]:
        """Get monitor alerts with filters."""

    async def acknowledge_alert(
        self,
        tenant_id: UUID,
        alert_id: UUID,
    ) -> MonitorAlert:
        """Mark alert as acknowledged."""
```

---

### ResearchService

**Responsibility:** Complex research task orchestration  
**Agent:** `AGT_ANALYSIS` delegates to this service  
**Dependencies:** `SearchService`, `LLMClient`, `ResearchTaskRepository`, `DocumentRepository`

**Public Methods:**
```python
class ResearchService:
    async def create_research_task(
        self,
        tenant_id: UUID,
        question: str,
        jurisdictions: list[str],
        output_format: str,
        max_sources: int,
    ) -> ResearchTask:
        """
        Create research task. Decompose question into sub-queries.
        Return task ID for polling (if async) or result (if sync < 60s).
        """

    async def execute_research(
        self,
        tenant_id: UUID,
        task_id: UUID,
    ) -> ResearchResult:
        """
        Execute research task:
        1. Decompose question into sub-queries
        2. Parallel search_legal calls for each sub-query
        3. Synthesize results with LLM
        4. Detect gaps
        5. Store results
        6. Return structured report
        """

    async def get_task_status(
        self,
        tenant_id: UUID,
        task_id: UUID,
    ) -> ResearchTaskStatus:
        """Get research task status and progress."""

    async def get_task_result(
        self,
        tenant_id: UUID,
        task_id: UUID,
    ) -> ResearchResult:
        """Get completed research task result."""
```

---

### CitationService

**Responsibility:** Citation graph traversal and authority scoring  
**Agent:** `AGT_CITE` delegates to this service  
**Dependencies:** `CitationRepository`, `DocumentRepository`

**Public Methods:**
```python
class CitationService:
    async def get_citations(
        self,
        tenant_id: UUID,
        doc_id: UUID,
        direction: str,
        depth: int,
    ) -> CitationGraph:
        """
        Traverse citation graph:
        1. Get direct citations (forward/backward/both)
        2. Recursively traverse to depth
        3. Detect cycles (should not happen with FK constraints)
        4. Score authority of each node
        5. Flag overruled cases
        6. Return graph with nodes, edges, authority chain
        """

    async def get_authority_chain(
        self,
        tenant_id: UUID,
        doc_id: UUID,
    ) -> list[UUID]:
        """Get the most authoritative path from this document to foundational precedent."""

    async def detect_overruled(
        self,
        tenant_id: UUID,
        doc_id: UUID,
    ) -> list[OverruledCase]:
        """Detect cases that have been overruled by this or subsequent decisions."""
```

---

## LexRadar Services

### ScanService

**Responsibility:** Code repository scanning for invention signals  
**Agent:** `AGT_SCANNER` delegates to this service  
**Dependencies:** `GitHubConnector`, `JiraConnector`, `NotionConnector`, `InventionRepository`

**Public Methods:**
```python
class ScanService:
    async def trigger_scan(
        self,
        tenant_id: UUID,
        source: str,
        source_id: str,
        trigger: str,  # manual, webhook, scheduled
    ) -> ScanJob:
        """
        Trigger code scan. Returns job ID for polling.
        """

    async def execute_scan(
        self,
        tenant_id: UUID,
        job_id: UUID,
    ) -> list[InventionSignal]:
        """
        Execute scan:
        1. Fetch recent commits/PRs/tickets from source
        2. Parse code changes and descriptions
        3. Detect invention signals (novel algorithms, novel data structures, novel systems)
        4. Classify signals by type
        5. Store detected signals
        6. Return signals for scoring
        """

    async def get_scan_status(
        self,
        tenant_id: UUID,
        job_id: UUID,
    ) -> ScanJobStatus:
        """Get scan job status and progress."""
```

---

### InventionService

**Responsibility:** Invention candidate lifecycle management  
**Dependencies:** `InventionRepository`, `PriorArtRepository`, `DisclosureRepository`

**Public Methods:**
```python
class InventionService:
    async def list_inventions(
        self,
        tenant_id: UUID,
        status: str | None,
        pagination: Pagination,
    ) -> PaginatedResult[InventionCandidate]:
        """List invention candidates with status filter."""

    async def get_invention(
        self,
        tenant_id: UUID,
        invention_id: UUID,
    ) -> InventionCandidate:
        """Get invention candidate with scores and evidence."""

    async def update_scores(
        self,
        tenant_id: UUID,
        invention_id: UUID,
        scores: PatentabilityScores,
    ) -> InventionCandidate:
        """
        Update 6-dimension scores after prior art search.
        Computes composite score.
        """

    async def promote_to_disclosure(
        self,
        tenant_id: UUID,
        invention_id: UUID,
    ) -> Disclosure:
        """
        Promote invention to disclosure generation.
        Triggers disclosure generation pipeline.
        """
```

---

### PriorArtService

**Responsibility:** Parallel prior art search across 7 sources  
**Agent:** `AGT_PRIORART` delegates to this service  
**Dependencies:** `PriorArtRepository`, `USPTOConnector`, `WIPOConnector`, `EPOConnector`, `LensConnector`, `GooglePatentsConnector`, `PatentScopeConnector`, `IPcomConnector`

**Public Methods:**
```python
class PriorArtService:
    async def search_prior_art(
        self,
        tenant_id: UUID,
        invention_id: UUID,
        keywords: list[str],
        sources: list[str] | None = None,  # None = all 7 sources
    ) -> PriorArtSearchJob:
        """
        Trigger parallel prior art search across 7 sources.
        Returns job ID for polling.
        """

    async def execute_search(
        self,
        tenant_id: UUID,
        job_id: UUID,
    ) -> list[PriorArtResult]:
        """
        Execute parallel search:
        1. Spawn 7 concurrent searches (one per source)
        2. Each search: query API, parse results, compute relevance
        3. Merge results, deduplicate by patent number
        4. Rank by relevance score
        5. Store results
        6. Trigger scoring service
        """

    async def get_search_results(
        self,
        tenant_id: UUID,
        invention_id: UUID,
    ) -> list[PriorArtResult]:
        """Get prior art results for an invention."""
```

---

### DisclosureService

**Responsibility:** Generate and manage patent disclosure drafts  
**Agent:** `AGT_DISCLOSER` delegates to this service  
**Dependencies:** `DisclosureRepository`, `LLMClient`, `PriorArtRepository`, `InventionRepository`

**Public Methods:**
```python
class DisclosureService:
    async def generate_disclosure(
        self,
        tenant_id: UUID,
        invention_id: UUID,
        disclosure_type: str,  # PROVISIONAL, NON_PROVISIONAL, PCT
        claim_themes: list[str] | None,
    ) -> DisclosureGenerationJob:
        """
        Trigger disclosure draft generation.
        Returns job ID for polling.
        """

    async def execute_generation(
        self,
        tenant_id: UUID,
        job_id: UUID,
    ) -> Disclosure:
        """
        Generate 10-section LHP disclosure:
        1. Fetch invention candidate and prior art
        2. Generate each section with LLM (grounded in evidence)
        3. Compute grounding score
        4. If grounding < 0.70: flag for review
        5. Store draft
        6. Return disclosure
        """

    async def get_disclosure(
        self,
        tenant_id: UUID,
        disclosure_id: UUID,
    ) -> Disclosure:
        """Get disclosure draft with all 10 sections."""

    async def approve_disclosure(
        self,
        tenant_id: UUID,
        disclosure_id: UUID,
    ) -> Disclosure:
        """Mark disclosure as APPROVED. Triggers handoff eligibility."""
```

---

### FilingBundleService

**Responsibility:** Package approved disclosures into filing bundles  
**Dependencies:** `FilingBundleRepository`, `DisclosureRepository`, `S3Client`

**Public Methods:**
```python
class FilingBundleService:
    async def create_bundle(
        self,
        tenant_id: UUID,
        disclosure_ids: list[UUID],
        bundle_name: str,
        patent_type: str,
    ) -> FilingBundle:
        """
        Create filing bundle from approved disclosures.
        Package as ZIP with PDFs.
        Upload to S3.
        """

    async def get_bundle(
        self,
        tenant_id: UUID,
        bundle_id: UUID,
    ) -> FilingBundle:
        """Get filing bundle with download URL."""

    async def download_bundle(
        self,
        tenant_id: UUID,
        bundle_id: UUID,
    ) -> StreamingResponse:
        """Stream bundle download from S3 with presigned URL."""
```

---

### HandoffService

**Responsibility:** Deliver handoff packages to attorneys and manage review lifecycle  
**Agent:** `AGT_ATTYFLOW` delegates to this service  
**Dependencies:** `AttorneyReviewRepository`, `DisclosureRepository`, `EmailService`, `JWTService`

**Public Methods:**
```python
class HandoffService:
    async def deliver_handoff(
        self,
        tenant_id: UUID,
        disclosure_id: UUID,
        attorney_email: str,
        attorney_name: str,
        message: str | None,
    ) -> HandoffDelivery:
        """
        Deliver handoff to attorney:
        1. Verify disclosure is APPROVED
        2. Generate scoped JWT (48h expiry)
        3. Generate portal URL
        4. Send email with link
        5. Create attorney review record
        6. Return delivery confirmation
        """

    async def get_handoff_for_review(
        self,
        handoff_id: UUID,
        scoped_jwt: str,
    ) -> HandoffPackage:
        """
        Get handoff package for attorney review:
        1. Validate scoped JWT
        2. Check expiry
        3. Check review status (not already completed)
        4. Return handoff package with editable sections
        """

    async def submit_review(
        self,
        handoff_id: UUID,
        scoped_jwt: str,
        action: str,  # APPROVE, REJECT, REQUEST_CHANGES
        notes: str | None,
        rejection_reason: str | None,
        request_changes_details: str | None,
    ) -> AttorneyReview:
        """
        Submit attorney review:
        1. Validate scoped JWT
        2. Check status is PENDING or IN_PROGRESS
        3. Update review record
        4. Update disclosure status
        5. Notify client
        6. If APPROVED: trigger filing bundle creation
        7. Invalidate scoped JWT
        8. Return review confirmation
        """
```

---

## Shared Services

### AuthService

**Responsibility:** Authentication and token management  
**Dependencies:** `UserRepository`, `APIKeyRepository`, `RedisClient`, `VaultClient`

**Public Methods:**
```python
class AuthService:
    async def exchange_api_key(self, api_key: str) -> TokenPair:
        """Exchange API key for JWT access + refresh tokens."""

    async def refresh_tokens(self, refresh_token: str) -> TokenPair:
        """Refresh access token using refresh token (rotation)."""

    async def validate_token(self, token: str) -> JWTClaims:
        """Validate JWT and extract claims."""

    async def blacklist_token(self, jti: str) -> None:
        """Blacklist a token in Redis."""

    async def generate_scoped_jwt(
        self,
        tenant_id: UUID,
        handoff_id: UUID,
        attorney_email: str,
        expires_hours: int = 48,
    ) -> str:
        """Generate scoped JWT for attorney portal."""
```

---

### TenantService

**Responsibility:** Tenant lifecycle and context management  
**Dependencies:** `TenantRepository`, `JurisdictionRepository`

**Public Methods:**
```python
class TenantService:
    async def get_tenant(self, tenant_id: UUID) -> Tenant:
        """Get tenant by ID."""

    async def create_tenant(self, tenant: TenantCreate) -> Tenant:
        """Create new tenant with default settings."""

    async def get_active_jurisdictions(self, tenant_id: UUID) -> list[Jurisdiction]:
        """Get tenant's active jurisdictions with coverage stats."""

    async def set_tenant_context(self, conn, tenant_id: UUID) -> None:
        """Set PostgreSQL RLS tenant context on connection."""
        await conn.execute("SET app.tenant_id = $1", tenant_id)
```

---

### AuditService

**Responsibility:** Write audit rows for all critical state changes  
**Dependencies:** `AuditLogRepository`

**Public Methods:**
```python
class AuditService:
    async def log(
        self,
        tenant_id: UUID,
        action_type: str,
        entity_type: str,
        entity_id: UUID | None,
        user_id: UUID | None,
        details: dict,
    ) -> AuditLogEntry:
        """Write audit row. Append-only — no updates allowed."""
```

---

### CacheService

**Responsibility:** Redis cache operations with tenant scoping  
**Dependencies:** `RedisClient`

**Public Methods:**
```python
class CacheService:
    async def get(self, tenant_id: UUID, key: str) -> Any | None:
        """Get cached value with tenant prefix."""
        return await redis.get(f"tenant:{tenant_id}:{key}")

    async def set(
        self,
        tenant_id: UUID,
        key: str,
        value: Any,
        ttl: int = 86400,
    ) -> None:
        """Set cached value with tenant prefix and TTL."""
        await redis.setex(f"tenant:{tenant_id}:{key}", ttl, json.dumps(value))

    async def delete(self, tenant_id: UUID, key: str) -> None:
        """Delete cached value."""
        await redis.delete(f"tenant:{tenant_id}:{key}")

    async def get_query_result(
        self,
        tenant_id: UUID,
        fingerprint: str,
    ) -> SearchResult | None:
        """Get cached search result."""

    async def set_query_result(
        self,
        tenant_id: UUID,
        fingerprint: str,
        result: SearchResult,
        ttl: int = 86400,
    ) -> None:
        """Cache search result."""
```

---

## Pipeline Services

### IngestPipelineService

**Responsibility:** Orchestrate document ingestion pipeline  
**Dependencies:** `DocumentRepository`, `ChunkRepository`, `EmbeddingService`, `QdrantClient`, `ConnectorRegistry`

**Public Methods:**
```python
class IngestPipelineService:
    async def ingest_document(
        self,
        tenant_id: UUID,
        source: str,
        doc_id: str,
    ) -> IngestResult:
        """
        Run full ingestion pipeline:
        1. Fetch from source
        2. Parse with Docling
        3. Chunk hierarchically
        4. Generate embeddings
        5. Store in PostgreSQL
        6. Index in Qdrant
        7. Write audit row
        """

    async def batch_ingest(
        self,
        tenant_id: UUID,
        source: str,
        doc_ids: list[str],
    ) -> BatchIngestResult:
        """Batch ingest multiple documents."""

    async def schedule_ingest(
        self,
        source: str,
        schedule: str,  # cron expression
    ) -> ScheduledJob:
        """Schedule recurring ingestion."""
```

---

### SearchPipelineService

**Responsibility:** Execute multi-stage search pipeline  
**Dependencies:** `SearchService`, `CacheService`

**Public Methods:**
```python
class SearchPipelineService:
    async def execute_hybrid_search(
        self,
        tenant_id: UUID,
        query: str,
        jurisdiction: str | None,
        body_of_law: str | None,
        top_k: int,
    ) -> SearchResult:
        """Execute full hybrid search pipeline with caching."""
```

---

### PatentPipelineService

**Responsibility:** Orchestrate full patent pipeline from detection to handoff  
**Dependencies:** `ScanService`, `InventionService`, `PriorArtService`, `DisclosureService`, `HandoffService`, `BlockchainService`

**Public Methods:**
```python
class PatentPipelineService:
    async def run_full_pipeline(
        self,
        tenant_id: UUID,
        invention_id: UUID,
    ) -> PipelineResult:
        """
        Run complete patent pipeline:
        1. Prior art search (parallel across 7 sources)
        2. Patentability scoring (6 dimensions)
        3. Disclosure generation (10-section LHP)
        4. Blockchain anchoring (proof of existence)
        5. Attorney handoff (email + portal link)
        Returns pipeline status and artifacts.
        """

    async def get_pipeline_status(
        self,
        tenant_id: UUID,
        pipeline_id: UUID,
    ) -> PipelineStatus:
        """Get pipeline execution status and progress."""
```

---

## Service Interface Contract

Every service MUST implement:

```python
class BaseService(ABC):
    """Base class for all services."""
    
    @property
    @abstractmethod
    def service_name(self) -> str:
        """Unique service identifier."""
    
    @abstractmethod
    async def health_check(self) -> dict:
        """Return service health status."""
    
    async def with_audit(
        self,
        tenant_id: UUID,
        action: str,
        entity_type: str,
        entity_id: UUID | None,
        operation: Callable,
    ) -> Any:
        """Execute operation and write audit row."""
        result = await operation()
        await self.audit_service.log(
            tenant_id=tenant_id,
            action_type=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=None,  # Set from JWT context
            details={"service": self.service_name},
        )
        return result
```

---

## Service Health Checks

| Service | Health Check | Dependency Checks |
|---------|-------------|-------------------|
| SearchService | `SELECT 1` on pgvector + Qdrant ping | PostgreSQL, Qdrant, Redis |
| DocumentService | `SELECT 1` on PostgreSQL | PostgreSQL |
| MonitorService | `SELECT 1` + rule count | PostgreSQL |
| ResearchService | OpenAI API ping | PostgreSQL, OpenAI |
| CitationService | `SELECT 1` + citation count | PostgreSQL |
| ScanService | GitHub API ping | PostgreSQL, GitHub API |
| InventionService | `SELECT 1` + invention count | PostgreSQL |
| PriorArtService | USPTO API ping | PostgreSQL, USPTO, WIPO, EPO |
| DisclosureService | OpenAI API ping | PostgreSQL, OpenAI |
| FilingBundleService | S3 ping | PostgreSQL, S3 |
| HandoffService | Email service ping | PostgreSQL, Email service |
| AuthService | JWT validation round-trip | PostgreSQL, Redis, Vault |
| TenantService | `SELECT 1` | PostgreSQL |
| AuditService | `SELECT 1` | PostgreSQL |
| CacheService | Redis ping | Redis |
| IngestPipelineService | Connector ping | PostgreSQL, Qdrant, Redis, all connectors |
| SearchPipelineService | `SELECT 1` + Qdrant ping | PostgreSQL, Qdrant, Redis |
| PatentPipelineService | All dependency pings | All above |

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-29 | Initial service catalog | C05 services definition |
