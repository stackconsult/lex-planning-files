# ADR-002: Authentication and Authorization Strategy

> **Status:** Accepted  
> **Date:** 2026-04-29  
> **Deciders:** HORDE-ARCH  
> **Context:** C02 — Architecture + Contracts  

---

## Problem Statement

LexCore + LexRadar serves two distinct user populations with different authentication needs:

1. **LexCore/LexRadar Platform Users** — Attorneys, compliance teams, engineers who sign up via web app and need SSO, session management, and MFA
2. **LexRadar Attorney Portal Users** — External IP attorneys who receive handoff package links via email and need time-limited, scope-restricted access to a single handoff

Additionally, the system must support:
- Multi-tenant isolation (one tenant's data must never leak to another)
- API key access for integrations and machine-to-machine communication
- BYOK (Bring Your Own Key) for enterprise encryption

---

## Decision

### Primary Auth: Clerk (Frontend)

**For:** LexCore/LexRadar web application users (internal platform users)

| Feature | Implementation |
|---------|---------------|
| Sign-up | Clerk OAuth (Google, GitHub) + email/password |
| SSO | Clerk Enterprise (SAML, OIDC) — deferred to LOOP |
| MFA | Clerk built-in TOTP — FIRM/ENTERPRISE tiers |
| Session | Clerk managed sessions with refresh tokens |
| JWT | Clerk issues JWT with custom claims: `tenant_id`, `tier`, `role` |
| Claims | `sub` (user_id), `tid` (tenant_id), `tier` (SOLO/FIRM/ENTERPRISE), `role` (admin/member/viewer) |

### Secondary Auth: JWT + API Keys (Backend API)

**For:** API consumers, integrations, machine-to-machine, attorney portal

| Feature | Implementation |
|---------|---------------|
| API Key Format | `lex_{tenant_id}_{random_32}` (128-bit entropy) |
| Key Storage | Hashed with bcrypt in PostgreSQL (`api_keys` table) |
| Token Exchange | `POST /v1/auth/token` — API key → JWT access token (1h expiry) |
| Refresh Token | `POST /v1/auth/refresh` — Refresh token → new JWT pair (rotation) |
| Attorney Portal | Scoped JWT: `handoff_id`, `attorney_email`, `exp` (48h), `tenant_id` |

### Tenant Isolation Strategy (Defense in Depth)

| Layer | Mechanism |
|-------|-----------|
| Database | PostgreSQL RLS — `USING (tenant_id = current_setting('app.tenant_id')::UUID)` |
| API | JWT claims — middleware extracts `tenant_id`, rejects mismatched requests |
| Cache | Redis key prefix — `tenant:{tenant_id}:query:{fingerprint}` |
| Vector DB | Qdrant payload filter — `must: [{key: "tenant_id", match: {value: "..."}}]` |
| Object Storage | S3 path prefix — `/{tenant_id}/documents/...` |

---

## Alternatives Considered

### Clerk vs Auth0 vs自建 (Self-built)

| Factor | Clerk | Auth0 | Self-built |
|--------|-------|-------|------------|
| Setup time | Days | Weeks | Months |
| React integration | Native hooks | Wrapper library | Custom implementation |
| Pricing (1K MAU) | $25/mo | $23/mo | $0 + ops cost |
| SAML/OIDC | Enterprise tier | Available | Custom implementation |
| Session management | Built-in | Built-in | Custom implementation |
| MFA | Built-in | Available | Custom implementation |

**Decision:** Clerk for rapid MVP launch. Migration path to Auth0 or self-built documented if enterprise requirements exceed Clerk's capabilities.

### JWT Signing: HS256 vs RS256

| Factor | HS256 | RS256 |
|--------|-------|-------|
| Algorithm | HMAC-SHA256 | RSA-SHA256 |
| Key management | Single shared secret | Public/private key pair |
| Performance | Faster (~2x) | Slower (asymmetric crypto) |
| Key rotation | Requires all services restart | Rotate public key independently |
| Microservices | All services know secret | Services verify with public key |

**Decision:** HS256 for MVP (single backend service). Migration to RS256 documented for microservices split in future.

### API Key Format: UUID vs Structured

**Structured format chosen:** `lex_{tenant_id_prefix}_{random_32}`
- Enables quick tenant identification from key (first segment)
- `lex_` prefix enables secret scanning patterns
- 32-char random segment provides 128-bit entropy

**Alternative (UUID v4):** Rejected — no tenant identification from key itself, requires DB lookup first.

---

## Consequences

### Positive
- Clerk reduces auth implementation from ~2 weeks to ~2 days
- API key format enables fast routing and secret detection
- RLS + JWT + cache prefix provides defense-in-depth tenant isolation
- Scoped attorney portal JWT enables secure external access without user accounts

### Negative
- Clerk dependency for frontend auth — vendor lock-in risk
- HS256 requires secret rotation coordination (all services must update simultaneously)
- API key storage in PostgreSQL (not Vault) — acceptable for MVP, migration to Vault documented

### Risks
- **Clerk outage:** Mitigation — backend JWT validation works independently; users with active JWTs remain authenticated for token lifetime
- **JWT secret compromise:** Mitigation — short expiry (1h access, 7d refresh), rotation procedure documented
- **Attorney portal token leak:** Mitigation — 48h expiry, single handoff scope, email delivery tracking

---

## Implementation Details

### JWT Claims Structure

```json
{
  "sub": "user_uuid",
  "tid": "tenant_uuid",
  "tier": "SOLO|FIRM|ENTERPRISE",
  "role": "admin|member|viewer",
  "iat": 1714399200,
  "exp": 1714402800,
  "jti": "unique_token_id"
}
```

### Attorney Portal Scoped JWT

```json
{
  "sub": "attorney_email_hash",
  "tid": "tenant_uuid",
  "handoff_id": "handoff_uuid",
  "scope": "handoff:read handoff:edit handoff:action",
  "iat": 1714399200,
  "exp": 1714831200,
  "jti": "unique_token_id"
}
```

### Middleware Execution Order

1. `CORSMiddleware` — CORS headers
2. `TrustedHostMiddleware` — Host validation
3. `RateLimitMiddleware` — Redis sliding window
4. `TenantContextMiddleware` — Set `app.tenant_id` for RLS
5. `JWTAuthMiddleware` — Validate token, extract claims

### RLS Policy Activation

```python
# After JWT validation, before DB query
async with db_pool.acquire() as conn:
    await conn.execute(
        "SET app.tenant_id = $1",
        token_claims["tid"]
    )
    # All subsequent queries on this connection are RLS-filtered
```

---

## Related Decisions

- ADR-001: Technology Stack Choice (Clerk selected)
- ADR-003: Async Processing Strategy (affects session storage)

---

## References

- Clerk: https://clerk.com/docs
- JWT RFC 7519: https://tools.ietf.org/html/rfc7519
- PostgreSQL RLS: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
