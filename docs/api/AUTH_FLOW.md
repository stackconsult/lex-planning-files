# AUTH_FLOW.md — LexCore + LexRadar Authentication & Authorization

> **Build System:** Unified Build System v2  
> **Chunk:** C04 — API Contracts + MCP Tools  
> **Horde:** HORDE-API  
> **Control Plane:** SECURITY  

---

## Overview

LexCore + LexRadar uses a dual authentication system:

1. **Primary Auth (Frontend):** Clerk — Modern React SSO with OAuth (Google, GitHub), SAML-ready, MFA
2. **Secondary Auth (API/M2M):** JWT with refresh token rotation — For API keys, machine-to-machine, attorney portal

All authentication flows enforce **defense-in-depth tenant isolation** at every layer.

---

## Authentication Flows

### Flow 1: Frontend User Sign-In (Clerk)

```
┌─────────────┐     ┌──────────┐     ┌──────────┐     ┌─────────┐
│   User      │     │  Clerk   │     │  Next.js │     │ FastAPI │
│  (Browser)  │     │  (OAuth) │     │  (App)   │     │  (API)  │
└──────┬──────┘     └────┬─────┘     └────┬─────┘     └────┬────┘
       │                 │                │                │
       │ 1. Click Sign In │                │                │
       │─────────────────>│                │                │
       │                  │                │                │
       │ 2. OAuth redirect │                │                │
       │<─────────────────│                │                │
       │                  │                │                │
       │ 3. Complete OAuth │                │                │
       │─────────────────>│                │                │
       │                  │                │                │
       │ 4. Session cookie + JWT │        │                │
       │<─────────────────│                │                │
       │                  │                │                │
       │ 5. API request with JWT in Authorization header
       │──────────────────────────────────>│                │
       │                  │                │                │
       │                  │                │ 6. Validate JWT │
       │                  │                │────────────────>│
       │                  │                │                │
       │                  │                │ 7. Extract claims
       │                  │                │<────────────────│
       │                  │                │                │
       │                  │                │ 8. Set tenant_id
       │                  │                │────────────────>│
       │                  │                │                │
       │                  │                │ 9. Return data  │
       │                  │                │<────────────────│
       │                  │                │                │
       │ 10. Render page  │                │                │
       │<──────────────────────────────────│                │
```

**JWT Claims (Clerk-issued):**
```json
{
  "sub": "user_clerk_id_123",
  "tid": "550e8400-e29b-41d4-a716-446655440000",
  "tier": "FIRM",
  "role": "admin",
  "email": "user@example.com",
  "iat": 1714399200,
  "exp": 1714402800,
  "jti": "unique_token_id"
}
```

---

### Flow 2: API Key Authentication (Machine-to-Machine)

```
┌─────────────┐     ┌──────────┐     ┌──────────┐     ┌─────────┐
│   Client    │     │ FastAPI  │     │  Redis   │     │   PG    │
│  (Script)   │     │  (API)   │     │  (Cache) │     │ (DB)    │
└──────┬──────┘     └────┬─────┘     └────┬─────┘     └────┬────┘
       │                 │                │                │
       │ 1. POST /v1/auth/token
       │   {api_key: "lex_tenant_123456..."}
       │─────────────────>│                │                │
       │                  │                │                │
       │                  │ 2. Validate key format
       │                  │                │                │
       │                  │ 3. Hash key, lookup in DB
       │                  │──────────────────────────────────>│
       │                  │                │                │
       │                  │ 4. Return tenant_id, tier, scopes
       │                  │<──────────────────────────────────│
       │                  │                │                │
       │                  │ 5. Generate JWT pair
       │                  │                │                │
       │                  │ 6. Store refresh token hash in Redis
       │                  │────────────────>│                │
       │                  │                │                │
       │ 7. Return access_token + refresh_token
       │<─────────────────│                │                │
       │                  │                │                │
       │ 8. Use access_token in Authorization: Bearer header
       │─────────────────>│                │                │
       │                  │                │                │
       │                  │ 9. Validate JWT, extract claims
       │                  │                │                │
       │                  │ 10. Set tenant_id for RLS
       │                  │                │                │
       │ 11. Return API data│                │                │
       │<─────────────────│                │                │
```

**API Key Format:**
```
lex_{tenant_id_prefix}_{random_32}
Example: lex_550e84_1234567890abcdef1234567890abcdef
```

