# SCREEN_MAP.md — LexCore + LexRadar Frontend Screen Registry

> **Build System:** Unified Build System v2  
> **Chunk:** C06 — Frontend  
> **Horde:** HORDE-UI  
> **Control Plane:** ENGINEERING  

---

## Overview

This document defines all screens (routes) in the LexCore + LexRadar frontend application. Screens are organized by domain (LexCore, LexRadar, Platform) and include route definitions, required permissions, key actions, and data dependencies.

**Technology Stack:** Next.js 14 (App Router), TypeScript, React Server Components + Client Components  
**Authentication:** Clerk (`<SignIn>`, `<SignUp>`, `<UserButton>`)  
**Styling:** Tailwind CSS, shadcn/ui components  
**State Management:** React Server Components (async data), Client Components (local state) + SWR for cache  

---

## Route Structure

```
/                          → Landing Page (marketing)
/app                       → Main application shell (authenticated)
  /lexcore                 → LexCore domain
    /dashboard             → LexCore Dashboard
    /search                → Legal Search
    /document/[id]         → Document Detail
    /research              → Research Tasks
    /research/[id]         → Research Result
    /monitor               → Monitor Rules
    /monitor/new           → Create Monitor Rule
    /monitor/[id]/edit     → Edit Monitor Rule
    /jurisdictions         → Jurisdiction Browser
  /lexradar                → LexRadar domain
    /dashboard             → LexRadar Dashboard
    /inventions            → Invention Candidates
    /invention/[id]        → Invention Detail
    /disclosure/[id]       → Disclosure Draft
    /prior-art/[id]        → Prior Art Results
    /bundles               → Filing Bundles
    /bundles/new           → Create Filing Bundle
    /handoffs              → Handoff History
  /settings                → Platform Settings
    /account               → Account Settings
    /billing               → Billing & Plans
    /team                  → Team Management
    /api-keys              → API Key Management
    /jurisdictions         → Active Jurisdictions
  /attorney-portal         → Attorney Review Portal (scoped JWT, no Clerk)
    /[handoff-id]          → Handoff Review Page
```

---

## Platform Screens

### `/` — Landing Page

**Route Type:** Static (marketing)  
**Auth:** None (public)  
**Permissions:** N/A  

**Content:**
- Hero section: "AI-Powered Legal Intelligence & IP Protection"
- Feature cards: LexCore (search, research, monitoring) + LexRadar (scan, score, draft, file)
- Pricing tiers: SOLO ($49/mo), FIRM ($199/mo), ENTERPRISE (custom)
- CTA: "Start Free Trial" → `/app`

**Key Actions:**
- Navigate to sign-in
- View pricing
- Contact sales (ENTERPRISE)

**Data Dependencies:** None (static)

---

### `/app` — Application Shell

**Route Type:** Layout  
**Auth:** Required (Clerk)  
**Permissions:** Any authenticated user

**Content:**
- Sidebar navigation (LexCore, LexRadar, Settings)
- Header with tenant name, user avatar, search bar
- Main content area (renders child routes)
- Breadcrumbs

**Key Actions:**
- Navigate between domains
- Global search (Ctrl+K)
- Notifications bell
- User menu (profile, sign out)

**Data Dependencies:**
- `GET /v1/mcp/capabilities` — Navigation items based on tenant tier
- `GET /v1/lexcore/monitor-rules?status=ACTIVE` — Active monitor rules (badge count)

---

## LexCore Screens

### `/app/lexcore/dashboard` — LexCore Dashboard

**Route Type:** Server Component  
**Auth:** Required  
**Permissions:** `read` on `legal_documents`

**Content:**
- Stats cards: documents indexed, jurisdictions covered, last search, active monitors
- Recent searches (last 5)
- Recent documents viewed (last 5)
- Active monitor rules with alert counts
- Jurisdiction coverage chart

**Key Actions:**
- Navigate to search
- Navigate to research tasks
- Navigate to monitor rules
- View jurisdiction coverage

**Data Dependencies:**
- `GET /v1/lexcore/documents?limit=5` — Recent documents
- `GET /v1/lexcore/monitor-rules` — Monitor rules + alert counts
- `GET /v1/mcp/capabilities` — Jurisdiction coverage stats

---

### `/app/lexcore/search` — Legal Search

**Route Type:** Client Component (interactive)  
**Auth:** Required  
**Permissions:** `read` on `legal_documents`

