# AGENT_MANIFEST.md — LexCore + LexRadar Agent Registry

> **Build System:** Unified Build System v2  
> **Chunk:** C05 — Services + Workers + Agents  
> **Horde:** HORDE-AGENTS  
> **Control Plane:** ENGINEERING  

---

## Overview

LexCore + LexRadar uses an **agent-based execution model** where specialized agents (from the HORDE) are dispatched to handle domain-specific tasks. Each agent is a stateless, idempotent worker that:
1. Receives a **BAM (Binary Action Matrix) signal** from the `AGT_ROUTER`
2. Executes its specific function via service calls
3. Produces an **artifact** (document, report, scoring result, filing bundle)
4. Logs all actions to the `audit_log` table
5. Never directly imports another agent (AGT-G1 enforcement)

All agents implement `BaseAgent` and are registered with the `AgentRegistry`.

---

## Agent Architecture

```
┌───────────────┐
│  AGT_ROUTER   │  → Parses BAM compound, dispatches to target agent
│  (Dispatcher) │
└───────┬───────┘
        │
        ├──→ AGT_SEARCH    → SearchService.search()
        ├──→ AGT_CITE      → CitationService.get_citations()
        ├──→ AGT_ANALYSIS  → ResearchService.execute_research()
        ├──→ AGT_MONITOR   → MonitorService.evaluate_rules()
        ├──→ AGT_SCANNER   → ScanService.execute_scan()
        ├──→ AGT_DISCLOSER → DisclosureService.generate_disclosure()
        ├──→ AGT_PRIORART  → PriorArtService.search_prior_art()
        ├──→ AGT_ATTYFLOW  → HandoffService.deliver_handoff()
        ├──→ AGT_BAM     → BAM service (verifies/genesis hash)
        ├──→ AGT_EVAL     → Evaluation service (LLM evals)
        ├──→ AGT_LOG      → Structured logging service
        └──→ AGT_NOTIFY   → Notification service (email, slack)
```

---

## Base Agent Interface

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from uuid import UUID

@dataclass
class AgentResult:
    """Standard result from any agent execution."""
    agent_name: str
    correlation_id: UUID
    success: bool
    artifact: Any | None  # The produced artifact
    error: str | None
    latency_ms: float
    audit_log_id: UUID | None

