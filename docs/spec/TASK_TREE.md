# TASK_TREE.md — LexCore + LexRadar

> **Build System:** Unified Build System v2  
> **Chunk:** C01 — Product Definition  
> **Horde:** HORDE-ARCH  
> **Generated From:** PRODUCT_SPEC.md  

---

## Build Arc Overview

```
C01  Product Definition ───────────┐
C02  Architecture + Contracts ─────┤ Foundation
C03  Data Model + Storage ─────────┤ (P0)
C04  API + Event Contracts ────────┘
C05  Services + Agents ────────────┐
C06  Frontend + UI System ─────────┤ Core Build
C07  Wiring + Critical Path ───────┤ (P1)
C08  Testing + Evals ──────────────┘
C09  Security + Tenant Safety ─────┐
C10  CI/CD + Promotion System ─────┤ Quality & Ops
C11  Deploy + Onboarding + Handoff ─┘ (P2)
→ ENHANCEMENT LOOP (continuous)
```

---

## C01 — Product Definition

**Status:** IN PROGRESS
**Horde:** HORDE-ARCH (1 instance)
**Outputs:**
- [x] docs/spec/PRODUCT_SPEC.md
- [x] docs/spec/TASK_TREE.md ← YOU ARE HERE
- [ ] docs/spec/JTBD_MAP.md
- [ ] docs/spec/ONBOARDING_SUCCESS.md
- [ ] docs/spec/OUT_OF_SCOPE.md
- [ ] docs/spec/SPEC_HASH.txt

**Gate:** All 5 verify items green → UNLOCK C02

---

## C02 — Architecture + Contracts

**Status:** PENDING
**Horde:** HORDE-ARCH (1 instance)
**Dependencies:** C01
**Control Plane:** ENGINEERING

**READ:**
- docs/spec/PRODUCT_SPEC.md
- docs/spec/TASK_TREE.md

**BUILD:**
- [ ] docs/architecture/SYSTEM_LAYERS.md (7 layers defined)
- [ ] docs/architecture/DEPENDENCY_GRAPH.json (no cycles)
- [ ] docs/architecture/INTERFACE_CONTRACTS.json
- [ ] docs/architecture/EVENT_SCHEMA_REGISTRY.json
- [ ] docs/architecture/ADR/001_stack_choice.md
- [ ] docs/architecture/ADR/002_auth.md
- [ ] docs/architecture/ADR/003_async_strategy.md
- [ ] docs/architecture/CONSUMER_MAP.json
- [ ] docs/architecture/ARCH_HASH.txt

**Gate:** No cycles, all 7 layers, all contracts + events, ADRs for stack choices

---

## C03 — Data Model + Storage

**Status:** PENDING
**Horde:** HORDE-SCHEMA (2 instances: migrations | indexes+RLS)
**Dependencies:** C02
**Control Plane:** ENGINEERING + QUALITY

**READ:**
- docs/architecture/SYSTEM_LAYERS.md
- docs/architecture/INTERFACE_CONTRACTS.json

**BUILD:**
- [ ] docs/schema/ERD.md
- [ ] docs/schema/COLUMN_SPEC.json (every table, column, type, constraint)
- [ ] docs/schema/QUERY_INTENT_MATRIX.json (query → expected index)
- [ ] docs/schema/MIGRATION_BLAST_RADIUS.md
- [ ] alembic/versions/001_initial_schema.py
- [ ] alembic/versions/002_indexes.py
- [ ] db/seeds/base_seed.sql
- [ ] tests/db/test_migrations.py
- [ ] tests/db/test_rls.py

**Gate:** upgrade/downgrade/upgrade passes, schema verifier passes, RLS tests pass, query intent index aligned, blast radius report written

---

## C04 — API + Event Contracts

**Status:** PARTIALLY COMPLETE (routes generated, not fully validated)
**Horde:** HORDE-API (3 instances: OpenAPI | Pydantic models | auth+events)
**Dependencies:** C03
**Control Plane:** ENGINEERING

**READ:**
- docs/schema/COLUMN_SPEC.json
- docs/architecture/INTERFACE_CONTRACTS.json
- docs/architecture/EVENT_SCHEMA_REGISTRY.json

**BUILD:**
- [ ] api/openapi.yaml (fully validated)
- [ ] api/models/request_models.py
- [ ] api/models/response_models.py
- [ ] api/auth/auth_spec.md
- [ ] api/auth/claims_map.json
- [ ] api/events/event_contracts.json
- [ ] api/errors/error_envelopes.json
- [ ] api/OPENAPI_HASH.txt