**Content:**
- Search input with placeholder: "Search statutes, regulations, case law..."
- Filters: Jurisdiction dropdown, Body of Law (STATUTE/REGULATION/CASE), Date range
- Search results list (cards)
- Pagination
- "Search with AI" toggle → triggers research_task

**Search Result Card:**
- Title + citation
- Jurisdiction badge
- Body of law badge
- Summary snippet (highlighted query matches)
- Relevance score
- "View Document" button
- "Get Citations" button

**Key Actions:**
- Submit search query
- Apply filters
- Navigate to document detail
- Trigger citation graph
- Toggle AI research mode

**Data Dependencies:**
- `POST /v1/mcp/search_legal` — Search results
- `GET /v1/mcp/jurisdiction/{code}` — Jurisdiction options

**State:**
- Query string
- Active filters
- Pagination (limit/offset)
- Results cache (SWR)

---

### `/app/lexcore/document/[id]` — Document Detail

**Route Type:** Server Component + Client Component (tabs)  
**Auth:** Required  
**Permissions:** `read` on `legal_documents`

**Content (Tabs):**
1. **Overview:** Full metadata, summary, source URL, version history
2. **Full Text:** Document content with chunk navigation
3. **Citations:** Forward and backward citation lists
4. **Citation Graph:** Interactive graph visualization (D3/vis.js)
5. **History:** Version changes, amendment tracking

**Key Actions:**
- Navigate between tabs
- Copy citation
- Export to PDF
- Add to research task
- Create monitor rule from document

**Data Dependencies:**
- `GET /v1/mcp/document?doc_id={id}` — Document + chunks
- `POST /v1/mcp/citations` — Citation graph

---

### `/app/lexcore/research` — Research Tasks

**Route Type:** Server Component  
**Auth:** Required  
**Permissions:** `read` on `research_tasks`

**Content:**
- "New Research" button → opens modal
- List of research tasks (table)
  - Question (truncated)
  - Status (PENDING/RUNNING/COMPLETED/FAILED)
  - Confidence score (if completed)
  - Gap detected flag
  - Created date
  - Actions: View, Re-run, Delete

**Key Actions:**
- Create new research task
- View research result
- Re-run failed task
- Delete old tasks

**Data Dependencies:**
- `GET /v1/lexcore/research-tasks` — Task list

---

### `/app/lexcore/research/[id]` — Research Result

**Route Type:** Server Component  
**Auth:** Required  
**Permissions:** `read` on `research_tasks`

**Content:**
- Original question
- Status badge + progress bar (if running)
- Structured report (markdown rendered)
- Citation chain (linked documents)
- Confidence score with visual indicator
- Gap detection banner (if gaps found)
- Gap list with "Search for this" buttons

**Key Actions:**
- Export report (PDF, Word)
- Copy citations
- Navigate to cited documents
- Trigger follow-up search for gaps

**Data Dependencies:**
- `GET /v1/lexcore/research-tasks/{id}` — Task + result

---

### `/app/lexcore/monitor` — Monitor Rules

**Route Type:** Server Component  
**Auth:** Required  
**Permissions:** `read` on `monitor_rules`

**Content:**
- "Create Rule" button
- List of monitor rules (cards)
  - Rule name
  - Jurisdiction(s)
  - Keywords
  - Status (ACTIVE/PAUSED/ARCHIVED)
  - Last triggered
  - Unacknowledged alert count
  - Actions: Edit, Pause/Resume, Delete, View Alerts

**Key Actions:**
- Create new rule
- Edit existing rule
- Pause/resume rule
- Delete rule
- View alerts for rule

**Data Dependencies:**
- `GET /v1/lexcore/monitor-rules` — Rule list

---

### `/app/lexcore/monitor/new` — Create Monitor Rule

**Route Type:** Client Component (form)  
**Auth:** Required  
**Permissions:** `write` on `monitor_rules`

**Content:**
- Rule name input
- Jurisdiction selector (multi-select)
- Body of law selector (optional)
- Keywords input (comma-separated, with tag UI)
- "Preview matches" button → shows sample matching documents
- Submit / Cancel

**Data Dependencies:**
- `GET /v1/mcp/capabilities` — Jurisdiction options
- `POST /v1/mcp/search_legal` — Preview matches

---

### `/app/lexcore/jurisdictions` — Jurisdiction Browser

**Route Type:** Server Component  
**Auth:** Required  
**Permissions:** `read` on `jurisdictions`

