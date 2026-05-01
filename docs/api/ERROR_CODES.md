# ERROR_CODES.md — LexCore + LexRadar API Error Reference

> **Build System:** Unified Build System v2  
> **Chunk:** C04 — API Contracts + MCP Tools  
> **Horde:** HORDE-API  
> **Control Plane:** ENGINEERING  

---

## Error Response Format

All API errors follow a standardized JSON structure:

```json
{
  "error": {
    "code": "SEARCH_TIMEOUT",
    "message": "Search exceeded 5 second timeout",
    "status": 504,
    "request_id": "req_abc123",
    "timestamp": "2024-04-29T10:00:00Z",
    "details": {}  // Optional additional context
  }
}
```

---

## HTTP Status Code Categories

| Range | Category | Description |
|-------|----------|-------------|
| 2xx | Success | Request completed successfully |
| 3xx | Redirect | Redirected (not used in v1 API) |
| 4xx | Client Error | Request is malformed, unauthorized, or not found |
| 5xx | Server Error | Server-side failure |

---

## 400 Bad Request — Client Input Errors

| Code | Message | Context | Resolution |
|------|---------|---------|------------|
| `INVALID_QUERY` | Query is empty or exceeds 500 characters | MCP `search_legal` | Provide query between 1-500 characters |
| `INVALID_JURISDICTION` | Jurisdiction code is not supported or not in tenant's active jurisdictions | MCP `search_legal`, `check_updates` | Use `get_capabilities` to list valid jurisdictions |
| `INVALID_BODY_OF_LAW` | body_of_law must be STATUTE, REGULATION, or CASE | MCP `search_legal` | Use valid enum value |
| `INVALID_QUESTION` | Question is empty or exceeds 2000 characters | MCP `research_task` | Provide question between 10-2000 characters |
| `INVALID_JURISDICTIONS` | One or more jurisdiction codes are not supported | MCP `research_task` | Verify jurisdiction codes with `get_capabilities` |
| `INVALID_OUTPUT_FORMAT` | Output format must be structured_report, memo, or brief | MCP `research_task` | Use valid enum value |
| `INVALID_DEPTH` | Citation depth must be between 1 and 5 | MCP `get_citations` | Use depth in range [1, 5] |
| `INVALID_DATE` | Date is in the future or more than 2 years ago | MCP `check_updates` | Provide valid historical date |
| `INVALID_ALERT_TYPES` | One or more alert types are not supported | MCP `check_updates` | Use valid enum: AMENDMENT, REPEAL, NEW |
| `MISSING_IDENTIFIER` | Either doc_id or citation must be provided | MCP `get_document` | Provide at least one identifier |
| `INVALID_API_KEY` | API key format is invalid or not found | Auth `token_exchange` | Verify key format: `lex_{tenant_id}_{32chars}` |
| `ATTORNEY_INVALID_EMAIL` | Attorney email format is invalid | LexRadar `handoff_deliver` | Provide valid email address |
| `SOURCE_NOT_CONNECTED` | OAuth connection not configured for source | LexRadar `scan_trigger` | Connect source via settings first |
| `SCAN_IN_PROGRESS` | Scan already running for this source | LexRadar `scan_trigger` | Wait for current scan to complete |
| `INSUFFICIENT_PRIOR_ART` | Prior art search is incomplete for this invention | LexRadar `disclosure_generate` | Run prior art search first |
| `GROUNDING_FAILED` | Grounding score below threshold (0.70) | LexRadar `disclosure_generate` | Improve invention documentation or evidence chain |
| `DISCLOSURE_NOT_APPROVED` | Disclosure must be in APPROVED status before handoff | LexRadar `handoff_deliver` | Approve disclosure in UI first |
| `WEBHOOK_INVALID` | Webhook signature verification failed | LexRadar webhook | Verify webhook secret and signature format |
| `INVALID_STATUS` | Status filter is not in allowed enum | LexRadar `candidate_list` | Use valid status value |

---

## 401 Unauthorized — Authentication Errors