**Already Exists (Generated in Prior Session):**
- api/src/main.py (FastAPI app with lifespan, middleware, health probes)
- api/src/models.py (Pydantic models from ERD — needs refinement to match COLUMN_SPEC)
- api/src/routes/mcp.py (7 MCP tools with stubs)
- api/src/routes/lexcore.py (LexCore routes with stubs)
- api/src/routes/lexradar.py (LexRadar routes with stubs)
- api/src/routes/auth.py (JWT auth with stubs)

**Gate:** openapi-spec-validator passes, no Any types, auth claims map complete, event contracts complete, error envelopes defined

---

## C05 — Services + Agents

**Status:** NOT STARTED
**Horde:** HORDE-AGENTS (5 parallel instances: service_layer | repo_layer | workers | agents | integration_tests)
**Dependencies:** C04
**Control Plane:** ENGINEERING + QUALITY

**READ:**
- api/openapi.yaml
- docs/architecture/INTERFACE_CONTRACTS.json
- docs/architecture/EVENT_SCHEMA_REGISTRY.json

**BUILD:**
- [ ] services/ (one file per bounded domain)
- [ ] repositories/ (one file per DB entity)
- [ ] workers/ (background jobs + queue consumers)
- [ ] agents/ (agent classes + tool registries)
- [ ] shared/resilience.py (timeout, retry, circuit breaker)
- [ ] shared/exceptions.py (typed exception hierarchy)
- [ ] shared/logging.py (structlog config + correlation helpers)
- [ ] shared/audit.py (audit row factory)
- [ ] tests/integration/test_services_*.py

**LexCore Agents:**
1. **AGT_ROUTER** — BAM compound parsing, agent dispatch
2. **AGT_SEARCH** — Hybrid search orchestration (vector + full-text)
3. **AGT_ANALYSIS** — Legal analysis, research task decomposition
4. **AGT_DRAFT** — Document drafting assistance
5. **AGT_INGEST** — Document ingestion pipeline
6. **AGT_MONITOR** — Legislative change monitoring
7. **AGT_CITE** — Citation graph traversal and validation

**LexRadar Agents:**
1. **AGT_SCANNER** — Code/repo scanning for invention signals
2. **AGT_SIGNAL_CLASSIFIER** — Classify invention signals by type
3. **AGT_NOVELTY_SCORER** — Score novelty dimension
4. **AGT_NONOBVIOUSNESS_SCORER** — Score nonobviousness dimension
5. **AGT_ENABLEMENT_SCORER** — Score enablement dimension
6. **AGT_CLAIM_DRAFTER** — Draft patent claims
7. **AGT_FILING_PACKAGER** — Package filing bundles (9 documents)
8. **AGT_COMPLIANCE_CHECKER** — Verify compliance with IP policies
9. **AGT_PRIORART** — Prior art search across 7 sources

**Gate:** All integration tests pass, mypy strict passes, resilience on all external calls, audit logging present, ToolCallJudge ≥ 0.90

---

## C06 — Frontend + UI System

**Status:** NOT STARTED
**Horde:** HORDE-PORTAL (3 parallel instances: pages+routing | components | onboarding+activation)
**Dependencies:** C04, C05
**Control Plane:** PRODUCT + ENGINEERING

**READ:**
- docs/spec/PRODUCT_SPEC.md
- api/openapi.yaml
- docs/spec/ONBOARDING_SUCCESS.md

**BUILD:**
- [ ] app/(routes)/ (all pages and layouts)
- [ ] components/ui/ (primitive UI library)
- [ ] components/features/ (domain-specific components)
- [ ] lib/api-client.ts (ONLY place raw fetch/axios lives)
- [ ] lib/validators.ts (Zod schemas for every API response)
- [ ] lib/auth.ts (Clerk or JWT session helpers)
- [ ] app/onboarding/ (multi-step wizard)
- [ ] app/onboarding/activation-tracker.ts
- [ ] tests/e2e/test_onboarding.spec.ts

**Gate:** TypeScript strict passes, ESLint clean, typed API client only, empty/loading/error states on all lists, activation events fire, first-value journey E2E passes

---

## C07 — Wiring + Critical Path

**Status:** PARTIALLY COMPLETE (local dev wiring done)
**Horde:** HORDE-API + HORDE-INFRA
**Dependencies:** C04, C05, C06
**Control Plane:** ENGINEERING + QUALITY

**READ:**
- api/openapi.yaml
- docs/architecture/DEPENDENCY_GRAPH.json
- docs/spec/JTBD_MAP.md

