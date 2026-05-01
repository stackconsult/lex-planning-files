# ADR-001: Technology Stack Choice

> **Status:** Accepted  
> **Date:** 2026-04-29  
> **Deciders:** HORDE-ARCH  
> **Context:** C02 — Architecture + Contracts  

---

## Problem Statement

LexCore + LexRadar requires a technology stack that supports:
1. High-performance legal document search (hybrid vector + full-text)
2. Multi-tenant data isolation with strong security guarantees
3. Patent pipeline automation with blockchain anchoring
4. Real-time legislative change monitoring
5. Attorney portal with complex document rendering
6. Scalable ingestion from 9 legal + 7 patent data sources

The stack must support Python (ML/AI ecosystem) for backend services and TypeScript/React for frontend, with PostgreSQL as the primary datastore.

---

## Decision

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Backend** | Python 3.12 + FastAPI 0.110+ | Native async, automatic OpenAPI generation, Pydantic v2 validation, extensive ML/AI library ecosystem |
| **Frontend** | Next.js 14+ App Router + TypeScript strict | Server components for SEO/performance, App Router for nested layouts, TypeScript for type safety |
| **Styling** | Tailwind CSS + Shadcn/UI | Utility-first CSS, pre-built accessible components, consistent design system |
| **Database** | PostgreSQL 15 + pgvector | ACID transactions, mature ecosystem, pgvector for 1536-dim embeddings, RLS for tenant isolation |
| **Vector DB** | Qdrant | Purpose-built for vector search, HNSW index, payload filtering for tenant isolation, easier to operate than Milvus |
| **Cache** | Redis 7 | Session store, query cache, Celery backend, rate limiting counters |
| **Queue** | Celery + Redis | Battle-tested for Python, supports scheduling, retries, dead letter queues |
| **Auth** | Clerk (primary) / JWT (API) | Clerk for frontend SSO (OAuth, SAML-ready), JWT for API keys and machine-to-machine |
| **Secrets** | HashiCorp Vault | Dynamic secrets, BYOK support, audit logging, Kubernetes integration |
| **Infra** | Terraform + Kubernetes (EKS) | Infrastructure as code, auto-scaling, rolling deployments, standard for enterprise |
| **Observability** | Prometheus + Grafana + OpenTelemetry + Loki + structlog | Metrics, dashboards, distributed tracing, log aggregation, structured logging |
| **Blockchain** | Polygon mainnet | Low gas fees, fast finality, EVM-compatible, sufficient for proof anchoring |

---

## Alternatives Considered

### Backend: Django vs FastAPI
- **Django:** Mature ORM, admin interface, but sync-by-default, heavier for microservices
- **FastAPI:** Native async, auto-generated OpenAPI, Pydantic validation, lighter — **chosen for async ML pipeline orchestration**

### Frontend: Next.js vs Remix
- **Remix:** Excellent form handling, server-side rendering focus
- **Next.js 14:** Larger ecosystem, App Router for nested layouts, Vercel deployment ease — **chosen for ecosystem and App Router**

### Vector DB: Qdrant vs Pinecone vs Weaviate
- **Pinecone:** Fully managed, but vendor lock-in, higher cost at scale
- **Weaviate:** GraphQL interface, good for complex queries, but heavier operational burden
- **Qdrant:** Open source, easy to operate, excellent payload filtering, HNSW built-in — **chosen for operational simplicity and tenant filtering**

### Auth: Clerk vs Auth0 vs自建
- **Auth0:** Enterprise features, but expensive at scale ($$$ per MAU)
- **自建 JWT:** Full control, but high maintenance burden for SSO/SAML
- **Clerk:** Modern React-focused, built-in SSO, reasonable pricing, excellent DX — **chosen for rapid frontend integration**

### Blockchain: Polygon vs Ethereum vs Avalanche
- **Ethereum mainnet:** High gas fees (~$50-200/tx), slow finality
- **Avalanche:** Fast finality, but smaller ecosystem for proof anchoring use cases
- **Polygon:** $0.01-0.10/tx, 2s finality, EVM-compatible, widely used for proofs — **chosen for cost and speed**

---

## Consequences

### Positive
- FastAPI + Pydantic v2 provides automatic API documentation and strict typing
- Next.js App Router enables nested layouts ideal for complex attorney portal navigation
- pgvector + Qdrant provides best-of-both relational + vector storage
- Clerk reduces frontend auth implementation from weeks to days
- Polygon anchoring costs <$1/month even at high volume

### Negative
- FastAPI ecosystem less mature than Django for admin interfaces (no built-in admin)
- pgvector HNSW index building is CPU-intensive during initial load
- Qdrant requires separate operational expertise from PostgreSQL
- Clerk is newer than Auth0 — some enterprise SSO features may be missing
- Polygon requires RPC endpoint (Alchemy/Infura) — additional dependency

### Risks
- **Vendor lock-in (Clerk):** Mitigation — JWT standard means migration path exists; claims structure is documented
- **Vector DB migration:** Mitigation — Qdrant is open source with backup/restore; export format is standard JSON
- **Blockchain network issues:** Mitigation — batch anchoring reduces tx count; fallback to delayed anchoring if network congested

---

## Related Decisions

- ADR-002: Authentication Strategy (Clerk + JWT hybrid)
- ADR-003: Async Processing Strategy (Celery + Redis vs. Kafka)

---

## References

- FastAPI: https://fastapi.tiangolo.com/
- pgvector: https://github.com/pgvector/pgvector
- Qdrant: https://qdrant.tech/
- Clerk: https://clerk.com/
- Polygon: https://polygon.technology/