| Code | Message | Context | Resolution |
|------|---------|---------|------------|
| `MISSING_TOKEN` | Authorization header is missing | All protected endpoints | Include `Authorization: Bearer <token>` header |
| `INVALID_TOKEN` | Token format is invalid or malformed | All protected endpoints | Verify JWT format (3 base64 segments) |
| `TOKEN_EXPIRED` | Access token has expired | All protected endpoints | Use refresh token to obtain new access token |
| `TENANT_NOT_FOUND` | JWT tenant_id claim does not exist in database | All protected endpoints | Verify token was issued for valid tenant |
| `API_KEY_EXPIRED` | API key has been revoked or expired | Auth `token_exchange` | Generate new API key from dashboard |
| `REFRESH_TOKEN_INVALID` | Refresh token is invalid or expired | Auth `refresh` | Re-authenticate with API key or Clerk |
| `REFRESH_TOKEN_REVOKED` | Refresh token has been blacklisted | Auth `refresh` | Re-authenticate with API key or Clerk |

---

## 403 Forbidden — Authorization Errors

| Code | Message | Context | Resolution |
|------|---------|---------|------------|
| `TENANT_ISOLATION` | Document belongs to a different tenant | MCP `get_document`, `search_legal` | Request document from correct tenant context |
| `TENANT_INACTIVE` | Tenant account is suspended | Auth `token_exchange`, `refresh` | Contact support to reactivate account |
| `INSUFFICIENT_PERMISSIONS` | User role does not have permission for this action | LexRadar `handoff_deliver` | Use admin account or upgrade role |
| `FORBIDDEN` | Access to this resource is forbidden | All endpoints | Verify user role and resource permissions |

---

## 404 Not Found — Resource Errors

| Code | Message | Context | Resolution |
|------|---------|---------|------------|
| `DOCUMENT_NOT_FOUND` | No document matches the provided ID or citation | MCP `get_document`, `get_citations` | Verify document ID or citation exists |
| `JURISDICTION_NOT_FOUND` | Unknown jurisdiction code | MCP `jurisdiction_summary` | Use `get_capabilities` to list valid codes |
| `JURISDICTION_NOT_MONITORED` | No active monitor rule for jurisdiction | MCP `check_updates` | Create monitor rule for jurisdiction |
| `RULE_NOT_FOUND` | Monitor rule not found | LexCore `monitor_rules` CRUD | Verify rule ID exists for tenant |
| `INVENTION_NOT_FOUND` | Invention candidate not found | LexRadar `disclosure_generate` | Verify invention ID exists |
| `DISCLOSURE_NOT_FOUND` | Disclosure draft not found | LexRadar `handoff_deliver` | Verify disclosure ID exists |
| `HANDOFF_NOT_FOUND` | Handoff package not found | Attorney portal | Verify handoff ID or check expiry |
| `USER_NOT_FOUND` | User not found | Auth, management | Verify user ID exists |
| `WORKSPACE_NOT_FOUND` | Workspace not found | Management | Verify workspace ID exists |

---

## 409 Conflict — State Errors

| Code | Message | Context | Resolution |
|------|---------|---------|------------|
| `SCAN_IN_PROGRESS` | Scan already running for this source | LexRadar `scan_trigger` | Wait for current scan to complete |
| `DISCLOSURE_ALREADY_EXISTS` | Disclosure already generated for this invention | LexRadar `disclosure_generate` | Use existing disclosure or create new version |
| `DUPLICATE_MONITOR_RULE` | Monitor rule with this name already exists | LexCore monitor rules | Use different rule name |
| `EMAIL_ALREADY_EXISTS` | Email address already registered | Signup | Use different email or sign in |

---

## 422 Unprocessable Entity — Validation Errors

| Code | Message | Context | Resolution |
|------|---------|---------|------------|
| `GROUNDING_FAILED` | Grounding score below threshold (0.70) | LexRadar `disclosure_generate` | Add more evidence or prior art references |
| `DISCLOSURE_NOT_APPROVED` | Disclosure must be APPROVED before handoff | LexRadar `handoff_deliver` | Complete review and approve disclosure |
| `INVALID_CLAIM_THEMES` | Claim themes must be valid patent claim types | LexRadar `disclosure_generate` | Use valid themes: system, method, apparatus, computer-readable medium |

