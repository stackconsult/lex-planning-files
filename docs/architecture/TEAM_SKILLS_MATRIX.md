---
name: lexcore-lexradar-team-skills
description: Define required team skills for each architecture segment of LexCore + LexRadar system. Use when hiring, planning team composition, conducting skill gap analysis, or determining training requirements for backend, frontend, DevOps, ML/AI, security, data engineering, blockchain, and legal domain expertise.
license: MIT
metadata:
  author: LexCore + LexRadar Architecture Team
  version: "2.0.0"
  framework: Microsoft Skills Format v2.0
  source: microsoft/skills marketplace
---

# Team Skills Matrix — LexCore + LexRadar

> **Date:** 2026-05-02  
> **Purpose:** Define required team skills for each architecture segment  
> **Scope:** Full system (L0-L7)  
> **Use Case:** Hiring, team composition, skill gap analysis  
> **Format:** Based on Microsoft Skills Format v2.0 from microsoft/skills marketplace

---

## Executive Summary

LexCore + LexRadar requires **multi-disciplinary team** with expertise across 8 architecture layers. Key skill clusters:

**Primary Skill Clusters:**
1. **Backend Engineering** — Python, FastAPI, async/await, PostgreSQL
2. **Frontend Engineering** — Next.js, TypeScript, React, Tailwind
3. **DevOps/Infrastructure** — Kubernetes, AWS, Terraform, CI/CD
4. **Data Engineering** — ETL, vector databases, search optimization
5. **Security Engineering** — RLS, JWT, encryption, compliance
6. **ML/AI Engineering** — Embeddings, LLM integration, prompt engineering
7. **Legal Domain Expertise** — Patent law, legal document parsing
8. **Blockchain Engineering** — Polygon, smart contracts, IP anchoring

**Minimum Team Size:** 8-10 engineers for MVP
**Recommended Team Size:** 12-15 engineers for production

## Quick Start

Use this skills matrix to:
1. **Hiring:** Match candidate skills to required levels (Junior/Intermediate/Advanced/Expert)
2. **Team Composition:** Determine optimal team size and role distribution
3. **Skill Gap Analysis:** Identify missing skills in current team
4. **Training Planning:** Define learning paths for skill development
5. **Project Planning:** Ensure team has required expertise for each architecture layer

---

## Part 1: Skills Matrix by Architecture Layer

### L0: External Sources (9 Legal + 7 Patent + 3 Code)

**Required Skills:**

| Skill | Level | Role | Why Needed |
|-------|-------|------|------------|
| **API Integration** | Intermediate | Backend Engineer | Connect to 19 external APIs with different auth patterns |
| **Webhook Handling** | Intermediate | Backend Engineer | Process GitHub/Jira/Notion webhooks in real-time |
| **Rate Limiting** | Intermediate | Backend Engineer | Respect source rate limits (20-120 req/min) |
| **HTML/XML Parsing** | Intermediate | Backend Engineer | Parse legal documents from eCFR, CourtListener, etc. |
| **OAuth 1.0a/2.0** | Intermediate | Backend Engineer | Authenticate with WIPO, EPO, Lens APIs |
| **Error Handling** | Intermediate | Backend Engineer | Handle API failures, timeouts, rate limit errors |
| **Data Validation** | Intermediate | Backend Engineer | Validate source schemas, detect malformed data |

**Team Composition:**
- **1-2 Backend Engineers** with API integration experience
- **Skill Level:** Intermediate (2-3 years experience)

**Estimated Onboarding Time:** 2-3 weeks per connector

---

### L1: Connectors / Ingestion Workers

**Required Skills:**

| Skill | Level | Role | Why Needed |
|-------|-------|------|------------|
| **Python Async** | Advanced | Backend Engineer | Async/await for high-throughput ingestion |
| **Document Parsing** | Intermediate | Backend Engineer | Docling parser for HTML, PDF, Markdown, Word |
| **Chunking Strategies** | Intermediate | Backend Engineer | Hierarchical chunking (section/paragraph/sentence) |
| **Embedding Services** | Intermediate | ML/AI Engineer | OpenAI text-embedding-3-large integration |
| **Celery** | Advanced | Backend Engineer | Task queues, retries, circuit breakers, DLQ |
| **Redis** | Intermediate | Backend Engineer | Cache, queue backend, session management |
| **Idempotency Design** | Intermediate | Backend Engineer | Prevent duplicate ingestion on retry |

