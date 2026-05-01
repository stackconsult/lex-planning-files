# ONBOARDING_SUCCESS.md — LexCore + LexRadar

> **Build System:** Unified Build System v2  
> **Chunk:** C01 — Product Definition  
> **Horde:** HORDE-ARCH  

---

## Activation Funnel

The system is not "live" until a real user completes the activation path. This document defines the exact steps, events, and success criteria for both LexCore and LexRadar onboarding.

---

## LexCore Activation Funnel

### Step 1: User Signs Up
**Event:** `user.signed_up`  
**Trigger:** Account creation via Clerk (or email + password for non-Clerk tier)  
**Success Criteria:**
- Account created in `tenants` table
- Tenant tier assigned (SOLO / FIRM / ENTERPRISE)
- Welcome email sent
- Onboarding wizard initialized

**Friction Points:**
- Email verification required before proceeding
- Password complexity enforced
- CAPTCHA on sign-up (anti-bot)

---

### Step 2: Workspace Created
**Event:** `workspace.created`  
**Trigger:** User names their workspace (firm name, company name, or individual)  
**Success Criteria:**
- Workspace record created with `tenant_id`
- Default jurisdiction preferences set (user-selectable: US Federal, Canada, etc.)
- Default monitor rules created (optional — user can skip)
- Team member invitation page shown (skip allowed for SOLO tier)

**Friction Points:**
- Workspace name must be unique (validated)
- Jurisdiction selection required (at least one)
- SOLO tier: skip team invitation
- FIRM/ENTERPRISE: must invite at least one team member

---

### Step 3: Integration Connected
**Event:** `integration.connected`  
**Trigger:** User connects a data source or API key  
**Success Criteria:**
- LexCore: No external integration required (data comes from built-in connectors)
  - Optional: Slack webhook for legislative alerts
  - Optional: Custom API key for enterprise data sources
- LexRadar: Source connector configured
  - GitHub: OAuth connection to organization repos
  - Jira: OAuth or API token connection
  - Notion: OAuth connection to workspace

**Friction Points:**
- GitHub OAuth requires org admin approval
- Jira API token requires admin to generate
- Notion OAuth requires integration approval
- Clear error messages if connection fails
- Retry guidance provided

---

### Step 4: First Value Action Completed ← THE ACTIVATION GATE
**Event:** `first_value_action.completed`  
**Trigger:** LexCore: User runs `search_legal` and views a document with full citation chain  
**Success Criteria:**
- Search query submitted via MCP `search_legal` tool or web UI
- Results returned with ≥ 3 documents
- User clicks into a document detail view
- Citation chain rendered (at least 1 level deep)
- Page load time < 5 seconds

**LexRadar-specific Activation:**
- IP attorney logs into attorney portal
- Opens a handoff package
- Clicks "Approve" or "Request Changes" (not "Reject")

**Why this is the activation gate:**
- Search + citation chain view proves the core value proposition (attorney-quality legal intelligence)
- It demonstrates BAM routing, hybrid search, and citation graph — all core differentiators
- It creates data in `agent_queries`, `query_cache`, and user engagement metrics
- It sets up the user for repeat usage (same queries, monitor rules)

---

### Step 5: Team Member Invited
**Event:** `team_member.invited`  
**Trigger:** User invites colleague to workspace  
**Success Criteria:**
- Invitation email sent
- Invite link contains scoped JWT (48h expiry)
- Team member appears in workspace member list (pending)

**Friction Points:**
- SOLO tier: feature disabled (upgrade prompt shown)
- FIRM tier: max 10 members
- ENTERPRISE tier: unlimited members

---

### Step 6: Feature Used Twice
**Event:** `feature.used_twice`  
**Trigger:** User performs the same feature action twice within 7 days  
**LexCore Examples:**
- Search used twice
- Monitor rule created + triggered once
- Research task run twice
- Citation lookup used twice

**LexRadar Examples:**
- Handoff package reviewed twice
- Prior art search run twice
- Invention candidate scored twice

**Why this matters:**
- First use could be accidental or exploratory
- Second use within 7 days indicates habit formation
- Signals product-market fit for this user segment

---

## LexRadar Activation Funnel (IP Attorney-Specific)

### Step 1: Handoff Package Received
**Event:** `handoff.received`  
**Trigger:** LexRadar system emails attorney with portal link  
**Success Criteria:**
- Email delivered (bounce tracking)
- Link contains scoped JWT (valid 48h)
- Email explains: 10 sections, 3 editable, action buttons

---

### Step 2: Portal Accessed
**Event:** `portal.accessed`  
**Trigger:** Attorney clicks email link and portal loads  
**Success Criteria:**
- Portal loads < 3 seconds
- JWT validated (not expired, not tampered)
- Handoff package data fetched and rendered
- 10 sections visible, 3 editable sections highlighted

---

### Step 3: Review Completed ← THE ACTIVATION GATE
**Event:** `first_value_action.completed`  
**Trigger:** Attorney clicks "Approve" or "Request Changes"  
**Success Criteria:**
- Action recorded in `attorney_reviews` table
- Status transitions: `PENDING` → `IN_PROGRESS` → `APPROVED` or `REJECTED` or `REQUESTED_CHANGES`
- Feedback form submitted (structured fields)
- If approved: disclosure status moves to `APPROVED`, filing bundle becomes available
- If requested changes: task assigned back to LexRadar system with specific change requests

