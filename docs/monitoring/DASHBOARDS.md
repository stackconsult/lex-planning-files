# DASHBOARDS.md — LexCore + LexRadar Monitoring Dashboards

> **Build System:** Unified Build System v2 | **Chunk:** C09 — Monitoring | **Horde:** HORDE-MONITOR

---

## Overview

Dashboards provide real-time visibility into system health, performance, and operational metrics. All dashboards are available in Grafana (primary) and CloudWatch (backup).

**Dashboard Tool:** Grafana (primary), CloudWatch Dashboards (backup)  
**Data Source:** Amazon Managed Prometheus (AMP), CloudWatch Metrics  
**Refresh Interval:** 30 seconds (default), 5 seconds (critical)  

---

## Dashboard 1: API Overview

**Purpose:** High-level API health and performance  
**Panels:**

| Panel | Query | Threshold |
|-------|-------|-----------|
| Request Rate | `sum(rate(http_requests_total[5m]))` | — |
| Error Rate | `sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))` | > 1% (red) |
| P50 Latency | `histogram_quantile(0.5, http_request_duration_seconds)` | < 100ms (green) |
| P95 Latency | `histogram_quantile(0.95, http_request_duration_seconds)` | < 500ms (green), > 2s (red) |
| P99 Latency | `histogram_quantile(0.99, http_request_duration_seconds)` | < 1s (green) |
| Active Users | `count(distinct(user_id))` | — |
| Request Volume by Endpoint | `sum by (endpoint) (rate(http_requests_total[5m]))` | — |
| Error Rate by Endpoint | `sum by (endpoint, status) (rate(http_requests_total[5m]))` | — |
| Status Code Distribution | `sum by (status) (rate(http_requests_total[5m]))` | — |

**Alert Links:** PERF-001 (High Latency), API-001 (Service Down)

---

## Dashboard 2: Worker Performance

**Purpose:** Celery worker queue health and task performance  
**Panels:**

| Panel | Query | Threshold |
|-------|-------|-----------|
| Queue Depth (Ingestion) | `celery_queue_length{queue="ingestion"}` | < 100 (green), > 1000 (red) |
| Queue Depth (Patent) | `celery_queue_length{queue="patent"}` | < 50 (green), > 500 (red) |
| Task Duration P95 (Ingestion) | `histogram_quantile(0.95, celery_task_duration_seconds{queue="ingestion"})` | < 60s (green) |
| Task Duration P95 (Patent) | `histogram_quantile(0.95, celery_task_duration_seconds{queue="patent"})` | < 300s (green) |
| Task Failure Rate | `sum(rate(celery_task_failure_total[5m])) / sum(rate(celery_task_success_total[5m]))` | < 5% (green), > 20% (red) |
| Workers Active | `celery_worker_active_count` | — |
| Tasks by Status | `sum by (status) (celery_task_count)` | — |
| Failed Tasks by Queue | `sum by (queue) (celery_task_failure_total)` | — |
| DLQ Size | `celery_dead_letter_queue_size` | > 10 (yellow) |

**Alert Links:** QUEUE-001 (Backlog), WORKER-001 (Worker Failures)

---

## Dashboard 3: Database Health

**Purpose:** PostgreSQL connection pool and query performance  
**Panels:**

| Panel | Query | Threshold |
|-------|-------|-----------|
| Active Connections | `postgres_connections_active` | < 50 (green), > 90 (red) |
| Idle Connections | `postgres_connections_idle` | — |
| Connection Pool Utilization | `postgres_connections_active / postgres_connections_max` | < 70% (green) |
| Query Duration P95 | `histogram_quantile(0.95, postgres_query_duration_seconds)` | < 100ms (green), > 5s (red) |
| Slow Queries (>1s) | `sum(rate(postgres_query_duration_seconds_bucket{le="+Inf"}[5m])) - sum(rate(postgres_query_duration_seconds_bucket{le="1"}[5m]))` | — |
| Transaction Rate | `rate(postgres_transactions_total[5m])` | — |
| Cache Hit Ratio | `postgres_cache_hit_ratio` | > 95% (green) |
| Replication Lag | `postgres_replication_lag_seconds` | < 1s (green), > 10s (red) |
| Table Size | `postgres_table_size_bytes` | — |

**Alert Links:** DB-001 (Database Unreachable), PERF-002 (Slow Queries)

---

## Dashboard 4: Infrastructure

**Purpose:** EKS node, ALB, and storage health  
**Panels:**

