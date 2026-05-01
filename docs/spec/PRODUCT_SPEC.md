# PRODUCT_SPEC.md — LexCore + LexRadar

> **Build System:** Unified Build System v2  
> **Chunk:** C01 — Product Definition  
> **Horde:** HORDE-ARCH  
> **Last Updated:** 2026-04-29  
> **Hash:** (computed after all C01 artifacts complete)

---

## 5 Required Clarifying Questions (Answered)

### Q1: Who is the primary user and what is their role?

**LexCore Primary Users:**
- **Legal tech operators** — responsible for monitoring legislative changes, maintaining compliance databases
- **IP attorneys** — searching legal precedents, analyzing case law, drafting opinions
- **Compliance teams** — tracking regulatory changes across jurisdictions

**LexRadar Primary Users:**
- **IP attorneys** — reviewing patent disclosures, prior art analysis, filing decisions
- **In-house counsel** — managing company IP portfolio, invention capture
- **Patent operations teams** — running prior art searches, managing disclosure workflows

**User Segments by Tier:**
- **SOLO** — Individual practitioners, small firms (< 5 attorneys)
- **FIRM** — Mid-size law firms, boutique IP practices (5-50 attorneys)
- **ENTERPRISE** — Large firms, in-house legal departments, tech companies (50+ users)

### Q2: What is the single problem this system must solve?

**LexCore:** Legal professionals spend 40%+ of their time manually searching, tracking, and analyzing scattered legal data across multiple jurisdictions and sources. There is no unified, queryable, BAM-routed legal intelligence database for North American law that delivers attorney-quality results with full citation chains and legislative change monitoring.

**LexRadar:** Engineering teams generate patentable inventions daily, but the path from code commit to patent filing is broken. Inventions are lost in Jira/GitHub/Notion, prior art searches are manual and slow, disclosure drafting takes weeks, and the attorney review handoff is ad-hoc. There is no autonomous pipeline that detects signals → scores patentability → drafts disclosures → packages filing bundles → anchors proof on-chain → delivers attorney-ready handoff packages.

**Unified Value Proposition:** A single platform where legal intelligence and IP pipeline share tenant isolation, BAM routing infrastructure, and observability — reducing time-to-insight for legal research and time-to-filing for patent capture.

### Q3: What are the hard technical or legal constraints?

**Legal Constraints:**
- **No unauthorized practice of law (UPL):** System provides information and drafting assistance; final legal advice and filing decisions remain with licensed attorneys
- **No raw IP content on-chain (IP-G1):** Proof ledger stores hashes only, never invention descriptions, claims, or source code
- **Attorney review gate (IP-G7):** No autonomous filing. All disclosures require attorney approval before status reaches "filed"
- **Multi-tenant data isolation (SEC-G1):** One tenant's data must never be visible to another, enforced at database (RLS), API (JWT claims), and cache (tenant-scoped keys) layers
- **Data retention compliance:** Support GDPR/CCPA deletion requests; audit logs immutable

**Technical Constraints:**
- **Multi-tenant architecture:** Every table has `tenant_id` with PostgreSQL RLS `FORCE` enabled
- **BAM routing required:** Every agent query, search, and ingestion event carries a BAM compound signal for traceability
- **Latency budget:** P95 < 300ms for search queries (with cache hit), P95 < 5s for full research tasks
- **Embedding model lock:** OpenAI `text-embedding-3-large` (1536-dim) — changing requires re-embedding entire corpus
- **Polygon mainnet for proof anchoring:** Chain ID 137, transaction hashes stored immutably
- **BYOK (Bring Your Own Key):** Enterprise tenants may supply their own Vault encryption keys

**Compliance Constraints:**
- **SOC 2 Type II target:** Audit trail for all data access, encryption at rest + in transit, access controls
- **No PII in logs:** Structured logging must never contain passwords, encryption keys, or tenant secrets

### Q4: What does success look like in 30, 60, 90 days?

