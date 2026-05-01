# OPERATIONS_GUIDE.md — LexCore + LexRadar Operations

> **Build System:** Unified Build System v2 | **Chunk:** C10 — Runbooks | **Horde:** HORDE-LOG

---

## Overview

This guide provides operational procedures for day-to-day system maintenance, capacity planning, cost optimization, and routine tasks.

**Target Audience:** DevOps Engineers, SREs  
**Cadence:** Daily, weekly, monthly tasks  

---

## Daily Operations

### Morning Checklist

**9:00 AM UTC:**
- [ ] Check PagerDuty for overnight incidents
- [ ] Review CloudWatch dashboards for anomalies
- [ ] Check deployment queue (staging, production)
- [ ] Review security alerts (GuardDuty, Security Hub)
- [ ] Check backup completion status

### Health Checks

```bash
# API health
curl https://api.lexcore.com/health

# Database health
aws rds describe-db-instances --db-instance-identifier lexcore-prod

# Worker queue depth
kubectl get pods -n production -l workload=workers

# External API status
curl https://api.uspto.gov/status
```

### Log Review

```bash
# Check for errors in last hour
aws logs filter-log-events \
  --log-group-name /aws/eks/lexcore/api \
  --start-time $(date -d '1 hour ago' +%s) \
  --filter-pattern "ERROR"

# Check for security violations
aws logs filter-log-events \
  --log-group-name /aws/eks/lexcore/api \
  --start-time $(date -d '1 hour ago' +%s) \
  --filter-pattern "SECURITY_VIOLATION"
```

---

## Weekly Operations

### Monday: Capacity Planning

**Review Metrics:**
- CPU utilization trend (last 7 days)
- Memory utilization trend (last 7 days)
- Storage utilization trend (last 7 days)
- Request volume trend (last 7 days)

**Actions:**
- If CPU > 70% for 3+ days: Scale nodes
- If storage > 80%: Plan expansion
- If request volume trending up: Plan capacity increase

### Tuesday: Security Review

**Review:**
- GuardDuty findings
- Security Hub alerts
- IAM access key usage
- SSL certificate expiry (30-day lookahead)

### Wednesday: Performance Review

**Review:**
- P95 latency trend
- Database query performance
- Worker task duration
- External API latency

### Thursday: Cost Review

**Review:**
- AWS Cost Explorer daily cost
- Cost by service (EC2, RDS, ElastiCache)
- Cost by tenant (if available)
- Identify cost anomalies

### Friday: Backup Verification

**Verify:**
- Database backups completed
- R2 backups completed
- Backup integrity checks passed
- Restore test (monthly)

---

## Monthly Operations

### Week 1: Maintenance

**Tasks:**
- Apply OS patches (via EKS node rotation)
- Update dependencies (Python packages, npm packages)
- Review and rotate secrets (30-day expiry)
- Clean up old logs (retention policy)

### Week 2: Performance Optimization

**Tasks:**
- Review slow queries (pg_stat_statements)
- Add missing indexes
- Tune connection pools
- Optimize caching strategy

### Week 3: Security Hardening

**Tasks:**
- Run security scan (Trivy, Bandit)
- Review IAM policies (least privilege)
- Review security groups (open ports)
- Update WAF rules

### Week 4: Documentation

**Tasks:**
- Update runbooks based on incidents
- Review and update architecture docs
- Update onboarding guide
- Document new procedures

---

## Scaling Procedures

### Scale API Pods

```bash
# Manual scale
kubectl scale deployment lexcore-api --replicas=5 -n production

# Auto-scaling via HPA
kubectl autoscale deployment lexcore-api \
  --cpu-percent=70 \
  --min=3 \
  --max=10 \
  -n production
```

### Scale Workers

```bash
# Scale specific queue
kubectl scale deployment celery-patent-worker --replicas=4 -n production

# Scale all workers
kubectl scale deployment -l workload=workers --replicas=8 -n production
```

### Scale Database

**Via AWS Console:**
- RDS → Modify DB Instance
- Increase instance class (e.g., db.t3.medium → db.t3.large)
- Apply immediately or during maintenance window

---

## Backup and Restore

### Backup Verification

```bash
# Verify latest backup
aws rds describe-db-snapshots \
  --db-instance-identifier lexcore-prod \
  --query 'DBSnapshots[0]'

# Verify R2 backup
aws s3 ls s3://lexcore-backups/ --recursive
```

### Restore Test (Monthly)

```bash
# Restore to test instance
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier lexcore-test-restore \
  --db-snapshot-identifier lexcore-prod-snapshot-YYYYMMDD

# Verify restore
aws rds describe-db-instances --db-instance-identifier lexcore-test-restore

# Delete test instance after verification
aws rds delete-db-instance --db-instance-identifier lexcore-test-restore --skip-final-snapshot
```

---

## Cost Optimization

### Right-Sizing

**Review EC2 instances:**
- If CPU < 30% consistently: Downsize
- If CPU > 80% consistently: Upsize

**Review RDS:**
- If CPU < 30%: Consider smaller instance
- If storage < 50%: Reduce allocated storage

### Reserved Instances

**Purchase RI for:**
- Production EKS nodes (1-year or 3-year)
- Production RDS instances (1-year or 3-year)
- Production ElastiCache (1-year or 3-year)

**Savings:** 30-60% vs on-demand

### Spot Instances

**Use for:**
- Non-critical workers (evaluation, research)
- Batch processing jobs
- Development/staging environments

**Savings:** 70-90% vs on-demand

---

## Disaster Recovery

### RPO/RTO Targets

| Service | RPO | RTO |
|---------|-----|-----|
| API | 0 | 15 min |
| Database | 5 min | 30 min |
| Redis | 0 | 15 min |
| Qdrant | 1 hour | 1 hour |

### Failover Test (Quarterly)

**Test Database Failover:**
```bash
# Initiate failover
aws rds failover-db-cluster --db-cluster-identifier lexcore-prod

# Verify failover
aws rds describe-db-clusters --db-cluster-identifier lexcore-prod
```

**Test Region Failover (Yearly):**
- Deploy to secondary region
- Route 53 failover
- Verify traffic routing
- Fail back after test

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-30 | Initial operations guide | C10 Runbooks definition |