**Team Composition:**
- **1 Backend Engineer** with Celery/async experience
- **1 ML/AI Engineer** for embedding optimization
- **Skill Level:** Advanced (4-5 years experience)

**Estimated Onboarding Time:** 3-4 weeks

---

### L2: Storage Layer

**Required Skills:**

| Skill | Level | Role | Why Needed |
|-------|-------|------|------------|
| **PostgreSQL** | Advanced | Backend/DB Engineer | RLS, pgvector, indexes, migrations |
| **pgvector** | Intermediate | Backend/DB Engineer | HNSW indexes, vector similarity search |
| **Full-Text Search** | Intermediate | Backend/DB Engineer | GIN indexes, tsvector, ranking |
| **Redis** | Intermediate | Backend/DB Engineer | ElastiCache, multi-DB, eviction policies |
| **Qdrant** | Intermediate | ML/AI Engineer | Vector database, HNSW tuning, payload filtering |
| **S3/R2** | Intermediate | DevOps Engineer | Object storage, encryption, lifecycle policies |
| **Connection Pooling** | Intermediate | Backend Engineer | asyncpg, pool sizing, timeout tuning |
| **Database Migrations** | Intermediate | Backend/DB Engineer | Alembic, upgrade/downgrade symmetry |

**Team Composition:**
- **1 Backend/DB Engineer** with PostgreSQL expertise
- **1 ML/AI Engineer** for Qdrant optimization
- **1 DevOps Engineer** for S3/R2 management
- **Skill Level:** Advanced (5+ years experience)

**Estimated Onboarding Time:** 4-6 weeks

---

### L3: Services / Workers / Agents

**Required Skills:**

| Skill | Level | Role | Why Needed |
|-------|-------|------|------------|
| **FastAPI** | Advanced | Backend Engineer | Async endpoints, Pydantic validation, OpenAPI |
| **SQLAlchemy ORM** | Intermediate | Backend Engineer | Async sessions, repositories, query optimization |
| **Service Layer Design** | Intermediate | Backend Engineer | Bounded contexts, repository pattern |
| **Celery Chains/Groups** | Advanced | Backend Engineer | Pipeline orchestration, task dependencies |
| **Event-Driven Architecture** | Intermediate | Backend Engineer | Event schemas, consumer groups, DLQ |
| **Agent Design Patterns** | Intermediate | Backend/ML Engineer | Agent isolation, contract enforcement |
| **Circuit Breaker Pattern** | Intermediate | Backend Engineer | Resilience patterns, failure handling |
| **Graceful Shutdown** | Intermediate | Backend Engineer | SIGTERM handling, queue flushing |

**Team Composition:**
- **2-3 Backend Engineers** with FastAPI/Celery experience
- **1 ML/AI Engineer** for agent design
- **Skill Level:** Advanced (4-5 years experience)

**Estimated Onboarding Time:** 4-5 weeks

---

### L4: API Gateway + MCP Boundary

**Required Skills:**

| Skill | Level | Role | Why Needed |
|-------|-------|------|------------|
| **FastAPI Middleware** | Intermediate | Backend Engineer | Custom middleware, execution order |
| **JWT Authentication** | Intermediate | Backend/Security Engineer | Token validation, claims extraction, refresh rotation |
| **Rate Limiting** | Intermediate | Backend Engineer | Redis sliding window, token bucket |
| **Tenant Context** | Intermediate | Backend Engineer | Session variable injection, RLS integration |
| **API Security** | Intermediate | Security Engineer | CORS, trusted hosts, input validation |
| **OpenAPI Specification** | Intermediate | Backend Engineer | API contracts, versioning, deprecation |
| **Error Handling** | Intermediate | Backend Engineer | Structured errors, exception handlers |

**Team Composition:**
- **1 Backend Engineer** with FastAPI middleware experience
- **1 Security Engineer** for auth/security
- **Skill Level:** Intermediate (3-4 years experience)

**Estimated Onboarding Time:** 2-3 weeks

---

### L5: Frontend / UI / Attorney Portal

**Required Skills:**

