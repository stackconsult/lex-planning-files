# INTEGRATION_TEST_PLAN.md — LexCore + LexRadar Integration Tests

> **Build System:** Unified Build System v2 | **Chunk:** C08 — Testing + QA | **Horde:** HORDE-QA

---

## Overview

Integration tests verify that components work together correctly. They require real (containerized) infrastructure: PostgreSQL + pgvector, Redis, Qdrant. External APIs are mocked or use sandbox credentials.

**Framework:** pytest + Docker Compose  
**Runtime:** Docker Compose stack  
**Coverage target:** 70% of service boundaries  
**Timeout:** P95 < 15 minutes  

---

## Test Infrastructure (Docker Compose)

```yaml
# docker-compose.test.yml
version: "3.8"
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: lexcore_test
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
    ports:
      - "5432:5432"
    volumes:
      - ./schema/migrations:/docker-entrypoint-initdb.d

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  qdrant:
    image: qdrant/qdrant:v1.8
    ports:
      - "6333:6333"
      - "6334:6334"

  api:
    build:
      context: .
      dockerfile: docker/api/Dockerfile
    depends_on:
      - postgres
      - redis
      - qdrant
    environment:
      DATABASE_URL: postgresql://test:test@postgres:5432/lexcore_test
      REDIS_URL: redis://redis:6379/0
      QDRANT_URL: http://qdrant:6333
      ENVIRONMENT: test
    ports:
      - "8000:8000"
```

---

## Test Categories

### 1. API Endpoint Integration

**Scope:** Full HTTP request/response cycle  
**Database:** Real PostgreSQL (rolled back after each test)  

```python
# tests/integration/test_search_api.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
class TestSearchAPI:
    async def test_search_returns_results_with_auth(self, client: AsyncClient, auth_headers):
        """Verify authenticated search returns results."""
        response = await client.get(
            "/api/v1/search",
            params={"query": "machine learning", "page": 1, "page_size": 10},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) <= 10
    
    async def test_search_without_auth_returns_401(self, client: AsyncClient):
        """Verify unauthenticated requests are rejected."""
        response = await client.get("/api/v1/search", params={"query": "test"})
        assert response.status_code == 401
        assert response.json()["error_code"] == "AUTH_MISSING_TOKEN"
    
    async def test_search_rate_limit_enforced(self, client: AsyncClient, auth_headers):
        """Verify rate limit after 30 requests/min."""
        for _ in range(30):
            await client.get("/api/v1/search", params={"query": "test"}, headers=auth_headers)
        
        response = await client.get("/api/v1/search", params={"query": "test"}, headers=auth_headers)
        assert response.status_code == 429
        assert response.json()["error_code"] == "RATE_LIMIT_EXCEEDED"
    
    async def test_search_caches_results(self, client: AsyncClient, auth_headers):
        """Verify search results are cached in Redis."""
        query = "unique_test_query_12345"
        
        # First request
        response1 = await client.get("/api/v1/search", params={"query": query}, headers=auth_headers)
        assert response1.status_code == 200
        
        # Verify cache key exists in Redis
        cache_key = f"search:{query}:tenant-1:1:10"
        assert await redis.exists(cache_key) == 1
        
        # Second request should be faster (cached)
        response2 = await client.get("/api/v1/search", params={"query": query}, headers=auth_headers)
        assert response2.json() == response1.json()
```

### 2. Database + RLS Integration

```python
# tests/integration/test_rls_enforcement.py
import pytest
from asyncpg import Connection

@pytest.mark.asyncio
class TestRLSEnforcement:
    async def test_tenant_a_cannot_read_tenant_b_data(self, db: Connection):
        """SYS-CRIT-04: Verify tenant isolation at database level."""
        # Insert document for tenant-1
        await db.execute(
            "INSERT INTO documents (id, tenant_id, title) VALUES ($1, $2, $3)",
            "doc-1", "tenant-1", "Tenant 1 Document"
        )
        
        # Switch to tenant-2 context
        await db.execute("SELECT set_config('app.current_tenant_id', 'tenant-2', true)")
        
        # Tenant-2 should not see tenant-1's document
        rows = await db.fetch("SELECT * FROM documents WHERE id = $1", "doc-1")
        assert len(rows) == 0
    
    async def test_superuser_bypasses_rls(self, db: Connection):
        """Verify admin role can read all tenants."""
        await db.execute("SET ROLE admin")
        rows = await db.fetch("SELECT * FROM documents")
        # Should see all documents across all tenants
        assert len(rows) >= 1
```

