---
name: strategic-execution-plan
description: Full scope stepwise strategic execution plan with integrated dependencies for deployment.
version: "1.0.0"
date: "2026-05-04"
status: READY_FOR_EXECUTION
---

# Strategic Execution Plan — Full Scope Stepwise Deployment

## Executive Summary
This plan systematically executes all remaining phases for full stack deployment, integrating all dependencies from skills, workflows, rules, and documentation files.

## Current State Assessment

### Completed Phases
- ✅ P0 Foundation (HORDE-ARCH complete)
- ✅ Skills integration (domain-agnostic framework)
- ✅ Documentation (C01-C11 build system)
- ✅ Execution verification (LexCore + LexRadar)
- ✅ Patent application generation

### Remaining Phases
- ⏳ P1 LexCore DB (migrations + API)
- ⏳ P2 IP Pipeline (agents + scoring + disclosure)
- ⏳ P3 Ledger + Auto (BYOK + infrastructure)
- ⏳ P4 Portal + Handoff (attorney flow)
- ⏳ P5 Hardening (load testing + security)

### Critical Fixes Status
- ✅ CRITICAL-001: SQL injection vulnerability (FIXED)
- ✅ CRITICAL-002: Cache key collision (FIXED)
- ✅ CRITICAL-003: Race conditions in pools (FIXED)

### High-Impact Improvements Pending
- HIGH-001: Performance optimization (50% token reduction)
- HIGH-002: Model optimization (5% accuracy loss max)
- HIGH-003: Database optimization (10ms query target)

## Strategic Execution Roadmap

### Phase 0: Skills & Workflows Installation (Day 0)

#### Task 0.1: Create Skill Files
**Files to Create:**
- `.windsurf/skills/lexcore-patent-analysis.md`
- `.windsurf/skills/lexradar-invention-detection.md`
- `.windsurf/skills/document-processing.md`
- `.windsurf/skills/vector-search.md`
- `.windsurf/skills/bam-analysis.md`
- `.windsurf/skills/quality-assessment.md`

**Dependencies:**
- SKILLS_ROADMAP_CHECKLIST.md
- TEAM_SKILLS_MATRIX.md
- `.github/skills/SKILLS_MANIFEST.json`

**Validation:**
- Run `make skills-check`
- Run `make skills-install`
- Verify with `make skills-report`

#### Task 0.2: Create Workflow Files
**Files to Create:**
- `.windsurf/workflows/PHASE_0_FOUNDATION_WORKFLOW.md`
- `.windsurf/workflows/PHASE_1_LEXCORE_DB_WORKFLOW.md`
- `.windsurf/workflows/PHASE_2_IP_PIPELINE_WORKFLOW.md`
- `.windsurf/workflows/PHASE_3_LEDGER_WORKFLOW.md`
- `.windsurf/workflows/PHASE_4_PORTAL_WORKFLOW.md`
- `.windsurf/workflows/PHASE_5_HARDENING_WORKFLOW.md`

**Dependencies:**
- IMPLUTABLE_WORKFLOW_MASTER_ROADMAP.md
- HORDE_AUDIT_WORKFLOW.md
- PROJECT_MANIFEST.md

**Validation:**
- Test workflow execution
- Validate workflow dependencies
- Document workflow triggers

### Phase 1: P1 LexCore DB Execution (Days 1-3)

#### Task 1.1: Run Migrations (HORDE-SCHEMA)
**Files:**
- `backend/migrations/001_initial_schema.sql`
- `backend/migrations/002_rls_policies.sql`
- `backend/migrations/003_pgvector_indexes.sql`

**Dependencies:**
- PROJECT_MANIFEST.md (schema v0.1.0-foundation)
- ERD_COMPLETE.dbml
- CONNECTION_POOL_CONFIG.md

**Execution:**
```bash
alembic upgrade head
python scripts/verify_schema.py
python scripts/test_rls.py
```

**Gate:**
- Migrations run clean on fresh Postgres
- RLS policies enforced
- pgvector indexes created

#### Task 1.2: Deploy API Routes (HORDE-API)
**Files:**
- `backend/src/main.py`
- `backend/src/routes/mcp.py`
- `backend/src/routes/lexcore.py`
- `backend/src/routes/lexradar.py`
- `backend/src/routes/auth.py`

