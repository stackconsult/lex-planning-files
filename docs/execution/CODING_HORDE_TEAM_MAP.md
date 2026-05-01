# CODING_HORDE_TEAM_MAP.md

> **Build System:** Unified Build System v2 | **Phase:** P1-P5 Coding Execution  
> **Status:** PLANNED — Awaiting User Review Before Execution  
> **Date:** 2026-04-30

## Phase Execution Map

| Phase | Trigger | Active Hordes | Primary Gate Metric |
|-------|---------|---------------|---------------------|
| **P0 Foundation** | `@phase0` | HORDE-ARCH, HORDE-INFRA, HORDE-SECURITY | Contracts hash locked, terraform clean, CI passes |
| **P1 LexCore DB** | P0 gate pass | HORDE-SCHEMA, HORDE-API, HORDE-INGEST, HORDE-EVAL | ToolCallJudge >= 0.90, P95 search < 300ms |
| **P2 IP Pipeline** | P1 gate pass | HORDE-AGENTS, HORDE-SCORING, HORDE-DISCLOSURE, HORDE-EVAL | Grounding >= 0.85, all 7 fetchers live |
| **P3 Ledger** | P2 gate pass | HORDE-LEDGER, HORDE-AGENTS, HORDE-INFRA, HORDE-EVAL | BYOK passes, full pipeline < 3s |
| **P4 Portal** | P3 gate pass | HORDE-PORTAL, HORDE-API, HORDE-SECURITY, HORDE-EVAL, HORDE-DOCS | Tenant isolation clean, attorney flow < 5 min |
| **P5 Hardening** | P4 gate pass | HORDE-EVAL, HORDE-INFRA, HORDE-SECURITY, HORDE-DOCS, HORDE-SCHEMA | All agents >= 0.90, load P99 < 10s, zero HIGH CVEs |

## Horde Directory

| Horde | Instances | Role | Owner | Control Plane | Status |
|-------|-----------|------|-------|---------------|--------|
| HORDE-ARCH | 1 | Architecture & Contracts | EN-01 + AI-01 | ENGINEERING | SPEC COMPLETE |
| HORDE-INFRA | 2 | Terraform + K8s + CI/CD | EN-02 | OPERATIONS | SPEC COMPLETE |
| HORDE-SECURITY | 1 | Security Pipeline | EN-03 | QUALITY | SPEC COMPLETE |
| HORDE-AUDIT | 1 | 5-Layer Quality Gate | EN-04 | QUALITY | SPEC COMPLETE |
| HORDE-SCHEMA | 2 | Migrations + RLS + Indexes | EN-05 | ENGINEERING + QUALITY | PENDING |
| HORDE-API | 3 | OpenAPI + Routes + Auth | EN-06 | ENGINEERING | PENDING |
| HORDE-INGEST | 3 | Document Ingestion | EN-07 | ENGINEERING | PENDING |
| HORDE-EVAL | 2 | Tests + Evals + Fitness | EN-08 | QUALITY | PENDING |
| HORDE-AGENTS | 5 | Services + Repos + Workers + Agents | AI-02 + AI-03 | ENGINEERING + QUALITY | PENDING |
| HORDE-SCORING | 2 | Prior Art Scoring | AI-03 + IP-01 | ENGINEERING | PENDING |
| HORDE-DISCLOSURE | 2 | Disclosure Drafting | AI-03 + IP-02 | ENGINEERING | PENDING |
| HORDE-LEDGER | 1 | Blockchain Anchoring | EN-07 + EN-03 | ENGINEERING | PENDING |
| HORDE-PORTAL | 3 | Next.js Frontend + UI | EN-05 | PRODUCT + ENGINEERING | PENDING |
| HORDE-DOCS | 1 | User Docs + Handoff | EN-09 | PRODUCT | PENDING |
| HORDE-CONDUCTOR | 1 | Orchestration + Release | EN-01 | PRODUCT + OPERATIONS | PENDING |

---

## Instance-Level Role Breakdown

### P0 Foundation (Specs Complete)