**BUILD:**
- [ ] lib/api-client.ts (complete bindings)
- [ ] api/routes/*.py (bindings to service layer — full implementation)
- [ ] workers/queue_bindings.py
- [ ] integrations/client_adapters.py
- [ ] docs/quality/CRITICAL_PATH_TRACE.md
- [ ] tests/e2e/test_critical_path.spec.ts

**Already Exists:**
- docker-compose.yml (local dev wiring)
- api/Dockerfile (container build)

**Gate:** E2E critical path passes, correlation_id present at every hop, DB mutation visible in UI, queue/event consumed successfully, audit log row written, no trace gaps

---

## C08 — Testing + Evals

**Status:** NOT STARTED
**Horde:** HORDE-EVAL (2 parallel instances: test_suite | evals+release_fitness)
**Dependencies:** C05, C07
**Control Plane:** QUALITY

**READ:**
- docs/spec/PRODUCT_SPEC.md
- api/openapi.yaml
- docs/quality/CRITICAL_PATH_TRACE.md

**BUILD:**
- [ ] tests/unit/
- [ ] tests/integration/
- [ ] tests/e2e/
- [ ] tests/load/locustfile.py
- [ ] tests/regression/
- [ ] tests/db/test_migration_rollback.py
- [ ] evals/golden_sets/*.json (agent evals)
- [ ] evals/judges/*.py
- [ ] docs/quality/RELEASE_FITNESS.json
- [ ] docs/quality/TEST_GAP_REPORT.json

**Gate:** Coverage ≥ 80%, regression suite green, migration rollback passes, Playwright E2E all green, load P99 < 5s under 100 concurrent, judge scores pass, release fitness generated

---

## C09 — Security + Tenant Safety

**Status:** PARTIALLY COMPLETE (specs generated, not tested)
**Horde:** HORDE-SECURITY + HORDE-AUDIT
**Dependencies:** C03, C05, C08
**Control Plane:** OPERATIONS + QUALITY

**READ:**
- api/auth/auth_spec.md
- docs/schema/COLUMN_SPEC.json
- security/

**BUILD:**
- [ ] security/SBOM.json
- [ ] security/owasp_checklist.md
- [ ] security/findings_report.json
- [ ] security/secrets_inventory.md
- [ ] security/key_rotation_procedure.md
- [ ] tests/security/test_tenant_isolation.py
- [ ] tests/security/test_auth_enforcement.py

**Gate:** gitleaks zero, pip-audit zero HIGH/CRITICAL, bandit zero HIGH, cross-tenant API tests pass, cross-tenant DB tests pass, auth enforcement tests pass, SBOM generated, OWASP checklist complete

**Human Checkpoint 2:** Security trust — human reviews findings_report.json before production.

---

## C10 — CI/CD + Promotion System

**Status:** PARTIALLY COMPLETE (GitHub Actions specs generated)
**Horde:** HORDE-INFRA (2 instances: pipeline | monitoring+rollback)
**Dependencies:** C08, C09
**Control Plane:** OPERATIONS

**READ:**
- docs/quality/RELEASE_FITNESS.json
- security/findings_report.json
- docs/architecture/SYSTEM_LAYERS.md

**BUILD:**
- [ ] .github/workflows/ci.yaml (13-stage pipeline)
- [ ] .github/workflows/deploy_canary.yaml
- [ ] .github/workflows/rollback.yaml
- [ ] infra/terraform/ (complete modules)
- [ ] infra/k8s/ (complete manifests)
- [ ] infra/prometheus/alerts/
- [ ] infra/grafana/dashboards/
- [ ] scripts/rollback.sh
- [ ] scripts/restore.sh
- [ ] docs/ops/DEPLOYMENT_PROMOTION_POLICY.md
- [ ] docs/ops/RELEASE_IMPACT_REPORT_template.json

**Already Exists:**
- infra/terraform/main.tf
- infra/terraform/variables.tf
- infra/terraform/modules/redis/
- infra/k8s/namespace.yaml
- infra/k8s/api-deployment.yaml
- infra/k8s/hpa.yaml
- infra/k8s/monitoring/prometheus.yaml
- infra/k8s/monitoring/grafana.yaml
- infra/k8s/monitoring/loki.yaml
- infra/k8s/monitoring/alertmanager.yaml
- infra/ci-cd/github-actions/ci.yml
- infra/ci-cd/github-actions/deploy-dev.yml
- infra/ci-cd/github-actions/deploy-prod.yml

**Gate:** All 13 stages pass on test commit, forced rollback executes cleanly, alerts fire on injected SLO breach, dashboards render with real data, release impact report template ready

---

## C11 — Deploy + Onboarding + Handoff

**Status:** NOT STARTED
**Horde:** HORDE-DOCS + HORDE-INFRA + HORDE-CONDUCTOR
**Dependencies:** C10
**Control Plane:** PRODUCT + OPERATIONS

**READ:**
- docs/quality/RELEASE_FITNESS.json
- docs/ops/DEPLOYMENT_PROMOTION_POLICY.md
- docs/spec/ONBOARDING_SUCCESS.md

**BUILD:**
- [ ] docs/user/GETTING_STARTED.md
- [ ] docs/user/FAQ.md
- [ ] docs/user/FEATURE_GUIDES/
- [ ] docs/ops/RUNBOOK_DEPLOY.md
- [ ] docs/ops/RUNBOOK_INCIDENTS.md
- [ ] docs/ops/RUNBOOK_RESTORE.md
- [ ] docs/handoff/HANDOFF_PACKAGE.md
- [ ] docs/handoff/ARCHITECTURE_SUMMARY.md
- [ ] docs/handoff/OPEN_RISKS.md
- [ ] docs/handoff/POST_GO_LIVE_BACKLOG.md
- [ ] email_templates/welcome.html
- [ ] email_templates/onboarding_day1.html
- [ ] email_templates/onboarding_day3.html

**Pre-Deploy Checklist:**
- [ ] All C01-C10 gates green
- [ ] RELEASE_FITNESS.json: all dimensions true
- [ ] Staging smoke test green
- [ ] Backup confirmed
- [ ] Rollback script tested
- [ ] On-call owner assigned
- [ ] Sentry/alerting connected
- [ ] DNS + TLS confirmed

**Onboarding Activation Funnel:**
1. user.signed_up
2. workspace.created
3. integration.connected
4. first_value_action.completed ← THE activation gate
5. team_member.invited
6. feature.used_twice

**Gate:** Prod health check 200, first real user completes onboarding, activation event fires, restore drill passes, handoff package reviewed by named owner

**Human Checkpoint 3:** UX/Handoff — human reviews onboarding flow before claiming production-ready.

---

## Handoff Audiences + Required Deliverables

### Operator Handoff
- docs/ops/RUNBOOK_DEPLOY.md
- docs/ops/RUNBOOK_INCIDENTS.md
- docs/ops/RUNBOOK_RESTORE.md
- infra/prometheus/alerts/ (alert map)
- security/secrets_inventory.md
- On-call rotation assigned

### Engineer Handoff
- docs/handoff/ARCHITECTURE_SUMMARY.md
- docs/schema/ERD.md + COLUMN_SPEC.json
- docs/architecture/INTERFACE_CONTRACTS.json
- docs/architecture/EVENT_SCHEMA_REGISTRY.json
- docs/handoff/KNOWN_EXTENSION_POINTS.md
- docs/handoff/COMPATIBILITY_RULES.md

### Client/Admin Handoff
- docs/user/GETTING_STARTED.md
- docs/user/FAQ.md
- docs/user/FEATURE_GUIDES/
- email_templates/
- Support escalation path

### Legal/Compliance Handoff
- docs/handoff/DATA_FLOW_SUMMARY.md
- docs/handoff/AUDIT_TRAIL_DESIGN.md
- docs/handoff/TENANT_ISOLATION_STATEMENT.md
- docs/handoff/RETENTION_POLICY.md
- docs/handoff/SECURITY_CONTROLS_SUMMARY.md
- docs/handoff/OPEN_RISKS.md

---

## Dependency Graph (Simplified)

```
C01 ──▶ C02 ──▶ C03 ──▶ C04 ──▶ C05 ──▶ C06 ──▶ C07 ──▶ C08 ──▶ C09 ──▶ C10 ──▶ C11
          │       │       │       │       │       │       │       │       │       │
          └───────┴───────┴───────┴───────┴───────┴───────┴───────┴───────┴───────┘
                              (all feed into HORDE-AUDIT after each chunk)
```

**Parallel Opportunities:**
- C02 and C01 can overlap slightly (architecture exploration during spec writing)
- C06 frontend work can begin once C04 API contracts are stable (before C05 services complete)
- C08 test planning can begin once C05 service signatures are defined
- C09 security scans can run continuously from C03 onward
- C10 CI/CD can be set up after C04 (pipeline tests API contracts)

---

## Post-Go-Live Enhancement Loop

After C11, the system transitions to continuous enhancement:

1. **HORDE-MONITOR** surfaces signals (defects, friction, scale risks, enhancements)
2. **HORDE-PLANNER** triages: which control plane? which chunk?
3. **HORDE-ARCH** or appropriate coding horde executes scoped fix
4. **HORDE-AUDIT** runs 5-layer audit on changed files only
5. If audit passes: **HORDE-CONDUCTOR** promotes fix
6. **HORDE-DOCS** updates relevant handoff artifacts

**Loop Constraints:**
- Must NOT re-open locked contracts without compatibility report
- Must NOT bypass HORDE-AUDIT
- Must NOT skip affected consumer tests
- Must NOT promote without release fitness check
