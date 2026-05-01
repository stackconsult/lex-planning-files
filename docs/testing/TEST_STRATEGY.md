# TEST_STRATEGY.md — LexCore + LexRadar Testing Strategy

> **Build System:** Unified Build System v2 | **Chunk:** C08 — Testing + QA | **Horde:** HORDE-QA

---

## Overview

Testing is organized in 4 tiers plus HORDE-AUDIT gate. Objective: ≥ 80% code coverage, zero empty tests, zero trivial passes, mandatory security/resilience validation.

**Frameworks:** pytest (Python), Jest + React Testing Library (TS/React), Playwright (E2E)  
**CI Gate:** Coverage < 80% blocks merge  

---

## Testing Pyramid

```
         ┌─────────────────┐
         │   HORDE-AUDIT   │   (143 checks, 5 layers)
         │   Manual gate   │
         └─────────────────┘
         ┌─────────────────┐
         │   E2E Tests     │   (~50 tests, Playwright)
         │   P95 < 10 min  │
         └─────────────────┘
         ┌─────────────────┐
         │ Integration     │   (~200 tests, Docker Compose)
         │   P95 < 15 min  │
         └─────────────────┘
         ┌─────────────────┐
         │   Unit Tests    │   (~500 tests, pytest + Jest)
         │   P95 < 5 min   │
         └─────────────────┘
```

---

## Tier 1: Unit Tests

### API Unit Tests (Python)

**Framework:** pytest + pytest-asyncio + pytest-mock  
**Coverage target:** 85%  
**Location:** `api/tests/unit/`  

**Categories:**
- **Service tests** (60%): mock repositories, verify business logic, assert audit calls
- **Repository tests** (20%): mock database connection, verify SQL generation, RLS context
- **Utility tests** (15%): parsers, validators, formatters, hash functions
- **Agent tests** (5%): mock service calls, verify BAM routing, AGT-G1 isolation

**Required Mocks:**
- PostgreSQL (asyncpg connection pool)
- Redis (fakeredis)
- Qdrant (mock client)
- OpenAI (responses library)
- Clerk (JWKS mock)
- External APIs (responses + aioresponses)

### Frontend Unit Tests (TypeScript)

**Framework:** Jest + React Testing Library + MSW  
**Coverage target:** 80%  
**Location:** `frontend/src/__tests__/`  

**Categories:**
- **Component tests** (60%): render, interact, assert DOM state
- **Hook tests** (25%): custom hooks, SWR caching, Zustand store
- **Utility tests** (15%): formatters, validators, query builders

---

## Tier 2: Integration Tests

**Framework:** pytest + Docker Compose  
**Coverage target:** 70% of service boundaries  
**Location:** `api/tests/integration/`  

**Test Stack:** PostgreSQL + pgvector, Redis, Qdrant, API container

**Categories:**
- API endpoint tests: Full HTTP request/response cycle, auth validation, rate limiting
- Database integration: Migration runs, RLS policies, constraint validation
- Cache integration: Redis TTL, eviction, hit/miss behavior
- Search integration: End-to-end hybrid search (vector + full-text + re-rank)
- Pipeline integration: Ingestion pipeline (fetch → parse → chunk → embed → index)
- Auth integration: Clerk JWT → tenant context → RLS enforcement
- Worker integration: Celery task submission → execution → result storage

---

## Tier 3: E2E Tests

**Framework:** Playwright  
**Location:** `e2e/tests/`  

**Critical Paths:**
1. User signup → login → search → view result → export
2. Admin creates tenant → invites user → user accepts
3. Developer connects GitHub → scanner detects invention → scores prior art → drafts disclosure
4. Attorney portal: receives email → views handoff → edits sections → submits review
5. Blockchain anchoring: disclosure filed → verify hash on Polygon

**Devices:** Desktop Chrome, Mobile Safari

---

## Tier 4: HORDE-AUDIT Gate

**Trigger:** Before any production deploy  
**Check count:** 143 checks across 5 layers  
**Gate result:** PASS or BLOCKED  

### 5 Layers

| Layer | Checks | Key Criteria |
|-------|--------|-------------|
| L1 Contract Compliance | 35 | Every horde output matches spec |
| L2 Test Coverage | 25 | ≥ 80% coverage, no empty tests, no trivial passes |
| L3 Security/Guardrails | 38 | Zero critical CVEs, BYOK passes, no auto-filing paths, no agent-to-agent imports |
| L4 Eval Judge Scores | 25 | ToolCallJudge ≥ 0.90, GroundingJudge ≥ 0.85, adversarial pass ≥ 0.85 |
| L5 Documentation | 20 | Docstrings, API docs, runbooks, ADRs complete |

### Critical Conditions (5 System-Wide)

| ID | Condition | Violation |
|----|-----------|-----------|
| SYS-CRIT-01 | Raw IP in Polygon tx | IP-G1 violation |
| SYS-CRIT-02 | Auto-filing code path exists | IP-G7 violation |
| SYS-CRIT-03 | Agent imports another agent directly | AGT-G1 violation |
| SYS-CRIT-04 | test_byok fails | SEC-G2 violation |
| SYS-CRIT-05 | verify_bundle() missing after store | Integrity chain broken |

---

## Security Test Requirements

| Test | Purpose | Tool |
|------|---------|------|
| `test_byok` | Verify Bring-Your-Own-Key isolation | pytest |
| `test_rls_enforcement` | Verify row-level security per tenant | pytest |
| `test_rate_limiting` | Verify rate limit enforcement | pytest |
| `test_circuit_breaker` | Verify circuit breaker transitions | pytest |
| `test_correlation_id_propagation` | Verify tracing end-to-end | pytest |
| `test_no_raw_ip_in_tx` | Verify only hashes on-chain | pytest |
| `test_bundle_integrity` | Verify verify_bundle() chain | pytest |
| `test_tenant_isolation` | Verify no cross-tenant data leakage | pytest |
| `test_empty_disclosure_rejection` | Verify empty disclosures rejected | pytest |
| `test_citation_grounding` | Verify citations link real sources | pytest |

---

## Coverage Enforcement

```yaml
# .github/workflows/coverage-gate.yaml
jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests with coverage
        run: pytest --cov=api --cov-report=xml --cov-fail-under=80
      - name: Upload to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          fail_ci_if_error: true
```

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-30 | Initial test strategy | C08 Testing + QA definition |
