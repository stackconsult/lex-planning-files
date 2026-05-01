# MCP_TOOLS.md — Model Context Protocol Tools

> **Build System:** Unified Build System v2  
> **Chunk:** C04 — API Contracts + MCP Tools  
> **Horde:** HORDE-API  
> **Control Plane:** ENGINEERING  

---

## Overview

LexCore + LexRadar exposes 7 MCP (Model Context Protocol) tools. These tools are the primary interface for AI clients, providing standardized capabilities discovery, legal search, research, document retrieval, citation analysis, legislative monitoring, and jurisdiction coverage reporting.

**Protocol:** MCP v1.0  
**Transport:** HTTP REST (WebSocket deferred to Enhancement Loop)  
**Auth:** JWT Bearer token in `Authorization` header  
**Content-Type:** `application/json`  
**Base Path:** `/v1/mcp`

---

## Tool Catalog (7 Tools)

### Tool 1: `get_capabilities`

**Purpose:** Advertise supported jurisdictions, document types, and available tools to AI clients.  
**Method:** `GET`  
**Path:** `/v1/mcp/capabilities`  
**Auth:** None (public endpoint)  
**Idempotency:** Fully idempotent — safe to cache indefinitely  

**Response Format:**
```json
{
  "jurisdictions": {
    "J_US_FED": {
      "name": "United States Federal",
      "coverage_percent": 0.92,
      "doc_count": 145230,
      "last_ingest": "2024-04-29T06:00:00Z"
    }
  },
  "doc_types": ["STATUTE", "REGULATION", "CASE"],
  "tools": [
    {
      "name": "search_legal",
      "description": "Search legal documents using hybrid vector + full-text search",
      "parameters": {
        "query": {"type": "string", "required": true, "maxLength": 500},
        "jurisdiction": {"type": "string", "required": false},
        "body_of_law": {"type": "string", "required": false, "enum": ["STATUTE", "REGULATION", "CASE"]},
        "top_k": {"type": "integer", "required": false, "default": 10, "min": 1, "max": 100},
        "include_citations": {"type": "boolean", "required": false, "default": true}
      }
    }
  ],
  "version": "v1.0.0",
  "server_time": "2024-04-29T10:00:00Z"
}
```

**Implementation Notes:**
- Response cached for 5 minutes (configurable)
- `coverage_percent` is pre-computed during ingestion pipeline
- Tool parameters follow JSON Schema draft-07

---

### Tool 2: `search_legal`

**Purpose:** Execute hybrid search across legal document corpus.  
**Method:** `POST`  
**Path:** `/v1/mcp/search_legal`  
**Auth:** JWT (tenant_id claim required)  
**Timeout:** 5 seconds (soft), 30 seconds (hard via uvicorn)  
**Idempotency:** Keyed by `SHA-256(query + jurisdiction + body_of_law + top_k)`  
**Cache:** Redis, 24h TTL by default, configurable per tenant

**BAM Routing:**
- This tool receives a BAM compound signal from the client
- `AGT_ROUTER` parses the BAM compound, verifies it's a legal search intent
- Routes to `AGT_SEARCH` for execution
- All BAM signals logged with `correlation_id` for audit

**Request Parameters:**
```json
{
  "query": "patent obviousness software inventions Alice Mayo",
  "jurisdiction": "J_US_FED",         // Optional — null searches all tenant jurisdictions
  "body_of_law": "CASE",            // Optional — null searches all types
  "top_k": 10,                      // Optional — default 10, max 100
  "include_citations": true         // Optional — default true
}
```

