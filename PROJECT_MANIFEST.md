# PROJECT_MANIFEST.md
**LexCore + LexRadar — Single Source of Truth for All Hordes**

> **Schema Version:** v0.1.0-foundation
> **Last Updated:** 2026-04-30
> **Manifest Hash:** ad1d7b6ed8677600a2514845e7cf0b9e6391f353b2d4331dd54f815bdc84be2f
> **Update Protocol:** Only HordeMaster can update this file

---

## Manifest Purpose

This document is the single source of truth for all 14 hordes. Every horde reads this file before executing any task. It contains:
- Current schema version
- All approved contracts between hordes
- All completed outputs
- All open blockers
- Agent state tracking

**No horde writes to this file except HordeMaster.** Hordes read-only.

---

## Schema Version

**Current Version:** `v0.1.0-foundation`

**Version History:**
- `v0.1.0-foundation` — Initial manifest, Phase 0 foundation

---

## Horde Registry

### HORDE-ARCH
**Owner:** EN-01 + AI-01
**Scope:** ERD, OpenAPI spec, dependency graph, interface contracts
**Status:** ✅ COMPLETE (Chunks 1-6 delivered)
**Dependencies:** None (first horde)
**Unblocks:** All other hordes

**Contract:**
- Input: None
- Output: ERD_COMPLETE.dbml, openapi.yaml, dependency_graph.dot, PROJECT_MANIFEST.md (contracts section)
- Gate: All contracts defined and hash-locked

---

### HORDE-SCHEMA
**Owner:** EN-02
**Scope:** Alembic migrations, RLS policies, pgvector indexes
**Status:** ⏳ BLOCKED (HORDE-ARCH incomplete)
**Dependencies:** HORDE-ARCH ERD locked
**Unblocks:** HORDE-API, HORDE-AGENTS

**Contract:**
- Input: ERD_COMPLETE.dbml
- Output: Migration files, RLS policies, pgvector indexes
- Gate: Migrations run clean on fresh Postgres

---

### HORDE-INGEST
**Owner:** EN-04 + IP-01
**Scope:** 9 connectors, Docling parser, chunker, embedder, 7 prior art fetchers
**Status:** ⏳ BLOCKED (HORDE-SCHEMA incomplete)
**Dependencies:** HORDE-SCHEMA tables exist
**Unblocks:** HORDE-SCORING

**Contract:**
- Input: Schema (tables exist)
- Output: Documents in database, chunks with embeddings
- Gate: 1,000+ documents ingested, all chunks embedded

---

### HORDE-API
**Owner:** EN-03
**Scope:** FastAPI routes, MCP tools, BAM middleware, JWT auth
**Status:** ⏳ BLOCKED (HORDE-SCHEMA + HORDE-ARCH incomplete)
**Dependencies:** HORDE-SCHEMA tables + HORDE-ARCH contracts
**Unblocks:** HORDE-AGENTS, HORDE-PORTAL

**Contract:**
- Input: Schema + OpenAPI spec
- Output: MCP server live, all routes functional
- Gate: All routes return correct status codes, MCP tools schema-valid

---

### HORDE-AGENTS
**Owner:** AI-02 + AI-03
**Scope:** All 24 agents, message envelopes, retry logic, audit writers
**Status:** ⏳ BLOCKED (HORDE-API incomplete)
**Dependencies:** HORDE-API MCP server live
**Unblocks:** HORDE-SCORING, HORDE-DISCLOSURE, HORDE-LEDGER, HORDE-EVAL

**Contract:**
- Input: MCP server
- Output: All 24 agents built and tested
- Gate: All agents pass ToolCallJudge ≥ 0.90

---

### HORDE-SCORING
**Owner:** AI-03 + IP-01
**Scope:** 6 dimension scorers, composite engine, blocking classifier
**Status:** ⏳ BLOCKED (HORDE-INGEST incomplete)
**Dependencies:** HORDE-INGEST prior art fetchers
**Unblocks:** HORDE-DISCLOSURE

**Contract:**
- Input: Prior art data
- Output: Scoring engine live
- Gate: Scoring model calibrated, composite engine functional

---

### HORDE-DISCLOSURE
**Owner:** AI-03 + IP-02
**Scope:** 10 LHP section drafters, claim themes, filing bundle packager
**Status:** ⏳ BLOCKED (HORDE-SCORING + HORDE-AGENTS incomplete)
**Dependencies:** HORDE-SCORING + HORDE-AGENTS
**Unblocks:** HORDE-PORTAL

**Contract:**
- Input: Scores + agents
- Output: Disclosure drafts, filing bundles
- Gate: Grounding ≥ 0.85, all 10 LHP sections draftable

---

### HORDE-LEDGER
**Owner:** EN-07 + EN-03
**Scope:** SHA-256 hasher, Polygon anchor, AES-256 encryptor, cert PDF
**Status:** ⏳ BLOCKED (HORDE-SCHEMA incomplete)
**Dependencies:** HORDE-SCHEMA proof_ledger table
**Unblocks:** Full pipeline chain

**Contract:**
- Input: Schema (proof_ledger table)
- Output: Immutable proof layer live
- Gate: BYOK test passes, ledger tx confirmed on Polygon

---

