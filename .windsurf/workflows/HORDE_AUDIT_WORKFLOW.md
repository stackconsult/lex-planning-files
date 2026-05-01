# HORDE-AUDIT WORKFLOW.md

**Horde:** HORDE-AUDIT
**Phase:** All phases (continuous)
**Purpose:** Trust nothing, verify everything. Run 143 checks across 5 layers.

---

## READ ← Specifications to Load First

1. Load `docs/HORDE-AUDIT_ARCHITECTURE.md` — 5-layer audit stack definitions
2. Load `PROJECT_MANIFEST.md` — target horde's contract and dependencies
3. Load target horde's spec files from `output/lexradar/` — machine specs the coding horde read
4. Load target horde's output files — what was actually built
5. Load `SPEC_HASHES.md` — verify no unauthorized spec modifications

---

## BUILD ← Exact Audit Procedure

### Step 1: Identify Target Horde
```
Target Horde: {HORDE_ID}
Target Phase: {PHASE}
Target Files: {output files from PROJECT_MANIFEST.md Completed Outputs}
```

### Step 2: Run Layer 1 — Contract Compliance
```bash
# Verify every output file matches spec
# Verify all function signatures match spec contracts
# Verify all database schemas match ERD_COMPLETE.dbml
# Verify all API routes match openapi.yaml
# Verify all dependencies match dependency_graph.dot
```
- For each spec file, check every claim against actual output
- Mark CRITICAL if spec mismatch found
- Mark CRITICAL if file missing that spec requires
- Mark HIGH if file present but missing spec-required field

### Step 3: Run Layer 2 — Test Coverage
```bash
# Run test suite for target horde
# Verify coverage ≥ 80%
# Check for empty test bodies (assert True)
# Check for meaningful assertions
# Run integration tests against real services
```
- CRITICAL if coverage < 80%
- CRITICAL if any empty test body found
- HIGH if integration tests use mocks where real services should be used

### Step 4: Run Layer 3 — Security / Guardrail Enforcement
```bash
# Run BYOK test: encrypt with Vault, revoke access, attempt decrypt (must fail)
# Run on-chain IP content check: verify Polygon tx contains only SHA-256 hashes
# Run tenant isolation test: RLS bypass attempts
# Run secret scanning: no hardcoded credentials
# Run dependency vulnerability scan: no HIGH/CRITICAL CVEs
# Run auto-filing detection: scan for patent submission code paths
# Run agent import detection: scan for agent importing another agent
# Run bundle integrity check: verify_bundle() after every store operation
```
- CRITICAL if BYOK test fails (LexRadar can decrypt without Vault)
- CRITICAL if plaintext IP content found in Polygon tx
- CRITICAL if auto-filing code path detected (IP-G7 violation)
- CRITICAL if agent imports another agent directly (AGT-G1 violation)
- CRITICAL if verify_bundle() missing after store operation
- HIGH if RLS bypass found
- HIGH if secret found in code
- HIGH if HIGH/CRITICAL CVE in dependencies

### Step 5: Run Layer 4 — Eval Judge Scores (if target horde = HORDE-AGENTS)
```bash
# Run ToolCallJudge on agent test suite
# Run GroundingJudge on disclosure drafts
# Run adversarial test cases
# Run regression tests against previous build
```
- CRITICAL if ToolCallJudge < 0.90
- CRITICAL if GroundingJudge < 0.85
- CRITICAL if adversarial pass rate < 0.85
- CRITICAL if regression shows score degradation

### Step 6: Run Layer 5 — Documentation Completeness (if target horde = HORDE-ARCH/HORDE-PORTAL/HORDE-DOCS)
```bash
# Check docstring coverage on public functions
# Check API endpoint documentation
# Check runbook existence and currency
# Check ADR existence and signatures
# Check environment setup instructions
```
- HIGH if docstring coverage < 80%
- HIGH if runbook missing for critical operation
- HIGH if API docs out of sync with implementation
- MEDIUM if ADR missing for architectural decision

### Step 7: Generate Signed Audit Report

Report ID: `AUDIT-{HORDE_ID}-{PHASE}-{TIMESTAMP}`
Report Hash: SHA-256 of full report content
Format: Follow HORDE-AUDIT_ARCHITECTURE.md Signed Report Structure exactly

---

## GATE ← Boolean Checklist

### Critical Conditions (all must be true)
- [ ] Zero critical findings from any layer
- [ ] All spec files match output exactly
- [ ] Test coverage ≥ 80% (for code-producing hordes)
- [ ] No empty test bodies
- [ ] BYOK test passes (if applicable)
- [ ] No plaintext IP in Polygon tx (if applicable)
- [ ] No auto-filing code paths (IP-G7)
- [ ] No agent direct imports (AGT-G1)
- [ ] ToolCallJudge ≥ 0.90 (for HORDE-AGENTS)
- [ ] GroundingJudge ≥ 0.85 (for HORDE-AGENTS)
- [ ] No HIGH/CRITICAL CVEs in dependencies
- [ ] RLS audit passes
- [ ] verify_bundle() called after every store (if applicable)

### High Conditions (all must be true, or waived by EN-01 with documented reason)
- [ ] All high findings have fix assignments with deadlines
- [ ] No RLS bypass found
- [ ] No secrets in code
- [ ] Integration tests use real services where applicable
- [ ] Docstring coverage ≥ 80% (for doc-producing hordes)

### Medium/Low Conditions (tracked, not blocking)
- [ ] Medium findings have fix assignments
- [ ] Low findings batch-assigned for next iteration

### Authorization
**If all critical conditions pass:**
```
GATE DECISION: PASS
Phase gate authorized for {PHASE}
Authorization hash: {SHA-256 of gate decision}
Signed by: EN-01 + EN-06
```

**If any critical condition fails:**
```
GATE DECISION: BLOCKED
Phase gate NOT authorized
Critical findings must be resolved before re-audit
Fix assignments written to {HORDE_ID} with 48-hour deadline for criticals
Re-audit triggered automatically after fix submission
```

---

## UNBLOCKS

**If PASS:** Target phase can proceed to next phase
**If BLOCKED:** Target horde must fix findings and resubmit for re-audit
**After re-audit PASS:** Phase gate authorized
**After re-audit BLOCKED:** Loop continues until all criticals resolved

---

## CASCADE INSTRUCTION

After any horde claims completion, paste this workflow and specify:

```
Audit {HORDE_ID} output for Phase {PHASE}.
```

Cascade will:
1. Load all spec files for the target horde
2. Run all 5 audit layers (or relevant subset)
3. Generate signed audit report
4. Make gate decision (PASS or BLOCKED)
5. If BLOCKED: write fix assignments with file paths, line numbers, verification commands
6. If PASS: authorize phase gate and update PROJECT_MANIFEST.md

**No phase gate is authorized without HORDE-AUDIT approval.**
