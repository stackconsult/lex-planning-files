# INCIDENT_RESPONSE.md — LexCore + LexRadar Incident Response

> **Build System:** Unified Build System v2 | **Chunk:** C10 — Runbooks | **Horde:** HORDE-LOG

---

## Overview

This runbook defines incident response procedures for common operational issues. All incidents are categorized by severity (P0-P3) with defined response times and escalation paths.

**Incident Management:** PagerDuty  
**Communication:** Slack (#incidents), Email (stakeholders)  
**Documentation:** Incident log, Post-mortem  

---

## Incident Severity Levels

| Severity | Response Time | Impact | Examples |
|----------|---------------|--------|----------|
| P0 - Critical | 15 min | Service down, data loss, security breach | API down, DB unreachable, security breach |
| P1 - High | 30 min | Degraded performance, high error rate | High latency, queue backlog |
| P2 - Medium | 2 hours | Elevated latency, increased failures | Elevated errors, slow queries |
| P3 - Low | 24 hours | Resource warnings, capacity planning | CPU warning, storage warning |

---

## Incident Response Flow

```
1. Detect (Alert triggers)
   ↓
2. Acknowledge (PagerDuty)
   ↓
3. Investigate (Gather metrics, logs, traces)
   ↓
4. Mitigate (Implement fix or workaround)
   ↓
5. Resolve (Verify fix, close incident)
   ↓
6. Post-mortem (Document learnings)
```

---

## Incident 1: API Service Down

**Alert:** API-001 (API Service Down)  
**Severity:** P0  
**Response Time:** 15 minutes  

### Diagnosis

```bash
# Check pod status
kubectl get pods -n production

# Check pod logs
kubectl logs -f deployment/lexcore-api -n production --tail=100

# Check ALB health
aws elbv2 describe-target-health --target-group-arn $ALB_TG_ARN

# Check metrics
curl https://api.lexcore.com/health
```

### Mitigation

**If pods are crashing:**
```bash
# Check pod events
kubectl describe pod <pod-name> -n production

# Common causes:
# - OOMKilled → Increase memory limits
# - CrashLoopBackOff → Check application logs for errors
# - ImagePullBackOff → Verify ECR image exists
```

**If ALB is unhealthy:**
```bash
# Check ALB target group
aws elbv2 describe-target-health --target-group-arn $ALB_TG_ARN

# If unhealthy targets > 0, restart pods
kubectl rollout restart deployment/lexcore-api -n production
```

**If database unreachable:**
```bash
# Check DB connection
kubectl exec -it <api-pod> -n production -- psql $DATABASE_URL

# If connection fails, check DB health
aws rds describe-db-instances --db-instance-identifier lexcore-prod
```

### Resolution

- [ ] Pods healthy
- [ ] ALB health checks passing
- [ ] API health endpoint responding
- [ ] Error rate < 0.1%
- [ ] No alert firing

### Rollback (if fix fails)

```bash
# Rollback to previous Helm release
helm rollback lexcore 0 --namespace production
```

---

## Incident 2: Database Failure

**Alert:** DB-001 (Database Unreachable)  
**Severity:** P0  
**Response Time:** 15 minutes  

### Diagnosis

```bash
# Check DB instance status
aws rds describe-db-instances --db-instance-identifier lexcore-prod

# Check connection pool
kubectl exec -it <api-pod> -n production -- psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"

# Check DB metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name DatabaseConnections \
  --dimensions Name=DBInstanceIdentifier,Value=lexcore-prod
```

### Mitigation

**If DB instance is down:**
```bash
# Reboot DB (if automated recovery fails)
aws rds reboot-db-instance --db-instance-identifier lexcore-prod
```

**If connection pool exhausted:**
```bash
# Increase pool size in environment config
# Or scale API pods to reduce per-pod connections
kubectl scale deployment/lexcore-api --replicas=5 -n production
```

**If read replica lag:**
```bash
# Check replication lag
aws rds describe-db-clusters --db-cluster-identifier lexcore-prod

# If lag > 10s, restart replication or failover
aws rds failover-db-cluster --db-cluster-identifier lexcore-prod
```

### Resolution

- [ ] DB instance available
- [ ] Connections established
- [ ] Replication lag < 1s
- [ ] Query latency normal

---

## Incident 3: Security Breach

**Alert:** SEC-001 (Security Breach Detected)  
**Severity:** P0  
**Response Time:** 10 minutes  

### Immediate Actions

```bash
# Identify affected systems
grep "SECURITY_VIOLATION" /var/log/containers/*.log

# If unauthorized access detected:
# 1. Revoke compromised credentials
aws iam delete-access-key --access-key-id $COMPROMISED_KEY_ID

# 2. Rotate secrets
aws secretsmanager rotate-secret --secret-id $SECRET_ARN

# 3. Block offending IPs
aws wafv2 update-ip-set --scope REGIONAL --id $IP_SET_ID --addresses "1.2.3.4/32"
```

### Investigation

- [ ] Identify attack vector
- [ ] Determine scope of compromise
- [ ] Preserve logs for forensics
- [ ] Notify security team
- [ ] Notify customers if data exposed

### Resolution

- [ ] Vulnerability patched
- [ ] Credentials rotated
- [ ] Systems hardened
- [ ] Post-mortem completed

---

## Incident 4: Performance Degradation

**Alert:** PERF-001 (High API Latency)  
**Severity:** P1  
**Response Time:** 30 minutes  

### Diagnosis

```bash
# Check latency metrics
histogram_quantile(0.95, http_request_duration_seconds)

# Check slow queries
SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;

# Check worker queue depth
celery_queue_length{queue="ingestion"}

# Check external API latency
openai_api_duration_seconds
```

### Mitigation

**If slow queries:**
```bash
# Kill long-running queries
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'active' AND query_start < now() - interval '5 minutes';

# Add missing indexes (after review)
```

**If queue backlog:**
```bash
# Scale workers
kubectl scale deployment celery-patent-worker --replicas=4 -n production

# Or prioritize critical tasks
```

**If external API slow:**
```bash
# Enable circuit breaker
# Or increase timeout
```

### Resolution

- [ ] P95 latency < 500ms
- [ ] No slow queries > 5s
- [ ] Queue depth normal
- [ ] External API latency normal

---

## Incident 5: Queue Backlog

**Alert:** QUEUE-001 (Worker Queue Backlog)  
**Severity:** P1  
**Response Time:** 30 minutes  

### Diagnosis

```bash
# Check queue depth
celery_queue_length{queue="ingestion"}

# Check worker status
kubectl get pods -n production -l workload=workers

# Check worker logs
kubectl logs -f deployment/celery-ingestion-worker -n production
```

### Mitigation

**If workers are down:**
```bash
# Restart workers
kubectl rollout restart deployment/celery-ingestion-worker -n production
```

**If workers are slow:**
```bash
# Scale workers
kubectl scale deployment celery-ingestion-worker --replicas=8 -n production
```

**If tasks are failing:**
```bash
# Check DLQ
celery_dead_letter_queue_size

# Investigate failure cause
# Fix task implementation
# Re-queue failed tasks
```

### Resolution

- [ ] Queue depth < 100
- [ ] Workers processing tasks
- [ ] Failure rate < 5%

---

## Post-Incident Procedures

### Within 1 Hour

- [ ] Incident closed in PagerDuty
- [ ] Update incident log
- [ ] Notify stakeholders

### Within 24 Hours

- [ ] Post-mortem meeting
- [ ] Post-mortem document (5 Whys, Timeline, Action Items)
- [ ] Update runbooks if needed
- [ ] Implement preventive measures

### Post-Mortem Template

```markdown
# Post-Mortem: [Incident Title]

## Summary
[Brief description of incident]

## Timeline
- [Time]: Event occurred
- [Time]: Detected
- [Time]: Mitigated
- [Time]: Resolved

## Root Cause
[5 Whys analysis]

## Impact
[Users affected, duration, data loss]

## Action Items
- [ ] [Owner]: [Action]
- [ ] [Owner]: [Action]

## Lessons Learned
[What went well, what could be improved]
```

---

## On-Call Escalation

| Level | Role | Contact |
|-------|------|---------|
| L1 | On-call Engineer | PagerDuty |
| L2 | Engineering Lead | Slack @eng-lead |
| L3 | Engineering Director | Slack @eng-director |
| L4 | CTO | Slack @cto |

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-30 | Initial incident response runbook | C10 Runbooks definition |