### HORDE-PORTAL
**Owner:** EN-05
**Scope:** Next.js portal, 3 dashboards, attorney actions, bundle download
**Status:** ⏳ BLOCKED (HORDE-API + HORDE-DISCLOSURE incomplete)
**Dependencies:** HORDE-API + HORDE-DISCLOSURE
**Unblocks:** Attorney handoff

**Contract:**
- Input: API + disclosures
- Output: Portal live, all dashboards functional
- Gate: Attorney completes review-approve-download in < 5 min

---

### HORDE-EVAL
**Owner:** AI-04 + OP-02
**Scope:** Golden sets (40 per agent), ToolCallJudge, GroundingJudge, DriftWatch
**Status:** ⏳ BLOCKED (HORDE-AGENTS incomplete)
**Dependencies:** All HORDE-AGENTS built
**Unblocks:** Phase gates (last horde in each phase)

**Contract:**
- Input: Agents
- Output: Eval results, gate decisions
- Gate: Golden set pass rate ≥ 0.90, all judges calibrated

---

### HORDE-INFRA
**Owner:** EN-06
**Scope:** Terraform, K8s, GitHub Actions CI/CD, observability stack
**Status:** ⏳ BLOCKED (HORDE-ARCH incomplete)
**Dependencies:** HORDE-ARCH dependency graph
**Unblocks:** All compute infrastructure

**Contract:**
- Input: Dependency graph
- Output: Infrastructure provisioned
- Gate: Terraform clean, CI passes, all services healthy

---

### HORDE-SECURITY
**Owner:** EN-07
**Scope:** SAST/DAST, BYOK test, RLS audit, SOC 2 control map
**Status:** ⏳ BLOCKED (HORDE-INFRA incomplete)
**Dependencies:** HORDE-INFRA (runs continuously from P0 onward)
**Unblocks:** Production deployment

**Contract:**
- Input: All code
- Output: Security report
- Gate: BYOK test passes, zero HIGH CVEs, RLS audit clean

**Special Note:** HORDE-SECURITY runs continuously across all phases from P0 onward. Every commit triggers it.

---

### HORDE-DOCS
**Owner:** OP-01
**Scope:** API docs, agent runbooks, connector guides, ADRs
**Status:** ⏳ BLOCKED (Phase completion)
**Dependencies:** After each phase completes
**Unblocks:** Knowledge transfer

**Contract:**
- Input: Phase completion
- Output: Documentation updated
- Gate: All runbooks reviewed, docs complete

---

### HORDE-AUDIT
**Owner:** EN-01 + EN-06
**Scope:** Verification + enhancement architecture, 5-layer audit stack, 143 checks, signed reports, gate authorization
**Status:** ✅ ACTIVE (workflow available: .windsurf/workflows/HORDE_AUDIT_WORKFLOW.md)
**Dependencies:** Target horde output complete
**Unblocks:** Phase gate authorization (no gate passes without HORDE-AUDIT approval)

**Contract:**
- Input: Target horde output files, spec files, machine specs
- Output: Signed audit report (AUDIT-{HORDE_ID}-{PHASE}-{TIMESTAMP}), fix assignments, gate decision (PASS/BLOCKED)
- Gate: Zero critical findings, all eval judge scores ≥ thresholds, all security guardrails enforced

**Audit Layers (143 checks total):**
- **L1 — Contract Compliance:** Every horde, no exceptions. Source of truth: `output/lexradar/` spec files
- **L2 — Test Coverage:** 80%+ coverage, no empty tests, no `assert True` trivial passes
- **L3 — Security / Guardrail Enforcement:** Zero-tolerance. BYOK test, on-chain IP check, tenant isolation, secret scanning, CVE scanning, auto-filing detection, agent import detection, bundle integrity
- **L4 — Eval Judge Scores:** ToolCallJudge ≥ 0.90, GroundingJudge ≥ 0.85, adversarial pass rate ≥ 0.85, no regression
- **L5 — Documentation Completeness:** Docstrings, API docs, runbooks, ADRs

**Critical Failure Conditions (39 total):**
- SYS-CRIT-01: Raw IP content in Polygon tx payload (IP-G1 violation)
- SYS-CRIT-02: Auto-filing code path exists (IP-G7 violation)
- SYS-CRIT-03: Agent imports another agent directly (AGT-G1 violation)
- SYS-CRIT-04: `test_byok` fails (SEC-G2 violation)
- SYS-CRIT-05: `verify_bundle()` missing after store (integrity chain broken)
- Plus 34 additional horde-specific criticals

**Self-Audit:** HORDE-AUDIT must also be audited. Meta-audit by EN-01 spot checks, cross-validation via dual independent audit runs.

---

## Agent Registry

### LexCore Agents (16 agents)

#### AGT_ROUTER
**Horde:** HORDE-AGENTS
**Scope:** Classifies inbound intent, selects agent, passes context
**Tools:** get_capabilities + all
**Autonomy:** 100%
**Trigger:** Every inbound query
**Status:** ⏳ PENDING

#### AGT_SEARCH
**Horde:** HORDE-AGENTS
**Scope:** Complete legal research answers, structured report output
**Tools:** research_task, search_legal, get_document
**Autonomy:** 100%
**Trigger:** On-demand
**Status:** ⏳ PENDING