**Response Format:**
```json
{
  "results": [
    {
      "document_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Alice Corp. v. CLS Bank International",
      "citation": "573 U.S. 208 (2014)",
      "jurisdiction": "J_US_FED",
      "body_of_law": "CASE",
      "source": "CourtListener",
      "summary": "Supreme Court decision on patent eligibility of abstract ideas implemented on generic computers. The Court held that abstract ideas implemented on generic computers are not patent eligible under 35 U.S.C. 101.",
      "url": "https://courtlistener.com/opinion/2735709/alice-corp-v-cls-bank-intl/",
      "score": 0.9432,
      "published_date": "2014-06-19",
      "chunk_relevance": [
        {"chunk_index": 3, "chunk_type": "SECTION", "relevance": 0.98}
      ]
    }
  ],
  "total": 47,
  "latency_ms": 245.3,
  "cache_hit": false,
  "search_strategy": "hybrid",
  "vector_results": 23,
  "fulltext_results": 31,
  "reranked_results": 10,
  "citation_chains": [
    {
      "document_id": "550e8400-e29b-41d4-a716-446655440000",
      "direction": "backward",
      "depth": 2,
      "chain": [
        {"id": "uuid", "citation": "Mayo v. Prometheus", "authority_score": 0.91}
      ]
    }
  ],
  "query_normalized": "patent obviousness software invention alice mayo framework eligibility abstract idea generic computer 35 usc 101"
}
```

**Error Responses:**
- `400 INVALID_QUERY` — Query empty or exceeds 500 characters
- `400 INVALID_JURISDICTION` — Jurisdiction code not in tenant's active jurisdictions
- `400 INVALID_BODY_OF_LAW` — body_of_law not in [STATUTE, REGULATION, CASE]
- `401 TENANT_NOT_FOUND` — JWT tenant_id does not exist in database
- `429 RATE_LIMIT_EXCEEDED` — Request exceeds tenant's rate limit (SOLO: 10K/month)
- `504 SEARCH_TIMEOUT` — Search exceeded 5 second timeout (partial results may be returned)

**Search Strategy Breakdown:**
1. **Cache Check** — Check Redis for `tenant:{tenant_id}:query:{fingerprint}` (0-2ms)
2. **Query Embedding** — Generate 1536-dim embedding via OpenAI (50-100ms, cached)
3. **Vector Search** — HNSW approximate nearest neighbor in Qdrant (20-50ms)
4. **Full-Text Search** — PostgreSQL GIN tsvector query (30-80ms)
5. **Re-rank** — Cross-encoder re-ranking of combined results (100-300ms for top 50)
6. **Citation Chain** — Optional citation graph traversal (50-150ms)
7. **Cache Store** — Store results in Redis with TTL

**Latency Budgets:**
| Step | Target (P50) | Target (P95) | Max |
|------|-------------|-------------|-----|
| Cache hit | 2ms | 5ms | 10ms |
| Cache miss — vector search | 200ms | 350ms | 500ms |
| Cache miss — full pipeline | 300ms | 500ms | 5000ms |
| Citation chain | 50ms | 100ms | 150ms |

---

### Tool 3: `research_task`

**Purpose:** Execute complex legal research with question decomposition, parallel sub-searches, and structured synthesis.  
**Method:** `POST`  
**Path:** `/v1/mcp/research_task`  
**Auth:** JWT (tenant_id claim required)  
**Timeout:** 60 seconds (research may run longer via async task)  
**Idempotency:** At-most-once — each call may produce different results (not cacheable)  

**BAM Routing:**
- `AGT_ROUTER` identifies research task intent from BAM compound
- Dispatches to `AGT_ANALYSIS`
- `AGT_ANALYSIS` decomposes question into sub-queries, runs parallel `search_legal` calls, synthesizes report

**Request Parameters:**
```json
{
  "question": "How has the Alice/Mayo framework been applied to AI-generated inventions in 2023-2024?",
  "jurisdictions": ["J_US_FED", "J_CA_FED"],
  "output_format": "structured_report",  // Options: structured_report, memo, brief
  "max_sources": 20                     // Range: 5-50, default 20
}
```

**Response Format (Synchronous — < 60s):**
```json
{
  "report": "# AI Inventions Under Alice/Mayo Framework\n\n## Executive Summary\nThe Alice/Mayo two-step framework...",
  "citation_chain": [
    {
      "document_id": "uuid",
      "citation": "Thaler v. Perlmutter",
      "authority_level": "primary",
      "relevance": 0.89,
      "key_passage": "The court held that AI-generated works lack the human element required for copyright..."
    }
  ],
  "confidence": 0.87,
  "gap_detected": true,
  "gaps": [
    "No Federal Circuit decisions specifically addressing LLM-generated patent claims",
    "Limited guidance on AI inventorship from PTO (Oct 2023 guidance only)",
    "No Canadian precedent on AI inventorship"
  ],
  "sub_queries": [
    {"query": "Alice Mayo framework AI patent applications 2023 2024", "result_count": 12},
    {"query": "AI-generated inventions patent eligibility 35 USC 101", "result_count": 8},
    {"query": "PTO guidance AI inventorship October 2023", "result_count": 3}
  ],
  "latency_ms": 45678.2,
  "task_id": "uuid"
}
```

