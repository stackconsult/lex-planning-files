# SECURITY_HEADERS.md — LexCore + LexRadar API Security

> **Build System:** Unified Build System v2  
> **Chunk:** C04 — API Contracts + MCP Tools  
> **Horde:** HORDE-API  
> **Control Plane:** SECURITY  

---

## Overview

All API responses include security headers to protect against common web vulnerabilities. Headers are set at the API gateway (FastAPI middleware) and enforced for all routes.

---

## Required Security Headers

| Header | Value | Purpose | Enforced |
|--------|-------|---------|----------|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | Force HTTPS | Always |
| `X-Content-Type-Options` | `nosniff` | Prevent MIME sniffing | Always |
| `X-Frame-Options` | `DENY` | Prevent clickjacking | Always |
| `X-XSS-Protection` | `1; mode=block` | XSS filter (legacy browsers) | Always |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Limit referrer leakage | Always |
| `Content-Security-Policy` | See below | Prevent XSS, injection | Always |
| `Permissions-Policy` | See below | Restrict browser features | Always |
| `Cache-Control` | `no-store, max-age=0` | Prevent caching of auth responses | Auth endpoints |
| `Cache-Control` | `public, max-age=300` | Allow short cache for public endpoints | Public endpoints |
| `Vary` | `Authorization, Accept-Encoding` | Cache separation by auth | All |

---

## Content Security Policy (CSP)

**API responses** (JSON-only):
```
default-src 'none'; frame-ancestors 'none'; base-uri 'none'
```

**Rationale:** The API returns only JSON. No scripts, styles, images, or frames should ever be loaded. `default-src 'none'` blocks everything. `frame-ancestors 'none'` prevents clickjacking via iframes. `base-uri 'none'` prevents base tag injection.

---

## Permissions Policy

```
accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()
```

**Rationale:** The API has no need for browser hardware features. Disable all to prevent abuse via malicious HTML embedding of API responses.

---

## CORS Policy

```python
CORS_ALLOWED_ORIGINS = [
    "https://app.lexcore.com",
    "https://portal.lexradar.com",
    "https://lexcore.com",
    "https://lexradar.com",
]

CORS_ALLOWED_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

CORS_ALLOWED_HEADERS = [
    "Authorization",
    "Content-Type",
    "X-Request-ID",
    "X-Correlation-ID",
]

CORS_MAX_AGE = 86400  # 24 hours preflight cache
CORS_SUPPORTS_CREDENTIALS = True  # Allow cookies / auth headers
```

**Implementation:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_methods=CORS_ALLOWED_METHODS,
    allow_headers=CORS_ALLOWED_HEADERS,
    max_age=CORS_MAX_AGE,
    allow_credentials=CORS_SUPPORTS_CREDENTIALS,
)
```

**Security Notes:**
- Never use `allow_origins=["*"]` with `allow_credentials=True` — this creates a credential leak vulnerability
- Always validate the `Origin` header against the allowlist
- For local development, `localhost:3000` is allowed only in development environment

---

## Trusted Host Validation

```python
ALLOWED_HOSTS = [
    "api.lexcore.com",
    "api.lexradar.com",
    "localhost",  # Dev only
]

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=ALLOWED_HOSTS,
)
```

**Purpose:** Prevent Host header injection attacks (cache poisoning, password reset link manipulation).

---

## Request ID / Correlation ID

Every request must carry a unique correlation ID for tracing:

```python
# Client may provide X-Correlation-ID; if missing, server generates one
correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
request.state.correlation_id = correlation_id
response.headers["X-Correlation-ID"] = correlation_id
```

**Propagation:**
- API → Services: `correlation_id` passed in function calls
- API → External APIs: `X-Correlation-ID` header forwarded
- API → Redis: `correlation_id` included in cache keys (for debugging)
- API → Database: `correlation_id` logged in query comments

---

## Security Headers Middleware Implementation

```python
class SecurityHeadersMiddleware:
    """Add security headers to all responses."""
    
    SECURITY_HEADERS = {
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
        "Permissions-Policy": "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()",
        "Vary": "Authorization, Accept-Encoding",
    }
    
    async def __call__(self, request: Request, call_next):
        response = await call_next(request)
        
        for header, value in self.SECURITY_HEADERS.items():
            response.headers[header] = value
        
        # Cache-Control: no-store for auth endpoints, short cache for public
        if request.url.path.startswith("/v1/auth"):
            response.headers["Cache-Control"] = "no-store, max-age=0, must-revalidate"
        elif request.url.path.startswith("/v1/mcp/capabilities"):
            response.headers["Cache-Control"] = "public, max-age=300"
        else:
            response.headers["Cache-Control"] = "no-store, max-age=0"
        
        return response
```

---

## TLS Configuration

### Server-Side TLS
- **Minimum TLS version:** 1.3 (TLS 1.2 allowed for older clients with strong cipher suites)
- **Certificate:** Let's Encrypt (staging) / ACM (production)
- **HSTS:** `max-age=31536000; includeSubDomains; preload`
- **Certificate rotation:** Automated via cert-manager (Kubernetes) / ACM auto-renewal

### Cipher Suites (TLS 1.2 fallback)
```
TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256
```

### Client Certificate Authentication
Not used in MVP. Mutual TLS (mTLS) deferred to Enhancement Loop for enterprise integrations.

---

## Security Scanner Integration

| Scanner | Stage | Threshold |
|---------|-------|-----------|
| `gitleaks` | Pre-commit | Zero secrets in code |
| `bandit` | CI (Python) | Medium severity max |
| `semgrep` | CI (Python/TS) | Medium severity max |
| `trivy` | CI (Docker/Deps) | High severity max |
| `npm audit` | CI (Frontend) | High severity max |
| `pip-audit` | CI (Python) | High severity max |

---

## OWASP Top 10 Mitigations

| Risk | Mitigation | Verification |
|------|-----------|------------|
| Broken Access Control | RLS + JWT claims + middleware order | HORDE-AUDIT L3 checks |
| Cryptographic Failures | TLS 1.3, AES-256-S3, bcrypt passwords, Vault secrets | HORDE-AUDIT L3 checks |
| Injection | Parameterized queries, Pydantic validation, CSP | HORDE-AUDIT L3 checks |
| Insecure Design | Defense-in-depth tenant isolation, BAM routing | Architecture review |
| Security Misconfiguration | Terraform IaC, security headers, HSTS | CI security scan |
| Vulnerable Components | Dependabot, pip-audit, npm audit, trivy | CI dependency audit |
| Auth Failures | Clerk SSO, JWT with refresh rotation, rate limiting | HORDE-AUDIT L3 checks |
| Software Integrity | verify_bundle() after store, artifact signing | HORDE-AUDIT L3 checks |
| Logging Failures | structlog JSON, no PII, audit_log table | HORDE-AUDIT L3 checks |
| SSRF | URL validation on external API calls, egress rules | HORDE-AUDIT L3 checks |

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-29 | Initial security headers specification | C04 API contracts definition |
