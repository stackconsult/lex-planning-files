# E2E_TEST_SUITE.md — LexCore + LexRadar End-to-End Tests

> **Build System:** Unified Build System v2 | **Chunk:** C08 — Testing + QA | **Horde:** HORDE-QA

---

## Overview

End-to-end tests verify complete user journeys through the full stack: frontend → API → database → external services. They run against a deployed staging environment or full Docker Compose production-like stack.

**Framework:** Playwright  
**Browsers:** Chromium (primary), WebKit (mobile Safari), Firefox (smoke)  
**Devices:** Desktop (1280×720), Mobile (390×844)  
**Timeout:** P95 < 10 minutes for full suite  
**Retry:** 1 retry for flakiness (CI only)

---

## Critical Path Tests

### Path 1: User Signup → Login → Search

```typescript
// e2e/tests/user-journey.spec.ts
import { test, expect } from '@playwright/test'

test.describe('User Journey: Signup to Search', () => {
  test('user can signup, login, and search documents', async ({ page }) => {
    // Navigate to app
    await page.goto('https://app.lexcore.com')
    await expect(page).toHaveTitle(/LexCore/)
    
    // Signup with Clerk
    await page.click('button:has-text("Sign Up")')
    await page.fill('[name="email"]', 'test@example.com')
    await page.fill('[name="password"]', 'TestPassword123!')
    await page.click('button:has-text("Continue")')
    await expect(page).toHaveURL(/dashboard/)
    
    // Navigate to search
    await page.click('a:has-text("Search")')
    await page.fill('input[placeholder="Search legal documents..."]', 'machine learning patent')
    await page.click('button:has-text("Search")')
    
    // Verify results
    await expect(page.locator('.search-results')).toBeVisible()
    const results = await page.locator('.result-card').count()
    expect(results).toBeGreaterThan(0)
    
    // Export result
    await page.click('.result-card:first-child button:has-text("Export")')
    await expect(page.locator('.toast')).toHaveText(/Exported/)
  })
})
```

### Path 2: Admin Creates Tenant → Invites User

```typescript
test.describe('Admin Journey: Tenant Management', () => {
  test('admin can create tenant and invite user', async ({ page }) => {
    // Login as admin
    await page.goto('https://app.lexcore.com/login')
    await page.fill('[name="email"]', 'admin@lexcore.com')
    await page.fill('[name="password"]', process.env.ADMIN_PASSWORD)
    await page.click('button:has-text("Sign In")')
    
    // Navigate to admin panel
    await page.click('a:has-text("Admin")')
    await page.click('button:has-text("Create Tenant")')
    
    // Fill tenant form
    await page.fill('[name="name"]', 'Test Tenant LLC')
    await page.fill('[name="slug"]', 'test-tenant-llc')
    await page.selectOption('[name="plan"]', 'enterprise')
    await page.click('button:has-text("Create")')
    
    // Invite user
    await page.click('button:has-text("Invite User")')
    await page.fill('[name="email"]', 'user@testtenant.com')
    await page.click('button:has-text("Send Invitation")')
    await expect(page.locator('.toast')).toHaveText(/Invitation sent/)
  })
})
```

### Path 3: GitHub Scanner → Invention Detection → Prior Art Search → Disclosure Draft

```typescript
test.describe('Developer Journey: Invention to Disclosure', async () => {
  test('developer can connect GitHub and generate disclosure', async ({ page }) => {
    // Login as developer
    await page.goto('https://app.lexcore.com/login')
    await page.fill('[name="email"]', 'dev@example.com')
    await page.fill('[name="password"]', 'DevPassword123!')
    await page.click('button:has-text("Sign In")')
    
    // Connect GitHub
    await page.click('a:has-text("Settings")')
    await page.click('button:has-text("Connect GitHub")')
    await page.fill('[name="repo"]', 'owner/repo')
    await page.click('button:has-text("Connect")')
    
    // Wait for scanner to detect invention
    await page.click('a:has-text("Inventions")')
    await expect(page.locator('.invention-card')).toBeVisible({ timeout: 30000 })
    
    // Score prior art
    await page.click('.invention-card:first-child button:has-text("Score Prior Art")')
    await expect(page.locator('.prior-art-results')).toBeVisible({ timeout: 60000 })
    
    // Draft disclosure
    await page.click('button:has-text("Draft Disclosure")')
    await expect(page.locator('.disclosure-editor')).toBeVisible({ timeout: 60000 })
    
    // Verify 10 LHP sections
    const sections = await page.locator('.disclosure-section').count()
    expect(sections).toBe(10)
  })
})
```

