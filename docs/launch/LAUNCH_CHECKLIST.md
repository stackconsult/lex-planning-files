# LAUNCH_CHECKLIST.md — LexCore + LexRadar Launch Checklist

> **Build System:** Unified Build System v2 | **Chunk:** C11 — Launch | **Horde:** HORDE-MASTER

---

## Overview

This checklist defines all pre-launch, launch-day, and post-launch activities for the LexCore + LexRadar platform. All items must be completed and verified before production launch.

**Launch Type:** Initial Production Launch  
**Launch Date:** TBD  
**Launch Window:** TBD (off-peak hours recommended)  

---

## Pre-Launch Checklist (T-30 Days)

### Infrastructure

- [ ] EKS cluster provisioned and tested
- [ ] All node groups configured (general, api, workers, gpu)
- [ ] ALB configured with TLS certificate
- [ ] Cloudflare DNS configured and tested
- [ ] Cloudflare WAF rules deployed
- [ ] R2 buckets created with lifecycle policies
- [ ] Neon PostgreSQL configured (primary + read replicas)
- [ ] Upstash Redis configured (primary + replica)
- [ ] Qdrant Cloud configured (collections created)
- [ ] VPC flow logs enabled
- [ ] Security groups configured (least privilege)

### Database

- [ ] All migrations applied to production
- [ ] RLS policies verified
- [ ] pgvector indexes created
- [ ] Connection pool configured
- [ ] Backup schedule configured (daily, 7-day PITR)
- [ ] Restore test completed successfully
- [ ] Data integrity verified

### Security

- [ ] All secrets stored in AWS Secrets Manager
- [ ] External Secrets Operator configured
- [ ] Clerk JWT validation tested
- [ ] BYOK test passes (test_byok)
- [ ] Tenant isolation verified
- [ ] No auto-filing code paths exist
- [ ] No agent-to-agent imports exist
- [ ] Bundle integrity verification in place
- [ ] Security scan passes (Trivy, Bandit, npm audit)
- [ ] GuardDuty enabled
- [ ] Security Hub enabled

### Monitoring & Alerting

- [ ] CloudWatch dashboards created
- [ ] Grafana dashboards created
- [ ] Alerting rules configured (P0-P3)
- [ ] PagerDuty integration tested
- [ ] Slack integration tested
- [ ] Log aggregation configured (Fluent Bit → CloudWatch)
- [ ] Tracing configured (OpenTelemetry → X-Ray)
- [ ] Metrics configured (Prometheus → AMP)

### CI/CD

- [ ] GitHub Actions workflows tested
- [ ] ECR repositories created
- [ ] Helm charts configured
- [ ] Staging deployment tested
- [ ] Blue-green deployment tested
- [ ] Canary rollout tested
- [ ] Automatic rollback tested

### Testing

- [ ] Unit tests pass (≥80% coverage)
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Performance benchmarks met
- [ ] Load test completed
- [ ] Security penetration test completed
- [ ] HORDE-AUDIT gate PASS

### Documentation

- [ ] API docs updated
- [ ] Architecture docs updated
- [ ] Runbooks completed
- [ ] Onboarding guide complete
- [ ] Customer-facing docs published
- [ ] Release notes published

### Legal & Compliance

- [ ] Terms of Service published
- [ ] Privacy Policy published
- [ ] Data Processing Agreement (DPA) ready
- [ ] SOC 2 readiness verified
- [ ] GDPR compliance verified
- [ ] IP rights verified

### Customer Preparation

- [ ] Pilot customers notified
- [ ] Customer onboarding materials ready
- [ ] Support team trained
- [ ] Customer success team trained
- [ ] Sales team trained

---

## Launch Day Checklist

### Pre-Launch (T-2 Hours)

- [ ] On-call engineer on standby
- [ ] DevOps engineer on standby
- [ ] Security engineer on standby
- [ ] All stakeholders notified
- [ ] Slack channel created (#launch)
- [ ] Incident response plan reviewed
- [ ] Rollback plan reviewed

### Launch (T-0)

- [ ] Staging deployment verified
- [ ] Staging smoke tests pass
- [ ] Production deployment initiated
- [ ] Blue-green deployment executed
- [ ] Canary rollout (10% → 50% → 100%)
- [ ] Health checks verified
- [ ] Smoke tests pass
- [ ] E2E tests pass
- [ ] Metrics verified (error rate, latency)
- [ ] No alerts firing

### Post-Launch (T+1 Hour)

- [ ] All dashboards green
- [ ] No customer-reported issues
- [ ] Support tickets = 0
- [ ] Performance metrics normal
- [ ] Database performance normal
- [ ] Workers processing tasks normally
- [ ] External APIs responding normally

---

## Post-Launch Checklist (T+7 Days)

### Week 1

- [ ] Daily health checks completed
- [ ] Monitor for late-appearing issues
- [ ] Address customer feedback
- [ ] Fix any bugs discovered
- [ ] Update documentation based on issues
- [ ] Post-mortem meeting (if issues occurred)
- [ ] Capacity planning review

### Week 2

- [ ] Performance review
- [ ] Cost review
- [ ] Security review
- [ ] Customer satisfaction survey
- [ ] Feature backlog prioritization
- [ ] Sprint planning for next iteration

---

## Rollback Criteria

**Automatic rollback if any of the following occur:**
- Error rate > 1% for 2 minutes
- P95 latency > 2× baseline for 5 minutes
- Any critical health check fails
- Data corruption detected
- Security breach detected
- Customer-impacting bug discovered

**Manual rollback trigger:**
- Engineering Director approval
- Rollback plan executed
- Incident response initiated

---

## Launch Communication Plan

**Pre-Launch (T-7 days):**
- Email to all stakeholders
- Slack announcement
- Calendar invite for launch window

**Launch Day:**
- Slack #launch channel updates every 15 minutes
- Email to stakeholders at T-1 hour, T+1 hour
- Customer announcement (if public launch)

**Post-Launch:**
- Email to stakeholders at T+24 hours
- Slack announcement of successful launch
- Customer success outreach

---

## Success Criteria

**Launch is successful if:**
- [ ] Zero P0 incidents in first 24 hours
- [ ] Error rate < 0.1%
- [ ] P95 latency < 500ms
- [ ] No data loss
- [ ] No security breaches
- [ ] Customer satisfaction > 4.0/5.0

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-30 | Initial launch checklist | C11 Launch definition |