class BaseAgent(ABC):
    """All agents MUST inherit from BaseAgent."""
    
    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Unique agent identifier (matches HORDE naming)."""
    
    @property
    @abstractmethod
    def bam_intents(self) -> list[str]:
        """BAM intents this agent handles."""
    
    @abstractmethod
    async def execute(
        self,
        correlation_id: UUID,
        bam_signal: dict,
        tenant_id: UUID,
        user_id: UUID | None,
    ) -> AgentResult:
        """
        Execute agent function.
        
        Rules:
        1. MUST validate bam_signal['intent'] is in self.bam_intents
        2. MUST NOT import or call another agent directly (AGT-G1)
        3. MUST use Service layer for all business logic
        4. MUST write audit row for all state changes
        5. MUST catch all exceptions and return AgentResult with error
        6. MUST be idempotent (same correlation_id = same result)
        """
    
    async def health_check(self) -> dict:
        """Return agent health status. Default: check all service dependencies."""
        return {"status": "healthy", "agent": self.agent_name}
```

---

## Agent Registry

```python
class AgentRegistry:
    """Central registry for all agents."""
    
    _agents: dict[str, BaseAgent] = {}
    
    @classmethod
    def register(cls, agent: BaseAgent) -> None:
        cls._agents[agent.agent_name] = agent
    
    @classmethod
    def get(cls, agent_name: str) -> BaseAgent:
        if agent_name not in cls._agents:
            raise AgentNotFound(f"Agent {agent_name} not registered")
        return cls._agents[agent_name]
    
    @classmethod
    def list(cls) -> list[str]:
        return list(cls._agents.keys())
    
    @classmethod
    def health_all(cls) -> dict[str, dict]:
        return {name: agent.health_check() for name, agent in cls._agents.items()}
```

---

## AGT_ROUTER — The Dispatcher

**Purpose:** Parse BAM compounds and route to the correct agent  
**Singleton:** 1 instance per API worker  
**Critical Rule:** AGT_ROUTER is the ONLY agent that dispatches to other agents

```python
class AGT_ROUTER(BaseAgent):
    agent_name = "AGT_ROUTER"
    bam_intents = ["route"]  # Meta-intent
    
    async def execute(
        self,
        correlation_id: UUID,
        bam_signal: dict,
        tenant_id: UUID,
        user_id: UUID | None,
    ) -> AgentResult:
        """
        BAM Signal Structure:
        {
            "intent": "legal_search|research_task|document_retrieve|citation_graph|update_check|jurisdiction_query|...",
            "jurisdiction_scope": "J_US_FED|...",
            "doc_type_scope": "STATUTE|REGULATION|CASE|ALL",
            "confidence": 0.0-1.0,
            "routing_decision": "AGT_SEARCH|AGT_ANALYSIS|AGT_CITE|AGT_MONITOR|direct",
            "payload": {...}  # Agent-specific parameters
        }
        """
        
        intent = bam_signal["intent"]
        routing = self._determine_routing(intent, bam_signal)
        
        if routing == "direct":
            # Simple operations handled directly by service layer
            return AgentResult(
                agent_name="AGT_ROUTER",
                correlation_id=correlation_id,
                success=True,
                artifact=await self._handle_direct(bam_signal),
                error=None,
                latency_ms=0,
                audit_log_id=None,
            )
        
        # Dispatch to target agent
        target_agent = AgentRegistry.get(routing)
        return await target_agent.execute(
            correlation_id=correlation_id,
            bam_signal=bam_signal,
            tenant_id=tenant_id,
            user_id=user_id,
        )
    
    def _determine_routing(self, intent: str, bam_signal: dict) -> str:
        routing_map = {
            "legal_search": "AGT_SEARCH",
            "research_task": "AGT_ANALYSIS",
            "document_retrieve": "direct",
            "citation_graph": "AGT_CITE",
            "update_check": "AGT_MONITOR",
            "jurisdiction_query": "direct",
            "code_scan": "AGT_SCANNER",
            "disclosure_generate": "AGT_DISCLOSER",
            "prior_art_search": "AGT_PRIORART",
            "handoff_deliver": "AGT_ATTYFLOW",
            "bam_verify": "AGT_BAM",
            "eval_score": "AGT_EVAL",
            "log_event": "AGT_LOG",
            "notify_user": "AGT_NOTIFY",
        }
        return routing_map.get(intent, "direct")
```

---

## LexCore Domain Agents

### AGT_SEARCH — Legal Document Search

```python
class AGT_SEARCH(BaseAgent):
    agent_name = "AGT_SEARCH"
    bam_intents = ["legal_search", "hybrid_search", "citation_search"]
    
    def __init__(self, search_service: SearchService):
        self.search_service = search_service  # Dependency injection
    
    async def execute(self, correlation_id, bam_signal, tenant_id, user_id):
        result = await self.search_service.search(
            tenant_id=tenant_id,
            query=bam_signal["payload"]["query"],
            jurisdiction=bam_signal["payload"].get("jurisdiction"),
            body_of_law=bam_signal["payload"].get("body_of_law"),
            top_k=bam_signal["payload"].get("top_k", 10),
            include_citations=bam_signal["payload"].get("include_citations", True),
        )
        
        return AgentResult(
            agent_name=self.agent_name,
            correlation_id=correlation_id,
            success=True,
            artifact=result,
            error=None,
            latency_ms=result.latency_ms,
            audit_log_id=None,  # SearchService writes its own audit row
        )
```

**Artifacts Produced:**
- `SearchResult` — ranked documents with scores
- `CitationChain` — related citations (if requested)

**SLA:**
- P95: 500ms (cache miss), 5ms (cache hit)
- P99: 1000ms (cache miss)

---

### AGT_CITE — Citation Graph Traversal

```python
class AGT_CITE(BaseAgent):
    agent_name = "AGT_CITE"
    bam_intents = ["citation_graph", "authority_chain", "overruled_detect"]
    
    def __init__(self, citation_service: CitationService):
        self.citation_service = citation_service
    
    async def execute(self, correlation_id, bam_signal, tenant_id, user_id):
        result = await self.citation_service.get_citations(
            tenant_id=tenant_id,
            doc_id=UUID(bam_signal["payload"]["doc_id"]),
            direction=bam_signal["payload"]["direction"],
            depth=bam_signal["payload"]["depth"],
        )
        
        return AgentResult(
            agent_name=self.agent_name,
            correlation_id=correlation_id,
            success=True,
            artifact=result,
            error=None,
            latency_ms=0,
            audit_log_id=None,
        )
```

**Artifacts Produced:**
- `CitationGraph` — nodes, edges, authority chain, overruled cases

**SLA:**
- P95: 300ms (depth=3), 800ms (depth=5)
- P99: 1500ms (depth=5)

---

### AGT_ANALYSIS — Legal Research & Synthesis

```python
class AGT_ANALYSIS(BaseAgent):
    agent_name = "AGT_ANALYSIS"
    bam_intents = ["research_task", "synthesize", "gap_detect"]
    
    def __init__(self, research_service: ResearchService):
        self.research_service = research_service
    
    async def execute(self, correlation_id, bam_signal, tenant_id, user_id):
        task = await self.research_service.create_research_task(
            tenant_id=tenant_id,
            question=bam_signal["payload"]["question"],
            jurisdictions=bam_signal["payload"].get("jurisdictions", []),
            output_format=bam_signal["payload"].get("output_format", "structured_report"),
            max_sources=bam_signal["payload"].get("max_sources", 20),
        )
        
        # For sync execution (< 60s)
        result = await self.research_service.execute_research(
            tenant_id=tenant_id,
            task_id=task.id,
        )
        
        return AgentResult(
            agent_name=self.agent_name,
            correlation_id=correlation_id,
            success=True,
            artifact=result,
            error=None,
            latency_ms=0,
            audit_log_id=None,
        )
```

**Artifacts Produced:**
- `ResearchResult` — structured report, citation chain, confidence score, gaps

**SLA:**
- P50: 30s (synchronous)
- P95: 60s (triggers async task)
- Async task: 2-5 minutes

---

### AGT_MONITOR — Legislative Change Monitoring

```python
class AGT_MONITOR(BaseAgent):
    agent_name = "AGT_MONITOR"
    bam_intents = ["update_check", "monitor_evaluate", "alert_generate"]
    
    def __init__(self, monitor_service: MonitorService):
        self.monitor_service = monitor_service
    
    async def execute(self, correlation_id, bam_signal, tenant_id, user_id):
        if bam_signal["intent"] == "monitor_evaluate":
            # Scheduled evaluation (every 6 hours via Celery)
            alerts = await self.monitor_service.evaluate_rules(
                tenant_id=bam_signal["payload"].get("tenant_id"),
            )
            return AgentResult(
                agent_name=self.agent_name,
                correlation_id=correlation_id,
                success=True,
                artifact={"alerts_generated": len(alerts), "alerts": alerts},
                error=None,
                latency_ms=0,
                audit_log_id=None,
            )
        
        # update_check intent
        result = await self.monitor_service.get_alerts(
            tenant_id=tenant_id,
            filters=bam_signal["payload"].get("filters"),
            pagination=bam_signal["payload"].get("pagination"),
        )
        
        return AgentResult(
            agent_name=self.agent_name,
            correlation_id=correlation_id,
            success=True,
            artifact=result,
            error=None,
            latency_ms=0,
            audit_log_id=None,
        )
```

**Artifacts Produced:**
- `list[MonitorAlert]` — alerts for legislative changes
- `MonitorEvaluationReport` — summary of rule evaluation

**SLA:**
- P95: 200ms (alert retrieval)
- Scheduled eval: 5-30 minutes (depends on rule count)

---

## LexRadar Domain Agents

### AGT_SCANNER — Code Repository Scanning

```python
class AGT_SCANNER(BaseAgent):
    agent_name = "AGT_SCANNER"
    bam_intents = ["code_scan", "invention_detect"]
    
    def __init__(self, scan_service: ScanService):
        self.scan_service = scan_service
    
    async def execute(self, correlation_id, bam_signal, tenant_id, user_id):
        job = await self.scan_service.trigger_scan(
            tenant_id=tenant_id,
            source=bam_signal["payload"]["source"],  # GitHub, Jira, Notion
            source_id=bam_signal["payload"]["source_id"],
            trigger=bam_signal["payload"].get("trigger", "manual"),
        )
        
        return AgentResult(
            agent_name=self.agent_name,
            correlation_id=correlation_id,
            success=True,
            artifact=job,
            error=None,
            latency_ms=0,
            audit_log_id=None,
        )
```

**Artifacts Produced:**
- `ScanJob` — job ID, status, estimated completion
- `list[InventionSignal]` — detected invention signals (async)

**SLA:**
- Trigger: < 100ms
- Execution: 30s - 10 minutes (depends on repo size)

---

### AGT_PRIORART — Prior Art Search

```python
class AGT_PRIORART(BaseAgent):
    agent_name = "AGT_PRIORART"
    bam_intents = ["prior_art_search", "patent_search"]
    
    def __init__(self, prior_art_service: PriorArtService):
        self.prior_art_service = prior_art_service
    
    async def execute(self, correlation_id, bam_signal, tenant_id, user_id):
        job = await self.prior_art_service.search_prior_art(
            tenant_id=tenant_id,
            invention_id=UUID(bam_signal["payload"]["invention_id"]),
            keywords=bam_signal["payload"].get("keywords", []),
            sources=bam_signal["payload"].get("sources"),
        )
        
        return AgentResult(
            agent_name=self.agent_name,
            correlation_id=correlation_id,
            success=True,
            artifact=job,
            error=None,
            latency_ms=0,
            audit_log_id=None,
        )
```

**Artifacts Produced:**
- `PriorArtSearchJob` — job ID, sources to search
- `list[PriorArtResult]` — ranked prior art results (async)

**SLA:**
- Trigger: < 100ms
- Execution: 1-3 minutes (7 parallel API calls)

---

### AGT_DISCLOSER — Disclosure Draft Generation

```python
class AGT_DISCLOSER(BaseAgent):
    agent_name = "AGT_DISCLOSER"
    bam_intents = ["disclosure_generate", "patent_draft"]
    
    def __init__(self, disclosure_service: DisclosureService):
        self.disclosure_service = disclosure_service
    
    async def execute(self, correlation_id, bam_signal, tenant_id, user_id):
        job = await self.disclosure_service.generate_disclosure(
            tenant_id=tenant_id,
            invention_id=UUID(bam_signal["payload"]["invention_id"]),
            disclosure_type=bam_signal["payload"].get("disclosure_type", "PROVISIONAL"),
            claim_themes=bam_signal["payload"].get("claim_themes"),
        )
        
        return AgentResult(
            agent_name=self.agent_name,
            correlation_id=correlation_id,
            success=True,
            artifact=job,
            error=None,
            latency_ms=0,
            audit_log_id=None,
        )
```

**Artifacts Produced:**
- `DisclosureGenerationJob` — job ID
- `Disclosure` — 10-section LHP disclosure draft (async)

**SLA:**
- Trigger: < 100ms
- Execution: 2-5 minutes (LLM generation + grounding)

---

### AGT_ATTYFLOW — Attorney Handoff Delivery

```python
class AGT_ATTYFLOW(BaseAgent):
    agent_name = "AGT_ATTYFLOW"
    bam_intents = ["handoff_deliver", "attorney_notify"]
    
    def __init__(self, handoff_service: HandoffService):
        self.handoff_service = handoff_service
    
    async def execute(self, correlation_id, bam_signal, tenant_id, user_id):
        result = await self.handoff_service.deliver_handoff(
            tenant_id=tenant_id,
            disclosure_id=UUID(bam_signal["payload"]["disclosure_id"]),
            attorney_email=bam_signal["payload"]["attorney_email"],
            attorney_name=bam_signal["payload"]["attorney_name"],
            message=bam_signal["payload"].get("message"),
        )
        
        return AgentResult(
            agent_name=self.agent_name,
            correlation_id=correlation_id,
            success=True,
            artifact=result,
            error=None,
            latency_ms=0,
            audit_log_id=None,
        )
```

**Artifacts Produced:**
- `HandoffDelivery` — portal URL, expiry, delivery confirmation

**SLA:**
- P95: 500ms (email delivery may take 1-5 minutes)

---

## Cross-Cutting Agents

### AGT_BAM — BAM Verification

```python
class AGT_BAM(BaseAgent):
    agent_name = "AGT_BAM"
    bam_intents = ["bam_verify", "bam_sign"]
    
    def __init__(self, bam_service: BAMService):
        self.bam_service = bam_service
    
    async def execute(self, correlation_id, bam_signal, tenant_id, user_id):
        if bam_signal["intent"] == "bam_verify":
            # Verify BAM genesis hash
            valid = await self.bam_service.verify_genesis_hash(
                bam_signal["payload"]["bam_compound"],
                bam_signal["payload"]["expected_hash"],
            )
            return AgentResult(
                agent_name=self.agent_name,
                correlation_id=correlation_id,
                success=valid,
                artifact={"valid": valid},
                error=None if valid else "BAM genesis hash mismatch",
                latency_ms=0,
                audit_log_id=None,
            )
        
        # bam_sign intent
        signature = await self.bam_service.sign_bam(
            bam_signal["payload"]["bam_compound"],
        )
        return AgentResult(
            agent_name=self.agent_name,
            correlation_id=correlation_id,
            success=True,
            artifact={"signature": signature},
            error=None,
            latency_ms=0,
            audit_log_id=None,
        )
```

**Artifacts Produced:**
- `dict` — verification result or signature

---

### AGT_EVAL — LLM Evaluation

```python
class AGT_EVAL(BaseAgent):
    agent_name = "AGT_EVAL"
    bam_intents = ["eval_score", "eval_judge"]
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    async def execute(self, correlation_id, bam_signal, tenant_id, user_id):
        if bam_signal["intent"] == "eval_judge":
            # GroundingJudge: verify citations are real, traceable, authoritative
            result = await self._run_grounding_judge(
                bam_signal["payload"]["citations"],
                bam_signal["payload"]["document_id"],
            )
            return AgentResult(
                agent_name=self.agent_name,
                correlation_id=correlation_id,
                success=result["score"] >= 0.85,
                artifact=result,
                error=None if result["score"] >= 0.85 else "Grounding score below threshold",
                latency_ms=result["latency_ms"],
                audit_log_id=None,
            )
        
        # eval_score intent
        # ToolCallJudge: verify correct tool use, arguments
        result = await self._run_toolcall_judge(
            bam_signal["payload"]["tool_calls"],
        )
        return AgentResult(
            agent_name=self.agent_name,
            correlation_id=correlation_id,
            success=result["score"] >= 0.90,
            artifact=result,
            error=None if result["score"] >= 0.90 else "ToolCall score below threshold",
            latency_ms=result["latency_ms"],
            audit_log_id=None,
        )
```

**Artifacts Produced:**
- `dict` — evaluation score, details, threshold pass/fail

**SLA:**
- P95: 2000ms (LLM evaluation)

---

### AGT_LOG — Structured Logging

```python
class AGT_LOG(BaseAgent):
    agent_name = "AGT_LOG"
    bam_intents = ["log_event", "log_error", "log_audit"]
    
    def __init__(self, structlog_logger):
        self.logger = structlog_logger
    
    async def execute(self, correlation_id, bam_signal, tenant_id, user_id):
        level = bam_signal["payload"]["level"]
        message = bam_signal["payload"]["message"]
        
        self.logger.log(
            level=level,
            event=message,
            correlation_id=str(correlation_id),
            tenant_id=str(tenant_id),
            user_id=str(user_id) if user_id else None,
            agent=self.agent_name,
            **bam_signal["payload"].get("extra", {}),
        )
        
        return AgentResult(
            agent_name=self.agent_name,
            correlation_id=correlation_id,
            success=True,
            artifact=None,
            error=None,
            latency_ms=0,
            audit_log_id=None,
        )
```

**Artifacts Produced:** None (side effect: log entry)

---

### AGT_NOTIFY — User Notifications

```python
class AGT_NOTIFY(BaseAgent):
    agent_name = "AGT_NOTIFY"
    bam_intents = ["notify_user", "notify_attorney", "alert_change"]
    
    def __init__(self, email_service: EmailService, slack_service: SlackService):
        self.email_service = email_service
        self.slack_service = slack_service
    
    async def execute(self, correlation_id, bam_signal, tenant_id, user_id):
        channel = bam_signal["payload"]["channel"]  # email, slack, in_app
        
        if channel == "email":
            await self.email_service.send(
                to=bam_signal["payload"]["to"],
                subject=bam_signal["payload"]["subject"],
                body=bam_signal["payload"]["body"],
                html=bam_signal["payload"].get("html"),
            )
        elif channel == "slack":
            await self.slack_service.send_message(
                channel=bam_signal["payload"]["slack_channel"],
                message=bam_signal["payload"]["body"],
            )
        
        return AgentResult(
            agent_name=self.agent_name,
            correlation_id=correlation_id,
            success=True,
            artifact={"channel": channel, "sent": True},
            error=None,
            latency_ms=0,
            audit_log_id=None,
        )
```

**Artifacts Produced:**
- `dict` — notification confirmation

---

## Agent Deployment Model

| Agent | Deployment | Scaling | Trigger |
|-------|-----------|---------|---------|
| AGT_ROUTER | In-process (FastAPI) | Fixed per worker | Every API request |
| AGT_SEARCH | In-process | Fixed per worker | API request, async pipeline |
| AGT_CITE | In-process | Fixed per worker | API request |
| AGT_ANALYSIS | In-process + Celery | Scale workers | API request (< 60s) / Celery (> 60s) |
| AGT_MONITOR | Celery scheduled | Fixed (1 per tenant) | Every 6 hours |
| AGT_SCANNER | Celery | Scale workers | API request, webhook, scheduled |
| AGT_PRIORART | Celery | Scale workers | API request |
| AGT_DISCLOSER | Celery | Scale workers | API request |
| AGT_ATTYFLOW | In-process | Fixed per worker | API request |
| AGT_BAM | In-process | Fixed per worker | API request |
| AGT_EVAL | In-process + Celery | Scale workers | API request, async eval tasks |
| AGT_LOG | In-process | Fixed per worker | Every agent execution |
| AGT_NOTIFY | Celery | Scale workers | Event-driven |

---

## Agent Isolation Rules (AGT-G1)

1. **No direct agent-to-agent imports:** Agents must use `AgentRegistry.get()` via `AGT_ROUTER`
2. **No shared mutable state:** All state in PostgreSQL/Redis, agents are stateless
3. **Idempotency:** Same `correlation_id` must produce identical result (replay-safe)
4. **Audit logging:** Every agent execution writes to `audit_log`
5. **Error handling:** All exceptions caught, returned in `AgentResult.error`
6. **Resource limits:** Each agent has CPU/memory limits in Kubernetes

---

## Agent Health Monitoring

```python
# Kubernetes liveness/readiness probes check agent health
@app.get("/health/agents")
async def agent_health():
    health = AgentRegistry.health_all()
    
    all_healthy = all(
        h.get("status") == "healthy" 
        for h in health.values()
    )
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "agents": health,
    }
```

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-29 | Initial agent manifest | C05 agents definition |
