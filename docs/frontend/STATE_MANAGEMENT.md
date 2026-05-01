# STATE_MANAGEMENT.md — LexCore + LexRadar Frontend State Architecture

> **Build System:** Unified Build System v2  
> **Chunk:** C06 — Frontend  
> **Horde:** HORDE-UI  
> **Control Plane:** ENGINEERING  

---

## Overview

The LexCore + LexRadar frontend uses a **server-first, client-cache** state management pattern optimized for Next.js 14 App Router:
- **Server Components** fetch data directly from the API (React Server Components)
- **Client Components** use SWR for caching, mutation, and optimistic updates
- **Server Actions** handle form submissions and mutations
- **React Context** provides tenant/user context to the component tree
- **Zustand** manages global UI state (modals, toasts, sidebar state)

**Key Principles:**
1. Data fetching happens in Server Components where possible
2. Client cache is read-through (SWR) with automatic revalidation
3. Mutations invalidate related cache keys automatically
4. Tenant context is immutable after initial load
5. Correlation IDs propagate through all API calls

---

## State Architecture Diagram

```
┌─────────────────────────────────────────────┐
│  SERVER (Next.js App Router)                │
│  ├── React Server Components (async)         │
│  │   └── fetch() → LexCore API              │
│  │   └── pass data as props to children      │
│  ├── Client Components                       │
│  │   └── SWR useSWR() → cache / API         │
│  │   └── Zustand → global UI state           │
│  ├── Server Actions ("use server")           │
│  │   └── POST / PATCH / DELETE → API          │
│  │   └── revalidatePath() / revalidateTag()  │
│  └── Context Providers                       │
│      └── TenantContext                        │
│      └── AuthContext (Clerk)                │
│      └── CorrelationContext                   │
└─────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│  API (LexCore + LexRadar)                   │
│  ├── REST endpoints                          │
│  ├── MCP tools                               │
│  └── WebSocket (real-time updates)           │
└─────────────────────────────────────────────┘
```

---

## Server Components Data Fetching

### Pattern

```typescript
// app/app/lexcore/dashboard/page.tsx (Server Component)
import { LexCoreDashboard } from "@/components/lexcore/dashboard";
import { apiClient } from "@/lib/api-client";

export default async function LexCoreDashboardPage() {
  const tenantId = await getTenantIdFromSession(); // From Clerk session
  
  // Parallel data fetching
  const [documents, monitorRules, capabilities] = await Promise.all([
    apiClient.documents.list({ limit: 5, tenantId }),
    apiClient.monitorRules.list({ tenantId }),
    apiClient.capabilities.get(tenantId),
  ]);
  
  return (
    <LexCoreDashboard
      documents={documents}
      monitorRules={monitorRules}
      capabilities={capabilities}
    />
  );
}
```

### API Client (Server-Side)

```typescript
// lib/api-client.ts
class ApiClient {
  private baseUrl = process.env.API_BASE_URL;
  
  async request<T>(
    method: string,
    path: string,
    options: RequestOptions,
  ): Promise<T> {
    const headers = new Headers();
    headers.set("Content-Type", "application/json");
    headers.set("Authorization", `Bearer ${await getClerkToken()}`);
    headers.set("X-Correlation-ID", generateCorrelationId());
    headers.set("X-Tenant-ID", await getTenantId());
    
    const response = await fetch(`${this.baseUrl}${path}`, {
      method,
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
      next: { tags: options.tags }, // Next.js cache tags
    });
    
    if (!response.ok) {
      throw new ApiError(response.status, await response.json());
    }
    
    return response.json();
  }
}

export const apiClient = new ApiClient();
```

### Cache Strategy

| Data Type | Cache Strategy | Tags | Revalidation |
|-----------|---------------|------|-------------|
| Dashboard stats | Server fetch, no cache | — | On every request |
| Document list | SWR (client) | `documents` | On mutation |
| Search results | SWR (client), 5 min TTL | `search:{fingerprint}` | On new search |
| Document detail | Server fetch + SWR | `document:{id}` | On mutation |
| Research tasks | SWR (client) | `research-tasks` | On create/update |
| Monitor rules | SWR (client) | `monitor-rules` | On create/update/delete |
| Inventions | SWR (client) | `inventions` | On scan complete |
| Prior art | Server fetch | `prior-art:{id}` | On prior art search |
| Disclosures | SWR (client) | `disclosures` | On generate/update |
| Handoffs | SWR (client) | `handoffs` | On delivery |
| Team members | SWR (client) | `team` | On invite/remove |
| API keys | SWR (client) | `api-keys` | On create/revoke |
| Jurisdictions | SWR (client) | `jurisdictions` | Rarely changes |
| Capabilities | Server fetch | `capabilities` | On tier change |

