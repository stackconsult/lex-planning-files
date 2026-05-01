# JTBD_MAP.md — Jobs To Be Done: LexCore + LexRadar

> **Build System:** Unified Build System v2  
> **Chunk:** C01 — Product Definition  
> **Horde:** HORDE-ARCH  

---

## What is JTBD?

Jobs To Be Done identifies the "job" a user "hires" a product to do — the progress they want to make in a particular circumstance. For LexCore + LexRadar, we map jobs by user role, circumstance, and desired outcome.

---

## LexCore Jobs

### Job 1: "Help me find the exact legal precedent I need, even when I don't know the right terms."

**User:** IP attorney at a mid-size firm  
**Circumstance:** Drafting a patent infringement opinion, need to find case law on "obviousness in software patents post-Alice"  
**Current Struggle:** Westlaw/Lexis search returns 500+ results; relevance ranking is poor; no citation authority visualization; no legislative change alerts  
**Desired Outcome:** Top 10 ranked results with full citation chains, authority scores, and flagging of overruled cases — in under 5 seconds  
**Success Metric:** precision@10 > 0.85  

**Functional Requirements:**
- Hybrid vector + full-text search (hierarchical chunking)
- Citation graph traversal (forward/backward, depth 3)
- Authority scoring (based on citation count, jurisdiction hierarchy)
- Overruled case detection
- Bilingual support (English + French for Canadian sources)

**Emotional Drivers:**
- Confidence: "I didn't miss the key case"
- Speed: "I found it faster than my associate would have"
- Completeness: "The citation chain shows I'm covered"

---

### Job 2: "Alert me immediately when the law changes in a way that affects my client's compliance."

**User:** Compliance team lead at a technology company  
**Circumstance:** Monitoring US Federal, California state, and EU regulations for privacy and AI governance  
**Current Struggle:** Manual monitoring of Federal Register, state legislature sites, and EUR-Lex; alerts via email newsletters are noisy and untargeted  
**Desired Outcome:** Configurable monitor rules per jurisdiction + body_of_law; 24h detection SLA; structured change summary with impact assessment  
**Success Metric:** 100% of changes in monitored areas detected within 24h  

**Functional Requirements:**
- Monitor rule CRUD (jurisdiction, body_of_law, alert_type)
- Change detection via scheduled ingestion diff
- Structured change summary (what changed, previous version, current version)
- Alert delivery (in-app, email, webhook)
- Historical change tracking

**Emotional Drivers:**
- Control: "I'm on top of every change"
- Safety: "My client won't be surprised by a new regulation"
- Efficiency: "No more manual checking of 12 different websites"

---

### Job 3: "Give me a research report on a complex legal question with sources I can cite."

**User:** Senior associate at a large law firm  
**Circumstance:** Partner asks for a memo on "whether our client's AI training data use falls under fair use"  
**Current Struggle:** Manual research across cases, statutes, regulations, and commentaries; synthesis takes 8+ hours; risk of missing key sources  
**Desired Outcome:** Structured research report with question decomposition, sub-question answers, source citations, and gap detection — generated in < 10 minutes  
**Success Metric:** Research task completeness score > 0.85 (partner judgment)  

**Functional Requirements:**
- Question decomposition (complex → sub-questions)
- Parallel search per sub-question
- Synthesis with inline citations
- Citation chain extraction
- Gap detection ("no case law found on X aspect")
- Export to Word/PDF with proper citation formatting

**Emotional Drivers:**
- Competence: "This memo is partner-ready"
- Thoroughness: "I covered all the angles"
- Speed: "I delivered this in an hour, not a day"

---

### Job 4: "Show me the authoritative source for a legal citation I was given."

**User:** Paralegal or junior associate  
**Circumstance:** Received citation `410 U.S. 113` in a brief, need to verify text and context  
**Current Struggle:** Google search returns Wikipedia first; official source (CourtListener) is buried; no chunk-level navigation  
**Desired Outcome:** Direct document retrieval by citation with chunk-level browsing, related cases, and legislative history  
**Success Metric:** Citation resolution < 2 seconds (cached), < 5 seconds (uncached)  