**Response Format (Asynchronous — > 60s):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "QUEUED",
  "estimated_completion_seconds": 180,
  "poll_url": "/v1/mcp/research_task/550e8400-e29b-41d4-a716-446655440001/status"
}
```

**Status Polling:**
```
GET /v1/mcp/research_task/{task_id}/status
Response: {"task_id": "...", "status": "RUNNING|COMPLETED|FAILED", "progress_percent": 65}
```

**Error Responses:**
- `400 INVALID_QUESTION` — Question empty or > 2000 characters
- `400 INVALID_JURISDICTIONS` — Contains unsupported jurisdiction codes
- `400 INVALID_OUTPUT_FORMAT` — Not in [structured_report, memo, brief]
- `401 TENANT_NOT_FOUND` — JWT tenant_id invalid
- `429 RATE_LIMIT_EXCEEDED` — Research tasks limited to 50/month (SOLO), unlimited (FIRM+)
- `503 LLM_UNAVAILABLE` — Analysis engine (OpenAI/GPT-4) unavailable
- `504 RESEARCH_TIMEOUT` — Task queued for async processing

---

### Tool 4: `get_document`

**Purpose:** Retrieve a complete legal document with all chunks, citations, and metadata.  
**Method:** `GET`  
**Path:** `/v1/mcp/document`  
**Auth:** JWT (tenant_id claim required)  
**Timeout:** 2 seconds  
**Idempotency:** Keyed by `doc_id` or `citation` string  
**Cache:** Redis, 1h TTL

**BAM Routing:**
- Direct API call (no agent dispatch for simple document retrieval)
- RLS ensures tenant isolation at database layer

**Request Parameters (Query String):**
```
?doc_id=550e8400-e29b-41d4-a716-446655440000
?citation=CFR%201.1.1
```
*At least one parameter required. doc_id takes precedence if both provided.*

**Response Format:**
```json
{
  "document": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Title 35 — Patents",
    "citation": "35 U.S.C. 101",
    "jurisdiction": "J_US_FED",
    "body_of_law": "STATUTE",
    "source": "eCFR",
    "summary": "Whoever invents or discovers any new and useful process, machine, manufacture, or composition of matter...",
    "url": "https://ecfr.gov/current/title-35/chapter-I/part-1/section-101",
    "version": "2024-01-15",
    "metadata": {"title_number": "35", "chapter": "I", "part": "1"},
    "published_date": "2024-01-15",
    "last_modified": "2024-03-20",
    "is_current": true,
    "superseded_by": null
  },
  "chunks": [
    {
      "id": "uuid",
      "chunk_index": 0,
      "chunk_type": "SECTION",
      "content": "Whoever invents or discovers any new and useful process, machine, manufacture, or composition of matter, or any new and useful improvement thereof, may obtain a patent therefor, subject to the conditions and requirements of this title.",
      "embedding_preview": "[1536-dim vector — not returned in API]"
    }
  ],
  "citations": {
    "forward": [
      {"id": "uuid", "citation": "Diamond v. Chakrabarty", "cited_in": "section 101 discussion"}
    ],
    "backward": [
      {"id": "uuid", "citation": "Statute of Monopolies, 1624", "cites_this": "historical basis"}
    ]
  },
  "metadata": {
    "total_chunks": 12,
    "section_count": 3,
    "paragraph_count": 8,
    "word_count": 2847,
    "jurisdiction_name": "United States Federal"
  }
}
```

**Error Responses:**
- `400 MISSING_IDENTIFIER` — Neither doc_id nor citation provided
- `404 DOCUMENT_NOT_FOUND` — No document matches ID or citation in tenant's corpus
- `403 TENANT_ISOLATION` — Document belongs to different tenant (should not happen with RLS)

---

### Tool 5: `get_citations`

**Purpose:** Traverse citation graph with authority scoring and overruled detection.  
**Method:** `POST`  
**Path:** `/v1/mcp/citations`  
**Auth:** JWT (tenant_id claim required)  
**Timeout:** 3 seconds  
**Idempotency:** Keyed by `doc_id + direction + depth`  
**Cache:** Redis, 6h TTL

**BAM Routing:**
- `AGT_ROUTER` dispatches to `AGT_CITE`
- `AGT_CITE` performs graph traversal with cycle detection

**Request Parameters:**
```json
{
  "doc_id": "550e8400-e29b-41d4-a716-446655440000",
  "direction": "both",    // Options: forward, backward, both
  "depth": 3              // Range: 1-5, default 3
}
```

**Response Format:**
```json
{
  "nodes": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "citation": "Alice Corp. v. CLS Bank International, 573 U.S. 208 (2014)",
      "title": "Alice Corp. v. CLS Bank International",
      "authority_score": 0.95,
      "is_overruled": false,
      "depth_from_root": 0
    },
    {
      "id": "uuid2",
      "citation": "Mayo Collaborative Services v. Prometheus Laboratories, Inc., 566 U.S. 66 (2012)",
      "title": "Mayo Collaborative Services v. Prometheus Laboratories",
      "authority_score": 0.91,
      "is_overruled": false,
      "depth_from_root": 1
    }
  ],
  "edges": [
    {
      "source": "550e8400-e29b-41d4-a716-446655440000",
      "target": "uuid2",
      "direction": "BACKWARD",
      "context": "Alice Corp. cited Mayo as precedent for the two-step framework",
      "location": "Majority opinion, p. 7"
    }
  ],
  "authority_chain": [
    "550e8400-e29b-41d4-a716-446655440000",
    "uuid2",
    "uuid3"
  ],
  "overruled_cases": [
    {
      "id": "uuid4",
      "citation": "State Street Bank v. Signature Financial Group",
      "overruled_by": "550e8400-e29b-41d4-a716-446655440000",
      "overruled_date": "2014-06-19",
      "authority_score_at_overrule": 0.72
    }
  ],
  "graph_stats": {
    "total_nodes": 23,
    "total_edges": 34,
    "max_depth_reached": 3,
    "cycles_detected": 0
  }
}
```

**Error Responses:**
- `400 INVALID_DEPTH` — Depth must be 1-5
- `404 DOCUMENT_NOT_FOUND` — Document not found in tenant's corpus
- `500 CYCLE_DETECTED` — Circular citation detected (should not happen with data integrity constraints)

---

### Tool 6: `check_updates`

**Purpose:** Check for legislative changes since a given date for monitored jurisdictions.  
**Method:** `POST`  
**Path:** `/v1/mcp/check_updates`  
**Auth:** JWT (tenant_id claim required)  
**Timeout:** 2 seconds  
**Idempotency:** Keyed by `jurisdiction + since_date + alert_types`  
**Cache:** Redis, 1h TTL

**BAM Routing:**
- `AGT_ROUTER` dispatches to `AGT_MONITOR`
- `AGT_MONITOR` checks monitor rules, returns changes detected since date

**Request Parameters:**
```json
{
  "jurisdiction": "J_US_FED",
  "since_date": "2024-01-01",
  "alert_types": ["AMENDMENT", "NEW"]  // Options: AMENDMENT, REPEAL, NEW
}
```

**Response Format:**
```json
{
  "updates": [
    {
      "document_id": "uuid",
      "rule_id": "uuid",
      "rule_name": "Patent Law Updates",
      "change_type": "AMENDMENT",
      "change_summary": "Section 101 amended to clarify AI inventorship following PTO Oct 2023 guidance",
      "previous_version_url": "https://ecfr.gov/.../2024-01-01",
      "current_version_url": "https://ecfr.gov/.../2024-03-20",
      "detected_at": "2024-04-28T12:00:00Z",
      "acknowledged": false
    }
  ],
  "total": 23,
  "new_count": 5,
  "change_count": 18,
  "repeal_count": 0,
  "monitored_jurisdictions": ["J_US_FED", "J_CA_FED"],
  "monitor_rules_active": 3
}
```

**Error Responses:**
- `400 INVALID_DATE` — since_date in future or > 2 years ago
- `400 INVALID_ALERT_TYPES` — Contains unsupported alert type
- `404 JURISDICTION_NOT_MONITORED` — No active monitor rule for jurisdiction

---

### Tool 7: `jurisdiction_summary`

**Purpose:** Get coverage statistics and recent ingestion activity for a jurisdiction.  
**Method:** `GET`  
**Path:** `/v1/mcp/jurisdiction/{jurisdiction_code}`  
**Auth:** JWT (tenant_id claim required)  
**Timeout:** 1 second  
**Idempotency:** Keyed by `jurisdiction_code`  
**Cache:** Redis, 5 minutes TTL

**BAM Routing:**
- Direct API call (no agent dispatch)
- Aggregated statistics pre-computed during ingestion

**Path Parameters:**
```
jurisdiction_code: string (e.g., "J_US_FED", "J_CA_FED")
```

**Response Format:**
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
    {
      "document_id": "uuid",
      "change_type": "NEW",
      "change_summary": "New Federal Circuit decision: In re [Party]",
      "detected_at": "2024-04-28T12:00:00Z"
    }
  ],
  "sources": [
    {"source": "eCFR", "doc_count": 87650, "last_ingest": "2024-04-29T06:00:00Z"},
    {"source": "CourtListener", "doc_count": 55240, "last_ingest": "2024-04-29T05:00:00Z"},
    {"source": "US Congress API", "doc_count": 2340, "last_ingest": "2024-04-28T18:00:00Z"}
  ],
  "trend": {
    "documents_added_7d": 1240,
    "documents_added_30d": 5230,
    "avg_ingest_rate_per_day": 174
  }
}
```