| Skill | Level | Role | Why Needed |
|-------|-------|------|------------|
| **Next.js 14+** | Advanced | Frontend Engineer | App Router, server components, nested layouts |
| **TypeScript** | Advanced | Frontend Engineer | Strict mode, type safety, Zod validation |
| **React Query** | Intermediate | Frontend Engineer | Server state, caching, optimistic updates |
| **Tailwind CSS** | Intermediate | Frontend Engineer | Utility-first CSS, responsive design |
| **Shadcn/UI** | Intermediate | Frontend Engineer | Component library, customization |
| **Clerk Integration** | Intermediate | Frontend Engineer | Auth, SSO, session management |
| **Document Rendering** | Intermediate | Frontend Engineer | PDF viewer, syntax highlighting, diff views |
| **Real-time Updates** | Intermediate | Frontend Engineer | SSE/WebSockets, progress tracking |

**Team Composition:**
- **2-3 Frontend Engineers** with Next.js/React experience
- **1 UX Designer** for attorney portal UX
- **Skill Level:** Advanced (4-5 years experience)

**Estimated Onboarding Time:** 3-4 weeks

---

### L6: Observability

**Required Skills:**

| Skill | Level | Role | Why Needed |
|-------|-------|------|------------|
| **Prometheus** | Intermediate | DevOps/SRE Engineer | Metrics collection, querying, alerting |
| **Grafana** | Intermediate | DevOps/SRE Engineer | Dashboards, panels, templating |
| **OpenTelemetry** | Intermediate | Backend/SRE Engineer | Distributed tracing, span propagation |
| **Jaeger** | Intermediate | DevOps/SRE Engineer | Trace visualization, latency analysis |
| **structlog** | Intermediate | Backend Engineer | Structured logging, JSON output |
| **Loki** | Intermediate | DevOps/SRE Engineer | Log aggregation, querying |
| **Alertmanager** | Intermediate | DevOps/SRE Engineer | Alert routing, silencing, grouping |
| **SLO/SLI Design** | Intermediate | SRE Engineer | Error budgets, availability targets |

**Team Composition:**
- **1-2 DevOps/SRE Engineers** with observability experience
- **1 Backend Engineer** for instrumentation
- **Skill Level:** Intermediate (3-4 years experience)

**Estimated Onboarding Time:** 3-4 weeks

---

### L7: CI/CD + Infrastructure

**Required Skills:**

| Skill | Level | Role | Why Needed |
|-------|-------|------|------------|
| **Kubernetes (EKS)** | Advanced | DevOps Engineer | Deployments, services, ingress, HPA |
| **Terraform** | Advanced | DevOps Engineer | Infrastructure as code, state management |
| **Docker** | Intermediate | DevOps Engineer | Multi-stage builds, optimization |
| **CI/CD Pipelines** | Advanced | DevOps Engineer | GitHub Actions, canary deployments, rollbacks |
| **AWS Services** | Advanced | DevOps Engineer | EKS, ElastiCache, S3, Route 53, ACM |
| **HashiCorp Vault** | Intermediate | DevOps/Security Engineer | Secret management, BYOK, audit logging |
| **Network Security** | Intermediate | DevOps/Security Engineer | VPC, security groups, WAF |
| **Cost Optimization** | Intermediate | DevOps Engineer | AWS cost monitoring, right-sizing |

**Team Composition:**
- **2-3 DevOps Engineers** with Kubernetes/AWS experience
- **1 Security Engineer** for Vault/network security
- **Skill Level:** Advanced (5+ years experience)

**Estimated Onboarding Time:** 4-6 weeks

---

## Part 2: Skills Matrix by Functional Area

### Backend Engineering

**Core Skills:**
- Python 3.12+ (Advanced)
- FastAPI (Advanced)
- Async/await (Advanced)
- SQLAlchemy ORM (Intermediate)
- PostgreSQL (Advanced)
- pgvector (Intermediate)
- Redis (Intermediate)
- Celery (Advanced)
- Docker (Intermediate)

**Specializations:**
- **API Layer:** FastAPI middleware, JWT, rate limiting
- **Service Layer:** Repository pattern, bounded contexts
- **Data Layer:** RLS, connection pooling, query optimization
- **Ingestion:** Celery workers, connectors, parsing
- **Agents:** Event-driven architecture, circuit breakers

**Team Size:** 4-5 Backend Engineers

---

### Frontend Engineering

**Core Skills:**
- Next.js 14+ (Advanced)
- TypeScript (Advanced)
- React (Advanced)
- Tailwind CSS (Intermediate)
- React Query (Intermediate)
- Shadcn/UI (Intermediate)
- Clerk (Intermediate)