**Token Exchange Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "read write"
}
```

---

### Flow 3: Token Refresh

```
┌─────────────┐     ┌──────────┐     ┌──────────┐     ┌─────────┐
│   Client    │     │ FastAPI  │     │  Redis   │     │   PG    │
│  (Script)   │     │  (API)   │     │ (Blacklist)│    │ (DB)    │
└──────┬──────┘     └────┬─────┘     └────┬─────┘     └────┬────┘
       │                 │                │                │
       │ 1. POST /v1/auth/refresh
       │   {refresh_token: "eyJ..."}
       │─────────────────>│                │                │
       │                  │                │                │
       │                  │ 2. Check blacklist in Redis
       │                  │────────────────>│                │
       │                  │                │                │
       │                  │ 3. Validate JWT (signature + expiry)
       │                  │                │                │
       │                  │ 4. Generate new JWT pair
       │                  │                │                │
       │                  │ 5. Blacklist old refresh token
       │                  │────────────────>│                │
       │                  │                │                │
       │                  │ 6. Store new refresh token hash
       │                  │────────────────>│                │
       │                  │                │                │
       │ 7. Return new access_token + refresh_token
       │<─────────────────│                │                │
```

**Refresh Token Rotation:**
- Each refresh returns a **new** refresh token
- Old refresh token is immediately blacklisted in Redis (TTL = 7 days)
- Blacklist checked on every refresh request
- If old refresh token is used → `REFRESH_TOKEN_REVOKED` (401)

---

### Flow 4: Attorney Portal Scoped JWT

```
┌─────────────┐     ┌──────────┐     ┌──────────┐     ┌─────────┐
│  Attorney   │     │  Email   │     │  Portal  │     │ FastAPI │
│   (Email)   │     │  (Link)  │     │  (Web)   │     │  (API)  │
└──────┬──────┘     └────┬─────┘     └────┬─────┘     └────┬────┘
       │                 │                │                │
       │ 1. Receive handoff email
       │<─────────────────│                │                │
       │                  │                │                │
       │ 2. Click portal link (contains scoped JWT)
       │───────────────────────────────────>│                │
       │                  │                │                │
       │                  │                │ 3. Validate scoped JWT
       │                  │                │────────────────>│
       │                  │                │                │
       │                  │                │ 4. Check expiry (48h)
       │                  │                │                │
       │                  │                │ 5. Check scope (handoff:read)
       │                  │                │                │
       │                  │                │ 6. Return handoff data
       │                  │                │<────────────────│
       │                  │                │                │
       │ 7. Display handoff │                │                │
       │<───────────────────────────────────│                │
       │                  │                │                │
       │ 8. Attorney edits claims, reviews evidence
       │───────────────────────────────────>│                │
       │                  │                │                │
       │                  │                │ 9. Save draft (auto-save)
       │                  │                │────────────────>│
       │                  │                │                │
       │ 10. Attorney clicks Approve
       │───────────────────────────────────>│                │
       │                  │                │                │
       │                  │                │ 11. POST review action
       │                  │                │────────────────>│
       │                  │                │                │
       │                  │                │ 12. Update disclosure status
       │                  │                │                │
       │                  │                │ 13. Notify client
       │                  │                │                │
       │ 14. Confirmation page│              │                │
       │<───────────────────────────────────│                │
```

**Scoped JWT Claims (Attorney Portal):**
```json
{
  "sub": "patents@lawfirm.com",
  "tid": "550e8400-e29b-41d4-a716-446655440000",
  "handoff_id": "550e8400-e29b-41d4-a716-446655440001",
  "scope": "handoff:read handoff:edit handoff:action",
  "iat": 1714399200,
  "exp": 1714831200,  // 48 hours from issuance
  "jti": "unique_token_id",
  "iss": "lexradar"
}
```

**Scope Breakdown:**
- `handoff:read` — View handoff package (all 10 sections, evidence chain, prior art)
- `handoff:edit` — Edit 3 editable sections (claims, detailed description, abstract)
- `handoff:action` — Approve / Reject / Request Changes

**Token Lifecycle:**
- Issued: On handoff delivery (email sent)
- Expires: 48 hours from issuance
- Auto-save: Every 30 seconds during editing
- Refresh: Not available — single-use token
- Invalidation: On Approve/Reject/Request Changes (token consumed)

---

## Authorization Model

### Role-Based Access Control (RBAC)

| Role | Description | Permissions |
|------|-------------|-------------|
| `admin` | Full tenant administrator | All operations |
| `member` | Standard team member | Read all, write most (no admin settings) |
| `viewer` | Read-only access | Read all, no write |

**Role Assignment:**
- SOLO: Single user, always `admin`
- FIRM: First user is `admin`, can invite `member` and `viewer`
- ENTERPRISE: First user is `admin`, can assign any role, custom roles deferred to LOOP

### Resource-Level Permissions

Stored in `roles_permissions` table:
```json
{
  "resource": "legal_documents|monitor_rules|invention_candidates|disclosures|filing_bundles",
  "action": "read|write|delete|admin",
  "scope": "tenant|workspace|user"
}
```

### Middleware Execution Order

```
1. CORS (CORSMiddleware)
2. Trusted Host (TrustedHostMiddleware)
3. Rate Limit (RateLimitMiddleware)
4. Tenant Context (TenantContextMiddleware) — sets app.tenant_id
5. JWT Auth (JWTAuthMiddleware) — validates token, extracts claims
```

**Critical:** Tenant Context MUST be set before JWT Auth, so JWT validation can check tenant_id against the database with RLS active.

---

## JWT Validation

### Access Token Validation
```python
async def validate_access_token(token: str) -> JWTClaims:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,  # From Vault
            algorithms=["HS256"],
            audience="lexcore-api",
            issuer="lexcore",
        )
        
        # Extract claims
        tenant_id = UUID(payload["tid"])
        user_id = payload["sub"]
        tier = payload["tier"]
        role = payload["role"]
        
        # Verify tenant exists and is active
        tenant = await get_tenant(tenant_id)
        if not tenant or tenant.payment_status == "CANCELLED":
            raise TenantInactive()
        
        return JWTClaims(
            tenant_id=tenant_id,
            user_id=user_id,
            tier=tier,
            role=role,
            scopes=payload.get("scope", "read"),
        )
    
    except jwt.ExpiredSignatureError:
        raise TokenExpired()
    except jwt.InvalidTokenError:
        raise InvalidToken()