**HORDE-ARCH (arch-01):** System architecture, dependency graphs, interface contracts, event schemas, ADRs. Input: C01-C04 specs. Output: SYSTEM_LAYERS.md, DEPENDENCY_GRAPH.json, INTERFACE_CONTRACTS.json, EVENT_SCHEMA_REGISTRY.json, 3 ADRs. Gate: No cycles, all 7 layers, all contracts + events.

**HORDE-INFRA (infra-01):** Terraform IaC (VPC, EKS, ALB, CloudWatch). Input: Architecture docs, C07 specs. Output: Terraform modules. Gate: terraform plan clean, kubectl apply --dry-run passes.

**HORDE-INFRA (infra-02):** Kubernetes manifests, Helm charts, CI/CD pipelines, monitoring stack. Input: C07 specs. Output: K8s manifests, GitHub Actions workflows, Prometheus/Grafana configs. Gate: CI pipeline green on test commit.

**HORDE-SECURITY (sec-01):** Security pipeline, SAST/DAST, secret scanning, RLS auditing, CVE scanning. Input: All code from P1-P4. Output: SBOM.json, OWASP checklist, findings report. Gate: gitleaks zero, pip-audit zero HIGH/CRITICAL.

**HORDE-AUDIT (audit-01):** 5-layer quality gate. Input: All outputs from target horde. Output: Signed audit report (PASS or BLOCKED). Gate: Zero critical findings, coverage >= 80%, no security violations.

### P1 Core Build

**HORDE-SCHEMA (schema-01):** Alembic migrations, schema definitions, seed data. Input: Architecture docs, ERD.md. Output: Migration files, seed data, test_migrations.py. Gate: upgrade/downgrade/upgrade passes.

**HORDE-SCHEMA (schema-02):** RLS policies, pgvector indexes, query optimization, constraint registry. Input: Schema definitions. Output: RLS policies, indexes, test_rls.py. Gate: RLS tests pass, query intent index aligned.

**HORDE-API (api-01):** OpenAPI specification refinement, request/response models. Input: Schema specs, interface contracts. Output: openapi.yaml, request_models.py, response_models.py. Gate: openapi-spec-validator passes, no Any types.

**HORDE-API (api-02):** FastAPI routes implementation (MCP tools, LexCore, LexRadar). Input: OpenAPI spec, service contracts. Output: Fully implemented routes with service bindings. Gate: All routes return correct status codes, MCP tools schema-valid.

**HORDE-API (api-03):** Middleware (JWT auth, tenant context, rate limiting), event contracts, error envelopes. Input: Auth spec, event registry. Output: Middleware implementations, event handlers, error handling. Gate: Auth claims map complete, event contracts complete, error envelopes defined.

**HORDE-INGEST (ingest-01):** Document connectors (GitHub, USPTO, WIPO, EPO, PACER, SEC, State). Input: API routes, database schema. Output: 7 connectors with async clients. Gate: All 7 connectors fetch and parse correctly.

**HORDE-INGEST (ingest-02):** Docling parser, chunker, embedder (OpenAI embeddings). Input: Connector outputs. Output: Parser, chunker, embedder implementations. Gate: 1,000+ documents ingested, all chunks embedded.

**HORDE-INGEST (ingest-03):** Queue consumers, Celery workers, ingestion orchestration. Input: Parser/chunker/embedder. Output: 11 Celery tasks, 9 queue pools, DLQ handling. Gate: Queue processing < 5s per doc.

**HORDE-EVAL (eval-01):** Unit tests, integration tests, E2E tests (Playwright), load tests (Locust). Input: All code from target hordes. Output: Test suites for all layers. Gate: Coverage >= 80%, all E2E pass, load P99 < 5s under 100 concurrent.

**HORDE-EVAL (eval-02):** Agent evals (ToolCallJudge, GroundingJudge), regression tests, release fitness. Input: Agent implementations. Output: Golden sets, judge implementations, release fitness report. Gate: ToolCallJudge >= 0.90, GroundingJudge >= 0.85, adversarial pass rate >= 0.85.

### P2 IP Pipeline

**HORDE-AGENTS (agent-01):** Service layer (18 services: LexCore 5, LexRadar 6, Shared 4, Pipeline 3). Input: API contracts, event schemas. Output: services/ directory with complete implementations. Gate: All service methods have docstrings, type hints, error handling.