**Specializations:**
- **LexCore UI:** Search interface, document viewer, monitor dashboard
- **LexRadar UI:** Attorney portal, handoff viewer, claim editor
- **Real-time:** SSE/WebSockets, progress tracking
- **Performance:** Code splitting, lazy loading, caching

**Team Size:** 2-3 Frontend Engineers

---

### DevOps / SRE Engineering

**Core Skills:**
- Kubernetes (EKS) (Advanced)
- Terraform (Advanced)
- Docker (Intermediate)
- AWS (Advanced)
- CI/CD (Advanced)
- Prometheus (Intermediate)
- Grafana (Intermediate)
- OpenTelemetry (Intermediate)

**Specializations:**
- **Infrastructure:** Terraform modules, state management
- **Deployment:** Kubernetes, HPA, canary deployments
- **Observability:** Metrics, logging, tracing, alerting
- **Security:** Vault, network security, compliance

**Team Size:** 2-3 DevOps/SRE Engineers

---

### ML/AI Engineering

**Core Skills:**
- Python (Advanced)
- OpenAI API (Intermediate)
- Embeddings (Intermediate)
- Vector databases (Intermediate)
- LLM integration (Intermediate)
- Prompt engineering (Intermediate)
- Qdrant (Intermediate)

**Specializations:**
- **Embeddings:** text-embedding-3-large, caching, optimization
- **Vector Search:** HNSW tuning, re-ranking, hybrid search
- **LLM Integration:** Disclosure generation, research synthesis
- **Evaluation:** Grounding scores, quality metrics

**Team Size:** 1-2 ML/AI Engineers

---

### Security Engineering

**Core Skills:**
- JWT (Intermediate)
- OAuth 2.0 (Intermediate)
- SAML (Intermediate)
- Encryption (Intermediate)
- PostgreSQL RLS (Intermediate)
- BYOK (Intermediate)
- Compliance (Intermediate)

**Specializations:**
- **Authentication:** Clerk integration, JWT, API keys
- **Authorization:** RLS, tenant isolation, scoped tokens
- **Encryption:** Vault, BYOK, TLS 1.3
- **Compliance:** SOC 2, GDPR, HIPAA

**Team Size:** 1 Security Engineer

---

### Data Engineering

**Core Skills:**
- PostgreSQL (Advanced)
- ETL (Intermediate)
- Data modeling (Intermediate)
- Indexing (Intermediate)
- Migration management (Intermediate)

**Specializations:**
- **Schema Design:** ERD, normalization, denormalization
- **Performance:** Indexing, query optimization, connection pooling
- **Migrations:** Alembic, upgrade/downgrade symmetry
- **Data Quality:** Validation, deduplication, consistency

**Team Size:** 1 Data Engineer (can be shared with Backend)

---

### Blockchain Engineering

**Core Skills:**
- Polygon (Intermediate)
- Smart contracts (Intermediate)
- Web3.py (Intermediate)
- Cryptography (Intermediate)
- IP anchoring (Intermediate)

**Specializations:**
- **Polygon Integration:** RPC endpoints, transaction signing
- **Smart Contracts:** Proof anchoring, verification
- **Cryptography:** SHA-256 hashing, Merkle trees
- **Gas Optimization:** Batch transactions, cost reduction

**Team Size:** 1 Blockchain Engineer (can be shared with Backend)

---

### Legal Domain Expertise

**Core Skills:**
- Patent law (Intermediate)
- Legal document parsing (Intermediate)
- Jurisdiction mapping (Intermediate)
- Citation analysis (Intermediate)

**Specializations:**
- **Patent Law:** Novelty, non-obviousness, enablement
- **Legal Documents:** Statutes, regulations, cases
- **Jurisdictions:** US Federal, CA Federal, EU, UK, etc.
- **Citations:** Forward/backward citation chains, authority scoring

**Team Size:** 1 Legal Domain Expert (part-time consultant)

---

## Part 3: Skill Level Definitions

### Junior (0-2 years)
- Can implement well-defined tasks with guidance
- Familiar with core concepts, needs supervision
- Learning best practices and patterns

### Intermediate (2-4 years)
- Can design and implement features independently
- Understands trade-offs and can make architectural decisions
- Can mentor junior engineers
- Can handle production incidents with guidance

