# OBSERVABILITY_STACK.md — LexCore + LexRadar Observability

> **Build System:** Unified Build System v2 | **Chunk:** C09 — Monitoring | **Horde:** HORDE-MONITOR

---

## Overview

The observability stack provides full visibility into system health, performance, and reliability. It combines metrics, logs, traces, and alerts to enable rapid incident response and proactive issue detection.

**Core Components:**
- **Metrics:** Prometheus (AMP) + CloudWatch
- **Logs:** CloudWatch Logs + Fluent Bit
- **Traces:** OpenTelemetry + X-Ray
- **Alerting:** CloudWatch Alarms + PagerDuty + Slack
- **Dashboards:** Grafana + CloudWatch Dashboards
- **APM:** CloudWatch Application Insights

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Application Layer                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ API Pods     │  │ Frontend Pods│  │ Worker Pods  │             │
│  │ (FastAPI)    │  │ (Next.js)     │  │ (Celery)     │             │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │
│         │                 │                 │                      │
│         └─────────────────┼─────────────────┘                      │
│                           │                                         │
└───────────────────────────┼─────────────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ Fluent Bit     │  │ OpenTelemetry  │  │ Application    │
│ (Log Agent)    │  │ (Tracing)      │  │ Metrics        │
└────────┬───────┘  └────────┬───────┘  └────────┬───────┘
         │                   │                   │
         ▼                   ▼                   ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ CloudWatch     │  │ X-Ray          │  │ Prometheus    │
│ Logs           │  │ (Traces)       │  │ (AMP)         │
└────────────────┘  └────────────────┘  └────────┬───────┘
                                            │
                                            ▼
                                   ┌────────────────┐
                                   │ Grafana        │
                                   │ (Dashboards)   │
                                   └────────────────┘
```

---

## Metrics

### Prometheus + Amazon Managed Prometheus (AMP)

**Scrape Targets:**
- API Pods: `/metrics` (every 15s)
- Frontend Pods: `/metrics` (every 15s)
- Worker Pods: `/metrics` (every 15s)
- Kubernetes Nodes: `/metrics/cadvisor` (every 30s)
- PostgreSQL: Exporter (every 30s)
- Redis: Exporter (every 30s)
- Qdrant: `/metrics` (every 30s)

**Key Metrics:**

| Metric | Type | Labels | Purpose |
|--------|------|--------|---------|
| `http_requests_total` | Counter | method, endpoint, status | Request volume |
| `http_request_duration_seconds` | Histogram | endpoint, tenant | Request latency |
| `celery_task_duration_seconds` | Histogram | task_name, queue | Worker task duration |
| `celery_task_failure_total` | Counter | task_name, queue | Worker failures |
| `postgres_connections_active` | Gauge | — | DB connection pool |
| `redis_keys_count` | Gauge | db | Redis key count |
| `qdrant_search_latency_seconds` | Histogram | collection | Vector search latency |
| `openai_api_requests_total` | Counter | model, status | OpenAI API usage |
| `tenant_document_count` | Gauge | tenant_id | Tenant document volume |

### CloudWatch Metrics

**Custom Metrics (via Embedded Metric Format):**
- `TenantRequestCount` (Dimension: tenant_id)
- `TenantLatencyP95` (Dimension: tenant_id)
- `TenantErrorRate` (Dimension: tenant_id)
- `TenantStorageUsedGB` (Dimension: tenant_id)
- `TenantActiveUsers` (Dimension: tenant_id)

**Infrastructure Metrics:**
- EKS node CPU/memory utilization
- ALB request count, latency, error rate
- RDS CPU, connections, read/write IOPS
- ElastiCache CPU, memory, evictions
- EBS volume throughput

---

## Logging

### Fluent Bit Configuration

```yaml
# fluent-bit.conf
[SERVICE]
    Flush        5
    Log_Level    info
    Daemon       Off

[INPUT]
    Name              tail
    Path              /var/log/containers/*.log
    Parser            docker
    Tag               kube.*
    Mem_Buf_Limit     50MB
    Skip_Long_Lines   On

[FILTER]
    Name                kubernetes
    Match               kube.*
    Kube_URL            https://kubernetes.default.svc:443
    Kube_CA_File        /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    Kube_Token_File     /var/run/secrets/kubernetes.io/serviceaccount/token
    Merge_Log           On
    Keep_Log            Off
    K8S-Logging.Parser  On
    K8S-Logging.Exclude On

[OUTPUT]
    Name                cloudwatch_logs
    Match               *
    region              us-east-1
    log_group_name      /aws/eks/lexcore/containers
    log_stream_prefix   {namespace}
    auto_create_group   true
```

### Log Groups

| Log Group | Purpose | Retention |
|-----------|---------|-----------|
| `/aws/eks/lexcore/api` | API pod logs | 30 days |
| `/aws/eks/lexcore/frontend` | Frontend pod logs | 30 days |
| `/aws/eks/lexcore/workers` | Worker pod logs | 30 days |
| `/aws/eks/lexcore/ingestion` | Ingestion worker logs | 30 days |
| `/aws/eks/lexcore/evaluation` | Evaluation worker logs | 30 days |
| `/aws/eks/lexcore/blockchain` | Blockchain worker logs | 365 days |

### Log Format

```json
{
  "timestamp": "2026-04-30T12:00:00Z",
  "level": "INFO",
  "correlation_id": "req-abc123",
  "tenant_id": "tenant-1",
  "user_id": "user-1",
  "service": "legal_search",
  "message": "Search completed successfully",
  "duration_ms": 245,
  "metadata": {
    "query": "machine learning patent",
    "result_count": 42
  }
}
```

---

## Tracing

### OpenTelemetry + X-Ray

**Instrumentation:**
```python
# api/main.py
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

tracer = trace.get_tracer(__name__)
FastAPIInstrumentor.instrument_app(app)

# Trace external calls
@tracer.start_as_current_span("openai_embedding")
async def generate_embedding(text: str):
    # ... OpenAI call
```

**Trace Context Propagation:**
- HTTP headers: `x-correlation-id`, `x-tenant-id`
- Celery headers: `correlation_id`, `tenant_id`
- All downstream calls include trace context

---

## Alerting

### Alert Channels

| Channel | Purpose | Escalation |
|---------|---------|------------|
| PagerDuty | Critical incidents | 15 min → 30 min → on-call manager |
| Slack | Non-critical alerts | Channel-based routing |
| Email | Daily/weekly reports | Scheduled digests |

### Alert Severity Levels

| Severity | Response Time | Examples |
|----------|---------------|----------|
| P0 - Critical | 15 min | Service down, data loss, security breach |
| P1 - High | 30 min | Degraded performance, high error rate |
| P2 - Medium | 2 hours | Elevated latency, increased failures |
| P3 - Low | 24 hours | Resource warnings, capacity planning |

---

## Dashboards

### Grafana Dashboards

**Available Dashboards:**
1. **API Overview** — Request rate, latency, error rate, active users
2. **Worker Performance** — Queue depth, task duration, failure rate
3. **Database Health** — Connection pool, query latency, slow queries
4. **Infrastructure** — EKS node health, ALB metrics, storage usage
5. **Tenant Metrics** — Per-tenant request volume, latency, storage
6. **External APIs** — OpenAI rate limits, USPTO API status

### CloudWatch Dashboards

1. **LexCore-Production-Overview** — System-wide health
2. **LexCore-Performance** — Latency and throughput
3. **LexCore-Errors** — Error rates and types
4. **LexCore-Capacity** — Resource utilization trends

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-30 | Initial observability stack spec | C09 Monitoring definition |