---

## 429 Too Many Requests — Rate Limit Errors

| Code | Message | Context | Resolution |
|------|---------|---------|------------|
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded for this endpoint | All rate-limited endpoints | Wait for rate limit window to reset |

**Rate Limit Response Headers:**
```
X-RateLimit-Limit: 10000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1714399200
X-RateLimit-Window: monthly
Retry-After: 3600
```

---

## 500 Internal Server Error — Server Errors

| Code | Message | Context | Resolution |
|------|---------|---------|------------|
| `INTERNAL_ERROR` | An unexpected error occurred | All endpoints | Retry with exponential backoff; contact support if persistent |
| `DATABASE_ERROR` | Database connection failed | All endpoints | Retry; system will auto-recover with circuit breaker |
| `CYCLE_DETECTED` | Circular citation detected in graph | MCP `get_citations` | Report to HORDE-SCHEMA — data integrity issue |

---

## 502 Bad Gateway — Upstream Errors

| Code | Message | Context | Resolution |
|------|---------|---------|------------|
| `UPSTREAM_ERROR` | Upstream service (OpenAI, Qdrant, etc.) is unavailable | MCP `search_legal`, `research_task` | Retry with exponential backoff |
| `CONNECTOR_ERROR` | Legal document source API is unavailable | Ingestion | System will retry automatically; check source status |

---

## 503 Service Unavailable — Temporary Unavailability

| Code | Message | Context | Resolution |
|------|---------|---------|------------|
| `LLM_UNAVAILABLE` | Analysis engine (OpenAI/GPT-4) is unavailable | MCP `research_task` | Retry after 30-60 seconds |
| `SERVICE_UNAVAILABLE` | Service is temporarily unavailable | All endpoints | Wait and retry; check status page |

---

## 504 Gateway Timeout — Timeout Errors

| Code | Message | Context | Resolution |
|------|---------|---------|------------|
| `SEARCH_TIMEOUT` | Search exceeded 5 second timeout | MCP `search_legal` | Partial results may be returned; simplify query or reduce top_k |
| `RESEARCH_TIMEOUT` | Research task exceeded 60 second timeout | MCP `research_task` | Task queued for async processing; poll for status |
| `INGESTION_TIMEOUT` | Document ingestion exceeded timeout | Ingestion | System will retry automatically |
| `QUERY_TIMEOUT` | Database query exceeded timeout | All endpoints | Simplify query or retry |

---

## Error Code Summary Table

