# HORDE-AUDIT: Verification + Enhancement Architecture

**Horde ID:** HORDE-AUDIT
**Owner:** EN-01 + EN-06 (Chief Architect + Infra Lead)
**Status:** ✅ ACTIVE (runs after every horde completion)
**Phase:** Continuous across all phases (P0-P5)

---

## Core Mandate

> **Trust nothing. Verify everything.**

HORDE-AUDIT does not build. It does not fix. It runs **143 checks across 5 layers**, writes a signed report, assigns fixes back to the originating horde, and re-audits until every critical is resolved. Only then does it authorize the phase gate.

---

## Role Separation — Why It Works

The coding hordes and the audit horde operate in completely separate concerns. A horde that builds its own tests and verifies its own output is not verification — it is theater. HORDE-AUDIT reads the same machine spec files the coding horde read, then independently validates that what was built matches what was specified.

The feedback loop is a closed circuit with no shortcuts:

```
HORDE-BUILD (reads spec → writes code) 
    → HORDE-AUDIT (reads spec → audits output → writes signed report)
        → FINDING (assigns fix back to HORDE-BUILD)
            → HORDE-BUILD (fixes + resubmits)
                → HORDE-AUDIT (re-audits → gate decision)
                    → PASS → Phase gate authorizes
                    → FAIL → Loop continues until all criticals resolved
```

---

## The 5-Layer Audit Stack

Every horde gets audited on the layers that are relevant to what it built — not all 5 for everyone.

### L1 — Contract Compliance
**Applies to:** Every horde, no exceptions.

The source of truth is the machine spec files in `output/lexradar/`. If the spec says a table has a BAM dual-key column and the migration doesn't have it, that is a **CRITICAL** finding. The audit does not care why — it is **BLOCKED** until fixed.

**Checks per horde:**
- Verify all output files match spec definitions
- Verify all function signatures match spec contracts
- Verify all database schemas match ERD
- Verify all API routes match OpenAPI spec
- Verify all dependencies match dependency graph
- Verify no unauthorized modifications to PROJECT_MANIFEST.md

**Severity mapping:**
- MISSING_CRITICAL_SPEC_ITEM → CRITICAL → Blocks gate
- MISMATCH_IN_SPEC → HIGH → Must fix before next phase
- MISSING_MINOR_DETAIL → MEDIUM → Must fix before production
- TYPO_OR_FORMATTING → LOW → Track, fix in next iteration

### L2 — Test Coverage
**Applies to:** All hordes that produce code (HORDE-SCHEMA, HORDE-API, HORDE-INGEST, HORDE-AGENTS, HORDE-SCORING, HORDE-LEDGER, HORDE-PORTAL, HORDE-EVAL)

Enforces that every code path is covered at **80%+** and that no tests are empty or trivially passing.

**CRITICAL finding:** A test with `assert True` is worse than no test because it creates false confidence. Immediate block.

**Checks:**
- Coverage ≥ 80% for all new code
- No empty test bodies
- No `assert True` or `assert False` without logic
- All test assertions must be meaningful
- Integration tests must use real (not mocked) external services where applicable
- All edge cases must have tests

### L3 — Security / Guardrail Enforcement
**Applies to:** All hordes (continuously from P0)

Zero-tolerance. All **33 guardrails** are checked against the actual code via automated scans — not by reading the code and agreeing it looks compliant.

**Automated checks:**
- **BYOK test:** Runs actual encryption, revokes Vault access, attempts decryption — **must fail**
- **On-chain IP content check:** Reads actual Polygon tx payload — must contain only SHA-256 hashes, never plaintext IP
- **Tenant isolation:** Runs RLS bypass attempts against actual database
- **Secret scanning:** No hardcoded API keys, passwords, or tokens
- **Dependency vulnerability:** No HIGH or CRITICAL CVEs in dependencies
- **Auto-filing detection:** Scans for any code path that auto-submits to patent offices (IP-G7 violation)
- **Agent direct import:** Scans for any agent importing another agent directly (AGT-G1 violation)
- **Bundle integrity:** `verify_bundle()` must be called after every bundle store operation

### L4 — Eval Judge Scores
**Applies to:** HORDE-AGENTS and HORDE-EVAL

Runs against every agent horde. Runs `ToolCallJudge`, `GroundingJudge`, adversarial cases, and regression against the previous build.