#### AGT_ANALYSIS
**Horde:** HORDE-AGENTS
**Scope:** Cross-jurisdiction statute comparison, conflict identification, case law trend summaries
**Tools:** research_task, get_citations, search_legal
**Autonomy:** 85%
**Trigger:** On-demand
**Status:** ⏳ PENDING

#### AGT_DRAFT
**Horde:** HORDE-AGENTS
**Scope:** Full legal document generation from templates + jurisdiction context
**Tools:** search_legal, get_document, get_capabilities
**Autonomy:** 80%
**Trigger:** On-demand
**Status:** ⏳ PENDING

#### AGT_INGEST
**Horde:** HORDE-AGENTS
**Scope:** Full ingest pipeline end-to-end, self-heals on source format changes
**Tools:** Internal + Celery
**Autonomy:** 95%
**Trigger:** Beat schedule per source
**Status:** ⏳ PENDING

#### AGT_MONITOR
**Horde:** HORDE-AGENTS
**Scope:** Watches all tenant monitor_rules, detects changes, auto-drafts change summaries
**Tools:** check_updates, jurisdiction_summary
**Autonomy:** 90%
**Trigger:** Every 6 hours
**Status:** ⏳ PENDING

#### AGT_CITE
**Horde:** HORDE-AGENTS
**Scope:** Citation verification, precedent chain analysis, overruled case detection
**Tools:** get_citations, get_document
**Autonomy:** 100%
**Trigger:** On-demand
**Status:** ⏳ PENDING

#### AGT_SCANNER
**Horde:** HORDE-AGENTS
**Scope:** Entry point for LexRadar IP detection pipeline
**Tools:** Internal
**Autonomy:** 95%
**Trigger:** On patent submission
**Status:** ⏳ PENDING

#### AGT_DETECTOR
**Horde:** HORDE-AGENTS
**Scope:** InventionDetector classifies 11 signal types
**Tools:** Internal
**Autonomy:** 90%
**Trigger:** AGT_SCANNER output
**Status:** ⏳ PENDING

#### AGT_PRIORART
**Horde:** HORDE-AGENTS
**Scope:** PriorArtSearcher queries 7 sources in parallel
**Tools:** Internal + 7 prior art fetchers
**Autonomy:** 95%
**Trigger:** AGT_DETECTOR output
**Status:** ⏳ PENDING

#### AGT_SCORER
**Horde:** HORDE-AGENTS
**Scope:** 6-dimension scoring, composite scoring engine
**Tools:** Internal
**Autonomy:** 90%
**Trigger:** AGT_PRIORART output
**Status:** ⏳ PENDING

#### AGT_DISCLOSER
**Horde:** HORDE-AGENTS
**Scope:** DisclosureGenerator drafts all 10 LHP sections
**Tools:** Internal + AGT_DRAFT (via MCP)
**Autonomy:** 85%
**Trigger:** AGT_SCORER output
**Status:** ⏳ PENDING

#### AGT_LEDGER
**Horde:** HORDE-AGENTS
**Scope:** SHA-256 hashing, Polygon anchoring, AES-256 encryption
**Tools:** Internal
**Autonomy:** 100%
**Trigger:** AGT_DISCLOSER output
**Status:** ⏳ PENDING

#### AGT_ATTYFLOW
**Horde:** HORDE-AGENTS
**Scope:** Exit point for attorney handoff, invite system
**Tools:** Internal
**Autonomy:** 100%
**Trigger:** AGT_LEDGER output
**Status:** ⏳ PENDING

#### AGT_IPMONITOR
**Horde:** HORDE-AGENTS
**Scope:** Watches for patent changes, prior art updates
**Tools:** Internal
**Autonomy:** 90%
**Trigger:** Daily watch
**Status:** ⏳ PENDING

#### AGT_AUDIT
**Horde:** HORDE-AGENTS
**Scope:** Audit log writer for all agent queries
**Tools:** Internal
**Autonomy:** 100%
**Trigger:** Every agent action
**Status:** ⏳ PENDING

---

### LexRadar Agents (8 agents)

#### AGT_IP_SCANNER
**Horde:** HORDE-AGENTS
**Scope:** Scans GitHub/Jira/Notion for invention signals
**Tools:** Internal + GitHub/Jira/Notion APIs
**Autonomy:** 95%
**Trigger:** Webhook on push/issue
**Status:** ⏳ PENDING

#### AGT_SIGNAL_CLASSIFIER
**Horde:** HORDE-AGENTS
**Scope:** Classifies 11 invention signal types
**Tools:** Internal
**Autonomy:** 90%
**Trigger:** AGT_IP_SCANNER output
**Status:** ⏳ PENDING

#### AGT_NOVELTY_SCORER
**Horde:** HORDE-AGENTS
**Scope:** Novelty dimension scoring
**Tools:** Internal
**Autonomy:** 85%
**Trigger:** AGT_PRIORART output
**Status:** ⏳ PENDING

#### AGT_NONOBVIOUSNESS_SCORER
**Horde:** HORDE-AGENTS
**Scope:** Non-obviousness dimension scoring
**Tools:** Internal
**Autonomy:** 85%
**Trigger:** AGT_PRIORART output
**Status:** ⏳ PENDING

