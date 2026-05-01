# API_SPEC.md — LexCore + LexRadar API Specification

> **Build System:** Unified Build System v2  
> **Chunk:** C04 — API Contracts + MCP Tools  
> **Horde:** HORDE-API  
> **Control Plane:** ENGINEERING  

---

## Overview

This document defines the complete API surface for LexCore + LexRadar. The API is organized into:
- **MCP (Model Context Protocol) Tools** — 7 tools exposed to AI clients
- **LexCore Domain Routes** — Legal intelligence operations
- **LexRadar Domain Routes** — IP pipeline operations
- **Auth Routes** — Authentication, token exchange, refresh
- **Health Routes** — Kubernetes probes, diagnostics

**Base URL:** `https://api.lexcore.com/v1`  
**Protocol:** HTTPS only (TLS 1.3)  
**Content-Type:** `application/json` for requests/responses  
**Versioning:** Path-based (`/v1/...`), maximum 2 versions supported simultaneously

---

## Authentication

### JWT Bearer Token
All protected endpoints require a `Authorization: Bearer <jwt>` header.

### API Key Exchange
For machine-to-machine authentication:
```
POST /v1/auth/token
Body: {"api_key": "lex_{tenant_id}_{random_32}"}
Response: {"access_token": "...", "refresh_token": "...", "token_type": "Bearer", "expires_in": 3600}
```

### Attorney Portal Token
Scoped JWT for attorney portal access (48h expiry):
```
Authorization: Bearer <scoped_jwt>
# Scoped JWT claims: handoff_id, attorney_email, scope: "handoff:read handoff:edit handoff:action"
```

---

## MCP Tools (7 Tools)

### 1. `get_capabilities`
**Method:** `GET`  
**Path:** `/v1/mcp/capabilities`  
**Auth:** None (public)  
**Description:** Returns supported jurisdictions, document types, and available MCP tools.

**Response (200):**
```json
{
  "jurisdictions": {
    "J_US_FED": {"name": "United States Federal", "coverage_percent": 0.92, "doc_count": 145230},
    "J_CA_FED": {"name": "Canada Federal", "coverage_percent": 0.88, "doc_count": 87230}
  },
  "doc_types": ["STATUTE", "REGULATION", "CASE"],
  "tools": ["get_capabilities", "search_legal", "research_task", "get_document", "get_citations", "check_updates", "jurisdiction_summary"],
  "version": "v1.0.0"
}
```

---

### 2. `search_legal`
**Method:** `POST`  
**Path:** `/v1/mcp/search_legal`  
**Auth:** JWT (tenant_id required)  
**Description:** Hybrid search combining vector similarity (pgvector HNSW) + PostgreSQL full-text search + re-ranking.

**Request Body:**
```json
{
  "query": "patent obviousness software inventions",
  "jurisdiction": "J_US_FED",
  "body_of_law": "CASE",
  "top_k": 10,
  "include_citations": true
}
```

**Response (200):**
```json
{
  "results": [
    {
      "document_id": "uuid",
      "title": "Alice Corp. v. CLS Bank International",
      "citation": "573 U.S. 208 (2014)",
      "jurisdiction": "J_US_FED",
      "body_of_law": "CASE",
      "source": "CourtListener",
      "summary": "Supreme Court decision on patent eligibility of abstract ideas implemented on generic computers.",
      "url": "https://courtlistener.com/opinion/...",
      "score": 0.94,
      "published_date": "2014-06-19"
    }
  ],
  "total": 47,
  "latency_ms": 245.3,
  "cache_hit": false,
  "citation_chains": [
    {
      "document_id": "uuid",
      "direction": "backward",
      "chain": [{"id": "...", "citation": "Mayo v. Prometheus", "relevance": 0.91}]
    }
  ]
}
```

**Errors:**
- `400 INVALID_QUERY` — Query empty or > 500 chars
- `400 INVALID_JURISDICTION` — Jurisdiction not supported
- `401 TENANT_NOT_FOUND` — JWT tenant_id invalid
- `429 RATE_LIMIT_EXCEEDED` — Too many requests
- `504 SEARCH_TIMEOUT` — Search exceeded 5s