**Thresholds:**
- ToolCallJudge ≥ 0.90 (agent does not merge if below)
- GroundingJudge ≥ 0.85 (disclosure saved as draft, never reaches attorney)
- Adversarial case pass rate ≥ 0.85
- Regression: no score degradation from previous build

**CRITICAL:** A score below threshold means the agent does not ship — not even to the next phase.

### L5 — Documentation Completeness
**Applies to:** HORDE-ARCH, HORDE-PORTAL, HORDE-DOCS

Missing docstrings on public functions and missing runbooks are **HIGH** findings — they block production deploy even if they don't block the next phase.

**Checks:**
- All public functions have docstrings with parameters and return types
- All API endpoints have documentation
- All runbooks exist and are current
- All ADRs (Architecture Decision Records) are written and signed
- All environment setup instructions are tested and verified

---

## Check Distribution Per Horde

| Horde | L1 | L2 | L3 | L4 | L5 | Total Checks | Criticals |
|-------|----|----|----|----|----|-------------|-----------|
| HORDE-ARCH | ✅ | ❌ | ❌ | ❌ | ✅ | 11 | 3 |
| HORDE-SCHEMA | ✅ | ✅ | ✅ | ❌ | ❌ | 14 | 4 |
| HORDE-INGEST | ✅ | ✅ | ✅ | ❌ | ❌ | 14 | 4 |
| HORDE-API | ✅ | ✅ | ✅ | ❌ | ❌ | 16 | 4 |
| **HORDE-AGENTS** | ✅ | ✅ | ✅ | ✅ | ❌ | **20** | **5** |
| HORDE-SCORING | ✅ | ✅ | ❌ | ✅ | ❌ | 12 | 4 |
| HORDE-LEDGER | ✅ | ✅ | ✅ | ❌ | ❌ | 15 | 4 |
| HORDE-PORTAL | ✅ | ✅ | ✅ | ❌ | ✅ | 18 | 4 |
| HORDE-EVAL | ✅ | ✅ | ❌ | ❌ | ❌ | 9 | 3 |
| HORDE-INFRA | ✅ | ✅ | ✅ | ❌ | ❌ | 14 | 4 |
| HORDE-SECURITY | ✅ | ❌ | ✅ | ❌ | ❌ | 8 | 3 |
| HORDE-DISCLOSURE | ✅ | ✅ | ✅ | ❌ | ❌ | 12 | 4 |
| HORDE-DOCS | ✅ | ❌ | ❌ | ❌ | ✅ | 5 | 2 |
| **HORDE-AUDIT** | ✅ | ✅ | ✅ | ❌ | ✅ | 14 | 3 |
| **TOTAL** | | | | | | **162** | **47** |

HORDE-AGENTS carries the highest load because it sits at the intersection of contract compliance, test coverage, all security guardrails, AND eval quality — it is the layer that is most exposed to cascading failure if any check slips.

---

## The 39 Critical Failure Conditions

Every horde has between 2–5 hard-stop conditions that instantly block the phase gate with no negotiation.

### System-Wide Criticals (5)

| ID | Condition | Severity | Violation |
|----|-----------|----------|-----------|
| SYS-CRIT-01 | Raw IP content in Polygon tx payload | CRITICAL | IP-G1 violated |
| SYS-CRIT-02 | Auto-filing code path exists anywhere | CRITICAL | IP-G7 violated |
| SYS-CRIT-03 | Agent imports another agent directly | CRITICAL | AGT-G1 violated |
| SYS-CRIT-04 | `test_byok` fails — LexRadar can decrypt without Vault | CRITICAL | SEC-G2 violated |
| SYS-CRIT-05 | `verify_bundle()` missing or not called after bundle store | CRITICAL | Integrity chain broken |

### HORDE-ARCH Criticals (3)

| ID | Condition | Severity |
|----|-----------|----------|
| ARCH-CRIT-01 | Spec files missing or corrupted | CRITICAL |
| ARCH-CRIT-02 | PROJECT_MANIFEST.md hash mismatch | CRITICAL |
| ARCH-CRIT-03 | Dependency graph contains cycles | CRITICAL |

### HORDE-SCHEMA Criticals (4)

| ID | Condition | Severity |
|----|-----------|----------|
| SCHEMA-CRIT-01 | Migration fails on fresh database | CRITICAL |
| SCHEMA-CRIT-02 | RLS policies missing on tenant tables | CRITICAL |
| SCHEMA-CRIT-03 | pgvector extension not installed | CRITICAL |
| SCHEMA-CRIT-04 | BAM dual-key column missing from tables | CRITICAL |

