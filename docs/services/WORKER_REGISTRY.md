# WORKER_REGISTRY.md — LexCore + LexRadar Celery Workers & Background Jobs

> **Build System:** Unified Build System v2  
> **Chunk:** C05 — Services + Workers + Agents  
> **Horde:** HORDE-AGENTS  
> **Control Plane:** ENGINEERING  

---

## Overview

Background jobs are executed via Celery with Redis as the broker and result backend. Workers are organized into **queues** by priority and domain. Each worker is a stateless, idempotent process that:
1. Receives a task from the broker
2. Executes the corresponding agent/service method
3. Writes results to the database
4. Updates job status in Redis
5. Emits events to the event bus
6. Retries on failure with exponential backoff
7. Dead-letters after max retries

**Broker:** Redis (DB 0)  
**Result Backend:** Redis (DB 1)  
**Task Serializer:** JSON  
**Result Serializer:** JSON  
**Result Expiry:** 24 hours  

---

## Worker Deployment Model

```
┌─────────────────────────────────────────────┐
│  Celery Broker (Redis DB 0)                 │
│  ├── Queue: default                         │
│  ├── Queue: ingestion                       │
│  ├── Queue: search                          │
│  ├── Queue: research                        │
│  ├── Queue: patent                          │
│  ├── Queue: monitor                         │
│  ├── Queue: email                           │
│  ├── Queue: evaluation                      │
│  └── Queue: blockchain                      │
├─────────────────────────────────────────────┤
│  Celery Workers                             │
│  ├── Worker Pool: default (4 workers)       │
│  ├── Worker Pool: ingestion (8 workers)     │
│  ├── Worker Pool: search (4 workers)        │
│  ├── Worker Pool: research (4 workers)      │
│  ├── Worker Pool: patent (8 workers)        │
│  ├── Worker Pool: monitor (2 workers)       │
│  ├── Worker Pool: email (2 workers)         │
│  ├── Worker Pool: evaluation (4 workers)    │
│  └── Worker Pool: blockchain (2 workers)  │
├─────────────────────────────────────────────┤
│  Result Backend (Redis DB 1)                │
│  ├── Task results (24h TTL)                 │
│  ├── Job status tracking                    │
│  └── Rate limit counters                    │
└─────────────────────────────────────────────┘
```

---

## Task Definitions

### 1. `ingest_document` (Queue: `ingestion`)

**Purpose:** Ingest a single document from a legal source  
**Agent:** `AGT_INGEST` (internal)  
**Service:** `IngestPipelineService.ingest_document()`  
**Priority:** 5 (Normal)  
**Timeout:** 30 minutes  
**Retries:** 3  
**Backoff:** 60s, 300s, 900s (exponential with jitter)

```python
@celery.task(
    bind=True,
    queue="ingestion",
    max_retries=3,
    default_retry_delay=60,
    retry_backoff=True,
    retry_backoff_max=900,
    time_limit=30 * 60,
    soft_time_limit=25 * 60,
)
def ingest_document(
    self,
    tenant_id: str,
    source: str,
    doc_id: str,
    correlation_id: str,
):
    """
    1. Fetch document from source (eCFR, CourtListener, etc.)
    2. Parse with Docling
    3. Chunk hierarchically (section, paragraph, sentence)
    4. Generate embeddings (OpenAI text-embedding-3-large)
    5. Store in PostgreSQL (legal_documents, legal_chunks)
    6. Index in Qdrant (legal_chunks collection)
    7. Write audit row
    8. Emit event: document.ingested
    
    On success: Return document UUID
    On failure: Retry with exponential backoff, then dead-letter
    """
```

**Dead-Letter Action:**
- Store failed doc_id in `failed_ingestions` table
- Emit event: `ingestion.failed`
- Alert operations team via PagerDuty

---

### 2. `batch_ingest` (Queue: `ingestion`)