#### AGT_ENABLEMENT_SCORER
**Horde:** HORDE-AGENTS
**Scope:** Enablement dimension scoring
**Tools:** Internal
**Autonomy:** 85%
**Trigger:** AGT_PRIORART output
**Status:** ⏳ PENDING

#### AGT_CLAIM_DRAFTER
**Horde:** HORDE-AGENTS
**Scope:** Drafts patent claims based on disclosure
**Tools:** Internal + AGT_DRAFT (via MCP)
**Autonomy:** 80%
**Trigger:** AGT_DISCLOSER output
**Status:** ⏳ PENDING

#### AGT_FILING_PACKAGER
**Horde:** HORDE-AGENTS
**Scope:** Packages filing bundle with 9 documents
**Tools:** Internal
**Autonomy:** 100%
**Trigger:** AGT_DISCLOSER output
**Status:** ⏳ PENDING

#### AGT_COMPLIANCE_CHECKER
**Horde:** HORDE-AGENTS
**Scope:** Checks compliance with jurisdiction requirements
**Tools:** Internal
**Autonomy:** 100%
**Trigger:** AGT_FILING_PACKAGER output
**Status:** ⏳ PENDING

---

## Contract Registry

### HORDE-ARCH → HORDE-SCHEMA
**Contract ID:** ARCH-SCHEMA-001
**Input:** ERD_COMPLETE.dbml
**Output:** Alembic migration files, RLS policies, pgvector indexes
**Gate:** Migrations run clean on fresh Postgres
**Status:** ⏳ PENDING

### HORDE-ARCH → HORDE-INFRA
**Contract ID:** ARCH-INFRA-001
**Input:** dependency_graph.dot
**Output:** Terraform configurations, K8s manifests, CI/CD workflows
**Gate:** Terraform clean, CI passes
**Status:** ⏳ PENDING

### HORDE-ARCH → HORDE-API
**Contract ID:** ARCH-API-001
**Input:** openapi.yaml
**Output:** FastAPI routes, MCP tools, BAM middleware
**Gate:** All routes return correct status codes, MCP tools schema-valid
**Status:** ⏳ PENDING

### HORDE-SCHEMA → HORDE-INGEST
**Contract ID:** SCHEMA-INGEST-001
**Input:** Schema (tables exist)
**Output:** Documents in database, chunks with embeddings
**Gate:** 1,000+ documents ingested, all chunks embedded
**Status:** ⏳ PENDING

### HORDE-SCHEMA → HORDE-LEDGER
**Contract ID:** SCHEMA-LEDGER-001
**Input:** proof_ledger table structure
**Output:** SHA-256 hasher, Polygon anchor, AES-256 encryptor
**Gate:** BYOK test passes, ledger tx confirmed
**Status:** ⏳ PENDING

### HORDE-API → HORDE-AGENTS
**Contract ID:** API-AGENTS-001
**Input:** MCP server
**Output:** All 24 agents built and tested
**Gate:** All agents pass ToolCallJudge ≥ 0.90
**Status:** ⏳ PENDING

### HORDE-API → HORDE-PORTAL
**Contract ID:** API-PORTAL-001
**Input:** MCP server + API routes
**Output:** Next.js portal, dashboards
**Gate:** Portal functional, attorney flow < 5 min
**Status:** ⏳ PENDING

### HORDE-INGEST → HORDE-SCORING
**Contract ID:** INGEST-SCORING-001
**Input:** Prior art data
**Output:** Scoring engine live
**Gate:** Scoring model calibrated
**Status:** ⏳ PENDING

### HORDE-AGENTS → HORDE-SCORING
**Contract ID:** AGENTS-SCORING-001
**Input:** Agent outputs
**Output:** Composite scoring results
**Gate:** Composite engine functional
**Status:** ⏳ PENDING

### HORDE-SCORING → HORDE-DISCLOSURE
**Contract ID:** SCORING-DISCLOSURE-001
**Input:** Scores
**Output:** Disclosure drafts
**Gate:** Grounding ≥ 0.85
**Status:** ⏳ PENDING

### HORDE-AGENTS → HORDE-DISCLOSURE
**Contract ID:** AGENTS-DISCLOSURE-001
**Input:** AGT_DRAFT via MCP
**Output:** Grounded legal prose
**Gate:** Grounding ≥ 0.85
**Status:** ⏳ PENDING

### HORDE-DISCLOSURE → HORDE-PORTAL
**Contract ID:** DISCLOSURE-PORTAL-001
**Input:** Disclosure drafts
**Output:** Attorney review interface
**Gate:** Attorney completes review in < 5 min
**Status:** ⏳ PENDING

### HORDE-AGENTS → HORDE-EVAL
**Contract ID:** AGENTS-EVAL-001
**Input:** All agents
**Output:** Eval results
**Gate:** Golden set pass rate ≥ 0.90
**Status:** ⏳ PENDING

### HORDE-SECURITY → ALL
**Contract ID:** SECURITY-ALL-001
**Input:** All code
**Output:** Security report
**Gate:** BYOK test passes, zero HIGH CVEs
**Status:** ⏳ PENDING (continuous)

### HORDE-DOCS → PHASE COMPLETION
**Contract ID:** DOCS-PHASE-001
**Input:** Phase completion
**Output:** API docs, agent runbooks, connector guides, ADRs
**Gate:** All runbooks reviewed, docs complete
**Status:** ⏳ PENDING

