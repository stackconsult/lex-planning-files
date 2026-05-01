# Security Pipeline Requirements — Phase 0
**HORDE-SECURITY Specification for Chunk 9**

> **Schema Version:** v0.1.0-foundation
> **Created:** 2026-04-29
> **Horde:** HORDE-SECURITY
> **Status:** ⏳ PENDING (requires infrastructure from Chunk 7-8)

---

## Security Pipeline Overview

**Purpose:** Continuous security scanning, BYOK validation, and compliance monitoring
**Trigger:** Every commit to main branch
**Blocking:** Security gate must pass before merge to production

---

## 1. SAST (Static Application Security Testing)

### Tool: Semgrep or SonarQube
**Configuration:**
- Scan on every PR
- Block on HIGH and CRITICAL severity
- Allow MEDIUM with review required
- Custom rules for LexCore-specific patterns

**Rules:**
- No hardcoded secrets (API keys, passwords)
- No SQL injection vulnerabilities
- No XSS vulnerabilities
- No insecure deserialization
- No hardcoded encryption keys
- BYOK compliance (no plaintext keys in code)

**Semgrep Rules Example:**
```yaml
rules:
  - id: no-hardcoded-secrets
    pattern: $KEY = "..."
    message: "No hardcoded secrets allowed"
    severity: ERROR
  - id: no-plaintext-encryption-keys
    pattern: encryption_key = $KEY
    message: "Use Vault Transit engine for encryption keys"
    severity: ERROR
```

---

## 2. DAST (Dynamic Application Security Testing)

### Tool: OWASP ZAP
**Configuration:**
- Run on staging environment
- Automated scan after deployment
- Scan all API endpoints
- Check for common vulnerabilities:
  - SQL injection
  - XSS
  - CSRF
  - Authentication bypass
  - Authorization bypass

**Schedule:**
- Daily automated scans on staging
- Weekly full scan on production
- Manual scan before major releases

---

## 3. Dependency Scanning

### Tool: Snyk or Dependabot
**Configuration:**
- Scan on every PR
- Check for known vulnerabilities (CVEs)
- Block on HIGH and CRITICAL CVEs
- Auto-approve LOW and MEDIUM CVEs with review

**Policy:**
- Update dependencies weekly
- Review CVEs within 24 hours
- Patch HIGH CVEs within 7 days
- Patch CRITICAL CVEs within 48 hours

---

## 4. BYOK (Bring Your Own Key) Test

### Purpose: Verify LexRadar cannot decrypt tenant bundles
**Test Script:**
```python
def test_byok_compliance():
    # 1. Generate tenant-specific key in Vault
    tenant_key = vault.transit.generate_key(tenant_id)
    
    # 2. Encrypt test data with tenant key
    encrypted_data = vault.transit.encrypt(test_data, key=tenant_key)
    
    # 3. Verify LexRadar does not have access to plaintext key
    assert vault.transit.can_decrypt(encrypted_data, key=tenant_key) == True
    assert lexradar_has_plaintext_key(tenant_key) == False
    
    # 4. Verify only tenant can decrypt
    tenant_decrypted = vault.transit.decrypt(encrypted_data, key=tenant_key, context=tenant_context)
    assert tenant_decrypted == test_data
```

**Gate:**
- BYOK test must pass before production deployment
- Test runs on every commit to main
- Test runs on staging environment

---

## 5. RLS (Row-Level Security) Audit

### Purpose: Verify tenant isolation
**Test Script:**
```python
def test_tenant_isolation():
    # 1. Create test tenants
    tenant_a = create_tenant("tenant_a")
    tenant_b = create_tenant("tenant_b")
    
    # 2. Insert data for tenant A
    insert_legal_document(tenant_a, "secret_doc_a")
    
    # 3. Try to access tenant A data as tenant B
    with tenant_context(tenant_b):
        docs = list_legal_documents()
        assert "secret_doc_a" not in docs
    
    # 4. Verify tenant A can access their own data
    with tenant_context(tenant_a):
        docs = list_legal_documents()
        assert "secret_doc_a" in docs
```

**Gate:**
- RLS audit must pass before production deployment
- Test runs on every schema change
- Test runs on staging environment

---

## 6. SOC 2 Control Mapping

### Purpose: Map security controls to SOC 2 requirements
**Controls:**

| SOC 2 Control | Implementation | Status |
|---------------|----------------|--------|
| CC1.1 - Access Control | IAM roles, MFA, SSO | ✅ Implemented |
| CC2.1 - Asset Management | Asset inventory, tagging | ✅ Implemented |
| CC3.1 - Change Management | Git workflow, approvals | ✅ Implemented |
| CC4.1 - Risk Assessment | Security scans, CVE monitoring | ✅ Implemented |
| CC5.1 - Monitoring | Prometheus, Grafana, alerting | ✅ Implemented |
| CC6.1 - Incident Response | Runbooks, PagerDuty | ⏳ Pending |
| CC7.1 - Data Protection | BYOK, encryption at rest/in-transit | ✅ Implemented |

**Documentation:**
- Control mapping document: `docs/soc2_control_mapping.md`
- Evidence collection: Automated via security pipeline
- Annual audit: Scheduled with external auditor

---

## 7. Security Findings Dashboard

### Tool: DefectDojo or custom dashboard
**Metrics:**
- Open vulnerabilities by severity
- CVE trend over time
- BYOK test pass rate
- RLS audit pass rate
- Security gate pass rate

**Alerts:**
- HIGH CVE detected → Slack + PagerDuty
- CRITICAL CVE detected → Slack + PagerDuty (immediate)
- BYOK test failed → Slack + PagerDuty (immediate)
- RLS audit failed → Slack + PagerDuty (immediate)

---

## 8. Incident Response Runbook

### Template: `docs/security_runbooks.md`

**Incident Types:**
1. Data breach
2. Ransomware attack
3. DDoS attack
4. Unauthorized access
5. BYOK key compromise
6. RLS bypass

**Response Steps:**
1. Detect (monitoring alerts)
2. Contain (isolate affected systems)
3. Eradicate (remove threat)
4. Recover (restore from backups)
5. Lessons learned (post-mortem)

**Roles:**
- Incident Commander: EN-07 (Security Lead)
- Technical Lead: EN-06 (Infra Lead)
- Communications: EX-03 (IP Legal Counsel)

---

## Security Gate in CI/CD

### GitHub Actions Workflow
```yaml
name: Security Gate

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: SAST Scan
        run: semgrep --config=auto --severity=ERROR --error
      
      - name: Dependency Scan
        run: snyk test --severity-threshold=high
      
      - name: BYOK Test
        run: pytest tests/security/test_byok.py
      
      - name: RLS Audit
        run: pytest tests/security/test_rls_audit.py
      
      - name: Security Dashboard Update
        run: python scripts/update_security_dashboard.py
```

---

## Next Steps

1. Infrastructure must be provisioned (Chunks 7-8)
2. Install security scanning tools (Semgrep, Snyk, OWASP ZAP)
3. Configure security scanning in CI/CD
4. Write BYOK test script
5. Write RLS audit test script
6. Set up security findings dashboard
7. Create incident response runbooks
8. Complete SOC 2 control mapping
9. Run security pipeline on first commit
10. Verify all gates pass
