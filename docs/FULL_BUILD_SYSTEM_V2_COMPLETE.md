# ============================================================
# LEXCORE + LEXRADAR: FULL AGENT HORDE BUILD SYSTEM V2
# Single-file master — all chunks, rules, gates, audits,
# continuity engine, and session prompts in one place.
# ============================================================
# Generated: 2026-04-30T04:02:05.462562+00:00
# System:    LexCore (Legal Intelligence DB) + LexRadar (IP Pipeline)
# Use:       Paste directly into Cascade/Kode per-session
# Law:       Spec before code. Contracts before integration.
#            Resilience by default. Compatibility before merge.
#            Proof before promotion. Onboarding before claiming live.
#            Observability before scale.
# ============================================================


# ════════════════════════════════════════════════════════════
# PART 0 — CORE LAW
# ════════════════════════════════════════════════════════════

## The 7 Laws
1. Spec before code.
2. Contracts before integration.
3. Resilience by default — every service, worker, and agent
   inherits timeout, retry, circuit breaker, typed exceptions,
   correlation logging, health check, and graceful shutdown.
4. Compatibility before merge — any change to schema, API,
   event payload, or response shape requires a downstream
   impact report and updated consumer tests before merge.
5. Proof before promotion — promotion gates are satisfied by
   running commands, not by reading code or subjective review.
6. Onboarding before claiming live — the system is not live
   until a real user completes the activation path.
7. Observability before scale — dashboards, alerts, and
   structured traces must exist before traffic is increased.

## The 4 Control Planes
1. PRODUCT   — user outcomes, activation, scope, handoff quality
2. ENGINEERING — architecture, schema, contracts, events, agents
3. QUALITY   — tests, evals, contract diffs, regression, fitness
4. OPERATIONS — secrets, observability, runbooks, cost, restore

## The Build Arc
C01  Product Definition
C02  Architecture + Contracts
C03  Data Model + Storage
C04  API + Event Contracts
C05  Services + Agents
C06  Frontend + UI System
C07  Wiring + Critical Path
C08  Testing + Evals
C09  Security + Tenant Safety
C10  CI/CD + Promotion System
C11  Deploy + Onboarding + Handoff
→ ENHANCEMENT LOOP (continuous after C11)

## Universal Session Pattern
Every Cascade session:
  READ    → list the exact spec files to load
  BUILD   → list the exact files to produce
  VERIFY  → run commands, not visual review
  IMPACT  → write compatibility report if contracts changed
  GATE    → evaluate boolean checklist
  HANDOFF → update changelog, memories, next-horde briefing


# ════════════════════════════════════════════════════════════
# PART 1 — GLOBAL ENGINEERING STANDARDS
# ════════════════════════════════════════════════════════════

## Approved Stack
Backend:     Python 3.12, FastAPI 0.110+, Pydantic v2, asyncpg
Frontend:    Next.js 14+ App Router, TypeScript strict, Tailwind CSS, Shadcn/UI
Database:    PostgreSQL 15 + pgvector, Redis 7, Qdrant (vector-heavy search)
Auth:        Clerk OR JWT w/ refresh tokens — decide in C01, never change
Secrets:     HashiCorp Vault or cloud secret manager — never .env in production
Infra:       Terraform, Kubernetes, GitHub Actions
Observability: structlog + Prometheus + Grafana + OpenTelemetry + Loki

## Resilience Defaults (apply to ALL services, workers, agents)
  timeout:          asyncio.wait_for(op, timeout=30.0)
  retry:            max_attempts=3, backoff=exponential+jitter, skip on 4xx
  circuit breaker:  CLOSED → 5 failures → OPEN(60s) → HALF_OPEN → CLOSED
  typed exceptions: AppException > ValidationError | ExternalServiceError | etc.
  logging:          structlog.info(..., correlation_id=..., duration_ms=...)
  health check:     /health endpoint returns 200 or 503 with diagnostics
  graceful shutdown: SIGTERM/SIGINT handlers flush queues, close DB pools

## Never List
  Never hard-code secrets
  Never write business logic in API routes
  Never access DB directly outside repository layer
  Never let an agent import another agent directly
  Never use Any type in Pydantic models or TypeScript
  Never run raw SQL with string interpolation
  Never drop columns or tables in production migrations
  Never skip error handling — bare except: pass is a critical finding
  Never leave TODO in production-merged code
  Never log PII, passwords, or encryption keys

## Required Per-Function Standards
  - docstring on every public function
  - typed input and output
  - error handling for all failure modes
  - unit test or integration test coverage


# ════════════════════════════════════════════════════════════
# PART 2 — CASCADE SESSION RULES
# ════════════════════════════════════════════════════════════

## Session Opening Protocol
Always start a session by stating:
  "CHUNK {N} — {NAME}. Loading: {spec files}. Building: {file list}."

Never begin building until spec files are loaded and acknowledged.

## Spec Mutation Rule
If a spec file needs updating (because an audit fix changes a contract):
  1. Write docs/spec_changelog.json entry with old hash, new hash, change reason
  2. Update the spec file
  3. Notify downstream hordes via next-horde briefing
  4. Never mutate spec files silently

## Compatibility Gate Rule
Before merging any change that modifies:
  - schema tables or columns
  - OpenAPI routes or response shapes
  - queue or event payloads
  - auth claims or JWT structure
  - websocket event types
Write: docs/compatibility/COMPAT_REPORT_{date}.json
Contents: changed artifact, consumers affected, breaking: true/false, tests updated

## Test Quality Standards
Approved test patterns:
  Unit: mock repo → call service → assert output + side effects
  Integration: real DB (test schema) → call service/route → assert DB state
  E2E: Playwright → full user action → assert UI + DB + event
  Load: Locust → primary action at 100 concurrent → P99 < 5s
  Regression: spec item → code path → assertion
Disallowed test patterns:
  assert True
  assert 1 == 1
  test with no assertions
  test that always passes regardless of input
  DB tests that use only mocks

## Chunk Completion Standard
A chunk is DONE only when:
  [ ] All named build artifacts exist
  [ ] All verify commands pass
  [ ] Compatibility report written if needed
  [ ] Gate checklist is 100% green
  [ ] Changelog updated
  [ ] Next-horde briefing written