### Path 4: Attorney Portal: Receive Email → View Handoff → Edit → Submit Review

```typescript
test.describe('Attorney Journey: Handoff to Review', async () => {
  test('attorney can receive handoff, edit, and submit review', async ({ page }) => {
    // Access attorney portal via magic link (simulated)
    await page.goto(`https://attorney.lexcore.com/handoff/${testHandoffId}`)
    
    // Verify handoff package loaded
    await expect(page.locator('.handoff-header')).toBeVisible()
    await expect(page.locator('.disclosure-content')).toBeVisible()
    
    // Edit 3 attorney-editable sections
    await page.click('#section-claims button:has-text("Edit")')
    await page.fill('#section-claims textarea', 'Modified claims text')
    await page.click('button:has-text("Save")')
    
    await page.click('#section-detailed-description button:has-text("Edit")')
    await page.fill('#section-detailed-description textarea', 'Modified description')
    await page.click('button:has-text("Save")')
    
    await page.click('#section-embodiments button:has-text("Edit")')
    await page.fill('#section-embodiments textarea', 'Modified embodiments')
    await page.click('button:has-text("Save")')
    
    // Submit review
    await page.selectOption('[name="decision"]', 'approve')
    await page.fill('[name="comments"]', 'Ready for filing')
    await page.click('button:has-text("Submit Review")')
    
    await expect(page.locator('.toast')).toHaveText(/Review submitted/)
  })
})
```

### Path 5: Blockchain Anchoring

```typescript
test.describe('Blockchain: Verify Anchoring', async ({ page }) => {
  test('filed disclosure is anchored on Polygon', async ({ page, request }) => {
    // Get bundle ID from database (via API)
    const bundleId = await getTestBundleId()
    
    // Verify blockchain transaction exists
    const response = await request.get(`https://api.lexcore.com/v1/bundles/${bundleId}/blockchain`)
    const data = await response.json()
    
    expect(data.transaction_hash).toBeTruthy()
    expect(data.network).toBe('polygon')
    expect(data.block_number).toBeTruthy()
    
    // Verify only hash is stored (no raw IP)
    expect(data.on_chain_content).toMatch(/^[a-f0-9]{64}$/) // SHA-256 hash only
    expect(data.on_chain_content.length).toBe(64)
  })
})
```

---

## Test Data Management

```typescript
// e2e/fixtures/test-data.ts
export const testUsers = {
  admin: { email: 'admin@lexcore.com', password: process.env.ADMIN_PASSWORD },
  developer: { email: 'dev@example.com', password: 'DevPassword123!' },
  attorney: { email: 'attorney@firm.com', password: 'AttorneyPassword123!' }
}

export const testDocuments = {
  patent: { id: 'patent-123', title: 'Machine Learning Patent', source: 'USPTO' },
  disclosure: { id: 'disc-456', title: 'AI Method Disclosure', status: 'draft' }
}

export async function setupTestDatabase() {
  // Create test tenant, users, documents via API
  const apiClient = new APIClient(process.env.STAGING_API_URL)
  await apiClient.createTestTenant()
  await apiClient.createTestUsers()
}

export async function cleanupTestDatabase() {
  // Delete test data via API
  const apiClient = new APIClient(process.env.STAGING_API_URL)
  await apiClient.cleanupTestData()
}
```

---

## Running E2E Tests

```bash
# Run all E2E tests
npx playwright test

# Run specific test file
npx playwright test e2e/tests/user-journey.spec.ts

# Run with UI mode (interactive)
npx playwright test --ui

# Run headed (visible browser)
npx playwright test --headed

# Run on mobile viewport
npx playwright test --project=webkit

# Run on staging environment
STAGING_URL=https://staging.lexcore.com npx playwright test
```

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-30 | Initial E2E test suite | C08 Testing + QA definition |