### Advanced (4-6 years)
- Can design complex systems and lead technical decisions
- Can mentor intermediate engineers
- Can handle production incidents independently
- Deep expertise in specific domain

### Expert (6+ years)
- Can architect entire systems and set technical direction
- Can lead teams and set engineering culture
- Can solve novel problems and create new patterns
- Recognized authority in specific domain

---

## Part 4: Recommended Team Composition

### MVP Team (8-10 engineers)

**Backend (4):**
- 1 Senior Backend Engineer (Lead)
- 2 Backend Engineers (Intermediate)
- 1 ML/AI Engineer (Intermediate)

**Frontend (2):**
- 1 Senior Frontend Engineer (Lead)
- 1 Frontend Engineer (Intermediate)

**DevOps (2):**
- 1 Senior DevOps Engineer (Lead)
- 1 DevOps Engineer (Intermediate)

**Support (1-2):**
- 1 Security Engineer (can be shared)
- 1 Legal Consultant (part-time)

---

### Production Team (12-15 engineers)

**Backend (5-6):**
- 1 Staff Backend Engineer (Tech Lead)
- 2 Senior Backend Engineers
- 2 Backend Engineers (Intermediate)
- 1 ML/AI Engineer (Senior)

**Frontend (3-4):**
- 1 Senior Frontend Engineer (Lead)
- 2 Frontend Engineers (Intermediate)
- 1 UX Designer

**DevOps/SRE (3):**
- 1 Staff DevOps Engineer (Tech Lead)
- 1 Senior DevOps Engineer
- 1 DevOps Engineer (Intermediate)

**Support (2-3):**
- 1 Security Engineer (Senior)
- 1 Data Engineer (can be shared with Backend)
- 1 Legal Consultant (part-time)

---

### Enterprise Team (20+ engineers)

**Backend (8-10):**
- 1 Principal Backend Engineer (Architect)
- 2 Staff Backend Engineers (Tech Leads)
- 3 Senior Backend Engineers
- 3 Backend Engineers (Intermediate)
- 1 ML/AI Engineer (Staff)

**Frontend (5-6):**
- 1 Principal Frontend Engineer (Architect)
- 1 Senior Frontend Engineer (Lead)
- 3 Frontend Engineers (Intermediate)
- 1 UX Designer
- 1 Frontend Designer

**DevOps/SRE (4-5):**
- 1 Principal DevOps Engineer (Architect)
- 1 Staff DevOps Engineer (Tech Lead)
- 2 Senior DevOps Engineers
- 1 SRE Engineer (Intermediate)

**Specialized (2-3):**
- 1 Security Engineer (Staff)
- 1 Data Engineer (Senior)
- 1 Blockchain Engineer (Intermediate)
- 1 Legal Consultant (part-time)

---

## Part 5: Skill Gap Analysis Template

### How to Use

For each candidate or team member, assess:

1. **Core Skills:** Rate each skill (Junior/Intermediate/Advanced/Expert)
2. **Specializations:** Identify areas of deep expertise
3. **Gaps:** Identify missing skills for target role
4. **Training Plan:** Define learning path to close gaps

### Example Gap Analysis

**Candidate: Senior Backend Engineer**

| Skill | Current Level | Target Level | Gap | Training Plan |
|-------|--------------|--------------|-----|---------------|
| Python | Advanced | Advanced | None | - |
| FastAPI | Intermediate | Advanced | 1 level | FastAPI advanced patterns course |
| PostgreSQL | Intermediate | Advanced | 1 level | PostgreSQL performance tuning |
| pgvector | Junior | Intermediate | 1 level | pgvector documentation + hands-on |
| Celery | Intermediate | Advanced | 1 level | Celery chains/groups practice |
| Kubernetes | Junior | Intermediate | 1 level | Kubernetes fundamentals course |

**Estimated Training Time:** 4-6 weeks

---

## Part 6: Hiring Recommendations

### Priority Hires (First 3 months)

1. **Senior Backend Engineer (Lead)**
   - Required: FastAPI, PostgreSQL, Celery, async/await
   - Nice-to-have: pgvector, vector databases
   - Interview focus: System design, async patterns, database optimization

2. **Senior Frontend Engineer (Lead)**
   - Required: Next.js, TypeScript, React
   - Nice-to-have: Clerk, Shadcn/UI
   - Interview focus: React patterns, TypeScript, performance optimization