| Panel | Query | Threshold |
|-------|-------|-----------|
| Node CPU Utilization | `avg(node_cpu_usage_percentage)` | < 60% (green), > 80% (red) |
| Node Memory Utilization | `avg(node_memory_usage_percentage)` | < 70% (green), > 90% (red) |
| Pod Count | `kube_pod_status_phase{phase="Running"}` | — |
| Pod Pending | `kube_pod_status_phase{phase="Pending"}` | > 5 (yellow) |
| Pod Failed | `kube_pod_status_phase{phase="Failed"}` | > 0 (red) |
| ALB Request Rate | `aws_alb_request_count` | — |
| ALB Latency P95 | `aws_alb_latency_p95` | < 100ms (green) |
| ALB Error Rate | `aws_alb_target_response_code_count{code="5xx"}` | > 0 (red) |
| EBS Read IOPS | `aws_ebs_volume_read_ops` | — |
| EBS Write IOPS | `aws_ebs_volume_write_ops` | — |
| Disk Usage | `node_disk_usage_percentage` | < 70% (green), > 85% (red) |

**Alert Links:** CAP-001 (High CPU), STORAGE-001 (Disk Space)

---

## Dashboard 5: Tenant Metrics

**Purpose:** Per-tenant resource usage and performance  
**Panels:**

| Panel | Query | Threshold |
|-------|-------|-----------|
| Request Rate by Tenant | `sum by (tenant_id) (rate(http_requests_total[5m]))` | — |
| Latency P95 by Tenant | `histogram_quantile(0.95, sum by (tenant_id) (http_request_duration_seconds))` | — |
| Error Rate by Tenant | `sum by (tenant_id) (rate(http_requests_total{status=~"5.."}[5m])) / sum by (tenant_id) (rate(http_requests_total[5m]))` | — |
| Document Count by Tenant | `tenant_document_count` | — |
| Storage Used by Tenant | `tenant_storage_used_bytes` | — |
| Active Users by Tenant | `tenant_active_users` | — |
| Ingestion Queue Depth by Tenant | `celery_queue_length{queue="ingestion"}` by tenant_id | — |

**Use Cases:** Tenant engagement, capacity planning, anomaly detection

---

## Dashboard 6: External APIs

**Purpose:** External API rate limits, latency, and availability  
**Panels:**

| Panel | Query | Threshold |
|-------|-------|-----------|
| OpenAI Request Rate | `rate(openai_api_requests_total[5m])` | — |
| OpenAI Latency P95 | `histogram_quantile(0.95, openai_api_duration_seconds)` | — |
| OpenAI Rate Limit Errors | `rate(openai_api_requests_total{status="429"}[5m])` | > 0 (red) |
| USPTO Request Rate | `rate(uspto_api_requests_total[5m])` | — |
| USPTO Latency P95 | `histogram_quantile(0.95, uspto_api_duration_seconds)` | — |
| USPTO Error Rate | `rate(uspto_api_requests_total{status=~"5.."}[5m]) / rate(uspto_api_requests_total[5m])` | > 5% (red) |
| WIPO Request Rate | `rate(wipo_api_requests_total[5m])` | — |
| WIPO Error Rate | `rate(wipo_api_requests_total{status=~"5.."}[5m]) / rate(wipo_api_requests_total[5m])` | > 5% (red) |
| Polygon Transaction Rate | `rate(polygon_transactions_total[5m])` | — |
| Polygon Latency P95 | `histogram_quantile(0.95, polygon_transaction_duration_seconds)` | — |

**Alert Links:** EXT-001 (External API Degraded)

---

## Dashboard 7: Security

**Purpose:** Security events and guardrail violations  
**Panels:**

| Panel | Query | Threshold |
|-------|-------|-----------|
| Failed Auth Attempts | `rate(auth_failure_total[5m])` | — |
| Rate Limit Violations | `rate(rate_limit_violations_total[5m])` | — |
| Security Violations | `rate(security_violations_total[5m])` | > 0 (red) |
| Unauthorized Access Attempts | `rate(unauthorized_access_attempts[5m])` | > 0 (red) |
| BYOK Failures | `rate(byok_failure_total[5m])` | > 0 (red) |
| Agent Import Violations | `rate(agent_import_violations_total[5m])` | > 0 (red) |
| Auto-Filing Attempts | `rate(auto_filing_attempts[5m])` | > 0 (red) |

**Alert Links:** SEC-001 (Security Breach)

---

## CloudWatch Dashboards

### LexCore-Production-Overview

**Widgets:**
- API Health (green/yellow/red)
- Database Health (green/yellow/red)
- Worker Queue Status
- Infrastructure Health
- External API Status
- Security Status

### LexCore-Performance

**Widgets:**
- API Latency P50/P95/P99
- Database Query Latency
- Worker Task Duration
- External API Latency

### LexCore-Errors

**Widgets:**
- Error Rate by Service
- Error Rate by Endpoint
- Error Rate by Tenant
- Failed Tasks by Queue

### LexCore-Capacity

**Widgets:**
- CPU Utilization
- Memory Utilization
- Disk Usage
- Network I/O
- Storage Usage

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-30 | Initial dashboard specifications | C09 Monitoring definition |