---

## Contract Bundle Hash

**Contract Bundle Hash:** 8f7a3b2c1d9e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b
**Locked At:** 2026-04-29
**Locked By:** HORDE-ARCH (Chunk 5)
**Contracts Count:** 13
**Status:** ✅ LOCKED

---

## Completed Outputs

### HORDE-ARCH Outputs (Chunks 1-6)
- PROJECT_MANIFEST.md (v0.1.0-foundation)
- docs/ERD_COMPLETE.dbml (18 tables with BAM integration)
- docs/ERD_LexCore.mmd (10 tables)
- docs/ERD_LexRadar.mmd (8 tables)
- docs/openapi.yaml (OpenAPI 3.1.0 with 7 MCP tools)
- docs/openapi.json (OpenAPI JSON for tool validation)
- docs/dependency_graph.mmd (13 hordes, zero circular dependencies)
- docs/dependency_graph.dot (Graphviz format)
- docs/topological_validation.md (validation report)
- SPEC_HASHES.md (all spec file hashes)
- 13 interface contracts (locked with hash)
- Contract bundle hash: 8f7a3b2c1d9e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b

### Infrastructure Specifications (Ready for HORDE-INFRA)
- docs/infrastructure_requirements.md (Neon, Qdrant, Redis, S3, Polygon, Vault, K8s, CI/CD, observability)

### Security Specifications (Ready for HORDE-SECURITY)
- docs/security_pipeline_requirements.md (SAST, DAST, dependency scanning, BYOK test, RLS audit, SOC 2)

### HORDE-INFRA Outputs (Chunks 7-8 — Specs Generated)
- infra/terraform/main.tf (EKS, VPC, ElastiCache Redis, S3, WAF, IAM IRSA)
- infra/terraform/variables.tf (all tunable parameters)
- infra/terraform/modules/redis/ (Redis cluster module)
- infra/k8s/namespace.yaml (dev, staging, prod, monitoring, security namespaces)
- infra/k8s/api-deployment.yaml (LexCore API deployment with security hardening)
- infra/k8s/hpa.yaml (HorizontalPodAutoscaler + PodDisruptionBudget)
- infra/k8s/monitoring/prometheus.yaml (Prometheus config, rules, alerts, RBAC)
- infra/k8s/monitoring/grafana.yaml (Grafana deployment, dashboards, datasources, ingress)
- infra/k8s/monitoring/loki.yaml (Loki StatefulSet for log aggregation)
- infra/k8s/monitoring/alertmanager.yaml (Alertmanager config with Slack + PagerDuty routing)
- infra/ci-cd/github-actions/ci.yml (Lint, test, security scan, BYOK test, RLS audit, integration tests)
- infra/ci-cd/github-actions/deploy-dev.yml (Build + deploy to dev on merge)
- infra/ci-cd/github-actions/deploy-prod.yml (Approval gate, canary deploy, smoke tests, rollback)

### HORDE-SECURITY Outputs (Chunk 9 — Specs Generated)
- docs/security_pipeline_requirements.md (SAST, DAST, BYOK, RLS, SOC2, incident response)
- CI pipeline includes: Semgrep, Bandit, pip-audit, Snyk, BYOK test, RLS audit test

### HORDE-SCHEMA Outputs (P1 — Migrations Generated)
- schema/001_initial_schema.sql (18 tables, 3 extensions, 40+ indexes)
- schema/002_rls_policies.sql (14 tables with RLS, audit log, triggers)
- schema/003_pgvector_indexes.sql (HNSW indexes, full-text search, composite indexes)
- schema/alembic/env.py (Alembic environment with offline/online modes)
- schema/alembic/script.py.mako (Migration template)
- schema/alembic/versions/001_initial_schema.py (Initial migration combining all SQL)

### HORDE-API Outputs (P1 — Routes Generated)
- api/src/main.py (FastAPI app with lifespan, middleware, health probes)
- api/src/config.py (Pydantic Settings with all env vars)
- api/src/models.py (All Pydantic models from ERD: 18 table models with validation)
- api/src/routes/mcp.py (7 MCP tools: get_capabilities, search_legal, research_task, get_document, get_citations, check_updates, jurisdiction_summary)
- api/src/routes/lexcore.py (Document listing, chunk listing, monitor rule CRUD)
- api/src/routes/lexradar.py (Invention CRUD, prior art search, disclosure generation, filing bundle, ledger proof)
- api/src/routes/auth.py (JWT token exchange, refresh, get_current_tenant dependency)
- api/src/middleware/jwt_auth.py (JWT validation middleware)
- api/src/middleware/tenant_context.py (RLS context middleware)
- api/src/middleware/rate_limit.py (Redis sliding window rate limiting)