---

## Client-Side Caching (SWR)

### SWR Configuration

```typescript
// lib/swr-config.ts
import { SWRConfig } from "swr";

export const swrConfig = {
  // Global fetcher
  fetcher: async (url: string) => {
    const response = await fetch(url, {
      headers: {
        "Authorization": `Bearer ${await getClerkToken()}`,
        "X-Correlation-ID": generateCorrelationId(),
      },
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return response.json();
  },
  
  // Default options
  revalidateOnFocus: true,
  revalidateOnReconnect: true,
  dedupingInterval: 5000,  // 5 seconds
  errorRetryCount: 3,
  errorRetryInterval: 5000,
  shouldRetryOnError: (error: Error) => {
    // Don't retry 401/403 errors
    if (error.message.includes("401") || error.message.includes("403")) {
      return false;
    }
    return true;
  },
};

// Provider wrapper
export function SWRProvider({ children }: { children: React.ReactNode }) {
  return <SWRConfig value={swrConfig}>{children}</SWRConfig>;
}
```

### SWR Hooks by Domain

```typescript
// hooks/use-documents.ts
import useSWR from "swr";

export function useDocuments(filters: DocumentFilters) {
  const { data, error, isLoading, mutate } = useSWR(
    `/api/v1/lexcore/documents?${buildQueryString(filters)}`,
    { tags: ["documents"] }
  );
  
  return {
    documents: data,
    error,
    isLoading,
    mutate,
  };
}

// hooks/use-monitor-rules.ts
export function useMonitorRules() {
  return useSWR("/api/v1/lexcore/monitor-rules", {
    tags: ["monitor-rules"],
    refreshInterval: 30000,  // Refresh every 30s for live alerts
  });
}

// hooks/use-research-tasks.ts
export function useResearchTasks() {
  return useSWR("/api/v1/lexcore/research-tasks", {
    tags: ["research-tasks"],
  });
}

// hooks/use-inventions.ts
export function useInventions(filters: InventionFilters) {
  return useSWR(
    `/api/v1/lexradar/inventions?${buildQueryString(filters)}`,
    { tags: ["inventions"] }
  );
}

// hooks/use-handoffs.ts
export function useHandoffs() {
  return useSWR("/api/v1/lexradar/handoffs", {
    tags: ["handoffs"],
  });
}
```

### Mutation Pattern

```typescript
// hooks/use-create-monitor-rule.ts
import { useSWRConfig } from "swr";

export function useCreateMonitorRule() {
  const { mutate } = useSWRConfig();
  
  const createRule = async (rule: MonitorRuleCreate) => {
    const response = await fetch("/api/v1/lexcore/monitor-rules", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(rule),
    });
    
    if (!response.ok) throw new Error("Failed to create rule");
    
    // Invalidate cache to trigger re-fetch
    await mutate("/api/v1/lexcore/monitor-rules");
    
    return response.json();
  };
  
  return { createRule };
}
```

---

## Global UI State (Zustand)

### Store Definition

```typescript
// stores/ui-store.ts
import { create } from "zustand";

interface UIState {
  // Sidebar
  sidebarOpen: boolean;
  sidebarCollapsed: boolean;
  setSidebarOpen: (open: boolean) => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  
  // Command palette
  commandPaletteOpen: boolean;
  setCommandPaletteOpen: (open: boolean) => void;
  
  // Notifications
  unreadNotificationCount: number;
  setUnreadNotificationCount: (count: number) => void;
  
  // Search
  globalSearchQuery: string;
  setGlobalSearchQuery: (query: string) => void;
  
  // Modals
  activeModal: string | null;
  modalData: any;
  openModal: (modal: string, data?: any) => void;
  closeModal: () => void;
  
  // Toasts
  toasts: Toast[];
  addToast: (toast: Omit<Toast, "id">) => void;
  removeToast: (id: string) => void;
  
  // Theme
  theme: "light" | "dark" | "system";
  setTheme: (theme: "light" | "dark" | "system") => void;
}

interface Toast {
  id: string;
  title: string;
  description?: string;
  variant?: "default" | "destructive" | "success";
  duration?: number;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  sidebarCollapsed: false,
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
  
  commandPaletteOpen: false,
  setCommandPaletteOpen: (open) => set({ commandPaletteOpen: open }),
  
  unreadNotificationCount: 0,
  setUnreadNotificationCount: (count) => set({ unreadNotificationCount: count }),
  
  globalSearchQuery: "",
  setGlobalSearchQuery: (query) => set({ globalSearchQuery: query }),
  
  activeModal: null,
  modalData: null,
  openModal: (modal, data) => set({ activeModal: modal, modalData: data }),
  closeModal: () => set({ activeModal: null, modalData: null }),
  
  toasts: [],
  addToast: (toast) => set((state) => ({
    toasts: [...state.toasts, { ...toast, id: crypto.randomUUID() }],
  })),
  removeToast: (id) => set((state) => ({
    toasts: state.toasts.filter((t) => t.id !== id),
  })),
  
  theme: "system",
  setTheme: (theme) => set({ theme }),
}));
```