3. **Senior DevOps Engineer (Lead)**
   - Required: Kubernetes, Terraform, AWS
   - Nice-to-have: EKS, observability stack
   - Interview focus: Infrastructure design, CI/CD, security

### Secondary Hires (Months 4-6)

4. **ML/AI Engineer**
   - Required: OpenAI API, embeddings, vector databases
   - Nice-to-have: LLM integration, prompt engineering
   - Interview focus: Embedding optimization, vector search, LLM patterns

5. **Security Engineer**
   - Required: JWT, OAuth, encryption
   - Nice-to-have: RLS, BYOK, compliance
   - Interview focus: Auth design, security architecture, threat modeling

### Tertiary Hires (Months 7-12)

6. **Backend Engineers (2)**
   - Required: Python, FastAPI, PostgreSQL
   - Nice-to-have: Celery, async/await
   - Interview focus: API design, database queries, error handling

7. **Frontend Engineer**
   - Required: Next.js, TypeScript, React
   - Nice-to-have: Clerk, React Query
   - Interview focus: React patterns, state management, UX

---

## Part 7: Onboarding Timeline

### Week 1-2: Environment Setup
- Set up development environment (Docker, local DB)
- Review architecture documentation (SYSTEM_LAYERS.md, ADRs)
- Clone repo, run local instance
- Complete onboarding checklist

### Week 3-4: Core Skills
- Deep dive into primary technology stack
- Pair programming with senior engineers
- Complete small, well-defined tasks
- Code review process introduction

### Week 5-6: Domain Knowledge
- Learn business domain (patents, legal documents)
- Understand data models (ERD.md)
- Review API specification (API_SPEC.md)
- Shadow customer support calls (if applicable)

### Week 7-8: Independent Work
- Take ownership of small feature
- Implement with guidance
- Participate in code reviews
- Deploy to staging environment

### Week 9-12: Full Productivity
- Take ownership of larger features
- Participate in architectural discussions
- Mentor junior engineers
- On-call rotation (if applicable)

---

## Part 8: Training Resources

### Backend Engineering
- **FastAPI:** https://fastapi.tiangolo.com/tutorial/
- **PostgreSQL:** https://www.postgresql.org/docs/
- **pgvector:** https://github.com/pgvector/pgvector
- **Celery:** https://docs.celeryproject.org/
- **Async/Await:** https://docs.python.org/3/library/asyncio.html

### Frontend Engineering
- **Next.js:** https://nextjs.org/docs
- **TypeScript:** https://www.typescriptlang.org/docs/
- **React Query:** https://tanstack.com/query/latest
- **Tailwind:** https://tailwindcss.com/docs
- **Clerk:** https://clerk.com/docs

### DevOps/SRE
- **Kubernetes:** https://kubernetes.io/docs/
- **Terraform:** https://developer.hashicorp.com/terraform/docs
- **AWS:** https://docs.aws.amazon.com/
- **Prometheus:** https://prometheus.io/docs/
- **Grafana:** https://grafana.com/docs/

### ML/AI
- **OpenAI API:** https://platform.openai.com/docs/
- **Embeddings:** https://platform.openai.com/docs/guides/embeddings
- **Qdrant:** https://qdrant.tech/documentation/
- **Vector Search:** https://www.pinecone.io/learn/vector-database/

### Security
- **JWT:** https://jwt.io/introduction
- **OAuth 2.0:** https://oauth.net/2/
- **PostgreSQL RLS:** https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- **Vault:** https://developer.hashicorp.com/vault/docs

---

## Conclusion

LexCore + LexRadar requires a **multi-disciplinary team** with expertise across backend, frontend, DevOps, ML/AI, security, and legal domain. The architecture is well-designed to allow teams to work independently on different layers while maintaining clear interfaces.

**Key Takeaways:**
- **Minimum viable team:** 8-10 engineers (4 backend, 2 frontend, 2 DevOps, 1-2 support)
- **Production team:** 12-15 engineers with specialized roles
- **Enterprise team:** 20+ engineers with full specialization
- **Critical hires:** Senior Backend, Senior Frontend, Senior DevOps (first 3 months)
- **Onboarding time:** 8-12 weeks to full productivity
- **Continuous learning:** Technology stack evolves rapidly; invest in training

**Recommendation:** Start with MVP team (8-10 engineers), scale to production team (12-15) after product-market fit, then expand to enterprise team (20+) for ENTERPRISE tier and self-hosting.