## Memory Update Format
After each chunk, write to cascade memory:
  current_chunk: C{N+1}
  {chunk_N}_status: complete
  {chunk_N}_hash: {SHA256 of chunk output artifact set}
  next_horde_context: {brief list of what changed in this chunk}


# ════════════════════════════════════════════════════════════
# PART 3 — HORDE DIRECTORY
# ════════════════════════════════════════════════════════════

## Coding Hordes
  HORDE-ARCH      → C01, C02                  (1 instance)
  HORDE-SCHEMA    → C03                       (2 instances)
  HORDE-API       → C04, C07                  (3 instances)
  HORDE-AGENTS    → C05                       (5 instances)
  HORDE-PORTAL    → C06                       (3 instances)
  HORDE-EVAL      → C08                       (2 instances)
  HORDE-SECURITY  → C09                       (1 instance)
  HORDE-INFRA     → C10, C11 (partial)        (2 instances)
  HORDE-DOCS      → C11                       (1 instance)

## Quality Hordes (run after every coding horde)
  HORDE-AUDIT     → 5-layer gate on every chunk output   (3 instances)

## Continuity Hordes (run between phases after HORDE-AUDIT)
  HORDE-PLANNER   → read audit delta, map downstream impact  (1 instance)
  HORDE-REFINER   → surgical spec updates, changelog         (2 instances)
  HORDE-CONDUCTOR → re-brief and fire next hordes            (1 instance)

## Post-Production Horde
  HORDE-MONITOR   → continuous production health + enhancement signals (1 instance)

## Human Checkpoints (only 3 in the full arc)
  After C05: Quality utility — are disclosures / outputs good enough?
  After C09: Security trust — safe for real customer data?
  After C11: UX/Handoff — would a real end user/attorney/operator use this?


# ════════════════════════════════════════════════════════════
# PART 4 — DELIVERY CHUNKS C01–C11
# ════════════════════════════════════════════════════════════

# ┌────────────────────────────────────────────────────────┐
# │ C01 — PRODUCT DEFINITION                               │
# └────────────────────────────────────────────────────────┘
## Horde: HORDE-ARCH
## Control Planes: PRODUCT

## READ
  - raw requirements / client notes
  - prior product docs if extending

## BUILD
  docs/spec/PRODUCT_SPEC.md
  docs/spec/TASK_TREE.md
  docs/spec/JTBD_MAP.md
  docs/spec/ONBOARDING_SUCCESS.md
  docs/spec/OUT_OF_SCOPE.md
  docs/spec/SPEC_HASH.txt

## REQUIRED CONTENT: PRODUCT_SPEC.md
  - Problem statement
  - Primary user (role + company type)
  - Highest-value action (the one thing that delivers first value)
  - Must-have features with acceptance criteria
  - Nice-to-have features
  - Explicit out-of-scope list
  - Success metrics (measurable, time-bound)
  - Activation definition (what = first value event)
  - Compliance and legal constraints
  - External integrations
  - Known failure conditions

## 5 REQUIRED CLARIFYING QUESTIONS (ask before writing spec)
  Q1: Who is the primary user and what is their role?
  Q2: What is the single problem this system must solve?
  Q3: What are the hard technical or legal constraints?
  Q4: What does success look like in 30, 60, 90 days?
  Q5: What is explicitly out of scope for this build?

## VERIFY
  [ ] All 5 questions answered
  [ ] All required sections present
  [ ] Activation event is concrete and trackable
  [ ] Out-of-scope list exists
  [ ] Spec hash written

## GATE
  All 5 verify items green → UNLOCK C02

## HANDOFF
  current_chunk=C02, spec_locked=true, spec_hash={hash}


# ┌────────────────────────────────────────────────────────┐
# │ C02 — ARCHITECTURE + CONTRACTS                         │
# └────────────────────────────────────────────────────────┘
## Horde: HORDE-ARCH
## Control Planes: ENGINEERING

## READ
  docs/spec/PRODUCT_SPEC.md
  docs/spec/TASK_TREE.md

## BUILD
  docs/architecture/SYSTEM_LAYERS.md       ← 7 layers defined
  docs/architecture/DEPENDENCY_GRAPH.json  ← no cycles
  docs/architecture/INTERFACE_CONTRACTS.json
  docs/architecture/EVENT_SCHEMA_REGISTRY.json
  docs/architecture/ADR/001_stack_choice.md
  docs/architecture/ADR/002_auth.md
  docs/architecture/ADR/003_async_strategy.md
  docs/architecture/CONSUMER_MAP.json
  docs/architecture/ARCH_HASH.txt

## 7 SYSTEM LAYERS
  L0: External sources (APIs, scrapes, webhooks, file uploads)
  L1: Connectors / ingestion workers
  L2: Storage — PostgreSQL, Redis, Qdrant, S3/R2
  L3: Services / workers / agents
  L4: API gateway or MCP boundary
  L5: Frontend / UI / attorney portal
  L6: Observability — logs, metrics, traces, dashboards
  L7: CI/CD + infrastructure

## INTERFACE CONTRACT SCHEMA (per boundary)
  {
    "name": "service_name",
    "type": "REST|QUEUE|WEBSOCKET|MCP",
    "request": {schema},
    "response": {schema},
    "auth": "JWT|API_KEY|internal",
    "errors": [{code, description}],
    "idempotency": "keyed|at_most_once|at_least_once"
  }

## EVENT SCHEMA REGISTRY (per event)
  {
    "event": "event.name",
    "version": "1.0",
    "producer": "service_name",
    "consumers": ["consumer_a", "consumer_b"],
    "payload": {schema},
    "retry_semantics": "at_least_once",
    "dead_letter_queue": true|false
  }

## VERIFY
  [ ] All 7 layers defined
  [ ] All service boundaries have contracts
  [ ] All async events have schemas + DLQ decisions
  [ ] Dependency graph has no cycles
  [ ] ADR exists for all non-obvious choices
  [ ] Consumer map lists all contract dependents

## GATE
  All 6 verify items green → UNLOCK C03

## HANDOFF
  current_chunk=C03, architecture_locked=true


# ┌────────────────────────────────────────────────────────┐
# │ C03 — DATA MODEL + STORAGE                             │
# └────────────────────────────────────────────────────────┘
## Horde: HORDE-SCHEMA (2 instances: migrations | indexes+RLS)
## Control Planes: ENGINEERING + QUALITY