---

## Context Providers

### TenantContext

```typescript
// contexts/tenant-context.tsx
"use client";

import { createContext, useContext } from "react";

interface TenantContextType {
  tenantId: string;
  name: string;
  tier: "SOLO" | "FIRM" | "ENTERPRISE";
  activeJurisdictions: string[];
  features: string[];
  isLoading: boolean;
}

const TenantContext = createContext<TenantContextType | null>(null);

export function TenantProvider({
  children,
  initialTenant,
}: {
  children: React.ReactNode;
  initialTenant: TenantContextType;
}) {
  return (
    <TenantContext.Provider value={initialTenant}>
      {children}
    </TenantContext.Provider>
  );
}

export function useTenant() {
  const context = useContext(TenantContext);
  if (!context) {
    throw new Error("useTenant must be used within TenantProvider");
  }
  return context;
}
```

**Server Component Initialization:**
```typescript
// app/app/layout.tsx
import { TenantProvider } from "@/contexts/tenant-context";
import { apiClient } from "@/lib/api-client";

export default async function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const tenant = await apiClient.tenant.get();
  
  return (
    <TenantProvider initialTenant={tenant}>
      <AppShell>{children}</AppShell>
    </TenantProvider>
  );
}
```

### CorrelationContext

```typescript
// contexts/correlation-context.tsx
"use client";

import { createContext, useContext, useState } from "react";
import { v4 as uuidv4 } from "uuid";

const CorrelationContext = createContext<{
  correlationId: string;
  regenerate: () => void;
}>({ correlationId: "", regenerate: () => {} });

export function CorrelationProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [correlationId, setCorrelationId] = useState(() => uuidv4());
  
  return (
    <CorrelationContext.Provider
      value={{
        correlationId,
        regenerate: () => setCorrelationId(uuidv4()),
      }}
    >
      {children}
    </CorrelationContext.Provider>
  );
}

export function useCorrelationId() {
  return useContext(CorrelationContext);
}
```

---

## Form State Management

### React Hook Form + Zod

```typescript
// components/monitor/rule-form.tsx
"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const monitorRuleSchema = z.object({
  name: z.string().min(1, "Name is required").max(200),
  jurisdictions: z.array(z.string()).min(1, "Select at least one jurisdiction"),
  bodyOfLaw: z.enum(["STATUTE", "REGULATION", "CASE", "ALL"]).optional(),
  keywords: z.array(z.string()).min(1, "Add at least one keyword"),
});

type MonitorRuleFormData = z.infer<typeof monitorRuleSchema>;

export function RuleForm({ onSubmit }: { onSubmit: (data: MonitorRuleFormData) => void }) {
  const form = useForm<MonitorRuleFormData>({
    resolver: zodResolver(monitorRuleSchema),
    defaultValues: {
      jurisdictions: [],
      keywords: [],
    },
  });
  
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Rule Name</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        {/* ... */}
      </form>
    </Form>
  );
}
```

---

## Real-Time Updates

### WebSocket Connection

```typescript
// hooks/use-realtime.ts
import { useEffect } from "react";
import useSWR from "swr";

export function useRealtimeMonitorAlerts(tenantId: string) {
  const { data, mutate } = useSWR(
    `/api/v1/lexcore/monitor-alerts?tenant_id=${tenantId}&unacknowledged=true`,
    { refreshInterval: 30000 }
  );
  
  useEffect(() => {
    // WebSocket for real-time alerts (future enhancement)
    const ws = new WebSocket(`wss://api.lexcore.com/ws/monitor?tenant=${tenantId}`);
    
    ws.onmessage = (event) => {
      const alert = JSON.parse(event.data);
      // Optimistically update cache
      mutate((current: any) => ({
        ...current,
        items: [alert, ...current.items],
        total: current.total + 1,
      }), false);  // Don't revalidate
    };
    
    return () => ws.close();
  }, [tenantId, mutate]);
  
  return { alerts: data, mutate };
}
```

---

## Error Handling

### Error Boundary

```typescript
// components/shared/error-boundary.tsx
"use client";