**30 Days (C01-C05 Complete — Foundation + Core Features):**
- Product spec, architecture, schema, API contracts, and service layer complete
- Database migrations run clean on fresh PostgreSQL + pgvector
- FastAPI application starts locally with all 7 MCP tools routable
- LexRadar agents detect inventions from sample GitHub repos
- CI/CD pipeline passes all 13 stages on test commits
- Local development stack runs via `docker-compose up`

**60 Days (C06-C09 Complete — Frontend + Quality + Security):**
- Attorney portal renders handoff packages with 10 sections
- Search UI delivers results with citation chains in < 300ms (cached)
- 80%+ test coverage across unit, integration, E2E tiers
- Security scan: zero HIGH findings from gitleaks, pip-audit, bandit
- Tenant isolation tests pass: cross-tenant API and DB access blocked
- BYOK encryption/decryption test passes with access revocation

**90 Days (C10-C11 Complete — Deploy + Live):**
- Production deployment with canary rollout
- First real user completes onboarding and activation
- First patent disclosure handoff delivered to attorney portal
- First legal research query returns attorney-quality results with full citation chain
- Monitoring dashboards render real data; alerts fire on SLO breach
- Handoff package reviewed by named owner for 4 audiences (Operator, Engineer, Client, Legal)

### Q5: What is explicitly out of scope for this build?

**Out of Scope — LexCore:**
- Real-time court docket tracking (future enhancement)
- International jurisdictions beyond NA (EU, Asia-Pacific) — Phase 2
- AI-generated legal advice or interpretation (information retrieval only)
- e-filing integration with courts (future enhancement)
- Mobile native apps (web-only for MVP)
- Custom document upload / ingestion by end users (admin-only for MVP)

**Out of Scope — LexRadar:**
- Automatic patent filing with USPTO (system stops at attorney handoff)
- Patent prosecution management (responses to office actions)
- Trademark or copyright detection (patents only for MVP)
- Integration with external prior art databases beyond the 7 approved sources
- International patent filing (PCT national phase entry)
- Mobile native apps (web-only for MVP)
- Auto-approval of disclosures (attorney review is mandatory)

**Out of Scope — Platform:**
- White-label / reseller portal
- Custom AI model training per tenant
- Real-time collaborative editing (async handoff only)
- SLA guarantees for SOLO tier (best-effort only)
- Data migration from legacy systems (manual CSV import only)

---

## Problem Statement

Legal and IP professionals are overwhelmed by fragmented data, manual workflows, and slow research cycles. LexCore provides a unified North American legal intelligence database with BAM-routed search and monitoring. LexRadar provides an autonomous IP detection pipeline that turns engineering commits into attorney-ready patent disclosures. Together, they form a single tenant-isolated platform for legal intelligence and IP operations.

## Primary User (Role + Company Type)

**LexCore:** Legal tech operator at a mid-size law firm or in-house legal department  
**LexRadar:** IP attorney at a technology company or patent boutique firm  
**Both:** Compliance teams at enterprises with multi-jurisdiction obligations

## Highest-Value Action (First Value Event)

**LexCore:** A user runs `search_legal` on a jurisdiction + query, receives a ranked list of documents with full citation chains, and identifies a legislative change that affects their client's compliance posture — all in under 5 seconds.

**LexRadar:** An engineer pushes code to GitHub; within 24 hours, the IP attorney receives a handoff package in the portal with a scored disclosure draft, prior art comparison, and blockchain-anchored evidence chain — ready for review and filing decision.

## Must-Have Features (with Acceptance Criteria)

### LexCore

