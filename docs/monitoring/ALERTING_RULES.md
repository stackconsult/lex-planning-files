# ALERTING_RULES.md — LexCore + LexRadar Alerting Rules

> **Build System:** Unified Build System v2 | **Chunk:** C09 — Monitoring | **Horde:** HORDE-MONITOR

---

## Overview

Alerting rules define conditions that trigger notifications when system health or performance degrades. Rules are organized by severity (P0-P3) and target specific metrics, logs, or traces.

**Alert Manager:** CloudWatch Alarms  
**Notification Channels:** PagerDuty (P0/P1), Slack (P1-P3), Email (P3)  
**Evaluation Period:** 5 data points (5 minutes for most metrics)  

---

## P0 - Critical Alerts

### API-001: API Service Down

**Condition:** `http_requests_total{status="5xx"} / http_requests_total > 0.5` for 5 minutes  
**Description:** 50%+ of API requests returning 5xx errors  
**Channel:** PagerDuty → Slack  
**Response Time:** 15 minutes  
**Runbook:** INCIDENT_RESPONSE.md → Service Outage

### DB-001: Database Unreachable

**Condition:** `postgres_connections_active == 0` for 2 minutes  
**Description:** No active database connections  
**Channel:** PagerDuty → Slack  
**Response Time:** 15 minutes  
**Runbook:** INCIDENT_RESPONSE.md → Database Failure

### AUTH-001: Auth Service Failure

**Condition:** `http_requests_total{endpoint="/v1/auth/validate", status="5xx"} > 10` for 5 minutes  
**Description:** Auth validation endpoint failing  
**Channel:** PagerDuty → Slack  
**Response Time:** 15 minutes  
**Runbook:** INCIDENT_RESPONSE.md → Auth Failure

### SEC-001: Security Breach Detected

**Condition:** Log pattern: `SECURITY_VIOLATION` OR `UNAUTHORIZED_ACCESS`  
**Description:** Security violation detected in logs  
**Channel:** PagerDuty → Slack → Email (security team)  
**Response Time:** 10 minutes  
**Runbook:** INCIDENT_RESPONSE.md → Security Incident

### DATA-001: Data Loss Risk

**Condition:** `celery_task_failure_total{task_name="store_document"} > 10` for 5 minutes  
**Description:** Document storage failures exceeding threshold  
**Channel:** PagerDuty → Slack  
**Response Time:** 15 minutes  
**Runbook:** INCIDENT_RESPONSE.md → Data Loss

---

## P1 - High Priority Alerts

### PERF-001: High API Latency

**Condition:** `histogram_quantile(0.95, http_request_duration_seconds) > 2` for 10 minutes  
**Description:** P95 API latency exceeds 2 seconds  
**Channel:** PagerDuty → Slack  
**Response Time:** 30 minutes  
**Runbook:** INCIDENT_RESPONSE.md → Performance Degradation

### PERF-002: Slow Database Queries

**Condition:** `postgres_query_duration_seconds{quantile="0.95"} > 5` for 10 minutes  
**Description:** P95 database query latency exceeds 5 seconds  
**Channel:** Slack  
**Response Time:** 30 minutes  
**Runbook:** INCIDENT_RESPONSE.md → Database Performance

### QUEUE-001: Worker Queue Backlog

**Condition:** `celery_queue_length{queue="ingestion"} > 1000` for 15 minutes  
**Description:** Ingestion queue backlog exceeds 1000 tasks  
**Channel:** Slack  
**Response Time:** 30 minutes  
**Runbook:** INCIDENT_RESPONSE.md → Queue Backlog

### EXT-001: External API Degraded

**Condition:** `http_requests_total{endpoint=~"uspto|wipo|epo", status="5xx"} > 50` for 10 minutes  
**Description:** External patent API errors elevated  
**Channel:** Slack  
**Response Time:** 30 minutes  
**Runbook:** INCIDENT_RESPONSE.md → External API Failure

### CAP-001: High CPU Utilization

**Condition:** `node_cpu_usage_percentage > 80` for 15 minutes  
**Description:** EKS node CPU utilization exceeds 80%  
**Channel:** Slack  
**Response Time:** 30 minutes  
**Runbook:** INCIDENT_RESPONSE.md → Capacity Planning

---

## P2 - Medium Priority Alerts

### PERF-003: Elevated Latency

**Condition:** `histogram_quantile(0.95, http_request_duration_seconds) > 1` for 20 minutes  
**Description:** P95 API latency elevated (>1 second)  
**Channel:** Slack  
**Response Time:** 2 hours  
**Runbook:** OPERATIONS_GUIDE.md → Performance Tuning

### WORKER-001: Worker Failures Elevated

**Condition:** `rate(celery_task_failure_total[5m]) > 0.1` for 20 minutes  
**Description:** Worker failure rate exceeds 10%  
**Channel:** Slack  
**Response Time:** 2 hours  
**Runbook:** OPERATIONS_GUIDE.md → Worker Health

### STORAGE-001: Disk Space Warning

**Condition:** `node_disk_usage_percentage > 70`  
**Description:** Disk space usage exceeds 70%  
**Channel:** Slack  
**Response Time:** 4 hours  
**Runbook:** OPERATIONS_GUIDE.md → Storage Management

### RATE-001: Rate Limit Breach

**Condition:** `http_requests_total{status="429"} > 100` for 15 minutes  
**Description:** Rate limit errors elevated  
**Channel:** Slack  
**Response Time:** 2 hours  
**Runbook:** OPERATIONS_GUIDE.md → Rate Limit Tuning

---

## P3 - Low Priority Alerts

### CAP-002: Capacity Planning Needed

**Condition:** `node_cpu_usage_percentage > 60` for 1 hour  
**Description:** Sustained CPU usage at 60%+  
**Channel:** Email (daily digest)  
**Response Time:** 24 hours  
**Runbook:** OPERATIONS_GUIDE.md → Capacity Planning

### COST-001: Cloud Cost Alert

**Condition:** AWS Cost Explorer daily cost > $500  
**Description:** Daily cloud spend exceeds $500  
**Channel:** Email (daily digest)  
**Response Time:** 24 hours  
**Runbook:** OPERATIONS_GUIDE.md → Cost Optimization

### USAGE-001: Tenant Usage Spike

**Condition:** `tenant_request_count{tenant_id="*"}` > 10,000/hour  
**Description:** Single tenant request volume spike  
**Channel:** Slack (ops channel)  
**Response Time:** 24 hours  
**Runbook:** OPERATIONS_GUIDE.md → Tenant Engagement

---

## Alert Suppression Rules

**Maintenance Windows:**
- During deployments (suppress P2-P3 for 30 minutes)
- During scheduled maintenance (suppress all for window duration)

**Known Issues:**
- Suppress alerts for known issues documented in INCIDENT_RESPONSE.md
- Auto-resolve when issue is marked as resolved

---

## Alert Testing

**Monthly Alert Test:**
- Simulate P0 alert ( PagerDuty test event)
- Verify all channels receive notification
- Verify response team acknowledges within SLA
- Document test results in INCIDENT_RESPONSE.md

**Quarterly Alert Review:**
- Review alert effectiveness (false positive rate)
- Adjust thresholds based on baseline data
- Add new alerts for emerging patterns
- Remove obsolete alerts

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-30 | Initial alerting rules | C09 Monitoring definition |