## READ
  docs/architecture/SYSTEM_LAYERS.md
  docs/architecture/INTERFACE_CONTRACTS.json

## BUILD
  docs/schema/ERD.md
  docs/schema/COLUMN_SPEC.json        ← every table, column, type, constraint
  docs/schema/QUERY_INTENT_MATRIX.json ← query → expected index
  docs/schema/MIGRATION_BLAST_RADIUS.md
  alembic/versions/001_initial_schema.py
  alembic/versions/002_indexes.py
  db/seeds/base_seed.sql
  tests/db/test_migrations.py
  tests/db/test_rls.py

## SCHEMA RULES
  - Every table: UUID PK, created_at, updated_at TIMESTAMPTZ
  - Multi-tenant tables: tenant_id UUID NOT NULL + RLS policy
  - Every FK: reviewed for index need
  - Vector stores: index created before any vector writes
  - No many-to-many: always a named join table
  - Alembic: every migration has upgrade() AND downgrade()
  - Indexes: created CONCURRENTLY in production migrations

## VERIFY COMMANDS
  alembic upgrade head
  alembic downgrade -1
  alembic upgrade head
  python -m db.verify_schema
  pytest tests/db/test_migrations.py -v
  pytest tests/db/test_rls.py -v

## COMPATIBILITY
  If schema changes after first lock:
  Write docs/schema/SCHEMA_COMPAT_{date}.json
    { table, column, change_type, breaking, consumers, tests_updated }

## GATE
  [ ] upgrade/downgrade/upgrade cycle passes
  [ ] schema verifier passes
  [ ] RLS tests pass
  [ ] every query in intent matrix has a supporting index
  [ ] blast radius report written

## HANDOFF
  current_chunk=C04, schema_locked=true


# ┌────────────────────────────────────────────────────────┐
# │ C04 — API + EVENT CONTRACTS                            │
# └────────────────────────────────────────────────────────┘
## Horde: HORDE-API (3 instances: OpenAPI | Pydantic models | auth+events)
## Control Planes: ENGINEERING

## READ
  docs/schema/COLUMN_SPEC.json
  docs/architecture/INTERFACE_CONTRACTS.json
  docs/architecture/EVENT_SCHEMA_REGISTRY.json

## BUILD
  api/openapi.yaml                     ← fully validated
  api/models/request_models.py
  api/models/response_models.py
  api/auth/auth_spec.md
  api/auth/claims_map.json
  api/events/event_contracts.json
  api/errors/error_envelopes.json
  api/OPENAPI_HASH.txt

## API DESIGN RULES
  - Every route: description, request model, response model, error codes
  - Every list: pagination contract {page, per_page, total, items}
  - Every write: idempotency key documented
  - Every destructive op: explicit auth requirement + 2FA flag
  - Rate-limit class assigned per route group
  - No Pydantic model uses Any

## ERROR ENVELOPE STANDARD
  { "error": "ERROR_CODE", "message": "human description",
    "field": "field_name|null", "correlation_id": "uuid" }

## VERIFY COMMANDS
  openapi-spec-validator api/openapi.yaml
  python -m mypy api/models/ --strict
  python -m pytest tests/api/test_contracts.py -v

## COMPATIBILITY
  Write docs/architecture/API_CONSUMER_IMPACT_{date}.json
  for any breaking route, payload, or response shape change.

## GATE
  [ ] openapi-spec-validator passes
  [ ] no Any types in models
  [ ] auth claims map complete
  [ ] event contracts complete
  [ ] error envelopes defined
  [ ] contract diff explained if applicable

## HANDOFF
  current_chunk=C05, api_contracts_locked=true


# ┌────────────────────────────────────────────────────────┐
# │ C05 — SERVICES + AGENTS                                │
# └────────────────────────────────────────────────────────┘
## Horde: HORDE-AGENTS + HORDE-SERVICES (5 parallel instances)
## Instances: service_layer | repo_layer | workers | agents | integration_tests
## Control Planes: ENGINEERING + QUALITY

## READ
  api/openapi.yaml
  docs/architecture/INTERFACE_CONTRACTS.json
  docs/architecture/EVENT_SCHEMA_REGISTRY.json

## BUILD
  services/                   ← one file per bounded domain
  repositories/               ← one file per DB entity
  workers/                    ← background jobs + queue consumers
  agents/                     ← agent classes + tool registries
  shared/resilience.py        ← timeout, retry, circuit breaker
  shared/exceptions.py        ← typed exception hierarchy
  shared/logging.py           ← structlog config + correlation helpers
  shared/audit.py             ← audit row factory
  tests/integration/test_services_*.py

## RESILIENCE TEMPLATE (ALL services, workers, agents use this)
  @retry(max_attempts=3, backoff_base=1.0, skip_on=[400,401,404])
  @circuit_breaker(threshold=5, recovery_timeout=60)
  async def call_external(self, ...) -> ...:
      async with asyncio.timeout(30):
          result = await self._client.call(...)
          self._audit(event="external_call_complete", result=result)
          return result

## ARCHITECTURE LAWS (enforced, not advisory)
  - no business logic in route handlers
  - no raw DB access outside repository layer
  - no agent imports another agent directly (use router/bus)
  - agents receive typed inputs, return typed outputs
  - every critical state change writes an audit row
  - workers must handle restart without duplicate side effects

## VERIFY COMMANDS
  pytest tests/integration/test_services_*.py -v
  python -m mypy services/ repositories/ workers/ agents/ --strict
  python -m pytest tests/integration/test_resilience.py -v

## COMPATIBILITY
  Write docs/architecture/SERVICE_CONSUMER_IMPACT_{date}.json
  for any change to a service signature or agent tool contract.

## GATE
  [ ] all integration tests pass
  [ ] mypy strict passes
  [ ] resilience primitives used in all external calls
  [ ] no business logic in routes (reviewer confirms)
  [ ] audit logging present for critical operations
  [ ] ToolCallJudge ≥ 0.90 for agent systems

## HANDOFF
  current_chunk=C06, services_locked=true


# ┌────────────────────────────────────────────────────────┐
# │ C06 — FRONTEND + UI SYSTEM                             │
# └────────────────────────────────────────────────────────┘
## Horde: HORDE-PORTAL (3 parallel instances)
## Instances: pages+routing | components | onboarding+activation
## Control Planes: PRODUCT + ENGINEERING