| # | Feature | Acceptance Criteria | Chunk |
|---|---------|---------------------|-------|
| 1 | **Multi-jurisdiction legal search** | Search across US Federal, US State, Canadian Federal, Canadian Provincial, EU, UK, Australian, NZ sources with unified ranking | C04 |
| 2 | **Hybrid vector + full-text search** | Combine pgvector HNSW cosine similarity with PostgreSQL GIN full-text search, re-rank by citation authority | C04 |
| 3 | **Citation graph traversal** | Retrieve forward/backward citations up to depth 3, detect overruled cases, extract authority chain | C04 |
| 4 | **Legislative change monitoring** | Monitor rules configured per jurisdiction + body_of_law; detect changes within 24h; deliver alerts | C05 |
| 5 | **BAM-routed agent queries** | Every query carries BAM compound signal; router dispatches to correct agent lane; query cache stores by fingerprint | C05 |
| 6 | **Query result cache** | Redis-backed cache with TTL; cache hit rate > 60% for repeated queries; invalidation on data update | C05 |
| 7 | **Tenant isolation** | RLS policies enforce tenant separation at DB level; JWT claims enforce at API level; cache keys scoped by tenant | C03 |

### LexRadar

| # | Feature | Acceptance Criteria | Chunk |
|---|---------|---------------------|-------|
| 1 | **Invention detection from code** | Scan GitHub/Jira/Notion for patentable signals; generate invention candidates with BAM compound | C05 |
| 2 | **Prior art search (7 sources)** | Parallel search across USPTO, WIPO, EPO, Lens, Google Patents, PatentScope, IP.com; return top 50 ranked by relevance | C05 |
| 3 | **6-dimension patent scoring** | Novelty, nonobviousness, enablement, written description, definiteness, utility — each scored 0-1 with explanation | C05 |
| 4 | **Disclosure draft generation** | Generate 10 LHP sections with claim themes; grounding score > 0.85; editable by attorney in portal | C05 |
| 5 | **Blockchain proof anchoring** | Store document hash + bundle hash on Polygon mainnet; transaction hash stored immutably; never store content on-chain | C05 |
| 6 | **Attorney portal handoff** | Scoped JWT (48h, single attorney, single handoff); portal shows 10 sections with 3 editable; approve/reject/request-changes actions | C06 |
| 7 | **Filing bundle packaging** | Package 9 documents (disclosure, drawings, claims, abstract, etc.) into PDF/ZIP; download via secure link | C05 |

## Nice-to-Have Features

| Feature | Description | Target Chunk |
|---------|-------------|--------------|
| Real-time websocket alerts | Push legislative changes to connected clients | C07 |
| AI-powered query decomposition | Break complex research questions into sub-queries automatically | C05 (v2) |
| Custom jurisdiction connectors | Allow tenants to add their own data sources | LOOP |
| Batch prior art upload | Upload existing prior art for scoring comparison | LOOP |
| Patent family visualization | Interactive graph of patent family relationships | C06 (v2) |
| Multi-language search | Search across English, French, Spanish legal documents | LOOP |
| Slack/Teams integration | Alert delivery via Slack webhooks | LOOP |
| Advanced analytics dashboard | Query volume, cache hit rates, agent performance over time | C06 |

## Success Metrics (Measurable, Time-Bound)

| Metric | Target | Timeframe | Measurement |
|--------|--------|-----------|-------------|
| Search P95 latency | < 300ms | C08 | Prometheus histogram |
| Search result precision@10 | > 0.85 | C08 | Golden set evaluation |
| Cache hit rate | > 60% | C08 | Redis metrics |
| Invention detection recall | > 0.80 | C08 | Labeled test set |
| Prior art relevance score | > 0.70 top-10 avg | C08 | Attorney judgment |
| Disclosure grounding score | > 0.85 | C08 | GroundingJudge eval |
| Tenant isolation test pass | 100% | C09 | Security test suite |
| Test coverage | > 80% | C08 | pytest --cov |
| E2E onboarding pass rate | > 95% | C11 | Playwright tests |
| Activation event rate | > 50% of signups | C11 | Event tracking |

## Activation Definition

**LexCore Activation:** A tenant completes their first `search_legal` query that returns ≥ 3 results with citation chains, and the user clicks through to view a full document. Event: `first_value_action.completed`.

