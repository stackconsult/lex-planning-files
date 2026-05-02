# Penetration Test Report

**Timestamp**: 2026-05-02T03:00:22.453809Z
**Commit**: d579187
**Status**: PASS
**Risk Score**: 0/100
**Critical Findings**: 0
**High Findings**: 0

## Per-Vector Results
- **AUTH**: 1/1 — PASS
- **JWT**: 3/3 — PASS
- **RLS**: 4/4 — PASS
- **SECRETS**: 2/2 — PASS
- **INJECTION**: 2/2 — PASS
- **BLOCKCHAIN**: 3/3 — PASS
- **HEADERS**: 2/2 — PASS
- **DEPENDENCIES**: 1/1 — PASS

## Detailed Checks
- `MC1-01` (AUTH): Staging deploy report exists — **PASS** [INFO] Report found: True
- `JWT-01` (JWT): Public paths explicitly whitelisted — **PASS** [HIGH] public_paths defined: True
- `JWT-02` (JWT): Non-public routes require authentication — **PASS** [CRITICAL] Auth middleware enforced: True
- `JWT-03` (JWT): No unconditional bypass paths — **PASS** [CRITICAL] Unconditional bypass paths found: 0
- `RLS-01` (RLS): RLS policies defined in migration — **PASS** [CRITICAL] RLS policies found: True
- `RLS-02` (RLS): Tenant filter in RLS policies — **PASS** [CRITICAL] Tenant filter found: True
- `RLS-03` (RLS): Row Level Security enabled — **PASS** [CRITICAL] RLS enabled: True
- `RLS-04` (RLS): Services reference tenant_id — **PASS** [HIGH] Services with tenant_id: 3/3
- `SEC-01` (SECRETS): No hardcoded secrets in source — **PASS** [CRITICAL] Findings: 0
- `SEC-02` (SECRETS): Staging env uses placeholder secrets — **PASS** [INFO] Placeholder markers: 4
- `INJ-01` (INJECTION): No f-string SQL construction — **PASS** [CRITICAL] SQL injection risks: 0
- `INJ-02` (INJECTION): No raw HTML output with user input — **PASS** [HIGH] XSS risks: 0
- `ONC-01` (BLOCKCHAIN): Ledger uses hashlib for hashing — **PASS** [CRITICAL] hashlib usage: True
- `ONC-02` (BLOCKCHAIN): No raw claims in ledger without hashing — **PASS** [CRITICAL] No raw claims: True
- `ONC-03` (BLOCKCHAIN): verify_bundle() exists for integrity — **PASS** [HIGH] verify_bundle found: True
- `HDR-01` (HEADERS): All required security headers documented — **PASS** [HIGH] Headers found: 7/7
- `HDR-02` (HEADERS): CORS middleware configured — **PASS** [MEDIUM] CORS configured: True
- `CVE-01` (DEPENDENCIES): No known CVEs in requirements — **PASS** [HIGH] Known CVE matches: 0

## Report Signature
SHA-256: `ddfd78c977185c59eac30be7e7650e35f179f8339df7b2be59a7bcca63c2739e`