**Functional Requirements:**
- Citation-based document lookup (standard formats)
- Chunk-level navigation (hierarchical: Title → Chapter → Section)
- Related cases and legislative history sidebar
- Full-text download (PDF)
- Citation export (Bluebook, ALWD, etc.)

---

## LexRadar Jobs

### Job 5: "Capture patentable inventions from our engineering work before they're lost."

**User:** IP operations manager at a technology company  
**Circumstance:** Engineering team ships features weekly; inventions are discussed in PRs, Jira tickets, and Notion docs but never formally captured  
**Current Struggle:** Manual invention disclosure meetings are skipped; engineers don't know what's patentable; 60%+ of patentable ideas are lost  
**Desired Outcome:** Autonomous scanning of GitHub/Jira/Notion for invention signals; scored candidates delivered to IP team dashboard; 80%+ recall of patentable inventions  
**Success Metric:** Invention detection recall > 0.80 (compared to manual review)  

**Functional Requirements:**
- Connector integration (GitHub, Jira, Notion)
- Signal classification (novel algorithm, system architecture, UI innovation, etc.)
- Invention candidate scoring (novelty, nonobviousness indicators)
- IP team dashboard with candidate queue
- Engineer notification (opt-in: "Your PR may contain a patentable idea")

**Emotional Drivers:**
- Protection: "We're not losing valuable IP"
- Recognition: "Engineers get credit for their innovations"
- Efficiency: "No more manual invention mining meetings"

---

### Job 6: "Tell me if this invention is patentable before I spend $50K on a disclosure."

**User:** IP attorney evaluating an invention candidate  
**Circumstance:** Engineer submitted an invention disclosure; attorney needs to assess patentability before investing in prior art search and drafting  
**Current Struggle:** Preliminary assessment is gut-feel; no structured scoring; prior art search is expensive and slow; attorney time is $500+/hour  
**Desired Outcome:** 6-dimension patentability score with prior art comparison, relevance ranking, and recommendation (proceed / refine / decline) — in < 30 minutes  
**Success Metric:** Attorney agreement with system recommendation > 0.80  

**Functional Requirements:**
- 6-dimension scoring (novelty, nonobviousness, enablement, written description, definiteness, utility)
- Parallel prior art search (7 sources)
- Prior art relevance ranking with claim mapping
- Score explanation (why this score, what prior art influenced it)
- Recommendation engine (proceed / refine / decline with rationale)

**Emotional Drivers:**
- Confidence: "I'm making this decision with data"
- Efficiency: "I assessed this in 30 min, not 3 days"
- Risk management: "I know the prior art landscape before drafting"

---

### Job 7: "Draft a patent disclosure that I can review and file with minimal edits."

**User:** IP attorney or in-house counsel  
**Circumstance:** Invention approved for patenting; need to draft a 10-section provisional disclosure  
**Current Struggle:** Drafting takes 2-3 days; claims are hardest part; attorney drafts then sends to inventor for review, then back to attorney — cycle takes weeks  
**Desired Outcome:** Auto-generated 10-section disclosure with claims, grounded in actual invention evidence (commits, PRs, docs), editable in portal, ready for attorney review in < 2 hours  
**Success Metric:** GroundingJudge score > 0.85 (claims supported by evidence)  

**Functional Requirements:**
- 10 LHP section generation (title, field, background, summary, detailed description, claims, abstract, drawings, etc.)
- Claim theme extraction and drafting
- Grounding check (every claim maps to evidence in source data)
- Attorney portal with 3 editable sections (claims, detailed description, abstract)
- Version control and change tracking

**Emotional Drivers:**
- Quality: "This draft is solid — minimal edits needed"
- Speed: "I reviewed and approved this in 2 hours, not 2 weeks"
- Grounding: "Every claim is backed by actual code/commits"

---

### Job 8: "Give me a blockchain-anchored proof package that proves we invented this first."