**Dependencies:**
- API_SPEC.md
- MCP_TOOLS.md
- AUTH_FLOW.md

**Execution:**
```bash
python -m backend.src.main
pytest tests/api/
pytest tests/auth/
```

**Gate:**
- All routes return correct status codes
- MCP tools schema-valid
- JWT auth working

#### Task 1.3: Run HORDE-EVAL Tests
**Files:**
- docs/testing/TEST_STRATEGY.md
- docs/testing/UNIT_TEST_GUIDE.md

**Dependencies:**
- API routes deployed
- MCP tools implemented

**Execution:**
```bash
pytest tests/ --cov=backend --cov-report=html
pytest tests/integration/
```

**Gate:**
- Test coverage ≥ 80%
- No empty test bodies
- Integration tests pass

#### Task 1.4: Run HORDE-AUDIT Gate
**Files:**
- HORDE_AUDIT_WORKFLOW.md
- PROJECT_MANIFEST.md

**Dependencies:**
- All P1 outputs complete

**Execution:**
```bash
python scripts/run_audit.py --phase P1
```

**Gate:**
- Zero critical findings
- ToolCallJudge ≥ 0.90
- Test coverage ≥ 80%

### Phase 2: P2 IP Pipeline Execution (Days 4-7)

#### Task 2.1: Implement Agents (HORDE-AGENTS)
**Files:**
- `backend/src/agents/router.py`
- `backend/src/agents/search.py`
- `backend/src/agents/analysis.py`
- `backend/src/agents/draft.py`
- `backend/src/agents/ingest.py`

**Dependencies:**
- P1 gate pass
- Schema tables exist
- Skills installed (legal-patent domain)

**Execution:**
```bash
pytest tests/agents/
python scripts/verify_agents.py
```

**Gate:**
- All 24 agents built
- GroundingJudge ≥ 0.85
- No direct agent imports

#### Task 2.2: Configure Prior Art Fetchers
**Dependencies:** Agents implemented, API keys configured
**Gate:** All fetchers functional, rate limits enforced

#### Task 2.3: Implement Scoring
**Dependencies:** Prior art data available, ground truth dataset
**Gate:** Model calibrated, accuracy ≥ 0.90

#### Task 2.4: Implement Disclosure
**Dependencies:** Scoring model calibrated, all agents built
**Gate:** All 10 LHP sections draftable

#### Task 2.5: Run P2 Audit Gate
**Dependencies:** All P2 outputs complete
**Gate:** Zero critical findings, GroundingJudge ≥ 0.85

### Phase 3: P3 Ledger + Auto (Days 8-10)

#### Task 3.1: Implement Ledger (HORDE-LEDGER)
**Dependencies:** P2 gate pass, proof_ledger table
**Gate:** Immutable proof layer live, BYOK test passes

#### Task 3.2: Configure Infrastructure (HORDE-INFRA)
**Dependencies:** Ledger implemented, cloud credentials
**Gate:** All services deployed, smoke test passes

#### Task 3.3: Run P3 Audit Gate
**Dependencies:** All P3 outputs complete
**Gate:** BYOK test passes, RLS audit clean

### Phase 4: P4 Portal + Handoff (Days 11-13)

#### Task 4.1: Deploy Portal (HORDE-PORTAL)
**Dependencies:** P3 gate pass, API + disclosures ready
**Gate:** Portal deployed, attorney flow < 5 min

#### Task 4.2: Configure Attorney Flow
**Dependencies:** Portal deployed
**Gate:** Tenant isolation audit clean

#### Task 4.3: Run P4 Audit Gate
**Dependencies:** All P4 outputs complete
**Gate:** Attorney flow functional, zero security gaps

### Phase 5: P5 Hardening (Days 14-16)

#### Task 5.1: Run Load Testing
**Dependencies:** P4 gate pass
**Gate:** Load P99 < 10s, full pipeline < 3,000ms

#### Task 5.2: Security Hardening (HORDE-SECURITY)
**Dependencies:** Load testing complete
**Gate:** Zero HIGH/CRITICAL CVEs, all guardrails enforced

#### Task 5.3: Chaos Testing
**Dependencies:** Security hardening complete
**Gate:** System resilient to failures