---

### 3. `research_task`
**Method:** `POST`  
**Path:** `/v1/mcp/research_task`  
**Auth:** JWT (tenant_id required)  
**Description:** Complex legal research with question decomposition, parallel sub-searches, synthesis.

**Request Body:**
```json
{
  "question": "How has the Alice/Mayo framework been applied to AI-generated inventions in 2023-2024?",
  "jurisdictions": ["J_US_FED", "J_CA_FED"],
  "output_format": "structured_report",
  "max_sources": 20
}
```

**Response (200):**
```json
{
  "report": "# AI Inventions Under Alice/Mayo Framework\n\n## Executive Summary\n...",
  "citation_chain": [
    {"document_id": "...", "citation": "Thaler v. Perlmutter", "authority_level": "primary"}
  ],
  "confidence": 0.87,
  "gap_detected": true,
  "gaps": [
    "No Federal Circuit decisions specifically addressing LLM-generated patent claims",
    "Limited guidance on AI inventorship from PTO (Oct 2023 guidance only)",
    "No Canadian precedent on AI inventorship"
  ]
}
```

**Errors:**
- `400 INVALID_QUESTION` — Question empty or > 2000 chars
- `504 RESEARCH_TIMEOUT` — Research exceeded 60s
- `503 LLM_UNAVAILABLE` — Analysis engine unavailable

---

### 4. `get_document`
**Method:** `GET`  
**Path:** `/v1/mcp/document`  
**Auth:** JWT (tenant_id required)  
**Description:** Retrieve full document with chunks, citations, and metadata.

**Query Parameters:**
```
?doc_id=uuid (optional)
?citation=CFR%201.1.1 (optional)
```
*Note: At least one of doc_id or citation is required.*

**Response (200):**
```json
{
  "document": {
    "id": "uuid",
    "title": "...",
    "citation": "...",
    "jurisdiction": "J_US_FED",
    "body_of_law": "STATUTE",
    "source": "eCFR",
    "summary": "...",
    "url": "...",
    "version": "2024-01-15",
    "metadata": {"chapter": "1", "part": "1"},
    "published_date": "2024-01-15",
    "last_modified": "2024-03-20"
  },
  "chunks": [
    {"id": "uuid", "chunk_index": 0, "chunk_type": "SECTION", "content": "..."},
    {"id": "uuid", "chunk_index": 1, "chunk_type": "PARAGRAPH", "content": "..."}
  ],
  "citations": [
    {"id": "uuid", "citing_document": {...}, "cited_document": {...}, "citation_type": "FORWARD"}
  ],
  "metadata": {
    "total_chunks": 12,
    "word_count": 2847,
    "jurisdiction_name": "United States Federal"
  }
}
```

**Errors:**
- `400 MISSING_IDENTIFIER` — Neither doc_id nor citation provided
- `404 DOCUMENT_NOT_FOUND` — No document matches ID or citation
- `403 TENANT_ISOLATION` — Document belongs to different tenant

---

### 5. `get_citations`
**Method:** `POST`  
**Path:** `/v1/mcp/citations`  
**Auth:** JWT (tenant_id required)  
**Description:** Citation graph traversal with authority scoring and overruled detection.

**Request Body:**
```json
{
  "doc_id": "uuid",
  "direction": "both",
  "depth": 3
}
```

**Response (200):**
```json
{
  "nodes": [
    {"id": "uuid", "citation": "Alice Corp. v. CLS Bank", "authority_score": 0.95, "is_overruled": false}
  ],
  "edges": [
    {"source": "uuid1", "target": "uuid2", "direction": "FORWARD", "context": "..."}
  ],
  "authority_chain": ["uuid1", "uuid2", "uuid3"],
  "overruled_cases": [
    {"id": "uuid", "citation": "Diamond v. Chakrabarty", "overruled_by": "uuid", "overruled_date": "..."}
  ]
}
```