**Error Responses:**
- `404 JURISDICTION_NOT_FOUND` — Unknown jurisdiction code

---

## BAM (Binary Action Matrix) Integration

Every MCP tool call carries an implicit or explicit BAM compound signal:

```
BAM Signal Structure:
{
  "intent": "legal_search|research_task|document_retrieve|citation_graph|update_check|jurisdiction_query",
  "jurisdiction_scope": "J_US_FED|J_CA_FED|...",
  "doc_type_scope": "STATUTE|REGULATION|CASE|ALL",
  "confidence": 0.0-1.0,
  "routing_decision": "AGT_SEARCH|AGT_ANALYSIS|AGT_CITE|AGT_MONITOR|direct",
  "timestamp": "ISO 8601",
  "correlation_id": "uuid"
}
```

**BAM Genesis Hash:** `a96893482a3e79e75437ed19c21be1c9f618633c88cd5102f1e2d020035ade96`

**BAM Routing Rules:**
- Simple document retrieval (`get_document`, `jurisdiction_summary`) → Direct API, no agent
- Search queries (`search_legal`) → `AGT_ROUTER` → `AGT_SEARCH`
- Complex analysis (`research_task`) → `AGT_ROUTER` → `AGT_ANALYSIS`
- Citation traversal (`get_citations`) → `AGT_ROUTER` → `AGT_CITE`
- Update monitoring (`check_updates`) → `AGT_ROUTER` → `AGT_MONITOR`

---

## Rate Limits per Tool

| Tool | SOLO (10K/mo) | FIRM (Unlimited) | ENTERPRISE (Unlimited) |
|------|--------------|-----------------|----------------------|
| get_capabilities | 100/min | 1000/min | 1000/min |
| search_legal | 50/min | 500/min | 1000/min |
| research_task | 10/day | 100/day | 500/day |
| get_document | 200/min | 2000/min | 5000/min |
| get_citations | 50/min | 500/min | 1000/min |
| check_updates | 100/min | 1000/min | 1000/min |
| jurisdiction_summary | 100/min | 1000/min | 1000/min |

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-29 | Initial MCP tools specification | C04 API contracts definition |