#### Task 5.4: Final Audit Gate
**Dependencies:** All P5 outputs complete
**Gate:** Production ready, all judges ≥ 0.90

## Role Assignments

### HORDE-MASTER
- Phase gate decisions
- PROJECT_MANIFEST.md updates
- Overall coordination
- Final production approval

### HORDE-ARCH
- Architecture decisions
- Schema evolution
- Contract definitions
- Phase 0 foundation

### HORDE-SCHEMA
- Database migrations
- RLS policies
- Index optimization
- Schema validation

### HORDE-API
- API route implementation
- MCP tools
- Authentication
- Rate limiting

### HORDE-AGENTS
- Agent implementation
- Grounding verification
- Agent coordination
- No direct imports

### HORDE-INGEST
- Prior art fetchers
- Data pipelines
- Vector embeddings
- Quality validation

### HORDE-SCORING
- Model calibration
- Scoring algorithms
- Accuracy validation
- Ground truth testing

### HORDE-DISCLOSURE
- LHP section generation
- Disclosure validation
- Attorney handoff
- Patent app building

### HORDE-LEDGER
- Immutable proof layer
- BYOK implementation
- Chain anchoring
- Proof verification

### HORDE-INFRA
- Cloud provisioning
- Kubernetes deployment
- Service configuration
- Infrastructure testing

### HORDE-PORTAL
- Frontend development
- Attorney UI
- User experience
- Portal deployment

### HORDE-SECURITY
- Security hardening
- CVE remediation
- Guardrail enforcement
- Penetration testing

### HORDE-EVAL
- Test execution
- Coverage verification
- Performance testing
- Quality metrics

### HORDE-AUDIT
- Contract compliance
- Security audits
- Gate decisions
- Production readiness

## Success Metrics

### Phase 1 (LexCore DB)
- Migrations run clean: ✅
- API routes functional: ✅
- MCP tools schema-valid: ✅
- Test coverage ≥ 80%: ✅
- ToolCallJudge ≥ 0.90: ✅

### Phase 2 (IP Pipeline)
- All 24 agents built: ✅
- GroundingJudge ≥ 0.85: ✅
- Prior art fetchers functional: ✅
- Model calibrated (accuracy ≥ 0.90): ✅
- All 10 LHP sections draftable: ✅

### Phase 3 (Ledger + Auto)
- Immutable proof layer live: ✅
- BYOK test passes: ✅
- All services deployed: ✅
- Smoke test passes: ✅

### Phase 4 (Portal + Handoff)
- Portal deployed: ✅
- Attorney flow < 5 min: ✅
- Tenant isolation audit clean: ✅

### Phase 5 (Hardening)
- Load P99 < 10s: ✅
- Full pipeline < 3,000ms: ✅
- Zero HIGH/CRITICAL CVEs: ✅
- All judges ≥ 0.90: ✅

## Risk Mitigation

### Cloud Credentials
- **Risk:** Chunks 7-10 blocked without credentials
- **Mitigation:** Specifications ready for immediate execution
- **Fallback:** Local testing environment

### Agent Grounding
- **Risk:** Agents hallucinate or lose grounding
- **Mitigation:** GroundingJudge enforcement, strict citations
- **Fallback:** Manual review before production

### Security
- **Risk:** Security vulnerabilities in production
- **Mitigation:** HORDE-SECURITY review, penetration testing
- **Fallback:** Staged rollout with monitoring

## Next Steps

### Immediate Actions (Day 0)
1. Create skill files in `.windsurf/skills/`
2. Create workflow files in `.windsurf/workflows/`
3. Run `make skills-install`
4. Execute Phase 0 gate review
5. Update PROJECT_MANIFEST.md

### Phase 1 Execution (Days 1-3)
1. Run migrations (HORDE-SCHEMA)
2. Deploy API routes (HORDE-API)
3. Implement MCP tools
4. Run HORDE-EVAL tests
5. Run HORDE-AUDIT gate

### Phase 2-5 Execution (Days 4-16)
1. Follow systematic execution plan
2. Execute each phase in order
3. Pass all audit gates
4. Update PROJECT_MANIFEST.md after each phase
5. Production deployment after Phase 5

### Final Deliverables
- Full stack deployed to production
- All audit gates passed
- Patent application building functional
- Production-ready system
- Complete documentation