**Errors:**
- `400 INVALID_DEPTH` — Depth must be 1-5
- `404 DOCUMENT_NOT_FOUND` — Document not found
- `500 CYCLE_DETECTED` — Circular citation detected (should not happen)

---

### 6. `check_updates`
**Method:** `POST`  
**Path:** `/v1/mcp/check_updates`  
**Auth:** JWT (tenant_id required)  
**Description:** Check for legislative changes since a given date.

**Request Body:**
```json
{
  "jurisdiction": "J_US_FED",
  "since_date": "2024-01-01",
  "alert_types": ["AMENDMENT", "NEW"]
}
```

**Response (200):**
```json
{
  "updates": [
    {
      "document_id": "uuid",
      "change_type": "AMENDMENT",
      "change_summary": "Section 101 amended to clarify AI inventorship",
      "previous_version_url": "...",
      "current_version_url": "...",
      "detected_at": "2024-03-15T10:00:00Z"
    }
  ],
  "total": 23,
  "new_count": 5,
  "change_count": 18,
  "repeal_count": 0
}
```

**Errors:**
- `400 INVALID_DATE` — since_date in future or too old (> 2 years)
- `404 JURISDICTION_NOT_MONITORED` — No monitor rule for jurisdiction

---

### 7. `jurisdiction_summary`
**Method:** `GET`  
**Path:** `/v1/mcp/jurisdiction/{jurisdiction_code}`  
**Auth:** JWT (tenant_id required)  
**Description:** Get coverage statistics and recent changes for a jurisdiction.

**Path Parameters:**
```
jurisdiction_code: string (e.g., "J_US_FED")
```

**Response (200):**
```json
{
  "jurisdiction_code": "J_US_FED",
  "jurisdiction_name": "United States Federal",
  "coverage_percent": 0.92,
  "doc_count": 145230,
  "statute_count": 2340,
  "regulation_count": 87650,
  "case_count": 55240,
  "last_ingest_date": "2024-04-29T06:00:00Z",
  "recent_changes": [
    {"document_id": "...", "change_type": "NEW", "change_summary": "...", "detected_at": "2024-04-28T12:00:00Z"}
  ]
}
```

**Errors:**
- `404 JURISDICTION_NOT_FOUND` — Unknown jurisdiction code

---

## LexCore Domain Routes

### Document Management

**`GET /v1/lexcore/documents`**  
List documents with filters and pagination.

**Query Parameters:**
```
jurisdiction: string (optional)
body_of_law: string (optional)
source: string (optional)
search: string (optional, full-text search on title/citation/summary)
limit: integer (1-100, default 20)
offset: integer (default 0)
sort: string (published_date|relevance, default published_date)
order: string (asc|desc, default desc)
```

**Response (200):**
```json
{
  "documents": [/* array of LegalDocumentSummary */],
  "total": 145230,
  "limit": 20,
  "offset": 0,
  "has_more": true
}
```

---

**`GET /v1/lexcore/documents/{doc_id}/chunks`**  
Retrieve chunks for a specific document.

**Response (200):**
```json
{
  "document_id": "uuid",
  "chunks": [/* array of LegalChunk */],
  "total": 12,
  "limit": 50,
  "offset": 0
}
```

---

### Monitor Rules

**`GET /v1/lexcore/monitor-rules`**  
List monitor rules for the tenant.

**Response (200):**
```json
{
  "rules": [/* array of MonitorRule */],
  "total": 5,
  "active_count": 3
}
```

---

**`POST /v1/lexcore/monitor-rules`**  
Create a new monitor rule.

**Request Body:**
```json
{
  "rule_name": "Patent Law Updates",
  "jurisdiction_codes": "J_US_FED",
  "body_of_law": "CASE",
  "keywords": "Alice Mayo patent eligibility abstract idea"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "rule_name": "Patent Law Updates",
  "status": "ACTIVE",
  "created_at": "2024-04-29T10:00:00Z"
}
```

---

**`PATCH /v1/lexcore/monitor-rules/{rule_id}`**  
Update monitor rule (pause, resume, change keywords).