**Purpose:** Batch ingest multiple documents  
**Agent:** `AGT_INGEST` (internal)  
**Service:** `IngestPipelineService.batch_ingest()`  
**Priority:** 5 (Normal)  
**Timeout:** 2 hours  
**Retries:** 2  
**Backoff:** 300s, 900s

```python
@celery.task(
    queue="ingestion",
    max_retries=2,
    default_retry_delay=300,
    retry_backoff=True,
    retry_backoff_max=900,
    time_limit=2 * 60 * 60,
)
def batch_ingest(
    tenant_id: str,
    source: str,
    doc_ids: list[str],
    correlation_id: str,
):
    """Parallel ingestion of multiple documents."""
```

---

### 3. `execute_research` (Queue: `research`)

**Purpose:** Execute complex legal research task  
**Agent:** `AGT_ANALYSIS`  
**Service:** `ResearchService.execute_research()`  
**Priority:** 7 (High)  
**Timeout:** 10 minutes  
**Retries:** 2  
**Backoff:** 30s, 120s

```python
@celery.task(
    queue="research",
    max_retries=2,
    default_retry_delay=30,
    retry_backoff=True,
    retry_backoff_max=300,
    time_limit=10 * 60,
    soft_time_limit=8 * 60,
)
def execute_research(
    tenant_id: str,
    task_id: str,
    correlation_id: str,
):
    """
    1. Fetch research task from database
    2. Decompose question into sub-queries
    3. Parallel search_legal calls for each sub-query
    4. Synthesize results with LLM (GPT-4)
    5. Detect gaps
    6. Store results
    7. Update task status to COMPLETED
    8. Emit event: research.completed
    """
```

---

### 4. `execute_scan` (Queue: `patent`)

**Purpose:** Scan code repository for invention signals  
**Agent:** `AGT_SCANNER`  
**Service:** `ScanService.execute_scan()`  
**Priority:** 5 (Normal)  
**Timeout:** 30 minutes  
**Retries:** 2  
**Backoff:** 60s, 300s

```python
@celery.task(
    queue="patent",
    max_retries=2,
    default_retry_delay=60,
    retry_backoff=True,
    retry_backoff_max=300,
    time_limit=30 * 60,
)
def execute_scan(
    tenant_id: str,
    job_id: str,
    correlation_id: str,
):
    """
    1. Fetch scan job from database
    2. Authenticate to source (GitHub, Jira, Notion)
    3. Fetch recent commits/PRs/tickets
    4. Parse code changes and descriptions
    5. Detect invention signals (novel algorithms, data structures, systems)
    6. Classify signals by type
    7. Store detected signals as invention candidates
    8. Update scan job status
    9. Emit event: scan.completed
    """
```

---

### 5. `search_prior_art` (Queue: `patent`)

**Purpose:** Parallel prior art search across 7 sources  
**Agent:** `AGT_PRIORART`  
**Service:** `PriorArtService.execute_search()`  
**Priority:** 5 (Normal)  
**Timeout:** 10 minutes  
**Retries:** 2  
**Backoff:** 30s, 120s

```python
@celery.task(
    queue="patent",
    max_retries=2,
    default_retry_delay=30,
    retry_backoff=True,
    retry_backoff_max=300,
    time_limit=10 * 60,
)
def search_prior_art(
    tenant_id: str,
    job_id: str,
    invention_id: str,
    correlation_id: str,
):
    """
    1. Fetch prior art search job
    2. Spawn 7 concurrent sub-tasks (one per source)
    3. Each sub-task:
       a. Query source API (USPTO, WIPO, EPO, etc.)
       b. Parse results
       c. Compute relevance score
       d. Store results
    4. Merge results, deduplicate by patent number
    5. Rank by relevance
    6. Store combined results
    7. Trigger scoring (update invention candidate)
    8. Emit event: prior_art.completed
    """
```

---

### 6. `generate_disclosure` (Queue: `patent`)