### 3. Search Pipeline Integration

```python
# tests/integration/test_search_pipeline.py
import pytest

@pytest.mark.asyncio
class TestSearchPipeline:
    async def test_ingest_document_then_search_finds_it(self, client: AsyncClient, auth_headers):
        """End-to-end: ingest → chunk → embed → index → search."""
        # 1. Ingest document
        ingest_response = await client.post(
            "/api/v1/documents/ingest",
            json={
                "url": "https://example.com/patent.pdf",
                "source": "USPTO",
                "title": "Machine Learning Patent 2024",
                "authors": ["John Doe"]
            },
            headers=auth_headers
        )
        assert ingest_response.status_code == 202
        job_id = ingest_response.json()["job_id"]
        
        # 2. Wait for ingestion (poll or use test helper)
        await wait_for_job_completion(job_id, timeout=60)
        
        # 3. Search for the document
        search_response = await client.get(
            "/api/v1/search",
            params={"query": "machine learning patent 2024"},
            headers=auth_headers
        )
        assert search_response.status_code == 200
        results = search_response.json()["results"]
        
        # 4. Verify document appears in results
        doc_ids = [r["id"] for r in results]
        assert any("machine" in r["title"].lower() for r in results)
```

### 4. Auth Integration

```python
# tests/integration/test_auth_flow.py
import pytest

@pytest.mark.asyncio
class TestAuthFlow:
    async def test_clerk_jwt_validated_and_tenant_context_set(self, client: AsyncClient):
        """Verify Clerk JWT → tenant context → RLS chain."""
        # Generate test JWT with tenant claim
        jwt = generate_test_jwt(tenant_id="tenant-1", user_id="user-1")
        
        response = await client.get(
            "/api/v1/tenants/current",
            headers={"Authorization": f"Bearer {jwt}"}
        )
        assert response.status_code == 200
        assert response.json()["tenant_id"] == "tenant-1"
    
    async def test_expired_jwt_rejected(self, client: AsyncClient):
        """Verify expired tokens are rejected."""
        expired_jwt = generate_test_jwt(exp=time.time() - 3600)
        
        response = await client.get(
            "/api/v1/search",
            headers={"Authorization": f"Bearer {expired_jwt}"}
        )
        assert response.status_code == 401
        assert response.json()["error_code"] == "AUTH_TOKEN_EXPIRED"
```

### 5. Worker Integration

```python
# tests/integration/test_worker_execution.py
import pytest
from celery import Celery

@pytest.mark.asyncio
class TestWorkerExecution:
    async def test_ingest_document_task_executes_successfully(self, celery_app: Celery):
        """Verify Celery task runs and stores result."""
        result = celery_app.send_task(
            "api.workers.ingest_document",
            args=["https://example.com/test.pdf", "USPTO"]
        )
        
        # Wait for task completion
        task_result = result.get(timeout=60)
        assert task_result["status"] == "success"
        assert "document_id" in task_result
    
    async def test_worker_failure_stored_in_dlq(self, celery_app: Celery):
        """Verify failed tasks are stored in Dead Letter Queue."""
        result = celery_app.send_task(
            "api.workers.ingest_document",
            args=["invalid://url", "USPTO"]
        )
        
        # Task should fail and be retried
        with pytest.raises(Exception):
            result.get(timeout=30, propagate=True)
        
        # Verify DLQ entry
        dlq_count = await redis.llen("celery-dlq-ingestion")
        assert dlq_count >= 1
```

---

## Running Integration Tests

```bash
# Start test infrastructure
docker compose -f docker-compose.test.yml up -d

# Wait for services to be ready
python scripts/wait_for_services.py

# Run integration tests
pytest api/tests/integration/ -v --tb=short

# With coverage
pytest api/tests/integration/ --cov=api --cov-report=term-missing

# Cleanup
docker compose -f docker-compose.test.yml down -v
```

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-30 | Initial integration test plan | C08 Testing + QA definition |