**Response (200):**
```json
{
  "id": "uuid",
  "status": "PAUSED",
  "updated_at": "2024-04-29T11:00:00Z"
}
```

---

**`DELETE /v1/lexcore/monitor-rules/{rule_id}`**  
Delete (archive) a monitor rule.

**Response (204):** No content

---

## LexRadar Domain Routes

### Invention Candidates

**`GET /v1/lexradar/inventions`**  
List invention candidates with status filter.

**Query Parameters:**
```
status: string (DETECTED|SCORING|SCORED|DISCLOSING|DISCLOSED|FILED, optional)
limit: integer (1-1000, default 50)
offset: integer (default 0)
```

**Response (200):**
```json
{
  "inventions": [/* array of InventionSummary */],
  "total": 47,
  "limit": 50,
  "offset": 0
}
```

---

**`GET /v1/lexradar/inventions/{invention_id}`**  
Get detailed invention candidate with scores and evidence.

**Response (200):**
```json
{
  "id": "uuid",
  "title": "Distributed Consensus Algorithm for Legal Document Versioning",
  "description": "...",
  "source_url": "https://github.com/.../pull/123",
  "source_type": "GitHub",
  "novelty_score": 0.84,
  "nonobviousness_score": 0.79,
  "utility_score": 0.91,
  "enablement_score": 0.88,
  "scope_score": 0.72,
  "evidence_score": 0.85,
  "composite_score": 0.83,
  "status": "SCORED",
  "detected_at": "2024-04-15T08:00:00Z",
  "scored_at": "2024-04-16T02:00:00Z",
  "prior_art_count": 12,
  "disclosure_id": "uuid"
}
```

---

### Prior Art Search

**`POST /v1/lexradar/inventions/{invention_id}/prior-art/search`**  
Trigger prior art search across 7 sources.

**Request Body:**
```json
{
  "keywords": ["distributed consensus", "legal document", "versioning"],
  "sources": ["USPTO", "WIPO", "EPO", "Lens", "GooglePatents"]
}
```

**Response (202):**
```json
{
  "task_id": "uuid",
  "status": "queued",
  "estimated_duration_seconds": 180
}
```

---

**`GET /v1/lexradar/inventions/{invention_id}/prior-art`**  
Get prior art results for an invention.

**Response (200):**
```json
{
  "invention_id": "uuid",
  "results": [/* array of PriorArtResult */],
  "total": 23,
  "sources_searched": 7,
  "sources_with_results": 5
}
```

---

### Disclosure Generation

**`POST /v1/lexradar/inventions/{invention_id}/disclosure`**  
Generate disclosure draft (LHP format).

**Request Body:**
```json
{
  "disclosure_type": "PROVISIONAL",
  "claim_themes": ["system", "method", "computer-readable medium"]
}
```

**Response (202):**
```json
{
  "disclosure_id": "uuid",
  "invention_id": "uuid",
  "status": "DRAFT",
  "grounding_score": 0.0,
  "generation_job_id": "uuid"
}
```

---

**`GET /v1/lexradar/disclosures/{disclosure_id}`**  
Get disclosure draft (all 10 sections).

**Response (200):**
```json
{
  "id": "uuid",
  "invention_id": "uuid",
  "title": "Distributed Consensus Algorithm for Legal Document Versioning",
  "inventor": "Jane Doe",
  "status": "DRAFT",
  "grounding_score": 0.89,
  "sections": {
    "abstract": "...",
    "inventor": "Jane Doe",
    "title": "Distributed Consensus Algorithm...",
    "background": "...",
    "summary": "...",
    "detailed_description": "...",
    "claims": "...",
    "drawings_description": "...",
    "abstract_of_invention": "...",
    "advantages": "...",
    "alternative_implementations": "...",
    "example": "...",
    "prior_art_summary": "...",
    "references": "...",
    "grounding_sources": "...",
    "additional_materials": "..."
  }
}
```

---

### Handoff Delivery

**`POST /v1/lexradar/handoffs`**  
Deliver handoff package to attorney.