**Purpose:** Generate patent disclosure draft (10-section LHP)  
**Agent:** `AGT_DISCLOSER`  
**Service:** `DisclosureService.execute_generation()`  
**Priority:** 5 (Normal)  
**Timeout:** 10 minutes  
**Retries:** 1  
**Backoff:** 60s

```python
@celery.task(
    queue="patent",
    max_retries=1,
    default_retry_delay=60,
    retry_backoff=True,
    retry_backoff_max=300,
    time_limit=10 * 60,
)
def generate_disclosure(
    tenant_id: str,
    job_id: str,
    invention_id: str,
    correlation_id: str,
):
    """
    1. Fetch invention candidate and prior art results
    2. Generate each of 10 LHP sections with LLM
    3. Compute grounding score
    4. If grounding < 0.70: flag for review
    5. Store draft in disclosures table
    6. Update job status
    7. Emit event: disclosure.generated
    """
```

---

### 7. `evaluate_monitor_rules` (Queue: `monitor`)

**Purpose:** Evaluate all active monitor rules for legislative changes  
**Agent:** `AGT_MONITOR`  
**Service:** `MonitorService.evaluate_rules()`  
**Priority:** 5 (Normal)  
**Timeout:** 1 hour  
**Retries:** 2  
**Backoff:** 300s, 900s

```python
@celery.task(
    queue="monitor",
    max_retries=2,
    default_retry_delay=300,
    retry_backoff=True,
    retry_backoff_max=900,
    time_limit=60 * 60,
)
def evaluate_monitor_rules(
    tenant_id: str | None = None,  # None = all tenants
    correlation_id: str | None = None,
):
    """
    1. Fetch all active monitor rules
    2. For each rule:
       a. Check for new/changed documents since last_check
       b. Compare against rule keywords/jurisdiction
       c. Generate alert if match
    3. Write monitor_alerts rows
    4. Update last_triggered_at for each rule
    5. Emit event: monitor.alerts_generated (count)
    """
```

**Scheduling:**
- Cron: `0 */6 * * *` (every 6 hours)
- Tenant-level: Can be overridden per tenant in settings

---

### 8. `anchor_to_blockchain` (Queue: `blockchain`)

**Purpose:** Anchor IP artifacts to Polygon for timestamp proof  
**Agent:** `AGT_BLOCKCHAIN` (internal)  
**Service:** `BlockchainService.anchor()`  
**Priority:** 3 (Low)  
**Timeout:** 5 minutes  
**Retries:** 5  
**Backoff:** 10s, 30s, 60s, 120s, 300s

```python
@celery.task(
    queue="blockchain",
    max_retries=5,
    default_retry_delay=10,
    retry_backoff=True,
    retry_backoff_max=300,
    time_limit=5 * 60,
)
def anchor_to_blockchain(
    tenant_id: str,
    entity_id: str,
    entity_type: str,  # INVENTION, DISCLOSURE, FILING_BUNDLE
    document_hash: str,
    bundle_hash: str | None,
    correlation_id: str,
):
    """
    1. Validate document_hash format (64 hex chars)
    2. Connect to Polygon RPC
    3. Submit transaction with document_hash
    4. Wait for confirmation (1 block)
    5. Store transaction hash in blockchain_anchors table
    6. Emit event: blockchain.anchored
    
    CRITICAL: NEVER include raw IP content in the transaction.
    Only the SHA-256 hash is stored on-chain (SYS-CRIT-01 compliance).
    """
```

---

### 9. `send_email` (Queue: `email`)

**Purpose:** Send transactional emails (handoff, alerts, notifications)  
**Service:** `EmailService.send()`  
**Priority:** 5 (Normal)  
**Timeout:** 30 seconds  
**Retries:** 3  
**Backoff:** 10s, 30s, 60s

