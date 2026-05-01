# HANDOFF_PACKAGE.md — LexCore + LexRadar Handoff Package

> **Build System:** Unified Build System v2 | **Chunk:** C11 — Launch | **Horde:** HORDE-MASTER

---

## Overview

This handoff package provides all necessary information for the operations team to take over the LexCore + LexRadar platform after development completion. It includes architecture diagrams, runbooks, contact information, and operational procedures.

**Handoff Date:** TBD  
**Handoff To:** Operations Team, SRE Team, DevOps Team  
**Handoff From:** Engineering Team  

---

## Package Contents

### 1. Architecture Overview

**Files:**
- `docs/architecture/SYSTEM_LAYERS.md` — System architecture
- `docs/architecture/DEPENDENCY_GRAPH.json` — Dependency graph
- `docs/architecture/INTERFACE_CONTRACTS.json` — API contracts
- `docs/services/SERVICE_CATALOG.md` — Service layer
- `docs/services/AGENT_MANIFEST.md` — Agent registry
- `docs/services/WORKER_REGISTRY.md` — Worker registry
- `docs/devops/INFRASTRUCTURE_DIAGRAM.md` — Infrastructure diagram

**Key Points:**
- 3-tier architecture: Frontend (Next.js), API (FastAPI), Workers (Celery)
- Managed services: Neon (PostgreSQL), Upstash (Redis), Qdrant (Vector DB)
- Infrastructure: AWS EKS, ALB, Cloudflare (CDN/DNS/R2)
- 18 services, 13 agents, 11 worker queues

### 2. Operational Procedures

**Files:**
- `docs/runbooks/DEPLOYMENT_RUNBOOK.md` — Deployment procedures
- `docs/runbooks/INCIDENT_RESPONSE.md` — Incident response
- `docs/runbooks/OPERATIONS_GUIDE.md` — Day-to-day operations
- `docs/monitoring/ALERTING_RULES.md` — Alerting rules
- `docs/monitoring/DASHBOARDS.md` — Dashboard reference

**Key Points:**
- Blue-green deployment with canary rollout
- Automatic rollback on failure conditions
- P0 response time: 15 minutes
- Daily, weekly, monthly operational cadence

### 3. Security & Compliance

**Files:**
- `docs/api/AUTH_FLOW.md` — Authentication flow
- `docs/api/SECURITY_HEADERS.md` — Security headers
- `docs/services/RESILIENCE_RULES.md` — Resilience patterns
- `HORDE-AUDIT_ARCHITECTURE.md` — Audit framework

**Key Points:**
- Clerk JWT authentication
- Row-level security (RLS) per tenant
- 5 critical conditions (SYS-CRIT-01 through SYS-CRIT-05)
- BYOK (Bring Your Own Key) tenant isolation
- Zero tolerance for security violations

### 4. Monitoring & Observability

**Files:**
- `docs/monitoring/OBSERVABILITY_STACK.md` — Observability architecture
- `docs/monitoring/DASHBOARDS.md` — Dashboard reference
- `docs/monitoring/ALERTING_RULES.md` — Alerting rules

**Key Points:**
- Metrics: Prometheus (AMP) + CloudWatch
- Logs: CloudWatch Logs + Fluent Bit
- Traces: OpenTelemetry + X-Ray
- Dashboards: Grafana (primary), CloudWatch (backup)
- 7 Grafana dashboards, 4 CloudWatch dashboards

### 5. API Documentation

**Files:**
- `docs/api/API_SPEC.md` — API specification
- `docs/api/MCP_TOOLS.md` — MCP tools
- `docs/api/ERROR_CODES.md` — Error codes
- `docs/api/RATE_LIMIT_POLICY.md` — Rate limiting

**Key Points:**
- RESTful API with OpenAPI spec
- JWT authentication required
- Rate limiting: 30 requests/min per user
- Error codes: 100-199 (success), 400-499 (client), 500-599 (server)

### 6. Database Schema

**Files:**
- `schema/ERD.md` — Entity relationship diagram
- `schema/SCHEMA_MAP.json` — Schema mapping
- `schema/CONSTRAINT_REGISTRY.json` — Constraints
- `schema/migrations/` — Migration files

**Key Points:**
- PostgreSQL 16 with pgvector extension
- 20+ tables (tenants, users, documents, chunks, inventions, disclosures, bundles, etc.)
- RLS policies enforced per tenant
- Alembic for migrations

### 7. Contact Information

| Role | Name | Email | Slack | PagerDuty |
|------|------|-------|-------|-----------|
| Engineering Lead | TBD | eng-lead@lexcore.com | @eng-lead | Yes |
| DevOps Lead | TBD | devops@lexcore.com | @devops-lead | Yes |
| SRE Lead | TBD | sre-lead@lexcore.com | @sre-lead | Yes |
| Security Lead | TBD | security@lexcore.com | @security | Yes |
| On-Call Engineer | Rotating | on-call@lexcore.com | @on-call | Yes |
| Customer Success | TBD | cs@lexcore.com | @customer-success | No |

**Slack Channels:**
- #lexcore-ops — Operations
- #lexcore-incidents — Incidents
- #lexcore-dev — Development
- #lexcore-alerts — Alerts

### 8. Access & Credentials

**AWS:**
- EKS cluster: `production-lexcore` (us-east-1)
- ECR registry: `123456789012.dkr.ecr.us-east-1.amazonaws.com`
- RDS instance: `lexcore-prod`
- CloudWatch log groups: `/aws/eks/lexcore/*`

**Managed Services:**
- Neon: `lexcore-prod.neon.tech`
- Upstash: `lexcore-prod.upstash.io`
- Qdrant: `lexcore-prod.qdrant.io`
- Clerk: `lexcore-prod.clerk.accounts.dev`
- OpenAI: API key in AWS Secrets Manager

**Access:**
- All secrets in AWS Secrets Manager
- Kubeconfig via AWS CLI
- IAM roles for least privilege

### 9. Known Issues & Limitations

**Known Issues:**
- None at handoff

**Limitations:**
- Max file size: 100 MB (R2 upload limit)
- Max concurrent searches per tenant: 10
- Worker queue backlog: 1000 tasks (auto-scale trigger)
- External API rate limits: USPTO (30/min), WIPO (10/min)

### 10. Next Steps

**Immediate (Day 1):**
- [ ] Review all documentation
- [ ] Set up monitoring dashboards
- [ ] Configure alerting channels
- [ ] Test incident response procedures
- [ ] Verify access and credentials

**Week 1:**
- [ ] Daily health checks
- [ ] Monitor performance metrics
- [ ] Address any issues discovered
- [ ] Update documentation as needed

**Month 1:**
- [ ] Complete capacity planning review
- [ ] Complete cost optimization review
- [ ] Complete security audit
- [ ] Update runbooks based on incidents

---

## Handoff Meeting Agenda

**Duration:** 2 hours  
**Attendees:** Engineering Lead, DevOps Lead, SRE Lead, Security Lead  

**Agenda:**
1. Architecture overview (15 min)
2. Infrastructure walkthrough (15 min)
3. Security & compliance review (15 min)
4. Monitoring & alerting demo (15 min)
5. Incident response walkthrough (15 min)
6. Deployment procedures demo (15 min)
7. Q&A (30 min)

---

## Post-Handoff Support

**Week 1:** Engineering team on standby for questions  
**Week 2-4:** Reduced support (email/Slack only)  
**Month 2+:** Standard support (Jira tickets, on-call)

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-30 | Initial handoff package | C11 Launch definition |