**Request Body:**
```json
{
  "disclosure_draft_id": "uuid",
  "attorney_email": "patents@lawfirm.com",
  "attorney_name": "Sarah Johnson",
  "message": "Please review this provisional patent application draft."
}
```

**Response (201):**
```json
{
  "handoff_id": "uuid",
  "portal_url": "https://portal.lexradar.com/h/abc123-def456",
  "expires_at": "2024-05-01T10:00:00Z",
  "status": "DELIVERED"
}
```

---

## Auth Routes

### Token Exchange

**`POST /v1/auth/token`**  
Exchange API key for JWT access token pair.

**Request Body:**
```json
{
  "api_key": "lex_tenant_1234567890abcdef..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Errors:**
- `401 INVALID_API_KEY` — Invalid format or not found
- `401 API_KEY_EXPIRED` — API key revoked
- `403 TENANT_INACTIVE` — Tenant account suspended

---

### Token Refresh

**`POST /v1/auth/refresh`**  
Refresh access token using refresh token (rotation).

**Request Body:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",  // New refresh token, old invalidated
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Errors:**
- `401 REFRESH_TOKEN_INVALID` — Token invalid or expired
- `401 REFRESH_TOKEN_REVOKED` — Token blacklisted
- `403 TENANT_INACTIVE` — Tenant account suspended

---

## Health Routes

### Kubernetes Probes

**`GET /health/live`**  
Liveness probe — returns 200 if process is running.

**Response (200):**
```json
{"status": "alive"}
```

---

**`GET /health/ready`**  
Readiness probe — returns 200 if all dependencies are healthy.

**Response (200):**
```json
{
  "status": "ready",
  "dependencies": {
    "database": {"status": "healthy", "latency_ms": 12.4},
    "redis": {"status": "healthy", "latency_ms": 3.1},
    "qdrant": {"status": "healthy", "latency_ms": 45.2}
  }
}
```

**Response (503):**
```json
{
  "status": "not_ready",
  "dependencies": {
    "database": {"status": "unhealthy", "error": "Connection timeout"},
    "redis": {"status": "healthy", "latency_ms": 3.1},
    "qdrant": {"status": "healthy", "latency_ms": 45.2}
  }
}
```

---

**`GET /health/version`**  
API version and build info.

**Response (200):**
```json
{
  "version": "v1.0.0",
  "build_sha": "abc123",
  "build_date": "2024-04-29T10:00:00Z",
  "environment": "production"
}
```

---

## Common Response Formats

### Pagination
```json
{
  "data": [...],
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 145230,
    "has_more": true
  }
}
```

### Error Response
```json
{
  "error": {
    "code": "SEARCH_TIMEOUT",
    "message": "Search exceeded 5 second timeout",
    "status": 504,
    "request_id": "req_abc123",
    "timestamp": "2024-04-29T10:00:00Z"
  }
}
```

### Rate Limit Response (429)
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Retry after 60 seconds.",
    "status": 429,
    "retry_after": 60,
    "rate_limit": {
      "limit": 10000,
      "remaining": 0,
      "reset_at": "2024-04-30T00:00:00Z",
      "window": "monthly"
    }
  }
}
```

---

## Middleware Execution Order

1. **CORS** (`CORSMiddleware`) — CORS headers
2. **Trusted Host** (`TrustedHostMiddleware`) — Host validation
3. **Rate Limit** (`RateLimitMiddleware`) — Redis sliding window
4. **Tenant Context** (`TenantContextMiddleware`) — Set `app.tenant_id` for RLS
5. **JWT Auth** (`JWTAuthMiddleware`) — Validate token, extract claims

---

## Versioning Policy

- **Current:** `v1`
- **Path-based:** `/v1/...`
- **Breaking changes:** Require new version (v2, v3)
- **Deprecation notice:** 30 days before removal
- **Compatibility window:** 2 versions supported simultaneously
- **Sunset header:** `Sunset: <date>` on deprecated endpoints

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-29 | Initial API specification | C04 API contracts definition |