**HORDE-AGENTS (agent-02):** Repository layer (one file per DB entity, SQLAlchemy async). Input: Schema definitions, COLUMN_SPEC.json. Output: repositories/ directory. Gate: All CRUD operations implemented, RLS context enforced.

**HORDE-AGENTS (agent-03):** Celery workers (11 tasks, 9 queue pools, DLQ handling). Input: Service layer. Output: workers/ directory. Gate: All tasks have retry logic, correlation ID propagation, circuit breaker integration.

**HORDE-AGENTS (agent-04):** AI agents (16 agents: 7 LexCore + 9 LexRadar). Input: Service layer, OpenAI API. Output: agents/ directory with tool registries. Gate: ToolCallJudge >= 0.90, no agent-to-agent direct imports (AGT-G1).

**HORDE-AGENTS (agent-05):** Integration tests, shared utilities (resilience, exceptions, logging, audit). Input: All P1 outputs. Output: tests/integration/, shared/ directory. Gate: All integration tests pass, mypy strict passes.

**HORDE-SCORING (scoring-01):** Prior art scoring engine (6 dimension scorers). Input: Prior art data from ingest. Output: Scoring engine with composite scoring. Gate: Scoring model calibrated, composite engine functional.

**HORDE-SCORING (scoring-02):** Blocking classifier, scoring calibration, adversarial testing. Input: Scoring engine. Output: Calibrated model, adversarial test results. Gate: Grounding >= 0.85, no regression.

**HORDE-DISCLOSURE (disclosure-01):** 10 LHP section drafters, claim themes, claim drafting. Input: Scoring results, agent outputs. Output: Disclosure drafting engine. Gate: All 10 LHP sections draftable, Grounding >= 0.85.

**HORDE-DISCLOSURE (disclosure-02):** Filing bundle packager (9 documents), compliance checker, attorney handoff. Input: Disclosure drafts. Output: Filing bundle generator, compliance reports. Gate: All 9 documents generated, bundle integrity verified, no auto-filing paths (IP-G7).

### P3 Ledger + Automation

**HORDE-LEDGER (ledger-01):** Blockchain anchoring (Polygon), SHA-256 hashing, AES-256 encryption, cert PDF generation. Input: Schema (proof_ledger table), filing bundles. Output: Immutable proof layer. Gate: BYOK test passes, ledger tx confirmed on Polygon, zero plaintext IP in tx (SYS-CRIT-01).

### P4 Portal + Handoff

**HORDE-PORTAL (portal-01):** Next.js App Router pages, layouts, routing. Input: SCREEN_MAP.md, API spec. Output: All 23 screens with routes. Gate: TypeScript strict passes, all routes render without errors.

**HORDE-PORTAL (portal-02):** shadcn/ui components, feature components, forms. Input: COMPONENT_LIBRARY.md, API spec. Output: 30+ components with TypeScript interfaces. Gate: ESLint clean, accessibility tests pass, empty/loading/error states on all lists.

**HORDE-PORTAL (portal-03):** Onboarding wizard, activation tracker, client-side state (Zustand, SWR). Input: ONBOARDING_SUCCESS.md, API spec. Output: Multi-step wizard, activation tracker, state management. Gate: Activation events fire, first-value journey E2E passes.

**HORDE-DOCS (docs-01):** User docs, FAQ, feature guides, handoff package. Input: All P1-P4 outputs. Output: docs/user/, docs/handoff/, email templates. Gate: All handoff audiences covered, onboarding materials complete.

### P5 Hardening

**HORDE-EVAL (eval-03):** Extended load testing, penetration test support, final regression. Input: All P4 outputs. Output: Load test report, regression report. Gate: Load P99 < 10s under sustained load, zero regressions.

**HORDE-SECURITY (sec-02):** Final security audit, CVE remediation, pen test results. Input: All P4 outputs. Output: Final findings report, CVE remediation log. Gate: Zero HIGH/CRITICAL CVEs, all security findings addressed.

**HORDE-CONDUCTOR (conductor-01):** Final orchestration, release promotion, production deployment. Input: All P5 outputs, release fitness report. Output: Production deployment, git tag, release notes. Gate: All gates green, HORDE-AUDIT PASS, human checkpoint signed.

---