**Content:**
- Grid of jurisdiction cards
  - Flag/icon
  - Name
  - Coverage percentage (progress bar)
  - Document count
  - Last ingest date
  - Sources list
  - "View Recent Changes" link

**Key Actions:**
- Navigate to jurisdiction detail (future: per-jurisdiction document browser)
- Toggle jurisdiction activation (add/remove from tenant)

**Data Dependencies:**
- `GET /v1/mcp/capabilities` — Jurisdiction stats

---

## LexRadar Screens

### `/app/lexradar/dashboard` — LexRadar Dashboard

**Route Type:** Server Component  
**Auth:** Required  
**Permissions:** `read` on `invention_candidates`

**Content:**
- Stats cards: inventions detected, disclosures drafted, prior art searches run, handoffs delivered
- Pipeline visualization (horizontal stages)
  - DETECTED → SCORING → SCORED → DISCLOSING → DISCLOSED → FILED
  - Count at each stage
- Recent inventions (last 5)
- Recent handoffs (last 5)
- Quick actions: "Scan Now", "New Disclosure", "Create Bundle"

**Key Actions:**
- Trigger code scan
- Navigate to inventions
- Navigate to disclosures
- Navigate to handoffs

**Data Dependencies:**
- `GET /v1/lexradar/inventions?limit=5` — Recent inventions
- `GET /v1/lexradar/handoffs?limit=5` — Recent handoffs

---

### `/app/lexradar/inventions` — Invention Candidates

**Route Type:** Server Component + Client Component (filters)  
**Auth:** Required  
**Permissions:** `read` on `invention_candidates`

**Content:**
- Filter bar: Status dropdown, Source type, Date range, Score threshold
- Sort: Composite score, Detection date, Status
- Invention cards (grid or list view)
  - Title
  - Source (GitHub/Jira/Notion icon + link)
  - Detection date
  - Status badge
  - Score bars (6 dimensions: novelty, nonobviousness, utility, enablement, scope, evidence)
  - Composite score
  - Actions: View, Score Now, Generate Disclosure

**Key Actions:**
- Filter by status
- Sort by score/date
- Navigate to invention detail
- Trigger scoring
- Generate disclosure

**Data Dependencies:**
- `GET /v1/lexradar/inventions` — Invention list with filters

---

### `/app/lexradar/invention/[id]` — Invention Detail

**Route Type:** Server Component  
**Auth:** Required  
**Permissions:** `read` on `invention_candidates`

**Content:**
- Title + description
- Source link (GitHub PR, Jira ticket, Notion page)
- Detection metadata
- Score radar chart (6 dimensions)
- Composite score with visual gauge
- Prior art status (searched/pending)
- Disclosure status (generated/pending)
- Actions panel:
  - "Run Prior Art Search" → triggers AGT_PRIORART
  - "Generate Disclosure" → triggers AGT_DISCLOSER
  - "Create Handoff" → available after disclosure approved

**Key Actions:**
- Run prior art search
- View prior art results
- Generate disclosure
- View disclosure draft
- Create handoff

**Data Dependencies:**
- `GET /v1/lexradar/inventions/{id}` — Invention detail
- `GET /v1/lexradar/inventions/{id}/prior-art` — Prior art results

---

### `/app/lexradar/disclosure/[id]` — Disclosure Draft

**Route Type:** Client Component (rich text editing)  
**Auth:** Required  
**Permissions:** `read` on `disclosures`

**Content (10 LHP Sections as tabs/sections):**
1. **Abstract** (read-only)
2. **Inventor** (read-only)
3. **Title** (read-only)
4. **Background** (read-only)
5. **Summary** (read-only)
6. **Detailed Description** (editable)
7. **Claims** (editable)
8. **Drawings Description** (read-only)
9. **Abstract of Invention** (read-only)
10. **Advantages** (read-only)
11. **Alternative Implementations** (editable)
12. **Example** (read-only)
13. **Prior Art Summary** (read-only)
14. **References** (read-only)
15. **Grounding Sources** (read-only)
16. **Additional Materials** (read-only)

- Grounding score badge
- Status: DRAFT / REVIEWING / APPROVED / REJECTED / REQUESTED_CHANGES
- "Request Attorney Review" button (available when APPROVED)

**Key Actions:**
- Edit editable sections
- Save draft (auto-save every 30s)
- Preview final document
- Request attorney review
- View prior art evidence