```

### Refresh Token Validation
```python
async def validate_refresh_token(token: str) -> JWTClaims:
    # 1. Check blacklist
    jti = get_jti_from_token(token)
    if await redis.exists(f"token_blacklist:{jti}"):
        raise RefreshTokenRevoked()
    
    # 2. Validate JWT (same as access token)
    claims = await validate_access_token(token)
    
    # 3. Verify token type
    if claims.token_type != "refresh":
        raise InvalidToken("Not a refresh token")
    
    return claims
```

---

## Token Lifetimes

| Token Type | Lifetime | Refreshable | Storage |
|------------|----------|-------------|---------|
| Access Token (Clerk) | 1 hour | Yes (via Clerk) | Clerk-managed session |
| Access Token (API) | 1 hour | Yes (via refresh) | Client memory only |
| Refresh Token (API) | 7 days | No (rotation) | Client memory + Redis hash |
| Scoped JWT (Attorney) | 48 hours | No | Email link only |
| API Key | Indefinite (until revoked) | N/A | Server-side bcrypt hash |

---

## Secret Management

### Vault Integration
```python
# secrets retrieved from HashiCorp Vault at startup
VAULT_SECRETS = {
    "jwt_signing_key": "vault://secret/jwt/signing-key",
    "db_password": "vault://secret/database/password",
    "redis_password": "vault://secret/redis/password",
    "openai_api_key": "vault://secret/openai/api-key",
    "clerk_secret_key": "vault://secret/clerk/secret-key",
    "polygon_private_key": "vault://secret/polygon/private-key",
    "stripe_secret_key": "vault://secret/stripe/secret-key",
}
```

### Environment Variables (Development Only)
```bash
# .env (never committed — in .gitignore)
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
JWT_SECRET_KEY=dev-only-key-change-in-prod
OPENAI_API_KEY=sk-...
CLERK_SECRET_KEY=sk_test_...
```

---

## Audit Logging

Every authentication event is logged to `audit_log` table:

```json
{
  "action_type": "TOKEN_ISSUED|TOKEN_REFRESHED|TOKEN_REVOKED|LOGIN_FAILED|LOGOUT",
  "entity_type": "JWT_TOKEN|API_KEY|SCOPED_JWT",
  "entity_id": "jti_or_key_id",
  "user_id": "user_id_or_null",
  "details": {
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "tenant_id": "uuid",
    "tier": "FIRM",
    "success": true,
    "failure_reason": "null_or_error_code"
  }
}
```

---

## Security Checklist

- [ ] JWT signing key is 256-bit random, stored in Vault, rotated quarterly
- [ ] Refresh tokens are single-use (rotation)
- [ ] Token blacklist in Redis with 7-day TTL
- [ ] API keys are bcrypt-hashed (cost factor 12)
- [ ] Attorney portal JWTs are 48h expiry, single-scope
- [ ] RLS is active on all tenant-scoped tables
- [ ] Rate limiting is enforced before JWT validation (prevent DoS on auth)
- [ ] CORS origin is strictly validated (no wildcard with credentials)
- [ ] TLS 1.3 is required (1.2 fallback with strong ciphers only)
- [ ] All auth events logged to audit_log (append-only)

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-29 | Initial auth flow specification | C04 API contracts definition |