## Execution Dependency Graph

```
P0 Foundation (Specs Complete)
├── HORDE-ARCH (arch-01) ──▶ HORDE-INFRA, HORDE-SCHEMA
├── HORDE-INFRA (infra-01) ──▶ infra-02
├── HORDE-INFRA (infra-02) ──▶ P1, P4, P5
└── HORDE-SECURITY (sec-01) ──▶ Continuous (monitors all phases)
    └─▶ HORDE-AUDIT (audit-01) ──▶ Gates every phase

P1 Core Build
├── HORDE-SCHEMA (schema-01) ──▶ schema-02, HORDE-API
│   └── schema-02 ──▶ HORDE-INGEST
├── HORDE-API (api-01) ──▶ api-02
│   └── api-02 ──▶ api-03
│       └── api-03 ──▶ HORDE-INGEST, HORDE-AGENTS, HORDE-PORTAL
├── HORDE-INGEST (ingest-01) ──▶ ingest-02
│   └── ingest-02 ──▶ ingest-03
│       └── ingest-03 ──▶ HORDE-SCORING
└── HORDE-EVAL (eval-01) ──▶ Monitors P1, feeds into eval-02
    └── eval-02 ──▶ P2 gates

P2 IP Pipeline
├── HORDE-AGENTS (agent-01) ──▶ agent-02
│   └── agent-02 ──▶ agent-03
│       └── agent-03 ──▶ agent-04
│           └── agent-04 ──▶ agent-05
│               └── agent-05 ──▶ HORDE-DISCLOSURE, HORDE-EVAL
├── HORDE-SCORING (scoring-01) ──▶ scoring-02
│   └── scoring-02 ──▶ HORDE-DISCLOSURE
└── HORDE-DISCLOSURE (disclosure-01) ──▶ disclosure-02
    └── disclosure-02 ──▶ HORDE-LEDGER, HORDE-EVAL

P3 Ledger
├── HORDE-LEDGER (ledger-01) ──▶ HORDE-EVAL, HORDE-CONDUCTOR

P4 Portal + Handoff
├── HORDE-PORTAL (portal-01) ──▶ portal-02
│   └── portal-02 ──▶ portal-03
│       └── portal-03 ──▶ HORDE-DOCS, HORDE-EVAL
└── HORDE-DOCS (docs-01) ──▶ HORDE-CONDUCTOR

P5 Hardening
├── HORDE-EVAL (eval-03) ──▶ HORDE-CONDUCTOR
├── HORDE-SECURITY (sec-02) ──▶ HORDE-CONDUCTOR
└── HORDE-CONDUCTOR (conductor-01) ──▶ PRODUCTION
```

---

## Critical Path Analysis

**Longest chain (critical path):**
```
P0: HORDE-ARCH ──▶ P1: HORDE-SCHEMA ──▶ HORDE-API ──▶ HORDE-INGEST ──▶ P2: HORDE-AGENTS ──▶ HORDE-SCORING ──▶ HORDE-DISCLOSURE ──▶ P3: HORDE-LEDGER ──▶ P4: HORDE-PORTAL ──▶ P5: HORDE-EVAL + HORDE-SECURITY ──▶ HORDE-CONDUCTOR
```

**Parallelizable workstreams:**
- HORDE-INFRA (terraform + K8s) can run alongside HORDE-SCHEMA
- HORDE-SECURITY continuous scanning runs parallel to all coding
- HORDE-PORTAL (frontend) can begin after HORDE-API api-02 completes
- HORDE-DOCS (user docs) can begin after HORDE-PORTAL portal-03 completes

**Gate bottleneck:** HORDE-AUDIT runs after every phase — cannot be parallelized

---

## Human Checkpoints

| Checkpoint | Phase | Trigger | Decision Required |
|------------|-------|---------|-----------------|
| **HC-1: Architecture Lock** | End of P0 | All specs hash-locked | EN-01 approves architecture before schema migrations begin |
| **HC-2: Security Trust** | End of P2 | HORDE-SECURITY findings report | Human reviews security findings before IP pipeline production |
| **HC-3: UX/Handoff** | End of P4 | HORDE-DOCS handoff package | Human reviews onboarding flow before claiming production-ready |