**LexRadar Activation:** An IP attorney logs into the portal, opens a handoff package, and clicks either "Approve" or "Request Changes" (not just "Reject"). Event: `first_value_action.completed`.

## Compliance and Legal Constraints

1. **No UPL:** System is an information retrieval and drafting assistant. All legal advice disclaimers prominently displayed.
2. **No on-chain IP content:** Only SHA-256 hashes of documents and bundles are anchored on Polygon. Raw content never leaves encrypted storage.
3. **Attorney review mandatory:** LexRadar disclosures cannot reach "filed" status without attorney approval. Status machine enforces this.
4. **Data residency:** Enterprise tenants may specify data residency region (US, CA, EU).
5. **Audit trail:** Every data access, every agent action, every status change logged immutably to audit_log table.
6. **Retention:** Legal documents cached indefinitely (public law). Tenant data retained per subscription tier; deletion on request within 30 days.

## External Integrations

**LexCore Data Sources:**
- eCFR (US Federal Regulations)
- CanLII (Canadian Federal + Provincial)
- CourtListener (US Federal Courts)
- US Congress API (Legislation)
- EUR-Lex (European Union)
- UK Legislation API
- AustLII (Australian)
- NZ Legislation
- US State Legislative APIs (via LegiScan or individual)

**LexRadar Data Sources:**
- GitHub (code commits, issues, PRs)
- Jira (tickets, epics)
- Notion (pages, databases)
- USPTO PatentsView / Public Search
- WIPO PCT Database
- EPO Open Patent Services
- Lens (Cambia)
- Google Patents
- PatentScope (WIPO)
- IP.com

**Infrastructure:**
- Neon PostgreSQL (managed, serverless)
- Qdrant (vector database)
- Redis (cache, sessions, job queue)
- HashiCorp Vault (secrets, BYOK)
- AWS S3 (document storage, filing bundles)
- Polygon mainnet (proof anchoring)

## Known Failure Conditions

1. **Embedding model deprecation:** If OpenAI deprecates `text-embedding-3-large`, entire corpus requires re-embedding. Mitigation: model version pinning, migration plan in ADR.
2. **Source API rate limits:** eCFR, CanLII, USPTO all have rate limits. Mitigation: exponential backoff, request pacing, circuit breakers.
3. **Blockchain network congestion:** Polygon gas spikes could delay proof anchoring. Mitigation: batch anchoring, retry with backoff, status tracking.
4. **Tenant data leakage via cache:** Incorrect cache key scoping could expose cross-tenant data. Mitigation: tenant_id prefix on ALL cache keys, RLS at DB layer.
5. **Attorney portal token expiration:** Scoped JWT expires after 48h; attorney loses mid-review. Mitigation: email reminder at 24h, token refresh link, draft auto-save.
6. **Ingestion pipeline failure:** Source API changes schema without notice. Mitigation: schema validation on fetch, alerting on parse failures, manual fallback.
7. **Prior art source downtime:** One of 7 sources unavailable. Mitigation: parallel search with partial results, degraded mode indicator, retry on next scan.

---

## Spec Hash

**Combined SHA-256 (all C01 artifacts):** `01237d72a9ff3d59f38649a8b1defde5466a1d4c5e2815f403242f555b69ab98`

**Individual hashes:**
- PRODUCT_SPEC.md: `c0e02a281d11c0da7ac206402d761b0405050c819429e1645429860284ff0fd9`
- TASK_TREE.md: `b9209c393c358b3962361cda29fcfec3bf4ec2abf04e1c80de7b8951b8264682`
- JTBD_MAP.md: `f79b35af4d6f6732130a883d6fba8b81c7eac0f7cccb07fd82ff241cff031246`
- ONBOARDING_SUCCESS.md: `14372c8ab8fbf33f8199669c620e8661cf22b15b978b81a208a89c2133fb975b`
- OUT_OF_SCOPE.md: `1f4b7e2c20e3eea158ed97771faa9770012c3a318548a34bf3b4104379c63d35`
