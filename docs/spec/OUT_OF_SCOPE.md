# OUT_OF_SCOPE.md — LexCore + LexRadar

> **Build System:** Unified Build System v2  
> **Chunk:** C01 — Product Definition  
> **Horde:** HORDE-ARCH  

---

## Purpose

This document explicitly lists what is **NOT** included in the MVP build (C01-C11). Every item here requires a conscious decision to add later via the Enhancement Loop. No item on this list may be silently added during the build arc without updating this document and writing a compatibility report.

---

## Out of Scope — LexCore (Legal Intelligence)

### Jurisdictions
- **International jurisdictions beyond North America:** EU (partial — EUR-Lex is included for comparison but not primary focus), UK, Australia, New Zealand, Asia-Pacific, Latin America, Africa
- **US State court systems:** Individual state trial court opinions (appellate and supreme courts only)
- **Tribal law:** Native American tribal court decisions and codes
- **International arbitration:** ICSID, ICC, UNCITRAL cases
- **Military law:** UCMJ, military courts

### Features
- **Real-time court docket tracking:** Live case filing monitoring (future enhancement — requires PACER integration)
- **AI-generated legal advice or interpretation:** System is information retrieval only. No "this means you should..." conclusions.
- **e-Filing integration:** Direct filing with courts (future — requires per-court API integration)
- **Contract review / drafting:** General contract analysis (LexCore focuses on statutes, regulations, and case law)
- **Legal billing / time tracking:** Practice management features
- **Client matter management:** Docketing, calendaring, deadline management
- **Mobile native apps:** iOS and Android apps (web responsive only for MVP)
- **Custom document upload by end users:** Admin-only ingestion for MVP; tenant document upload deferred to LOOP
- **Real-time collaborative editing:** Multiple users editing same document simultaneously (async handoff only)
- **AI-powered legal prediction:** Predicting case outcomes, settlement values, etc.
- **Courtroom presentation tools:** Slide generation, exhibit management
- **Expert witness database:** Search and management of expert witnesses

### Integrations
- **PACER / CourtListener live dockets:** Federal court docket tracking (cost-prohibitive for MVP)
- **Westlaw / LexisNexis API:** Direct integration with paid legal research platforms (competitive, not complementary)
- **Practice management systems:** Clio, MyCase, PracticePanther, etc.
- **Billing systems:** QuickBooks, Xero, etc.
- **Calendar systems:** Google Calendar, Outlook Calendar sync for deadlines

---

## Out of Scope — LexRadar (IP Pipeline)

### Patent Types
- **Design patents:** Aesthetic/design IP only (utility patents only for MVP)
- **Plant patents:** Agricultural/biological inventions (utility patents only)
- **Trademarks:** Brand names, logos, slogans (patents only)
- **Copyrights:** Software copyright registration (patents only)
- **Trade secrets:** NDA, know-how management (patents only)

### Pipeline Stages
- **Automatic patent filing with USPTO:** System stops at attorney handoff. No auto-submission to USPTO, EPO, or WIPO.
- **Patent prosecution management:** Responses to office actions, examiner interviews, continuation strategy
- **Patent maintenance fee management:** Tracking and paying maintenance fees
- **Licensing and valuation:** Patent licensing deals, valuation models, royalty tracking
- **Portfolio analytics:** Cross-portfolio analysis, patent family strategy, landscape mapping
- **Freedom-to-operate (FTO) analysis:** Determining if a product infringes existing patents
- **Patent invalidity analysis:** Challenging validity of existing patents

### Integrations
- **Direct USPTO filing API:** No electronic filing system (EFS-Web) integration
- **Patent annuity services:** No integration with annuity payment providers
- **IP management systems:** Anaqua, CPA Global, Pattsy, etc.
- **Inventor reward systems:** No integration with HR/incentive platforms
- **External prior art databases beyond the 7 approved:** No Derwent, Thomson Innovation, Orbit, etc. for MVP

### Features
- **Mobile native apps:** iOS and Android apps (web responsive only for MVP)
- **Real-time code scanning:** Every commit triggers scan (batch mode only for MVP: daily scan)
- **IDE plugins:** VS Code, IntelliJ plugins for invention capture
- **Slack/Teams bot real-time notifications:** Daily digest only for MVP; real-time bot deferred
- **Custom scoring models per tenant:** All tenants use same 6-dimension scoring model for MVP
- **Multi-language patent drafting:** English only for MVP
- **Video / multimedia invention capture:** Text and code only for MVP

---

## Out of Scope — Platform / Shared