### HORDE-API Criticals (4)

| ID | Condition | Severity |
|----|-----------|----------|
| API-CRIT-01 | MCP tool schema validation fails | CRITICAL |
| API-CRIT-02 | API route returns wrong status code per spec | CRITICAL |
| API-CRIT-03 | Authentication middleware missing | CRITICAL |
| API-CRIT-04 | Rate limiting not enforced | CRITICAL |

### HORDE-AGENTS Criticals (5)

| ID | Condition | Severity |
|----|-----------|----------|
| AGT-CRIT-01 | ToolCallJudge < 0.90 | CRITICAL |
| AGT-CRIT-02 | GroundingJudge < 0.85 | CRITICAL |
| AGT-CRIT-03 | Agent directly imports another agent | CRITICAL |
| AGT-CRIT-04 | Empty test body or `assert True` test found | CRITICAL |
| AGT-CRIT-05 | Auto-filing code path detected | CRITICAL |

### HORDE-LEDGER Criticals (4)

| ID | Condition | Severity |
|----|-----------|----------|
| LEDGER-CRIT-01 | SHA-256 hash not matching file content | CRITICAL |
| LEDGER-CRIT-02 | Polygon tx not confirmed within 30 blocks | CRITICAL |
| LEDGER-CRIT-03 | AES-256 encryption not used | CRITICAL |
| LEDGER-CRIT-04 | BYOK test fails | CRITICAL |

### HORDE-INFRA Criticals (4)

| ID | Condition | Severity |
|----|-----------|----------|
| INFRA-CRIT-01 | Terraform plan shows destructive changes | CRITICAL |
| INFRA-CRIT-02 | Security group allows 0.0.0.0/0 ingress | CRITICAL |
| INFRA-CRIT-03 | Database password in plaintext | CRITICAL |
| INFRA-CRIT-04 | No backup strategy defined | CRITICAL |

### HORDE-PORTAL Criticals (4)

| ID | Condition | Severity |
|----|-----------|----------|
| PORTAL-CRIT-01 | XSS vulnerability in user input | CRITICAL |
| PORTAL-CRIT-02 | CSRF protection missing | CRITICAL |
| PORTAL-CRIT-03 | Tenant isolation bypass in UI | CRITICAL |
| PORTAL-CRIT-04 | Missing runbook for deployment | CRITICAL |

### HORDE-EVAL Criticals (3)

| ID | Condition | Severity |
|----|-----------|----------|
| EVAL-CRIT-01 | Golden set test coverage < 90% | CRITICAL |
| EVAL-CRIT-02 | Judge configuration drift from spec | CRITICAL |
| EVAL-CRIT-03 | Regression test not run before approval | CRITICAL |

### HORDE-SECURITY Criticals (3)

| ID | Condition | Severity |
|----|-----------|----------|
| SEC-CRIT-01 | HIGH or CRITICAL CVE in dependency | CRITICAL |
| SEC-CRIT-02 | RLS audit test fails | CRITICAL |
| SEC-CRIT-03 | Secret scanning finds exposed credential | CRITICAL |

### HORDE-DISCLOSURE Criticals (4)

| ID | Condition | Severity |
|----|-----------|----------|
| DISC-CRIT-01 | Grounding score < 0.85 on approved disclosure | CRITICAL |
| DISC-CRIT-02 | Missing required LHP section | CRITICAL |
| DISC-CRIT-03 | Claim theme not supported by description | CRITICAL |
| DISC-CRIT-04 | Attorney approval bypass detected | CRITICAL |

### HORDE-DOCS Criticals (2)

| ID | Condition | Severity |
|----|-----------|----------|
| DOCS-CRIT-01 | Missing runbook for critical operation | CRITICAL |
| DOCS-CRIT-02 | API documentation out of sync with implementation | CRITICAL |

---

## Audit Report Format

### Signed Report Structure