**Data Dependencies:**
- `GET /v1/lexradar/disclosures/{id}` — Disclosure draft
- `PATCH /v1/lexradar/disclosures/{id}` — Save edits

---

### `/app/lexradar/prior-art/[id]` — Prior Art Results

**Route Type:** Server Component  
**Auth:** Required  
**Permissions:** `read` on `prior_art`

**Content:**
- Search summary: sources searched, results found, search date
- Prior art list (table)
  - Source icon (USPTO, WIPO, EPO, etc.)
  - Patent number
  - Title
  - Authors
  - Published date
  - Relevance score (progress bar)
  - Actions: View details, Add to report
- Filter by source, relevance threshold

**Key Actions:**
- Filter by source
- Sort by relevance
- View patent details (external link)
- Export prior art report

**Data Dependencies:**
- `GET /v1/lexradar/inventions/{id}/prior-art` — Prior art results

---

### `/app/lexradar/bundles` — Filing Bundles

**Route Type:** Server Component  
**Auth:** Required  
**Permissions:** `read` on `filing_bundles`

**Content:**
- "Create Bundle" button
- Bundle list (table)
  - Bundle name
  - Patent type (PROVISIONAL/NON_PROVISIONAL/PCT)
  - Status (DRAFT/READY/SUBMITTED/ARCHIVED)
  - Disclosures count
  - Package size
  - Created date
  - Actions: Download, View, Archive

**Key Actions:**
- Create new bundle
- Download bundle (ZIP)
- View bundle details
- Archive bundle

**Data Dependencies:**
- `GET /v1/lexradar/filing-bundles` — Bundle list

---

### `/app/lexradar/bundles/new` — Create Filing Bundle

**Route Type:** Client Component (form)  
**Auth:** Required  
**Permissions:** `write` on `filing_bundles`

**Content:**
- Bundle name input
- Patent type selector
- Disclosure selector (multi-select, only APPROVED disclosures)
- Disclosure sort order (drag-and-drop)
- Disclosure role: PRIMARY / SECONDARY / REFERENCE
- Preview panel
- Submit / Cancel

**Data Dependencies:**
- `GET /v1/lexradar/disclosures?status=APPROVED` — Approved disclosures

---

### `/app/lexradar/handoffs` — Handoff History

**Route Type:** Server Component  
**Auth:** Required  
**Permissions:** `read` on `attorney_reviews`

**Content:**
- Handoff list (table)
  - Handoff ID
  - Disclosure title
  - Attorney name + email
  - Status (DELIVERED/OPENED/IN_PROGRESS/APPROVED/REJECTED/REQUESTED_CHANGES)
  - Portal URL (copy button)
  - Expires at
  - Reviewed at
  - Actions: Resend, Revoke, View Review

**Key Actions:**
- Resend handoff email
- Revoke handoff (invalidate portal link)
- View attorney review details
- Navigate to disclosure

**Data Dependencies:**
- `GET /v1/lexradar/handoffs` — Handoff list

---

## Settings Screens

### `/app/settings/account` — Account Settings

**Route Type:** Client Component  
**Auth:** Required  
**Permissions:** Own account only

**Content:**
- User profile (Clerk `<UserProfile>`)
- Display name
- Email preferences
- Notification settings
- Danger zone: Delete account

---

### `/app/settings/billing` — Billing & Plans

**Route Type:** Server Component + Client Component  
**Auth:** Required  
**Permissions:** `admin` role required for plan changes

**Content:**
- Current plan card (SOLO/FIRM/ENTERPRISE)
- Usage stats: API calls this month, research tasks, monitor rules
- Upgrade/downgrade options
- Payment method (Stripe Elements)
- Invoice history
- Cancel subscription

**Data Dependencies:**
- `GET /v1/settings/billing` — Billing info
- Stripe API (client-side)

---

### `/app/settings/team` — Team Management

**Route Type:** Server Component + Client Component  
**Auth:** Required  
**Permissions:** `admin` role required

**Content:**
- Team member list (table)
  - Name, email, role, last login, status
  - Actions: Change role, Remove
- "Invite Member" button → email input + role selector
- Pending invitations

**Data Dependencies:**
- `GET /v1/settings/team` — Team members
- `POST /v1/settings/team/invite` — Invite member

---

### `/app/settings/api-keys` — API Key Management

**Route Type:** Server Component + Client Component  
**Auth:** Required  
**Permissions:** `admin` role required