```python
@celery.task(
    queue="email",
    max_retries=3,
    default_retry_delay=10,
    retry_backoff=True,
    retry_backoff_max=60,
    time_limit=30,
)
def send_email(
    to: str,
    subject: str,
    body: str,
    html: str | None,
    from_address: str | None,
    correlation_id: str,
):
    """
    1. Validate email format
    2. Render template (if template_id provided)
    3. Send via SendGrid / AWS SES
    4. Track delivery status
    5. Emit event: email.sent or email.failed
    """
```

---

### 10. `evaluate_grounding` (Queue: `evaluation`)

**Purpose:** Run GroundingJudge on research results or disclosures  
**Agent:** `AGT_EVAL`  
**Service:** `LLMClient.evaluate()`  
**Priority:** 5 (Normal)  
**Timeout:** 5 minutes  
**Retries:** 2  
**Backoff:** 30s, 120s

```python
@celery.task(
    queue="evaluation",
    max_retries=2,
    default_retry_delay=30,
    retry_backoff=True,
    retry_backoff_max=300,
    time_limit=5 * 60,
)
def evaluate_grounding(
    tenant_id: str,
    entity_id: str,  # research_task_id or disclosure_id
    entity_type: str,  # research_task, disclosure
    correlation_id: str,
):
    """
    1. Fetch entity (research task result or disclosure)
    2. Extract all citations/claims
    3. Verify each citation exists in database
    4. Check traceability (document ID, URL, etc.)
    5. Check authority (primary vs secondary sources)
    6. Compute GroundingJudge score
    7. Store score in entity record
    8. If score < 0.85: flag for review
    9. Emit event: evaluation.completed
    """
```

---

### 11. `evaluate_toolcall` (Queue: `evaluation`)

**Purpose:** Run ToolCallJudge on agent tool usage  
**Agent:** `AGT_EVAL`  
**Service:** `LLMClient.evaluate()`  
**Priority:** 5 (Normal)  
**Timeout:** 5 minutes  
**Retries:** 2

```python
@celery.task(
    queue="evaluation",
    max_retries=2,
    default_retry_delay=30,
    retry_backoff=True,
    retry_backoff_max=300,
    time_limit=5 * 60,
)
def evaluate_toolcall(
    tenant_id: str,
    agent_execution_id: str,
    tool_calls: list[dict],
    correlation_id: str,
):
    """
    1. Review tool calls made by agent
    2. Verify correct tool was called for intent
    3. Verify arguments are valid and appropriate
    4. Verify no unnecessary tool calls
    5. Compute ToolCallJudge score
    6. Store score
    7. If score < 0.90: flag for review
    8. Emit event: evaluation.completed
    """
```

---

## Task Routing Configuration

```python
# Celery configuration
celery_app = Celery("lexcore")

celery_app.conf.update(
    broker_url="redis://localhost:6379/0",
    result_backend="redis://localhost:6379/1",
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=24 * 60 * 60,  # 24 hours
    
    # Task routing
    task_routes={
        "tasks.ingest_document": {"queue": "ingestion"},
        "tasks.batch_ingest": {"queue": "ingestion"},
        "tasks.execute_research": {"queue": "research"},
        "tasks.execute_scan": {"queue": "patent"},
        "tasks.search_prior_art": {"queue": "patent"},
        "tasks.generate_disclosure": {"queue": "patent"},
        "tasks.evaluate_monitor_rules": {"queue": "monitor"},
        "tasks.anchor_to_blockchain": {"queue": "blockchain"},
        "tasks.send_email": {"queue": "email"},
        "tasks.evaluate_grounding": {"queue": "evaluation"},
        "tasks.evaluate_toolcall": {"queue": "evaluation"},
    },
    
    # Worker configuration
    worker_prefetch_multiplier=1,  # Don't prefetch tasks (fair)
    task_acks_late=True,  # Acknowledge after completion
    task_reject_on_worker_lost=True,  # Re-queue if worker dies
    task_default_priority=5,  # Normal priority
    
    # Rate limiting (per task)
    task_rate_limit={
        "tasks.ingest_document": "100/m",  # 100 per minute per worker
        "tasks.search_prior_art": "50/m",  # 50 per minute (respect API limits)
        "tasks.anchor_to_blockchain": "10/m",  # 10 per minute (Polygon rate limit)
    },
)
```