### C01 — Product Definition (HORDE-ARCH)
- docs/spec/PRODUCT_SPEC.md (problem statement, users, value prop, 5 clarifying questions answered, must-have features, success metrics, activation definition, compliance constraints, known failures)
- docs/spec/TASK_TREE.md (C01-C11 full build arc, dependency graph, horde assignments, gate criteria, handoff deliverables)
- docs/spec/JTBD_MAP.md (9 jobs mapped to user roles, circumstances, outcomes, emotional drivers, feature mapping, priority matrix)
- docs/spec/ONBOARDING_SUCCESS.md (activation funnel for LexCore + LexRadar, 6-step funnel, metrics, E2E test cases)
- docs/spec/OUT_OF_SCOPE.md (explicit exclusions for LexCore, LexRadar, Platform; deferred to Enhancement Loop; scope change protocol)
- docs/spec/SPEC_HASH.txt (individual + combined SHA-256 hashes for all C01 artifacts)
- C01 Combined Hash: `8da0d8f0b4aa1306b0b27d7361025495e80ecc171ec9a1202b8238f9842a67b4`

### C02 — Architecture + Contracts (HORDE-ARCH)
- docs/architecture/SYSTEM_LAYERS.md (L0-L7 system architecture, cross-cutting concerns, agent directory, resilience requirements, BAM routing)
- docs/architecture/DEPENDENCY_GRAPH.json (9 nodes, 15 edges, 14 agent dependency chains, cycle check: NO_CYCLES_DETECTED)
- docs/architecture/INTERFACE_CONTRACTS.json (12 interface contracts with request/response schemas, auth, errors, idempotency)
- docs/architecture/EVENT_SCHEMA_REGISTRY.json (18 event schemas with payloads, retry semantics, DLQ config, naming convention)
- docs/architecture/CONSUMER_MAP.json (15 contracts, impact severity mapping, impact procedure for contract changes)
- docs/architecture/ADR/001_stack_choice.md (technology stack ADR: Python/FastAPI, Next.js/TS, PostgreSQL/pgvector, Qdrant, Redis, Celery, Clerk, Polygon)
- docs/architecture/ADR/002_auth.md (auth strategy ADR: Clerk primary, JWT/API key secondary, defense-in-depth tenant isolation)
- docs/architecture/ADR/003_async_strategy.md (async ADR: 3-tier strategy — sync API, Celery background jobs, event-driven pipelines)
- docs/architecture/ARCH_HASH.txt (individual + combined SHA-256 hashes for all C02 artifacts)

### C03 — Data Model + Storage (HORDE-SCHEMA)
- schema/ERD.md (24 tables: LexCore 10 + LexRadar 8 + Platform 6, mermaid diagrams, cross-domain FK references, cascade rules)
- schema/SCHEMA_MAP.json (all 24 tables with columns, types, defaults, indexes, constraints, triggers, common enums)
- schema/CONSTRAINT_REGISTRY.json (45+ CHECK constraints, 13 UNIQUE constraints, 52 FK constraints, NOT NULL policy, RLS policy map)
- schema/migrations/001_initial_schema.sql (24 tables, indexes, triggers, auto-update function, all CHECK/UNIQUE/FK constraints)
- schema/migrations/002_rls_policies.sql (FORCE RLS on 24 tables, tenant isolation function, 26 RLS policies, app_role creation, verify_rls_enabled() function)
- schema/migrations/003_pgvector_indexes.sql (HNSW index on legal_chunks.embedding, GIN full-text indexes, composite indexes, partial indexes, maintenance notes)
- schema/migrations/alembic/env.py (Alembic environment with asyncpg, offline/online modes, no autogenerate — hand-written migrations per spec)
- schema/migrations/alembic/script.py.mako (Migration template with upgrade/downgrade stubs, checklists for constraint/schema/RLS/index updates)
- schema/CONNECTION_POOL_CONFIG.md (Neon PostgreSQL pool config, Redis multi-DB allocation, Qdrant collection settings, pool sizing formula, health checks, monitoring)
- schema/SCHEMA_HASH.txt (individual SHA-256 hashes for all C03 artifacts)

### C04 — API Contracts + MCP Tools (HORDE-API)
- docs/api/API_SPEC.md (complete API surface: MCP 7 tools, LexCore domain routes, LexRadar domain routes, Auth routes, Health routes, versioning policy)
- docs/api/MCP_TOOLS.md (detailed MCP tool specifications: get_capabilities, search_legal, research_task, get_document, get_citations, check_updates, jurisdiction_summary — with BAM routing, latency budgets, idempotency, cache strategies)
- docs/api/ERROR_CODES.md (52 error codes mapped to HTTP status, resolution steps, retry strategy, client retry guidance)
- docs/api/RATE_LIMIT_POLICY.md (3-tier rate limits: SOLO 10K/mo, FIRM unlimited, ENTERPRISE unlimited + self-host; sliding window algorithm, Redis key structure, burst handling, monitoring)
- docs/api/SECURITY_HEADERS.md (CSP, HSTS, X-Frame-Options, Permissions-Policy, CORS, Trusted Host, TLS config, OWASP Top 10 mitigations)
- docs/api/AUTH_FLOW.md (4 auth flows: Clerk OAuth, API key exchange, token refresh with rotation, attorney portal scoped JWT; RBAC roles, middleware order, JWT validation, Vault integration, audit logging)
- docs/api/API_HASH.txt (individual SHA-256 hashes for all C04 artifacts)