**Content:**
- API key list (table)
  - Name, scopes, created, last used, expires, status
  - Actions: Copy, Revoke, Regenerate
- "Create Key" button → name + scopes selector
- Usage stats per key

**Data Dependencies:**
- `GET /v1/settings/api-keys` — Key list
- `POST /v1/settings/api-keys` — Create key

---

### `/app/settings/jurisdictions` — Active Jurisdictions

**Route Type:** Server Component  
**Auth:** Required  
**Permissions:** `admin` role required

**Content:**
- Available jurisdictions list
  - Name, code, coverage %, document count
  - Toggle to activate/deactivate
- Active jurisdictions summary
- Coverage chart

**Data Dependencies:**
- `GET /v1/mcp/capabilities` — All jurisdictions
- `GET /v1/settings/jurisdictions` — Tenant active jurisdictions

---

## Attorney Portal Screens

### `/attorney-portal/[handoff-id]` — Handoff Review Page

**Route Type:** Client Component (public, scoped JWT)  
**Auth:** Scoped JWT (no Clerk, 48h expiry)  
**Permissions:** `handoff:read handoff:edit handoff:action`

**Content:**
- Header: Client name, invention title, attorney name
- Expiry countdown banner
- 10-section LHP disclosure (same as disclosure draft)
- 3 editable sections with rich text editor:
  - Claims
  - Detailed Description
  - Abstract (of invention)
- Auto-save indicator
- Evidence panel (prior art results, grounding sources)
- Action buttons:
  - **Approve** → Success modal + client notification
  - **Reject** → Rejection reason textarea + submit
  - **Request Changes** → Changes textarea + submit

**Key Actions:**
- Edit 3 sections
- Auto-save (every 30s)
- Approve disclosure
- Reject with reason
- Request changes with details

**Data Dependencies:**
- `GET /v1/lexradar/handoffs/{handoff-id}` — Handoff package (with scoped JWT)
- `PATCH /v1/lexradar/handoffs/{handoff-id}` — Save edits (with scoped JWT)
- `POST /v1/lexradar/handoffs/{handoff-id}/review` — Submit review (with scoped JWT)

---

## Shared Components

### Global Search (Ctrl+K)

**Trigger:** Keyboard shortcut or header search icon  
**Content:**
- Modal with search input
- Results grouped by type: Documents, Research Tasks, Inventions, Disclosures
- Quick navigation
- Recent searches

### Notifications Panel

**Trigger:** Header bell icon  
**Content:**
- Monitor alerts (unacknowledged)
- Handoff status updates
- System notifications
- Mark all as read

---

## Screen Dependencies Matrix

| Screen | Server Component | Client Component | Clerk Auth | API Key Auth | Data Fetching |
|--------|-----------------|-----------------|------------|--------------|---------------|
| Landing | Yes | No | No | No | None |
| App Shell | Yes | Yes | Yes | No | Capabilities |
| LexCore Dashboard | Yes | No | Yes | No | Documents, Monitors |
| Search | No | Yes | Yes | No | search_legal |
| Document Detail | Yes | Yes | Yes | No | document, citations |
| Research Tasks | Yes | No | Yes | No | research_tasks |
| Research Result | Yes | No | Yes | No | research_task |
| Monitor Rules | Yes | No | Yes | No | monitor_rules |
| Monitor New | No | Yes | Yes | No | capabilities, preview |
| Jurisdictions | Yes | No | Yes | No | capabilities |
| LexRadar Dashboard | Yes | No | Yes | No | inventions, handoffs |
| Inventions | Yes | Yes | Yes | No | inventions |
| Invention Detail | Yes | Yes | Yes | No | invention, prior_art |
| Disclosure Draft | No | Yes | Yes | No | disclosure |
| Prior Art | Yes | No | Yes | No | prior_art |
| Bundles | Yes | No | Yes | No | filing_bundles |
| Bundles New | No | Yes | Yes | No | disclosures |
| Handoffs | Yes | No | Yes | No | handoffs |
| Settings Account | No | Yes | Yes | No | Clerk profile |
| Settings Billing | Yes | Yes | Yes | No | billing |
| Settings Team | Yes | Yes | Yes | No | team |
| Settings API Keys | Yes | Yes | Yes | No | api_keys |
| Settings Jurisdictions | Yes | No | Yes | No | jurisdictions |
| Attorney Portal | No | Yes | No | Yes (scoped JWT) | handoff |

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-29 | Initial screen map | C06 frontend definition |