```
AUDIT REPORT — HORDE-AUDIT
Report ID: AUDIT-{HORDE_ID}-{PHASE}-{TIMESTAMP}
Report Hash: SHA-256 of report content
Signed By: EN-01 + EN-06 (dual signature required)
Date: YYYY-MM-DDTHH:MM:SSZ

=== EXECUTIVE SUMMARY ===
Target Horde: {HORDE_ID}
Target Phase: {PHASE}
Total Checks: {N}
Passed: {N}
Failed: {N}
Critical Findings: {N}
High Findings: {N}
Medium Findings: {N}
Low Findings: {N}
Gate Decision: PASS / BLOCKED

=== L1: CONTRACT COMPLIANCE ===
- Check 1: [PASS/FAIL] {description}
- Check 2: [PASS/FAIL] {description}
...

=== L2: TEST COVERAGE ===
- Coverage: {X}%
- Check 1: [PASS/FAIL] {description}
...

=== L3: SECURITY / GUARDRAIL ENFORCEMENT ===
- BYOK Test: [PASS/FAIL]
- RLS Audit: [PASS/FAIL]
- CVE Scan: [PASS/FAIL]
- Auto-filing Scan: [PASS/FAIL]
- Agent Import Scan: [PASS/FAIL]
- Secret Scan: [PASS/FAIL]
...

=== L4: EVAL JUDGE SCORES ===
- ToolCallJudge: {score} [PASS/FAIL]
- GroundingJudge: {score} [PASS/FAIL]
- Adversarial Pass Rate: {score} [PASS/FAIL]
- Regression: [PASS/FAIL]
...

=== L5: DOCUMENTATION COMPLETENESS ===
- Docstring Coverage: {X}%
- Runbooks Present: [PASS/FAIL]
- ADRs Current: [PASS/FAIL]
...

=== FIX ASSIGNMENTS ===
[For each finding]
- Finding ID: {ID}
- Severity: {CRITICAL/HIGH/MEDIUM/LOW}
- Assigned To: {HORDE_ID}
- File: {path}
- Line: {number}
- Description: {detail}
- Verification Command: {command}
- Deadline: {date}

=== SIGNATURES ===
Signature 1 (EN-01): {GPG signature}
Signature 2 (EN-06): {GPG signature}
```

---

## Fix Assignment Protocol

1. **Critical findings** → Immediate assignment to originating horde
2. **High findings** → Assignment with 48-hour deadline
3. **Medium findings** → Assignment with 7-day deadline
4. **Low findings** → Batch assignment for next iteration

**Re-audit trigger:**
- Every fix submission triggers a targeted re-audit of only the changed files
- Full re-audit only when all findings from previous report are resolved
- If re-audit finds new issues, process restarts

---

## Gate Authorization Protocol

**PASS conditions:**
- Zero critical findings
- Zero high findings (unless explicitly waived by EN-01 with documented reason)
- All medium findings have assigned fixes with deadlines
- All eval judge scores ≥ thresholds

**BLOCKED conditions:**
- Any critical finding
- Any high finding without approved waiver
- ToolCallJudge < 0.90
- GroundingJudge < 0.85
- BYOK test failure
- RLS audit failure
- Any auto-filing or agent import violation

---

## Integration with Phase Execution

HORDE-AUDIT runs at the end of every phase:

| Phase | Hordes Audited | Gate Decision |
|-------|---------------|---------------|
| P0 | HORDE-ARCH, HORDE-INFRA, HORDE-SECURITY | Authorizes P1 start |
| P1 | HORDE-SCHEMA, HORDE-API, HORDE-INGEST, HORDE-EVAL | Authorizes P2 start |
| P2 | HORDE-AGENTS, HORDE-SCORING, HORDE-DISCLOSURE, HORDE-EVAL | Authorizes P3 start |
| P3 | HORDE-LEDGER, HORDE-AGENTS, HORDE-INFRA, HORDE-EVAL | Authorizes P4 start |
| P4 | HORDE-PORTAL, HORDE-API, HORDE-SECURITY, HORDE-EVAL, HORDE-DOCS | Authorizes P5 start |
| P5 | HORDE-EVAL, HORDE-INFRA, HORDE-SECURITY, HORDE-DOCS, HORDE-SCHEMA | Authorizes production |

---

## HORDE-AUDIT Self-Audit

HORDE-AUDIT must also be audited. This is done by:
1. Running HORDE-AUDIT's own checks against itself (meta-audit)
2. EN-01 performs spot checks on 10% of audit reports
3. Cross-validation: Two independent audit runs on the same output must match

---

## Memory Rule

> **Rule:** HORDE-AUDIT must run after every horde completes its phase work. No phase gate is authorized without HORDE-AUDIT approval. Cascade will automatically load the HORDE_AUDIT_WORKFLOW.md after any horde claims completion.