import { Component, ErrorInfo, ReactNode } from "react";
import { useCorrelationId } from "@/contexts/correlation-context";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };
  
  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }
  
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Error caught by boundary:", error, errorInfo);
    // Log to monitoring (Sentry, etc.)
    // Include correlation ID for debugging
  }
  
  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <ErrorState
            title="Something went wrong"
            description={this.state.error?.message || "An unexpected error occurred."}
            action={{
              label: "Reload Page",
              onClick: () => window.location.reload(),
            }}
          />
        )
      );
    }
    
    return this.props.children;
  }
}
```

### API Error Handling

```typescript
// lib/api-error.ts
class ApiError extends Error {
  constructor(
    public status: number,
    public data: any,
    public correlationId: string,
  ) {
    super(data.message || `API Error: ${status}`);
  }
  
  get isRetryable(): boolean {
    return this.status >= 500 || this.status === 429;
  }
  
  get isAuthError(): boolean {
    return this.status === 401 || this.status === 403;
  }
}

// Global error handler in SWR
export const swrConfig = {
  ...baseConfig,
  onError: (error: ApiError) => {
    if (error.isAuthError) {
      // Redirect to sign-in
      window.location.href = "/sign-in";
      return;
    }
    
    if (error.status === 429) {
      // Rate limit - show toast
      useUIStore.getState().addToast({
        title: "Rate Limited",
        description: "Too many requests. Please wait a moment.",
        variant: "destructive",
      });
      return;
    }
    
    // Log to monitoring
    console.error("API Error:", error);
  },
};
```

---

## Data Flow Examples

### Example 1: Creating a Monitor Rule

```
User clicks "Create Rule" in Monitor Rules page
  → Client: openModal("create-rule")
  → User fills form, clicks Submit
  → Client: POST /api/v1/lexcore/monitor-rules
  → Server Action: validate form, call API
  → API: creates rule, returns rule data
  → Server Action: revalidateTag("monitor-rules")
  → SWR: auto-refetches monitor-rules cache
  → UI: shows success toast, closes modal, updates list
```

### Example 2: Running a Research Task

```
User clicks "New Research" in Research page
  → Client: openModal("new-research")
  → User fills form, clicks Submit
  → Client: POST /api/v1/lexcore/research-tasks (sync, P50 < 30s)
  → API: creates task, AGT_ANALYSIS executes
  → If sync (< 60s): returns result directly
  → If async: returns task_id, poll every 5s
  → SWR: cache result, invalidate on new task
  → UI: shows result or progress indicator
```

### Example 3: Attorney Handoff Delivery

```
User clicks "Request Attorney Review" on disclosure
  → Client: POST /api/v1/lexradar/handoffs
  → API: creates handoff, AGT_ATTYFLOW delivers
  → Server Action: revalidateTag("handoffs")
  → SWR: auto-refetches handoffs list
  → UI: shows success toast with portal URL
  → Email sent to attorney with scoped JWT link
```

---

## State Persistence

### Local Storage

```typescript
// stores/persisted-store.ts
import { create } from "zustand";
import { persist } from "zustand/middleware";

export const usePersistedStore = create(
  persist<{
    recentSearches: string[];
    sidebarCollapsed: boolean;
    theme: "light" | "dark" | "system";
  }>(
    (set) => ({
      recentSearches: [],
      sidebarCollapsed: false,
      theme: "system",
      addRecentSearch: (query: string) =>
        set((state) => ({
          recentSearches: [query, ...state.recentSearches.slice(0, 9)],
        })),
    }),
    {
      name: "lexcore-ui-state",
      partialize: (state) => ({
        recentSearches: state.recentSearches,
        sidebarCollapsed: state.sidebarCollapsed,
        theme: state.theme,
      }),
    }
  )
);
```

### Session Storage

```typescript
// stores/session-store.ts
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

export const useSessionStore = create(
  persist<{
    formDrafts: Record<string, any>;
  }>(
    (set) => ({
      formDrafts: {},
      saveDraft: (formId: string, data: any) =>
        set((state) => ({
          formDrafts: { ...state.formDrafts, [formId]: data },
        })),
      clearDraft: (formId: string) =>
        set((state) => {
          const drafts = { ...state.formDrafts };
          delete drafts[formId];
          return { formDrafts: drafts };
        }),
    }),
    {
      name: "lexcore-session",
      storage: createJSONStorage(() => sessionStorage),
    }
  )
);
```

---

## Performance Optimizations

1. **React Server Components:** Fetch data on server, reduce client JS bundle
2. **SWR Deduplication:** 5-second deduping interval prevents duplicate requests
3. **Pagination:** All lists paginated (limit/offset), infinite scroll for search
4. **Virtualization:** TanStack Virtual for long lists (document text, large tables)
5. **Code Splitting:** Dynamic imports for heavy components (CitationGraph, charts)
6. **Image Optimization:** Next.js Image component for all images
7. **Font Optimization:** next/font for optimized font loading
8. **Route Prefetching:** Next.js automatic prefetching for navigation links

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-29 | Initial state management architecture | C06 frontend state definition |
