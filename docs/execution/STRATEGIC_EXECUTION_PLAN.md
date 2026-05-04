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
