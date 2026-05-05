# Security Module

This module implements security baseline for LexCore + LexRadar.

## Components

### BYOK (Bring Your Own Key)
- Tenant-specific encryption keys
- Key rotation with audit trail
- Revoked key blocking

### Audit Logging
- Structured JSON logging
- Correlation ID propagation
- No PII in logs

### Guardrails
- RLS policies enforcement
- Secret scanning
- Dependency vulnerability checks

## Tests

- BYOK tests: `backend/tests/security/test_byok.py`