## READ
  docs/spec/PRODUCT_SPEC.md
  api/openapi.yaml
  docs/spec/ONBOARDING_SUCCESS.md

## BUILD
  app/(routes)/              ← all pages and layouts
  components/ui/             ← primitive UI library
  components/features/       ← domain-specific components
  lib/api-client.ts          ← ONLY place raw fetch/axios lives
  lib/validators.ts          ← Zod schemas for every API response
  lib/auth.ts                ← Clerk or JWT session helpers
  app/onboarding/            ← multi-step wizard
  app/onboarding/activation-tracker.ts
  tests/e2e/test_onboarding.spec.ts

## FRONTEND LAWS
  - all data fetching through lib/api-client.ts
  - all API responses validated through lib/validators.ts
  - every list has: loading state, empty state, error state
  - every form has: inline validation, submit state, error display
  - real-time UI has: graceful fallback if websocket drops
  - onboarding tracks: signup, workspace, integration, first-action, invite, repeat

## ACTIVATION TRACKING EVENTS
  user.signed_up
  workspace.created
  integration.connected
  first_value_action.completed
  team_member.invited
  feature.used_twice

## VERIFY COMMANDS
  npx tsc --noEmit
  npx eslint app/ components/ lib/ --max-warnings=0
  npx playwright test tests/e2e/test_onboarding.spec.ts
  npx playwright test tests/e2e/test_first_value.spec.ts

## GATE
  [ ] TypeScript strict passes
  [ ] ESLint zero warnings
  [ ] no raw fetch outside api-client.ts
  [ ] empty/loading/error states on all lists
  [ ] onboarding E2E passes
  [ ] first-value journey E2E passes
  [ ] activation events fire correctly

## HANDOFF
  current_chunk=C07, frontend_locked=true


# ┌────────────────────────────────────────────────────────┐
# │ C07 — WIRING + CRITICAL PATH                           │
# └────────────────────────────────────────────────────────┘
## Horde: HORDE-API + HORDE-INFRA
## Control Planes: ENGINEERING + QUALITY

## READ
  api/openapi.yaml
  docs/architecture/DEPENDENCY_GRAPH.json
  docs/spec/JTBD_MAP.md