### Features
- **White-label / reseller portal:** No multi-brand support for MVP
- **Custom AI model training per tenant:** All tenants use shared OpenAI embeddings and models
- **On-premise deployment:** Cloud-only for MVP (SaaS model)
- **Air-gapped / offline mode:** Always requires internet connection
- **Custom SLA guarantees for SOLO tier:** Best-effort only; SLA guarantees for FIRM/ENTERPRISE only
- **Data migration from legacy systems:** Manual CSV import only; no automated migration from Westlaw, Lexis, Anaqua, etc.
- **GDPR/CCPA automated compliance workflows:** Data deletion on request (manual process for MVP); automated compliance portal deferred
- **SOC 2 Type II audit:** Target is SOC 2 Type I for MVP; Type II requires 6 months of operational data
- **FedRAMP / government cloud certification:** Commercial cloud only
- **HIPAA compliance:** Not a healthcare system
- **PCI-DSS compliance:** No payment processing in MVP (Stripe handles all payments)

### Integrations
- **Salesforce / HubSpot CRM:** No direct CRM integration for MVP
- **Slack real-time bot:** Webhook alerts only; interactive bot deferred
- **Microsoft Teams app:** Webhook alerts only; Teams app deferred
- **Zapier / Make (Integromat):** No low-code integration platform support for MVP
- **SSO beyond Clerk:** SAML, OIDC, Active Directory deferred to LOOP
- **LDAP / Active Directory sync:** Cloud identity only (Clerk) for MVP

### Infrastructure
- **Multi-region active-active deployment:** Single primary region for MVP; read replicas in secondary regions
- **Kubernetes multi-cluster:** Single EKS cluster for MVP
- **Custom bare-metal servers:** Cloud-only (AWS) for MVP
- **Private cloud / VMware:** Public cloud only
- **CDN for dynamic API responses:** Static assets only; API responses served from origin

---

## Deferred to Enhancement Loop

The following items are explicitly deferred to post-go-live enhancement iterations. They may be added via the Enhancement Loop (Part 10 of the build system) after C11 is complete and the system is live.

### High-Priority Loop Candidates
1. **Real-time code scanning:** Every commit triggers invention detection scan
2. **IDE plugins (VS Code, IntelliJ):** Invention capture at the developer's keyboard
3. **Mobile responsive attorney portal:** Native-feel mobile experience for handoff review
4. **Custom scoring models:** Enterprise tenants can train custom patentability scoring
5. **International patent filing (PCT):** National phase entry automation
6. **Additional legal jurisdictions:** EU primary focus, UK, Australia, NZ full support
7. **Practice management integration:** Clio, MyCase sync for law firms
8. **Slack/Teams interactive bot:** Natural language querying from chat

### Medium-Priority Loop Candidates
9. **Design patent support:** Aesthetic invention detection and scoring
10. **Trademark watch:** Brand monitoring and conflict detection
11. **Patent prosecution management:** Office action response drafting
12. **Portfolio analytics:** Cross-portfolio visualization and strategy tools
13. **Freedom-to-operate analysis:** Product-to-patent claim mapping
14. **e-Filing integration:** Direct court filing for LexCore
15. **Custom document upload by tenants:** Self-service ingestion portal
16. **Real-time collaborative editing:** Multiple attorneys editing same disclosure

### Low-Priority Loop Candidates
17. **Video invention capture:** Record and timestamp invention explanations
18. **Patent valuation models:** Automated valuation based on citations, family size, etc.
19. **Licensing marketplace:** Connect patent holders with licensees
20. **On-premise deployment option:** Air-gapped for defense/intelligence clients
21. **FedRAMP certification:** Government cloud deployment
22. **Blockchain beyond Polygon:** Ethereum, other L2s for proof anchoring

---

## Scope Change Protocol

If a stakeholder requests an out-of-scope item during the build arc:

1. **Record the request** in `docs/handoff/POST_GO_LIVE_BACKLOG.md`
2. **Do NOT add to current chunk** without:
   - Compatibility report (`docs/compatibility/COMPAT_REPORT_{date}.json`)
   - Impact assessment on existing chunks
   - Updated PRODUCT_SPEC.md and TASK_TREE.md
   - Re-computed SPEC_HASH.txt
3. **Escalate to HordeMaster** for scope change authorization
4. **If approved:** Add to Enhancement Loop with target chunk and priority

**Exception:** Critical security finding or compliance requirement may bypass this protocol with HORDE-AUDIT approval and immediate documentation.

---

## Sign-off

This out-of-scope list was reviewed and approved by:
- **HORDE-ARCH:** Architecture and build feasibility
- **HORDE-AUDIT:** No critical security or compliance gaps from exclusions
- **Human Checkpoint 1:** (after C05) Product utility confirmed with scope

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-29 | Initial scope definition | C01 product definition |
