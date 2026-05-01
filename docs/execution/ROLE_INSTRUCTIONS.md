# ROLE_INSTRUCTIONS.md

> **Status:** PLANNED — Awaiting User Review Before Execution

## General Execution Rules

1. Read PROJECT_MANIFEST.md first
2. Only HORDE-CONDUCTOR updates manifest
3. Hash-lock all outputs
4. No direct agent imports (AGT-G1)
5. Zero IP in blockchain (SYS-CRIT-01)
6. No auto-filing paths (SYS-CRIT-02)
7. HORDE-AUDIT after every phase
8. Fail fast on criticals
9. Document everything (docstrings)
10. Type hints everywhere (mypy strict)

## P1 Core Build Instructions

### schema-01: Migrations
- Read: SYSTEM_LAYERS.md, ERD.md, SCHEMA_MAP.json, CONSTRAINT_REGISTRY.json
- Build: alembic.ini, env.py, 001_initial_schema.py (24 tables), base_seed.sql
- Test: upgrade/downgrade/upgrade passes
- Gate: All 3 migration tests pass

### schema-02: RLS + Indexes
- Read: 002_rls_policies.sql, 003_pgvector_indexes.sql, SECURITY_HEADERS.md
- Build: 002_rls_policies.py (26 policies), 003_pgvector_indexes.py (HNSW + GIN), test_rls.py
- Test: Cross-tenant SELECT empty, INSERT raises 403
- Gate: RLS bypass blocked, indexes used in explain plans

### api-01: OpenAPI + Models
- Read: API_SPEC.md, INTERFACE_CONTRACTS.json, EVENT_SCHEMA_REGISTRY.json
- Build: openapi.yaml, request_models.py, response_models.py
- Test: openapi-spec-validator passes, mypy strict clean
- Gate: No Any types, all schemas valid

### api-02: FastAPI Routes
- Read: openapi.yaml, request_models.py, SERVICE_CATALOG.md
- Build: mcp.py (7 tools), lexcore.py, lexradar.py, auth.py
- Test: All routes return correct status codes
- Gate: MCP tools schema-valid

### api-03: Middleware
- Read: AUTH_FLOW.md, RATE_LIMIT_POLICY.md, ERROR_CODES.md
- Build: jwt_auth.py, tenant_context.py, rate_limit.py, events/, errors/
- Test: Auth claims map complete, rate limits enforced
- Gate: Middleware order correct, event contracts complete

### ingest-01: Connectors
- Read: API routes, schema
- Build: 7 connectors (GitHub, USPTO, WIPO, EPO, PACER, SEC, State)
- Test: All 7 fetch and parse correctly
- Gate: Async clients, error handling, rate limit respect

### ingest-02: Parser + Chunker + Embedder
- Read: Connector outputs
- Build: Docling parser, chunker, OpenAI embedder
- Test: 1000+ docs ingested, all chunks embedded
- Gate: Embedding dim=1536, chunk size 512 tokens

### ingest-03: Workers
- Read: Parser/chunker/embedder
- Build: 11 Celery tasks, 9 queue pools, DLQ handling
- Test: Queue processing < 5s per doc
- Gate: Retry logic, correlation ID, circuit breaker

### eval-01: Tests
- Read: All P1 code
- Build: Unit, integration, E2E (Playwright), load (Locust) tests
- Test: Coverage >= 80%, E2E all pass
- Gate: P99 < 5s under 100 concurrent

### eval-02: Agent Evals
- Read: Agent implementations
- Build: ToolCallJudge, GroundingJudge, golden sets, regression tests
- Test: Judge scores meet thresholds
- Gate: ToolCallJudge >= 0.90, GroundingJudge >= 0.85

## P2 IP Pipeline Instructions

### agent-01: Service Layer
- Read: API contracts, event schemas
- Build: 18 services (LexCore 5, LexRadar 6, Shared 4, Pipeline 3)
- Test: All methods have docstrings, type hints, error handling
- Gate: mypy strict passes

### agent-02: Repository Layer
- Read: COLUMN_SPEC.json, schema definitions
- Build: One file per DB entity (SQLAlchemy async)
- Test: All CRUD operations, RLS context enforced
- Gate: No raw SQL, parameterized queries only

### agent-03: Celery Workers
- Read: Service layer
- Build: 11 tasks, 9 queue pools, DLQ handling
- Test: Retry logic, correlation ID propagation
- Gate: Circuit breaker integration, task ack after completion

### agent-04: AI Agents
- Read: Service layer, OpenAI API
- Build: 16 agents (7 LexCore + 9 LexRadar) with tool registries
- Test: ToolCallJudge >= 0.90
- Gate: No agent-to-agent direct imports (AGT-G1)

### agent-05: Integration Tests + Shared
- Read: All P1 outputs
- Build: tests/integration/, shared/ (resilience, exceptions, logging, audit)
- Test: All integration tests pass
- Gate: mypy strict passes, audit logging present

### scoring-01: Scoring Engine
- Read: Prior art data from ingest
- Build: 6 dimension scorers with composite engine
- Test: Scoring model calibrated
- Gate: Composite engine functional

### scoring-02: Calibration + Testing
- Read: Scoring engine
- Build: Blocking classifier, adversarial tests
- Test: Grounding >= 0.85
- Gate: No regression from baseline

### disclosure-01: Disclosure Drafting
- Read: Scoring results, agent outputs
- Build: 10 LHP section drafters, claim themes
- Test: All 10 sections draftable
- Gate: Grounding >= 0.85

### disclosure-02: Filing Bundles
- Read: Disclosure drafts
- Build: 9-document bundle generator, compliance checker
- Test: Bundle integrity verified
- Gate: No auto-filing paths (IP-G7), verify_bundle() after every store

## P3 Ledger Instructions

### ledger-01: Blockchain Anchoring
- Read: proof_ledger table schema, filing bundles
- Build: SHA-256 hasher, Polygon anchor, AES-256 encryptor, cert PDF
- Test: BYOK test passes, ledger tx confirmed
- Gate: Zero plaintext IP in Polygon tx (SYS-CRIT-01)

## P4 Portal Instructions

### portal-01: Pages + Routing
- Read: SCREEN_MAP.md, API spec
- Build: 23 screens with Next.js App Router
- Test: TypeScript strict passes
- Gate: All routes render without errors

### portal-02: Components
- Read: COMPONENT_LIBRARY.md, API spec
- Build: 30+ components (shadcn/ui + feature components)
- Test: ESLint clean, accessibility tests pass
- Gate: Empty/loading/error states on all lists

### portal-03: Onboarding + State
- Read: ONBOARDING_SUCCESS.md, API spec
- Build: Multi-step wizard, activation tracker, Zustand + SWR state
- Test: Activation events fire
- Gate: First-value journey E2E passes

### docs-01: User Docs + Handoff
- Read: All P1-P4 outputs
- Build: docs/user/, docs/handoff/, email templates
- Test: All handoff audiences covered
- Gate: Onboarding materials complete

## P5 Hardening Instructions

### eval-03: Extended Testing
- Read: All P4 outputs
- Build: Load tests, regression tests, penetration test support
- Test: Load P99 < 10s under sustained load
- Gate: Zero regressions, performance baseline met

### sec-02: Final Security Audit
- Read: All P4 outputs
- Build: Final findings report, CVE remediation log
- Test: All security findings addressed
- Gate: Zero HIGH/CRITICAL CVEs

### conductor-01: Release
- Read: All P5 outputs, release fitness report
- Build: Production deployment, git tag, release notes
- Test: All gates green
- Gate: HORDE-AUDIT PASS, human checkpoint signed