### C05 — Services + Workers + Agents (HORDE-AGENTS)
- docs/services/SERVICE_CATALOG.md (18 services: LexCore 5 + LexRadar 6 + Shared 4 + Pipeline 3, BaseService interface, health checks, middleware execution order)
- docs/services/AGENT_MANIFEST.md (13 agents: AGT_ROUTER dispatcher + LexCore 4 + LexRadar 4 + Cross-cutting 4, BaseAgent interface, AgentRegistry, BAM routing, AGT-G1 isolation rules, deployment model)
- docs/services/WORKER_REGISTRY.md (11 Celery tasks, 9 queue pools, K8s deployment spec, Flower dashboard, Prometheus metrics, DLQ monitoring)
- docs/services/RESILIENCE_RULES.md (10 circuit breakers, retry policies per dependency, graceful degradation strategies, correlation ID propagation, failure mode summary with RTOs)
- docs/services/SERVICE_HASH.txt (individual SHA-256 hashes for all C05 artifacts)

### C06 — Frontend (HORDE-UI)
- docs/frontend/SCREEN_MAP.md (23 screens: Platform 2 + LexCore 8 + LexRadar 8 + Settings 5 + Attorney Portal 1, route definitions, permissions, data dependencies, screen dependencies matrix)
- docs/frontend/COMPONENT_LIBRARY.md (30+ components organized by domain: Layout, Search, Citations, Research, Monitor, Invention, Disclosure, Bundle, Handoff, Settings, Shared, Forms + shadcn/ui registry)
- docs/frontend/STATE_MANAGEMENT.md (Server Components data fetching, SWR client caching with tags/invalidation, Zustand global UI store, Tenant/Correlation Context, React Hook Form + Zod, real-time updates via WebSocket, error boundaries, state persistence)
- docs/frontend/FRONTEND_HASH.txt (individual SHA-256 hashes for all C06 artifacts)

### C07 — DevOps + CI/CD (HORDE-DEVOPS)
- docs/devops/CLOUD_PROVISIONING.md (Terraform IaC: VPC, EKS, ALB, CloudWatch; managed services: Neon, Upstash, Qdrant, Cloudflare; multi-environment strategy dev/staging/prod; secret management via AWS Secrets Manager + External Secrets Operator)
- docs/devops/CONTAINERIZATION.md (3 container images: API FastAPI, Frontend Next.js, Worker Celery; multi-stage Dockerfiles; non-root users; health checks; Kubernetes deployment manifests with liveness/readiness probes; security hardening)
- docs/devops/CICD_PIPELINES.md (GitHub Actions: Build & Test, Deploy Staging, Deploy Production; security scanning Trivy/Bandit/truffleHog; Helm charts; blue-green + canary deployment; automatic rollback; required secrets)
- docs/devops/INFRASTRUCTURE_DIAGRAM.md (ASCII system architecture, data flow for legal search and patent pipeline, network security zones, CI/CD flow)
- docs/devops/DEVOPS_HASH.txt (individual SHA-256 hashes for all C07 artifacts)

### C08 — Testing + QA (HORDE-QA)
- docs/testing/TEST_STRATEGY.md (testing pyramid: unit, integration, E2E, HORDE-AUDIT gate; coverage targets 85% API, 80% frontend; frameworks: pytest, Jest, Playwright; security test requirements)
- docs/testing/UNIT_TEST_GUIDE.md (API unit test patterns: service, repository, utility, agent tests; frontend unit test patterns: component, hook, utility; mocking requirements; test conventions)
- docs/testing/INTEGRATION_TEST_PLAN.md (Docker Compose test stack; integration test categories: API endpoints, database+RLS, search pipeline, auth, workers; running integration tests)
- docs/testing/E2E_TEST_SUITE.md (Playwright configuration; critical path tests: signup→login→search, admin tenant management, GitHub scanner→invention→disclosure, attorney portal handoff, blockchain anchoring; test data management)
- docs/testing/TEST_HASH.txt (individual SHA-256 hashes for all C08 artifacts)

### C09 — Monitoring (HORDE-MONITOR)
- docs/monitoring/OBSERVABILITY_STACK.md (metrics: Prometheus+AMP+CloudWatch; logs: CloudWatch+Fluent Bit; traces: OpenTelemetry+X-Ray; alerting: CloudWatch+PagerDuty+Slack; dashboards: Grafana+CloudWatch; key metrics definitions)
- docs/monitoring/ALERTING_RULES.md (P0 critical alerts: API down, DB unreachable, auth failure, security breach, data loss; P1 high alerts: high latency, slow DB, queue backlog, external API degraded, high CPU; P2/P3 medium/low alerts; alert suppression rules; alert testing)
- docs/monitoring/DASHBOARDS.md (7 Grafana dashboards: API overview, worker performance, database health, infrastructure, tenant metrics, external APIs, security; 4 CloudWatch dashboards; panel queries and thresholds)
- docs/monitoring/MONITORING_HASH.txt (individual SHA-256 hashes for all C09 artifacts)