## BUILD
  lib/api-client.ts (complete bindings)
  api/routes/*.py (bindings to service layer)
  workers/queue_bindings.py
  integrations/client_adapters.py
  docs/quality/CRITICAL_PATH_TRACE.md
  tests/e2e/test_critical_path.spec.ts

## CRITICAL PATH TRACE REQUIREMENT
  For each primary user action, document:
  Step 1: UI event (component, event type)
  Step 2: api-client.ts call (method, endpoint)
  Step 3: API route handler → service call
  Step 4: Repository → DB mutation
  Step 5: Event/queue emission if applicable
  Step 6: UI reflection (websocket / polling / react-query invalidation)
  Step 7: Audit log row written
  Each step must reference correlation_id propagation.

## VERIFY COMMANDS
  pytest tests/e2e/test_critical_path.spec.ts
  python -m pytest tests/integration/test_wiring.py -v
  python -m pytest tests/integration/test_event_propagation.py -v

## COMPATIBILITY
  Write docs/quality/TRACE_GAP_REPORT.md
  for any critical path with broken or untraceable hops.

## GATE
  [ ] E2E critical path passes
  [ ] correlation_id present at every hop
  [ ] DB mutation visible in UI
  [ ] queue/event consumed successfully
  [ ] audit log row written
  [ ] no trace gaps

## HANDOFF
  current_chunk=C08, wiring_complete=true


# ┌────────────────────────────────────────────────────────┐
# │ C08 — TESTING + EVALS                                  │
# └────────────────────────────────────────────────────────┘
## Horde: HORDE-EVAL (2 parallel instances)
## Instances: test_suite | evals+release_fitness
## Control Planes: QUALITY

## READ
  docs/spec/PRODUCT_SPEC.md
  api/openapi.yaml
  docs/quality/CRITICAL_PATH_TRACE.md

## BUILD
  tests/unit/
  tests/integration/
  tests/e2e/
  tests/load/locustfile.py
  tests/regression/
  tests/db/test_migration_rollback.py
  evals/golden_sets/*.json         ← agent evals
  evals/judges/*.py
  docs/quality/RELEASE_FITNESS.json
  docs/quality/TEST_GAP_REPORT.json

## TEST PYRAMID TARGETS
  Unit tests:        fastest, isolated, mock repos+clients
  Integration tests: real DB/Redis, mock external APIs
  E2E tests:         Playwright, real stack, primary journeys
  Load tests:        Locust, 100 concurrent, P99 < 5s
  Regression tests:  one test per TASK_TREE feature line

## TEST QUALITY RULES
  - no bare: assert True / assert 1 == 1
  - every test must be able to fail for a real reason
  - every business rule must have a test that breaks on violation
  - every DB test must use real DB (not mock) in integration tier
  - migration rollback test: upgrade → downgrade → upgrade passes

## EVALS (when agents are in scope)
  ToolCallJudge:     tool selection accuracy ≥ 0.90
  GroundingJudge:    output grounded in context ≥ 0.85
  AdversarialJudge:  adversarial input does not cause hallucination

## VERIFY COMMANDS
  pytest --cov=. --cov-fail-under=80 -v
  npx playwright test --reporter=html
  locust -f tests/load/locustfile.py --headless -u 100 -r 10 --run-time 2m
  pytest tests/db/test_migration_rollback.py -v
  python -m evals.run_all_judges

## GATE
  [ ] coverage ≥ 80%
  [ ] regression suite green
  [ ] migration rollback passes
  [ ] Playwright E2E all green
  [ ] load P99 < 5s under 100 concurrent
  [ ] judge scores pass for agent systems
  [ ] test gap report written
  [ ] RELEASE_FITNESS.json generated

## HANDOFF
  current_chunk=C09, quality_validated=true


# ┌────────────────────────────────────────────────────────┐
# │ C09 — SECURITY + TENANT SAFETY                         │
# └────────────────────────────────────────────────────────┘
## Horde: HORDE-SECURITY + HORDE-AUDIT
## Control Planes: OPERATIONS + QUALITY

## READ
  api/auth/auth_spec.md
  docs/schema/COLUMN_SPEC.json
  security/

## BUILD
  security/SBOM.json
  security/owasp_checklist.md
  security/findings_report.json
  security/secrets_inventory.md
  security/key_rotation_procedure.md
  tests/security/test_tenant_isolation.py
  tests/security/test_auth_enforcement.py

## REQUIRED CHECKS
  gitleaks detect --no-git
  pip-audit -r requirements.txt
  npm audit --audit-level=high
  bandit -r . -l
  semgrep --config=auto .
  python -m pytest tests/security/test_tenant_isolation.py -v
  python -m pytest tests/security/test_auth_enforcement.py -v

## TENANT ISOLATION TESTS MUST COVER
  - user A cannot read user B's data via API
  - user A cannot read user B's data via direct DB query
  - JWT from tenant A does not grant access in tenant B
  - admin scope cannot be escalated by non-admin JWT

## VERIFY COMMANDS
  gitleaks detect
  pip-audit -r requirements.txt
  bandit -r . -ll
  pytest tests/security/ -v

## GATE
  [ ] gitleaks: zero findings
  [ ] pip-audit: zero HIGH/CRITICAL
  [ ] bandit: zero HIGH
  [ ] cross-tenant API tests pass
  [ ] cross-tenant DB tests pass
  [ ] auth enforcement tests pass
  [ ] SBOM generated
  [ ] OWASP checklist complete

## HUMAN CHECKPOINT 2 — SECURITY TRUST
  A human reviews findings_report.json before production
  and signs off that the system is safe for real customer data.

## HANDOFF
  current_chunk=C10, security_complete=true


# ┌────────────────────────────────────────────────────────┐
# │ C10 — CI/CD + PROMOTION SYSTEM                         │
# └────────────────────────────────────────────────────────┘
## Horde: HORDE-INFRA (2 instances: pipeline | monitoring+rollback)
## Control Planes: OPERATIONS

## READ
  docs/quality/RELEASE_FITNESS.json
  security/findings_report.json
  docs/architecture/SYSTEM_LAYERS.md

## BUILD
  .github/workflows/ci.yaml
  .github/workflows/deploy_canary.yaml
  .github/workflows/rollback.yaml
  infra/terraform/
  infra/k8s/
  infra/prometheus/alerts/
  infra/grafana/dashboards/
  scripts/rollback.sh
  scripts/restore.sh
  docs/ops/DEPLOYMENT_PROMOTION_POLICY.md
  docs/ops/RELEASE_IMPACT_REPORT_template.json

## 13-STAGE CI/CD PIPELINE
  1.  code-quality:    black, isort, flake8, pylint, mypy
  2.  secret-scan:     gitleaks
  3.  dependency-audit: pip-audit, npm audit
  4.  unit-tests:      pytest --cov --fail-under=80
  5.  integration-tests: pytest tests/integration/ (real DB)
  6.  frontend-build:  tsc, eslint, next build
  7.  e2e-tests:       playwright
  8.  security-scan:   bandit, semgrep, trivy
  9.  build+push:      docker build, push to registry
  10. deploy-staging:  alembic upgrade head, k8s rollout
  11. smoke-test:      curl /health, run smoke suite
  12. canary-prod:     10% traffic, 5 min observation
  13. promote-or-rollback: auto-promote on fitness | rollback on breach

## AUTO-ROLLBACK TRIGGERS
  error_rate > 1%
  P95 latency > 500ms
  health check failures > 2
  canary fitness score < 0.90

## ROLLBACK PROCEDURE
  kubectl rollout undo deployment/{name} -n production
  alembic downgrade -1
  redis-cli flushdb (cache only, not data)

## VERIFY COMMANDS
  (trigger test push)
  gh run watch {run_id}
  kubectl rollout status deployment/{name}
  curl https://{staging}/health

## GATE
  [ ] all 13 stages pass on test commit
  [ ] forced rollback executes cleanly
  [ ] alerts fire on injected SLO breach
  [ ] dashboards render with real data
  [ ] release impact report template ready

## HANDOFF
  current_chunk=C11, cicd_complete=true


# ┌────────────────────────────────────────────────────────┐
# │ C11 — DEPLOY + ONBOARDING + HANDOFF                    │
# └────────────────────────────────────────────────────────┘
## Horde: HORDE-DOCS + HORDE-INFRA + HORDE-CONDUCTOR
## Control Planes: PRODUCT + OPERATIONS

## READ
  docs/quality/RELEASE_FITNESS.json
  docs/ops/DEPLOYMENT_PROMOTION_POLICY.md
  docs/spec/ONBOARDING_SUCCESS.md

## BUILD
  docs/user/GETTING_STARTED.md
  docs/user/FAQ.md
  docs/user/FEATURE_GUIDES/
  docs/ops/RUNBOOK_DEPLOY.md
  docs/ops/RUNBOOK_INCIDENTS.md
  docs/ops/RUNBOOK_RESTORE.md
  docs/handoff/HANDOFF_PACKAGE.md
  docs/handoff/ARCHITECTURE_SUMMARY.md
  docs/handoff/OPEN_RISKS.md
  docs/handoff/POST_GO_LIVE_BACKLOG.md
  email_templates/welcome.html
  email_templates/onboarding_day1.html
  email_templates/onboarding_day3.html

## PRE-DEPLOY CHECKLIST
  [ ] all C01-C10 gates green
  [ ] RELEASE_FITNESS.json: all dimensions true
  [ ] staging smoke test green
  [ ] backup confirmed
  [ ] rollback script tested
  [ ] on-call owner assigned
  [ ] Sentry/alerting connected
  [ ] DNS + TLS confirmed

## ONBOARDING ACTIVATION FUNNEL
  Step 1: user.signed_up
  Step 2: workspace.created
  Step 3: integration.connected
  Step 4: first_value_action.completed  ← THE activation gate
  Step 5: team_member.invited
  Step 6: feature.used_twice

## HANDOFF PACKAGE AUDIENCES
  Operator:   deploy runbook, rollback, restore, alert map, secret ownership
  Engineer:   architecture summary, schema map, service map, event registry,
              extension points, compatibility rules
  Client:     getting started, onboarding checklist, permissions guide, FAQ,
              support escalation
  Legal:      data flow summary, audit trail design, tenant isolation statement,
              retention policy, security controls, open risks

## HUMAN CHECKPOINT 3 — UX/HANDOFF
  A human reviews the onboarding flow and handoff package
  before claiming the system is production-ready.

## VERIFY
  [ ] prod health check: 200
  [ ] first real user completes onboarding
  [ ] activation event fires
  [ ] restore drill verified
  [ ] handoff package reviewed by named owner

## GATE
  ALL above green → PROJECT STATUS: LIVE

## HANDOFF
  Transition to ENHANCEMENT LOOP.
  current_chunk=LOOP, project_status=LIVE


# ════════════════════════════════════════════════════════════
# PART 5 — HORDE-AUDIT: 5-LAYER QUALITY GATE
# ════════════════════════════════════════════════════════════
# Runs after EVERY coding horde output, before unlock.
# 3 audit instances run in parallel. Majority rules for pass.

## AUDIT LAYER 1 — CODE QUALITY
  Checks: typing, no Any, no bare except, no TODO,
          docstrings on public functions, no hard-coded secrets
  Tools: mypy --strict, bandit, gitleaks, flake8
  Fail = block chunk gate

## AUDIT LAYER 2 — CONTRACT INTEGRITY
  Checks: schema matches spec, API matches contracts,
          event payloads match registry, Pydantic models match OpenAPI
  Tools: openapi-spec-validator, python -m db.verify_schema,
         contract-diff report review
  Fail = write CONTRACT_VIOLATION.md + block

## AUDIT LAYER 3 — RESILIENCE COMPLETENESS
  Checks: every external call has timeout + retry,
          circuit breakers on all external deps,
          typed exceptions used (no bare Exception),
          structured logging with correlation_id,
          graceful shutdown handled
  Tools: grep + AST scan + integration test execution
  Fail = list every missing instance, block

## AUDIT LAYER 4 — SECURITY SURFACE
  Checks: no new secrets in code, no new unvalidated inputs,
          auth enforced on protected routes,
          tenant scope respected in DB queries,
          no new dependencies without audit
  Tools: gitleaks, pip-audit, bandit --level HIGH, manual scan
  Fail = block until resolved

## AUDIT LAYER 5 — OPERATIONAL READINESS
  Checks: health endpoint exists, relevant tests pass,
          rollback path documented for new changes,
          observability events emitted for new critical ops,
          cost impact estimated for new infrastructure
  Tools: pytest, manual review of new infra changes
  Fail = write OPS_GAP.md + block

## AUDIT OUTPUT
  docs/audit/AUDIT_{chunk}_{date}.json
  {
    "chunk": "C05",
    "layers": {
      "code_quality":        { "pass": true,  "findings": [] },
      "contract_integrity":  { "pass": false, "findings": ["service X response missing field Y"] },
      "resilience":          { "pass": true,  "findings": [] },
      "security_surface":    { "pass": true,  "findings": [] },
      "operational_readiness": { "pass": true, "findings": [] }
    },
    "overall": "FAIL",
    "block_reason": "contract_integrity violation in service X",
    "remediation": "update response model + consumer test"
  }

## CONTINUITY ENGINE (runs after audit completes)
  HORDE-PLANNER:  reads audit delta → maps all downstream files impacted
  HORDE-REFINER:  applies surgical spec/code fixes → updates changelog
  HORDE-CONDUCTOR: re-briefs affected hordes → fires next chunk


# ════════════════════════════════════════════════════════════
# PART 6 — QUALITY GATES (ALL CHUNKS)
# ════════════════════════════════════════════════════════════

## RELEASE FITNESS DIMENSIONS
  Every chunk from C08 onward must write RELEASE_FITNESS.json
  All 6 dimensions must be TRUE before promotion to production.

  DIMENSION          VERIFY METHOD
  ─────────────────────────────────────────────────────
  schema_safe        alembic downgrade -1 + upgrade passes
  tenant_safe        cross-tenant isolation tests pass
  rollback_safe      kubectl rollout undo + smoke test passes
  observability_ready dashboards render + alerts fire
  onboarding_ready   first-user onboarding E2E passes
  critical_path_ready primary user journey E2E passes

## GATE SCORECARD FORMAT
  C01  [ ] spec_hash_written
       [ ] all_questions_answered
       [ ] out_of_scope_explicit
       [ ] activation_defined
       [ ] task_tree_complete

  C02  [ ] system_layers_complete
       [ ] dependency_graph_no_cycles
       [ ] interface_contracts_all_boundaries
       [ ] event_schema_registry_complete
       [ ] adrs_for_non_obvious_choices

  C03  [ ] upgrade_downgrade_upgrade_passes
       [ ] schema_verifier_passes
       [ ] rls_tests_pass
       [ ] query_intent_index_aligned
       [ ] blast_radius_report_written

  C04  [ ] openapi_validator_passes
       [ ] no_any_types
       [ ] auth_claims_map_complete
       [ ] event_contracts_complete
       [ ] error_envelopes_defined

  C05  [ ] integration_tests_pass
       [ ] mypy_strict_passes
       [ ] resilience_on_all_external_calls
       [ ] audit_logging_present
       [ ] tool_call_judge_passes

  C06  [ ] typescript_strict_passes
       [ ] eslint_zero_warnings
       [ ] typed_api_client_only
       [ ] empty_loading_error_states
       [ ] activation_events_fire

  C07  [ ] critical_path_e2e_passes
       [ ] correlation_ids_full_trace
       [ ] db_to_ui_reflection
       [ ] event_propagation_verified
       [ ] audit_log_written

  C08  [ ] coverage_80pct
       [ ] regression_suite_green
       [ ] migration_rollback_passes
       [ ] playwright_green
       [ ] load_p99_under_5s
       [ ] judge_scores_pass
       [ ] release_fitness_generated

  C09  [ ] gitleaks_zero
       [ ] pip_audit_zero_high
       [ ] bandit_zero_high
       [ ] tenant_isolation_passes
       [ ] auth_enforcement_passes
       [ ] owasp_complete

  C10  [ ] pipeline_all_13_stages_pass
       [ ] canary_works
       [ ] rollback_works
       [ ] alerts_fire
       [ ] dashboards_render

  C11  [ ] prod_health_200
       [ ] first_user_activates
       [ ] activation_event_fires
       [ ] restore_drill_passes
       [ ] handoff_package_complete


# ════════════════════════════════════════════════════════════
# PART 7 — HANDOFF RUNBOOK
# ════════════════════════════════════════════════════════════

## Handoff Audiences + Required Deliverables

  OPERATOR HANDOFF
    docs/ops/RUNBOOK_DEPLOY.md
    docs/ops/RUNBOOK_INCIDENTS.md
    docs/ops/RUNBOOK_RESTORE.md
    infra/prometheus/alerts/ (alert map)
    security/secrets_inventory.md
    on-call rotation assigned

  ENGINEER HANDOFF
    docs/handoff/ARCHITECTURE_SUMMARY.md
    docs/schema/ERD.md + COLUMN_SPEC.json
    docs/architecture/INTERFACE_CONTRACTS.json
    docs/architecture/EVENT_SCHEMA_REGISTRY.json
    docs/handoff/KNOWN_EXTENSION_POINTS.md
    docs/handoff/COMPATIBILITY_RULES.md

  CLIENT/ADMIN HANDOFF
    docs/user/GETTING_STARTED.md
    docs/user/FAQ.md
    docs/user/FEATURE_GUIDES/
    email_templates/
    support escalation path

  LEGAL/COMPLIANCE HANDOFF (when applicable)
    docs/handoff/DATA_FLOW_SUMMARY.md
    docs/handoff/AUDIT_TRAIL_DESIGN.md
    docs/handoff/TENANT_ISOLATION_STATEMENT.md
    docs/handoff/RETENTION_POLICY.md
    docs/handoff/SECURITY_CONTROLS_SUMMARY.md
    docs/handoff/OPEN_RISKS.md

## POST-GO-LIVE IMPROVEMENT LOOP
  Immediately post-handoff create backlog in 4 categories:
  1. Defects — things that are wrong
  2. Friction — things that work but feel bad
  3. Scale risks — things that will break at 10x
  4. Enhancements — new value to add

  Each item format:
  {
    "title": str,
    "symptom": str,
    "impact": "user|operator|engineer",
    "owner": str,
    "target_chunk": "C0X|LOOP",
    "priority": "HIGH|MEDIUM|LOW"
  }

## Handoff Acceptance Rule
  Handoff is NOT complete when files are exported.
  It IS complete when the next responsible human or horde can:
  - operate the system without reverse-engineering it
  - extend the system without breaking existing contracts
  - defend the system's security posture
  - explain the system to a new stakeholder in under 10 minutes


# ════════════════════════════════════════════════════════════
# PART 8 — LEXCORE SESSION PROMPTS (Paste into Cascade)
# ════════════════════════════════════════════════════════════

## LEXCORE C01 — PRODUCT DEFINITION
You are HORDE-ARCH. System: LexCore North America Legal Intelligence Database.
READ: raw requirements from this conversation thread.
TASK: Write docs/spec/PRODUCT_SPEC.md, TASK_TREE.md, JTBD_MAP.md,
ONBOARDING_SUCCESS.md, OUT_OF_SCOPE.md, SPEC_HASH.txt for LexCore.
Primary user: Legal tech operators, IP attorneys, compliance teams.
Core value: Fully autonomous NA legal data ingestion, BAM-addressed retrieval,
attorney-quality handoff packages, immutable evidence chain.
Clarify before writing: ask the 5 required C01 questions first.
Gate: all spec sections present, hash written, task tree numbered.

## LEXCORE C02 — ARCHITECTURE
You are HORDE-ARCH. System: LexCore.
READ: docs/spec/PRODUCT_SPEC.md
TASK: Write SYSTEM_LAYERS.md (7 layers), DEPENDENCY_GRAPH.json,
INTERFACE_CONTRACTS.json, EVENT_SCHEMA_REGISTRY.json, ADRs.
Key boundaries: scraper → ingest → PostgreSQL+Qdrant+Redis → MCP gateway → agents.
Key events: doc.ingested, doc.updated, doc.deprecated, search.executed, agent.dispatched.
Gate: no cycles, all 7 layers, all contracts + events, ADRs for stack choices.

## LEXCORE C03 — DATA MODEL
You are HORDE-SCHEMA (2 instances).
READ: docs/architecture/SYSTEM_LAYERS.md, INTERFACE_CONTRACTS.json
TASK: Write ERD.md, COLUMN_SPEC.json, QUERY_INTENT_MATRIX.json,
MIGRATION_BLAST_RADIUS.md, Alembic migrations, RLS tests.
Core tables: jurisdictions, legal_documents, legal_chunks (pgvector),
legal_citations, legal_updates, agent_queries, query_cache.
Dual-key: every document carries fabric_signal_hex + bam_domain_code.
Gate: upgrade/downgrade/upgrade passes, RLS passes, vector index before writes.

## LEXCORE C04 — API + MCP CONTRACTS
You are HORDE-API (3 instances).
READ: docs/schema/COLUMN_SPEC.json, docs/architecture/INTERFACE_CONTRACTS.json
TASK: Write api/openapi.yaml, Pydantic models, auth spec, MCP tool contracts.
MCP tools: search_legal, get_document, get_citations, check_updates,
jurisdiction_summary, verify_integrity.
Gate: openapi valid, no Any types, MCP tool schemas typed, auth claims complete.

## LEXCORE C05 — SERVICES + AGENTS
You are HORDE-AGENTS (5 instances).
READ: api/openapi.yaml, docs/architecture/INTERFACE_CONTRACTS.json
TASK: Write services/, repositories/, workers/, agents/.
Agents: LexIngest, LexSearch, LexAnalysis, LexDraft, LexMonitor, LexCite, LexRouter.
Resilience: ALL agents use shared/resilience.py — timeout, retry, circuit breaker.
Gate: integration tests pass, resilience applied, audit logging present.

## LEXCORE C06 — FRONTEND
You are HORDE-PORTAL (3 instances).
READ: docs/spec/PRODUCT_SPEC.md, api/openapi.yaml
TASK: Next.js 14 app — search UI, jurisdiction browser, document viewer,
monitoring dashboard, BAM signal display, query cache analytics.
Typed client only. Zod validators on all responses.
Gate: tsc passes, ESLint clean, first-value search journey E2E passes.

## LEXCORE C07–C11
Follow standard chunk specifications above.
Key LexCore specifics:
C07: trace search query → hybrid retrieval → chunk result → UI render
C08: include legal retrieval quality evals (precision@10, MRR)
C09: tenant isolation critical — each customer key isolates their query logs
C10: daily ingest cron tested in CI; canary on ingest pipeline
C11: attorney portal onboarding + operator runbook for ingest pipeline


# ════════════════════════════════════════════════════════════
# PART 9 — LEXRADAR SESSION PROMPTS (Paste into Cascade)
# ════════════════════════════════════════════════════════════

## LEXRADAR C01 — PRODUCT DEFINITION
You are HORDE-ARCH. System: LexRadar IP Intelligence and Patent Pipeline.
READ: raw requirements from this conversation thread.
TASK: Write full product spec for LexRadar.
Primary user: IP attorneys, in-house counsel, patent operations teams.
Core value: Fully autonomous repo → detect → prior art → score → disclose →
blockchain ledger → attorney handoff. Attorney's only job: review + file.
Clarify: ask all 5 C01 questions. Confirm autonomy boundary (system stops at
USPTO door — attorney files manually).
Gate: autonomy boundary explicit in spec, activation = attorney portal access.

## LEXRADAR C02 — ARCHITECTURE
You are HORDE-ARCH. System: LexRadar.
READ: docs/spec/PRODUCT_SPEC.md
TASK: Write all architecture artifacts.
Key boundaries: code connector → scanner → detector → prior art → scorer →
discloser → ledger → attyflow → attorney portal.
Key events: scan.triggered, candidate.created, disclosure.drafted,
ledger.anchored, handoff.delivered, attorney.approved, attorney.rejected.
Autonomy boundary: ledger.anchored → handoff.delivered is the last auto step.
ADR required: blockchain choice (Polygon vs others), embedding model, scoring model.

## LEXRADAR C03 — DATA MODEL
You are HORDE-SCHEMA (2 instances).
READ: docs/architecture/SYSTEM_LAYERS.md
TASK: Schema for LexRadar.
Core tables: tenants, connectors, scan_jobs, artifacts, ip_candidates,
prior_art_results, ip_scores, disclosures, ledger_anchors, handoff_packages,
attorney_reviews, agent_queries.
Critical: ip_candidates must be immutable after ledger_anchored=true.
Gate: upgrade/downgrade passes, immutability tests pass.

## LEXRADAR C04 — API CONTRACTS
You are HORDE-API (3 instances).
READ: docs/schema/COLUMN_SPEC.json
TASK: API contracts for LexRadar.
Key routes: POST /scans/trigger, GET /candidates, GET /candidates/{id}/disclosure,
POST /candidates/{id}/attorney-action (approve|reject|request-changes),
GET /handoffs/{id}/filing-bundle (download).
Auth: attorney portal uses scoped JWT (48h, single attorney, single handoff).
Gate: scoped JWT spec explicit, filing bundle download contract defined.

## LEXRADAR C05 — AGENTS
You are HORDE-AGENTS (5 instances).
READ: api/openapi.yaml, docs/architecture/INTERFACE_CONTRACTS.json
TASK: Implement the 9 LexRadar agents.
Agents: AGT_SCANNER, AGT_DETECTOR, AGT_PRIORART, AGT_SCORER,
AGT_DISCLOSER, AGT_LEDGER, AGT_ATTYFLOW, AGT_MONITOR, AGT_ROUTER.
BAM signals: every agent action emits a BAM-coded audit event.
Non-negotiable: AGT_LEDGER never stores IP content on-chain.
AGT_ATTYFLOW enforces attorney review — status cannot reach "filed" without it.
Gate: all agents typed, resilient, BAM-audited, immutability enforced.

## LEXRADAR C06 — ATTORNEY PORTAL + DASHBOARD
You are HORDE-PORTAL (3 instances).
READ: docs/spec/PRODUCT_SPEC.md, api/openapi.yaml
TASK: Next.js 14 attorney portal.
Sections: handoff package viewer (10 sections), claim theme editor (editable),
evidence chain viewer (read-only), prior art comparison table,
filing bundle download, action buttons (approve/reject/request-changes),
operator dashboard (pipeline health, BAM signal trace, agent activity).
Token-gated: portal access requires scoped JWT. Expired token = graceful lockout.
Gate: scoped token flow works, filing bundle download works, all 3 edit sections editable.

## LEXRADAR C07–C11
Follow standard chunk specs above.
Key LexRadar specifics:
C07: trace commit → scan → candidate → disclosure → ledger → attorney email → portal
C08: add hallucination check eval for disclosures (no unsupported claims)
C09: BYOK (bring your own key) must work for all evidence bundles
C10: webhook trigger tested in CI (fake GitHub push → pipeline executes)
C11: attorney portal onboarding + client admin guide + legal compliance handoff


# ════════════════════════════════════════════════════════════
# PART 10 — POST-LIVE ENHANCEMENT LOOP
# ════════════════════════════════════════════════════════════

## Loop Trigger Conditions
  Any of the following opens a new loop iteration:
  - defect from post-go-live backlog
  - new feature requested (new PRODUCT_SPEC amendment)
  - scale event (traffic 10x or new enterprise tenant)
  - security finding (new CVE in dependency)
  - contract change (schema, API, event)
  - quality degradation (test failure, eval regression)

## Loop Execution Model
  1. HORDE-MONITOR surfaces signal
  2. HORDE-PLANNER triages: which control plane? which chunk?
  3. HORDE-ARCH or appropriate coding horde executes scoped fix
  4. HORDE-AUDIT runs 5-layer audit on changed files only
  5. If audit passes: HORDE-CONDUCTOR promotes fix
  6. HORDE-DOCS updates relevant handoff artifacts

## Loop Scope Control
  Enhancement loops MUST NOT:
  - re-open locked contracts without compatibility report
  - bypass HORDE-AUDIT
  - skip affected consumer tests
  - promote without release fitness check

  Enhancement loops SHOULD:
  - scope narrowly (one bounded domain per loop)
  - produce a LOOP_DELTA.md explaining what changed
  - update SPEC_HASH.txt if spec changed
  - close one item from POST_GO_LIVE_BACKLOG.md per iteration