**Why this is the activation gate:**
- Attorney review is the non-negotiable human checkpoint in the patent pipeline
- It proves the handoff package quality is attorney-ready
- It validates the scoped JWT portal access flow
- It completes the end-to-end value chain: code → detection → disclosure → attorney → filing decision

---

## Onboarding Metrics Dashboard

### Funnel Conversion Rates

| Step | LexCore Target | LexRadar Target | Measurement |
|------|---------------|-----------------|-------------|
| Signup → Workspace | > 90% | > 90% | `workspace.created / user.signed_up` |
| Workspace → Integration | > 70% | > 60% | `integration.connected / workspace.created` |
| Integration → Activation | > 50% | > 40% | `first_value_action.completed / integration.connected` |
| Activation → Invite | > 30% | N/A | `team_member.invited / first_value_action.completed` |
| Activation → Repeat Use | > 60% | > 50% | `feature.used_twice / first_value_action.completed` |

### Time-to-Activation

| Segment | LexCore Target | LexRadar Target |
|---------|---------------|-----------------|
| SOLO | < 10 minutes | < 1 hour |
| FIRM | < 15 minutes | < 2 hours |
| ENTERPRISE | < 30 minutes | < 4 hours |

*Note: LexRadar takes longer due to source connector setup and handoff package generation.*

### Drop-off Points to Monitor

1. **Sign-up page abandonment:** Check if CAPTCHA is too aggressive, form too long
2. **Integration connection failure:** Track OAuth failures per source (GitHub, Jira, Notion)
3. **Search with no results:** Alert if > 10% of first searches return zero results
4. **Portal JWT expiration:** Alert if > 20% of attorneys never access portal before expiry
5. **Attorney rejects disclosure:** Track rejection rate; > 30% suggests disclosure quality issue

---

## Onboarding UX Requirements

### LexCore Onboarding Wizard (5 Steps)

1. **Welcome** — Product value proposition, 30-second video (optional)
2. **Workspace** — Name, jurisdiction selection, tier confirmation
3. **Data Sources** — (Optional) Connect Slack for alerts, API keys for enterprise sources
4. **First Search** — Guided first search with suggested queries:
   - "privacy law California"
   - "patent obviousness software"
   - "securities regulation 2024"
5. **Results Tour** — Walkthrough of search results, citation chain, document viewer
6. **Monitor Setup** — (Optional) Create first monitor rule with 1-click templates
7. **Done** — Dashboard shown, activation event fired

### LexRadar Onboarding (Engineering Team)

1. **Welcome** — Value proposition: "Turn your code into patents"
2. **Connectors** — OAuth connections to GitHub, Jira, Notion
3. **Scan Configuration** — Select repos/projects to monitor, signal types to detect
4. **First Scan** — Run initial scan, show detected candidates
5. **Review Queue** — IP team reviews first candidate, scores it
6. **Disclosure Preview** — Generate preview disclosure for top candidate
7. **Handoff Simulation** — Send test handoff to internal email, preview portal
8. **Done** — Dashboard shown, activation event fired when first real handoff is approved

### LexRadar Onboarding (Attorney — Via Email)

1. **Email Received** — Subject: "Patent Disclosure Handoff from [Client Name]"
2. **Link Clicked** — Scoped JWT portal link, 48h expiry
3. **Portal Loads** — Handoff package displayed with:
   - Client info, invention title, invention date
   - 10 sections with progress indicator
   - 3 editable sections highlighted
   - Evidence chain viewer (read-only)
   - Prior art comparison table
4. **Review + Action** — Attorney edits claims, reviews evidence, clicks action button
5. **Feedback Submitted** — Structured feedback form (if requesting changes)
6. **Done** — Status updated, client notified, next steps shown

---

## Onboarding Success Signals

### Positive Signals (indicate strong product-market fit)
- Activation within 24 hours of signup
- 3+ searches in first week (LexCore)
- 2+ handoff reviews in first month (LexRadar)
- Monitor rule created within 3 days
- Team member invited within 1 week (FIRM/ENTERPRISE)
- Custom API key configured (ENTERPRISE)

### Negative Signals (indicate friction or misalignment)
- No activation after 7 days
- Integration connection failure > 3 attempts
- Search with zero results > 2 times
- Attorney rejects > 50% of handoffs
- Portal JWT expires without access
- Support ticket filed within 24 hours of signup

---

## Onboarding Testing (E2E)

### Playwright Test Cases

1. **test_onboarding_lexcore_solo.ts**
   - Sign up as SOLO user
   - Create workspace
   - Skip integration
   - Run first search
   - View citation chain
   - Assert activation event fired

2. **test_onboarding_lexcore_firm.ts**
   - Sign up as FIRM user
   - Create workspace
   - Invite team member
   - Create monitor rule
   - Assert team member received invite

3. **test_onboarding_lexradar_engineer.ts**
   - Sign up as ENTERPRISE user
   - Connect GitHub OAuth
   - Run initial scan
   - Review first candidate
   - Assert candidate detected

4. **test_onboarding_lexradar_attorney.ts**
   - Receive handoff email
   - Click portal link
   - Review handoff package
   - Click "Approve"
   - Assert status updated to APPROVED

---

## Onboarding Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-29 | Initial spec | C01 product definition |
