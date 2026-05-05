# Security Baseline Governance

> **Chunk:** C04 — Phase 0 Foundation  
> **Horde:** HORDE-SECURITY  
> **Status:** PRODUCTION_READY

## Overview

Security baseline for LexCore + LexRadar with BYOK, audit logging, and guardrails.

## Security Controls

### BYOK (Bring Your Own Key)
- Each tenant uses distinct encryption key
- System default key never encrypts tenant data
- Key rotation leaves immutable audit trail
- Revoked keys immediately block decryption

### Audit Logging
- All data access logged to audit_log table
- Structured JSON logs with correlation IDs
- No PII in logs
- Log retention: 90 days

### Guardrails
- Zero HIGH/CRITICAL CVEs in dependencies
- RLS policies on all tenant tables
- No secrets in code
- TLS 1.3 enforced
- Security headers on all responses

## Security Scanners

| Scanner | Stage | Threshold |
|---------|-------|-----------|
| gitleaks | Pre-commit | Zero secrets |
| bandit | CI | Medium max |
| pip-audit | CI | Zero HIGH |
| trivy | CI | Zero HIGH |

## Governance

- Never overwrite: Additive changes only
- Always append: New controls added
- Track changes: Git commits with format `security: [Team L] Chunk {N}: {description}`
- No bloat: Remove unused controls

## Change History

| Date | Change | Chunk | Team |
|------|--------|-------|------|
| 2026-05-05 | Governance documentation added | Chunk 4 | HORDE-SECURITY |
