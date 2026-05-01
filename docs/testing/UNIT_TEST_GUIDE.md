# UNIT_TEST_GUIDE.md — LexCore + LexRadar Unit Testing

> **Build System:** Unified Build System v2 | **Chunk:** C08 — Testing + QA | **Horde:** HORDE-QA

---

## Overview

Unit tests verify individual functions, classes, and modules in isolation. All external dependencies must be mocked. No unit test should require a database, network, or filesystem.

**Coverage target:** 85% (API), 80% (Frontend)  
**Framework:** pytest (API), Jest + React Testing Library (Frontend)  
**Mocking:** pytest-mock, unittest.mock, MSW (Mock Service Worker)  

---

## API Unit Test Patterns

### Service Tests (60%)

```python
# tests/unit/services/test_legal_search_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.mark.asyncio
class TestLegalSearchService:
    async def test_hybrid_search_combines_vector_and_text(self, mocker):
        # Arrange
        mock_repo = mocker.AsyncMock(spec=DocumentRepository)
        mock_repo.hybrid_search.return_value = [
            DocumentResult(id="doc-1", title="Patent on ML", score=0.95, source="USPTO")
        ]
        
        service = LegalSearchService(repository=mock_repo)
        
        # Act
        results = await service.hybrid_search(
            tenant_id="tenant-1",
            query="machine learning patent",
            filters={"jurisdiction": "US"},
            page=1,
            page_size=10
        )
        
        # Assert
        assert len(results) == 1
        assert results[0].title == "Patent on ML"
        mock_repo.hybrid_search.assert_awaited_once_with(
            tenant_id="tenant-1",
            query="machine learning patent",
            filters={"jurisdiction": "US"},
            page=1,
            page_size=10
        )
    
    async def test_search_caches_results(self, mocker):
        mock_repo = mocker.AsyncMock(spec=DocumentRepository)
        mock_cache = mocker.AsyncMock(spec=RedisCache)
        mock_cache.get.return_value = None  # Cache miss
        
        service = LegalSearchService(repository=mock_repo, cache=mock_cache)
        
        await service.hybrid_search(tenant_id="tenant-1", query="test", filters={}, page=1, page_size=10)
        
        mock_cache.set.assert_awaited_once()
        
    async def test_search_rate_limit_enforced(self, mocker):
        mock_rate_limiter = mocker.AsyncMock(spec=RateLimiter)
        mock_rate_limiter.check_limit.return_value = False  # Limit exceeded
        
        service = LegalSearchService(rate_limiter=mock_rate_limiter)
        
        with pytest.raises(RateLimitExceeded):
            await service.hybrid_search(tenant_id="tenant-1", query="test", filters={}, page=1, page_size=10)
```

### Repository Tests (20%)

```python
# tests/unit/repositories/test_document_repository.py
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
class TestDocumentRepository:
    async def test_hybrid_search_builds_correct_sql(self, mocker):
        mock_pool = mocker.AsyncMock()
        mock_conn = mocker.AsyncMock()
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)
        
        repo = DocumentRepository(pool=mock_pool)
        
        await repo.hybrid_search(
            tenant_id="tenant-1",
            query="test",
            filters={"jurisdiction": "US"},
            page=1,
            page_size=10
        )
        
        # Verify SQL contains RLS clause
        call_args = mock_conn.fetch.call_args[0][0]
        assert "tenant_id = $1" in call_args
        assert "ts_rank_cd" in call_args
        assert "LIMIT $" in call_args
```

### Utility Tests (15%)

```python
# tests/unit/utils/test_hash_utils.py
import pytest
from api.utils.hash import compute_sha256, verify_bundle_integrity

class TestHashUtils:
    def test_compute_sha256_returns_hex_string(self):
        result = compute_sha256(b"test content")
        assert isinstance(result, str)
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)
    
    def test_verify_bundle_integrity_detects_tampering(self):
        bundle = {"docs": [{"id": "1", "hash": "abc123"}]}
        
        with pytest.raises(IntegrityError):
            verify_bundle_integrity(bundle, expected_hash="wrong_hash")
```

### Agent Tests (5%)

```python
# tests/unit/agents/test_base_agent.py
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
class TestBaseAgent:
    async def test_agt_g1_isolation_no_direct_agent_import(self, mocker):
        """SYS-CRIT-03: Agent must not import another agent directly."""
        agent = AGT_PRIORART()
        
        # Mock all service dependencies
        agent.patent_searcher = mocker.AsyncMock()
        agent.patent_searcher.search.return_value = []
        
        result = await agent.execute(query="test")
        
        # Verify no other agent was instantiated or called
        assert result.scores == {}
```

---

## Frontend Unit Test Patterns

### Component Tests

```typescript
// src/__tests__/components/LegalSearchBox.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { LegalSearchBox } from '@/components/search/LegalSearchBox'
import { mockRouter } from '@/test-utils'

describe('LegalSearchBox', () => {
  it('renders search input and button', () => {
    render(<LegalSearchBox />)
    expect(screen.getByRole('searchbox')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /search/i })).toBeInTheDocument()
  })
  
  it('navigates to results on submit', () => {
    const push = jest.fn()
    mockRouter({ push })
    
    render(<LegalSearchBox />)
    fireEvent.change(screen.getByRole('searchbox'), { target: { value: 'patent' } })
    fireEvent.click(screen.getByRole('button', { name: /search/i }))
    
    expect(push).toHaveBeenCalledWith('/search?q=patent')
  })
  
  it('shows loading state while searching', () => {
    render(<LegalSearchBox />)
    fireEvent.click(screen.getByRole('button', { name: /search/i }))
    expect(screen.getByRole('status')).toBeInTheDocument() // spinner
  })
})
```

### Hook Tests

```typescript
// src/__tests__/hooks/useTenantContext.test.tsx
import { renderHook } from '@testing-library/react'
import { useTenantContext } from '@/hooks/useTenantContext'
import { TenantProvider } from '@/components/providers/TenantProvider'

describe('useTenantContext', () => {
  it('returns current tenant from context', () => {
    const wrapper = ({ children }) => (
      <TenantProvider tenant={{ id: 'tenant-1', name: 'Acme Corp' }}>
        {children}
      </TenantProvider>
    )
    
    const { result } = renderHook(() => useTenantContext(), { wrapper })
    expect(result.current.tenant.id).toBe('tenant-1')
  })
  
  it('throws when used outside provider', () => {
    expect(() => renderHook(() => useTenantContext())).toThrow(
      'useTenantContext must be used within TenantProvider'
    )
  })
})
```

---

## Test Conventions

| Convention | Rule |
|------------|------|
| Naming | `test_{unit_under_test}_{scenario}_{expected_result}` |
| Arrange-Act-Assert | Explicitly separated with comments |
| One assertion per test | Prefer focused tests over catch-all |
| Mock external deps | Database, network, filesystem, time |
| No `assert True` | Every test must verify actual behavior |
| No empty tests | Delete or implement; empty tests fail CI |
| Async | Use `pytest.mark.asyncio` or `async/await` in Jest |
| Fixtures | Shared setup in `conftest.py` or `jest.setup.ts` |

---

## Running Unit Tests

```bash
# API
pytest api/tests/unit/ -v --cov=api --cov-report=term-missing

# Frontend
npm test -- --coverage --watchAll=false

# Specific file
pytest api/tests/unit/services/test_legal_search_service.py -v
npm test -- LegalSearchBox.test.tsx
```

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-30 | Initial unit test guide | C08 Testing + QA definition |