| Code | Status | Category | Tool/Route |
|------|--------|----------|-----------|
| INVALID_QUERY | 400 | Input | search_legal |
| INVALID_JURISDICTION | 400 | Input | search_legal, check_updates |
| INVALID_BODY_OF_LAW | 400 | Input | search_legal |
| INVALID_QUESTION | 400 | Input | research_task |
| INVALID_JURISDICTIONS | 400 | Input | research_task |
| INVALID_OUTPUT_FORMAT | 400 | Input | research_task |
| INVALID_DEPTH | 400 | Input | get_citations |
| INVALID_DATE | 400 | Input | check_updates |
| INVALID_ALERT_TYPES | 400 | Input | check_updates |
| MISSING_IDENTIFIER | 400 | Input | get_document |
| INVALID_API_KEY | 401 | Auth | token_exchange |
| ATTORNEY_INVALID_EMAIL | 400 | Input | handoff_deliver |
| SOURCE_NOT_CONNECTED | 400 | Input | scan_trigger |
| SCAN_IN_PROGRESS | 400/409 | State | scan_trigger |
| INSUFFICIENT_PRIOR_ART | 400 | State | disclosure_generate |
| GROUNDING_FAILED | 422 | Validation | disclosure_generate |
| DISCLOSURE_NOT_APPROVED | 422 | Validation | handoff_deliver |
| WEBHOOK_INVALID | 401 | Auth | webhooks |
| INVALID_STATUS | 400 | Input | candidate_list |
| MISSING_TOKEN | 401 | Auth | All protected |
| INVALID_TOKEN | 401 | Auth | All protected |
| TOKEN_EXPIRED | 401 | Auth | All protected |
| TENANT_NOT_FOUND | 401 | Auth | All protected |
| API_KEY_EXPIRED | 401 | Auth | token_exchange |
| REFRESH_TOKEN_INVALID | 401 | Auth | refresh |
| REFRESH_TOKEN_REVOKED | 401 | Auth | refresh |
| TENANT_ISOLATION | 403 | Authorization | get_document, search_legal |
| TENANT_INACTIVE | 403 | Authorization | token_exchange, refresh |
| INSUFFICIENT_PERMISSIONS | 403 | Authorization | handoff_deliver, admin routes |
| FORBIDDEN | 403 | Authorization | All |
| DOCUMENT_NOT_FOUND | 404 | Resource | get_document, get_citations |
| JURISDICTION_NOT_FOUND | 404 | Resource | jurisdiction_summary |
| JURISDICTION_NOT_MONITORED | 404 | Resource | check_updates |
| RULE_NOT_FOUND | 404 | Resource | monitor_rules CRUD |
| INVENTION_NOT_FOUND | 404 | Resource | disclosure_generate |
| DISCLOSURE_NOT_FOUND | 404 | Resource | handoff_deliver |
| HANDOFF_NOT_FOUND | 404 | Resource | attorney portal |
| USER_NOT_FOUND | 404 | Resource | management |
| WORKSPACE_NOT_FOUND | 404 | Resource | management |
| DISCLOSURE_ALREADY_EXISTS | 409 | State | disclosure_generate |
| DUPLICATE_MONITOR_RULE | 409 | State | monitor rules |
| EMAIL_ALREADY_EXISTS | 409 | State | signup |
| INVALID_CLAIM_THEMES | 422 | Validation | disclosure_generate |
| RATE_LIMIT_EXCEEDED | 429 | Rate Limit | All rate-limited |
| INTERNAL_ERROR | 500 | Server | All |
| DATABASE_ERROR | 500 | Server | All |
| CYCLE_DETECTED | 500 | Data Integrity | get_citations |
| UPSTREAM_ERROR | 502 | Upstream | search_legal, research_task |
| CONNECTOR_ERROR | 502 | Upstream | Ingestion |
| LLM_UNAVAILABLE | 503 | Service | research_task |
| SERVICE_UNAVAILABLE | 503 | Service | All |
| SEARCH_TIMEOUT | 504 | Timeout | search_legal |
| RESEARCH_TIMEOUT | 504 | Timeout | research_task |
| INGESTION_TIMEOUT | 504 | Timeout | Ingestion |
| QUERY_TIMEOUT | 504 | Timeout | All |

---

## Client Retry Strategy

| Status Code | Retry Strategy | Max Retries | Backoff |
|-------------|---------------|-------------|---------|
| 400 | Do not retry — fix request | 0 | N/A |
| 401 | Do not retry — re-authenticate | 0 | N/A |
| 403 | Do not retry — insufficient permissions | 0 | N/A |
| 404 | Do not retry — verify resource exists | 0 | N/A |
| 409 | Retry once after 5s (state may resolve) | 1 | Fixed 5s |
| 422 | Do not retry — fix validation | 0 | N/A |
| 429 | Retry after `Retry-After` header | 5 | Exponential with jitter |
| 500 | Retry with exponential backoff | 3 | 1s, 2s, 4s |
| 502 | Retry with exponential backoff | 3 | 1s, 2s, 4s |
| 503 | Retry with exponential backoff | 5 | 2s, 4s, 8s, 16s, 32s |
| 504 | Retry once (partial results may be cached) | 1 | 5s |

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-29 | Initial error code registry | C04 API contracts definition |