**User:** IP attorney preparing for potential litigation or licensing  
**Circumstance:** Need to prove invention date and disclosure completeness for a patent  
**Current Struggle:** Lab notebooks are paper-based or scattered in Google Docs; no immutable timestamp; opposing counsel challenges invention date  
**Desired Outcome:** Download a filing bundle with blockchain-anchored proof (SHA-256 hashes on Polygon), evidence chain, and attorney review certificate  
**Success Metric:** Proof package accepted by USPTO / court as evidence of invention date  

**Functional Requirements:**
- Document + bundle hash generation (SHA-256)
- Polygon mainnet anchoring (transaction hash, block number)
- Proof package assembly (9 documents + proof ledger)
- Secure download link (scoped JWT, time-limited)
- Attorney review certificate (signed approval)

**Emotional Drivers:**
- Security: "This proof is tamper-evident"
- Professionalism: "My client has bulletproof evidence"
- Peace of mind: "Even if notebooks are lost, the blockchain record remains"

---

### Job 9: "Review a disclosure handoff package and approve, reject, or request changes — all in one portal."

**User:** External IP attorney reviewing a client handoff  
**Circumstance:** Client (tech company) sent a disclosure handoff via email with 10 attachments; attorney needs to review, provide feedback, and decide on filing  
**Current Struggle:** Email threads with 10 attachments; no version control; feedback is in email text; no structured approval workflow  
**Desired Outcome:** Single portal with handoff package (10 sections, 3 editable), claim theme editor, evidence chain viewer, and approve/reject/request-changes buttons — with scoped access (48h JWT)  
**Success Metric:** Attorney completes review in < 1 hour (vs. 3+ hours via email)  

**Functional Requirements:**
- Scoped JWT portal access (48h, single attorney, single handoff)
- 10-section handoff viewer (3 editable: claims, detailed description, abstract)
- Claim theme editor with syntax highlighting
- Evidence chain viewer (read-only, links to source commits/PRs)
- Prior art comparison table
- Action buttons: Approve / Reject / Request Changes
- Feedback form with structured fields
- Filing bundle download (PDF/ZIP)

**Emotional Drivers:**
- Convenience: "Everything I need is in one place"
- Professionalism: "This is how client handoffs should work"
- Control: "I can edit claims directly in the portal"

---

## Job Priority Matrix

| Job | User | Frequency | Value | Pain | Priority |
|-----|------|-----------|-------|------|----------|
| 1 | IP attorney (LexCore) | Daily | High | High | P0 |
| 5 | IP operations (LexRadar) | Weekly | High | High | P0 |
| 7 | IP attorney (LexRadar) | Weekly | High | High | P0 |
| 2 | Compliance team | Daily | High | Medium | P1 |
| 6 | IP attorney (LexRadar) | Weekly | High | Medium | P1 |
| 9 | External IP attorney | Weekly | High | Medium | P1 |
| 3 | Senior associate | Weekly | Medium | High | P2 |
| 8 | IP attorney (litigation) | Monthly | Medium | Medium | P2 |
| 4 | Paralegal/junior | Daily | Medium | Low | P3 |

---

## Job → Feature Mapping

| Job # | Primary Feature | Chunk |
|-------|----------------|-------|
| 1 | Hybrid search + citation graph | C04/C05 |
| 2 | Monitor rules + change detection | C05 |
| 3 | Research task decomposition | C05 |
| 4 | Document retrieval by citation | C04 |
| 5 | Invention detection + scanning | C05 |
| 6 | Prior art search + 6-dim scoring | C05 |
| 7 | Disclosure draft generation | C05 |
| 8 | Blockchain proof anchoring | C05 |
| 9 | Attorney portal handoff | C06 |

---

## Job → Activation Event Mapping

| Job # | Activation Event | Measurement |
|-------|-----------------|-------------|
| 1 | First search with citation chain viewed | `first_value_action.completed` |
| 2 | First alert received and acknowledged | `first_value_action.completed` |
| 3 | First research report exported | `first_value_action.completed` |
| 5 | First invention candidate detected from code | `first_value_action.completed` |
| 7 | First disclosure approved by attorney | `first_value_action.completed` |
| 9 | First handoff package action (approve/request changes) | `first_value_action.completed` |