---

## Worker Pool Sizing

| Queue | Workers | Concurrency | Memory Limit | CPU Limit |
|-------|---------|-------------|-------------|-----------|
| default | 4 | 4 | 512Mi | 500m |
| ingestion | 8 | 8 | 1Gi | 1000m |
| search | 4 | 4 | 512Mi | 500m |
| research | 4 | 4 | 2Gi | 2000m |
| patent | 8 | 8 | 2Gi | 2000m |
| monitor | 2 | 2 | 512Mi | 500m |
| email | 2 | 2 | 256Mi | 250m |
| evaluation | 4 | 4 | 2Gi | 2000m |
| blockchain | 2 | 2 | 512Mi | 500m |

**Kubernetes Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: celery-patent-worker
spec:
  replicas: 2  # 2 pods × 4 concurrency = 8 workers
  selector:
    matchLabels:
      app: celery-patent-worker
  template:
    spec:
      containers:
      - name: worker
        image: lexcore-api:latest
        command: ["celery", "-A", "tasks", "worker", "-Q", "patent", "-c", "4"]
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
```

---

## Dead Letter Queue (DLQ)

Failed tasks after max retries are sent to the DLQ for manual review:

```python
# Celery DLQ configuration
celery_app.conf.update(
    task_routes={
        "celery.*": {"queue": "celery"},
    },
    task_reject_on_worker_lost=True,
    task_acks_late=True,
)

# Monitor DLQ
from celery.events.state import State

async def monitor_dlq():
    """Monitor DLQ for stuck tasks and alert."""
    # Query Redis for failed tasks
    failed_tasks = await redis.keys("celery:task:failed:*")
    
    if len(failed_tasks) > 10:
        await alert_ops(
            f"{len(failed_tasks)} tasks in DLQ",
            severity="warning",
        )
    
    if len(failed_tasks) > 50:
        await alert_ops(
            f"{len(failed_tasks)} tasks in DLQ — critical",
            severity="critical",
        )
```

**DLQ Processing:**
1. Failed tasks stored in `failed_tasks` table
2. Dashboard shows failed tasks with error details
3. Retry button triggers manual re-execution
4. After 3 manual retries, escalate to engineering

---

## Task Monitoring

### Flower Dashboard
```
URL: https://flower.lexcore.com (protected by SSO)
Features:
- Real-time task monitoring
- Worker status and resource usage
- Task retry controls
- Rate limit visualization
```

### Prometheus Metrics
```python
# Celery Prometheus metrics
celery_task_received_total = Counter("celery_task_received_total", "Tasks received", ["task_name", "queue"])
celery_task_completed_total = Counter("celery_task_completed_total", "Tasks completed", ["task_name", "queue", "status"])
celery_task_duration_seconds = Histogram("celery_task_duration_seconds", "Task duration", ["task_name"])
celery_task_retry_total = Counter("celery_task_retry_total", "Task retries", ["task_name"])
celery_task_failed_total = Counter("celery_task_failed_total", "Task failures", ["task_name", "exception"])
celery_worker_up = Gauge("celery_worker_up", "Worker status", ["worker_name", "queue"])
```

### Alerts
| Alert | Threshold | Action |
|-------|-----------|--------|
| Task queue depth | > 1000 tasks | Scale workers |
| Task failure rate | > 5% for 5 min | Alert ops, check source APIs |
| Worker down | Any worker missing for 2 min | Restart pod, alert ops |
| Task duration P95 | > 2x SLA | Alert ops, optimize task |
| DLQ size | > 10 tasks | Alert ops |
| DLQ size | > 50 tasks | Critical alert, page on-call |

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-29 | Initial worker registry | C05 background jobs definition |