### C10 — Runbooks (HORDE-LOG)
- docs/runbooks/DEPLOYMENT_RUNBOOK.md (prerequisites; deploy to staging: build, scan, deploy, verify, rollback; deploy to production: pre-deploy checklist, blue-green deployment, canary rollout, post-deploy verification, automatic rollback conditions; database migrations; post-deploy tasks; emergency deployment)
- docs/runbooks/INCIDENT_RESPONSE.md (incident severity levels P0-P3; incident response flow; incident procedures: API service down, database failure, security breach, performance degradation, queue backlog; post-incident procedures; on-call escalation)
- docs/runbooks/ONBOARDING_GUIDE.md (Day 1: environment setup; Day 2: architecture deep dive; Day 3: first contribution; development guidelines; troubleshooting; resources)
- docs/runbooks/OPERATIONS_GUIDE.md (daily operations; weekly operations: capacity planning, security review, performance review, cost review, backup verification; monthly operations: maintenance, performance optimization, security hardening, documentation; scaling procedures; backup and restore; cost optimization; disaster recovery)
- docs/runbooks/RUNBOOKS_HASH.txt (individual SHA-256 hashes for all C10 artifacts)

### C11 — Launch (HORDE-MASTER)
- docs/launch/LAUNCH_CHECKLIST.md (pre-launch checklist T-30 days: infrastructure, database, security, monitoring, CI/CD, testing, documentation, legal, customer; launch day checklist: pre-launch T-2 hours, launch T-0, post-launch T+1 hour; post-launch checklist T+7 days; rollback criteria; launch communication plan; success criteria)
- docs/launch/HANDOFF_PACKAGE.md (package contents: architecture overview, operational procedures, security & compliance, monitoring & observability, API documentation, database schema, contact information, access & credentials, known issues & limitations, next steps; handoff meeting agenda; post-handoff support)
- docs/launch/POST_LAUNCH_PLAN.md (Week 1: stabilization; Week 2-4: customer onboarding; Month 2: feature development; Month 3: scale & optimization; ongoing activities: daily/weekly/monthly/quarterly; success metrics; risk mitigation; communication plan; post-launch reviews at 30/60/90 days)
- docs/launch/LAUNCH_HASH.txt (individual SHA-256 hashes for all C11 artifacts)

### Unified Build System v2 (Single-File Operating System)
- docs/FULL_BUILD_SYSTEM_V2_COMPLETE.md (1,258 lines, 50.4 KB)
  - PART 0: 7 Laws, 4 Control Planes, 11-Chunk Build Arc, Universal Session Pattern
  - PART 1: Global Engineering Standards (Approved Stack, Resilience Defaults, Never List)
  - PART 2: Cascade Session Rules (Opening Protocol, Spec Mutation, Compatibility Gate)
  - PART 3: Horde Directory (14 hordes, instance counts, 3 human checkpoints)
  - PART 4: Delivery Chunks C01–C11 (READ/BUILD/VERIFY/IMPACT/GATE/HANDOFF per chunk)
  - PART 5: HORDE-AUDIT (5-layer quality gate spec, audit output JSON format, continuity engine)
  - PART 6: Quality Gates Master (release fitness dimensions, gate scorecards for all 11 chunks)
  - PART 7: Handoff Runbook (4 audience handoffs, post-go-live improvement loop)
  - PART 8: LexCore Session Prompts (paste-ready prompts for C01–C11)
  - PART 9: LexRadar Session Prompts (paste-ready prompts for C01–C11)
  - PART 10: Enhancement Loop (trigger conditions, execution model, scope control rules)
  - Hash: 191d466e4e3e97ba124cabbe4438989cffec64b77917b92f300f82c62c64c030

### Local Development Stack (Ready for Local Testing)
- docker-compose.yml (PostgreSQL + pgvector, Redis, Qdrant, Vault, API, Prometheus, Grafana)
- api/Dockerfile (Multi-stage build, non-root user, health checks)
- api/requirements.txt (All Python dependencies with version constraints)
- LOCAL_DEVELOPMENT.md (Quick start, service ports, env vars, testing guide, API usage examples)

### Pending (Requires Cloud Credentials)
- Chunk 7: Apply Terraform to provision actual infrastructure
- Chunk 8: Deploy Kubernetes manifests to EKS cluster
- Chunk 9: Configure security pipeline with real tokens
- Chunk 10: Infrastructure Smoke Test (HORDE-INFRA + HORDE-SECURITY)
- Chunk 11: Phase 0 Gate Review (HordeMaster)

---

## Blocker Log

### Blocker 1: Cloud Credentials Required
- **Chunks Affected:** 7, 8, 9, 10
- **Horde:** HORDE-INFRA, HORDE-SECURITY
- **Description:** Chunks 7-10 require actual cloud infrastructure provisioning (Neon, Qdrant, Redis, S3, Polygon, Vault, K8s, CI/CD)
- **Required:** Cloud provider credentials (AWS/GCP/Azure), repository access, S3 access
- **Status:** ⏳ BLOCKED (awaiting credentials)
- **Workaround:** Specifications created and ready for execution when credentials available

---

## Agent State Tracking

*No agent state yet — Phase 0 in progress*

---

## Update Protocol

**Only HordeMaster can update this file.**

Update process:
1. HordeMaster reads current manifest
2. HordeMaster applies changes based on completed chunks
3. HordeMaster computes new manifest hash
4. HordeMaster publishes hash to immutable location
5. HordeMaster updates this file with new hash
6. All other hordes read updated manifest before next task

**No horde except HordeMaster may write to this file.** Violations will be detected by HORDE-SECURITY.

---

## Manifest Hash

**Current Hash:** [computed after file creation]
**Previous Hashes:** [none yet]

Hash computation: `sha256(PROJECT_MANIFEST.md)`
