# COMPONENT_LIBRARY.md — LexCore + LexRadar UI Component Registry

> **Build System:** Unified Build System v2  
> **Chunk:** C06 — Frontend  
> **Horde:** HORDE-UI  
> **Control Plane:** ENGINEERING  

---

## Overview

This document defines the reusable UI component library for the LexCore + LexRadar frontend. Components are organized by domain (Platform, LexCore, LexRadar) and follow the shadcn/ui + Tailwind CSS design system. All components are TypeScript React components with strict prop typing.

**Design System:**
- **Framework:** Next.js 14 (App Router)
- **Styling:** Tailwind CSS v3.4
- **UI Components:** shadcn/ui + custom extensions
- **Animation:** Framer Motion for transitions
- **Icons:** Lucide React
- **Charts:** Recharts
- **Data Tables:** TanStack Table v8
- **Forms:** React Hook Form + Zod validation

---

## Component Hierarchy

```
ui/                          # shadcn/ui base components (install via CLI)
  ├── button.tsx
  ├── input.tsx
  ├── select.tsx
  ├── dialog.tsx
  ├── card.tsx
  ├── badge.tsx
  ├── tabs.tsx
  ├── table.tsx
  ├── toast.tsx
  ├── skeleton.tsx
  ├── dropdown-menu.tsx
  ├── avatar.tsx
  ├── command.tsx
  ├── popover.tsx
  └── ... (full shadcn registry)

components/
  ├── layout/                  # Shell components
  │   ├── app-shell.tsx
  │   ├── sidebar.tsx
  │   ├── header.tsx
  │   ├── breadcrumb.tsx
  │   └── footer.tsx
  ├── search/                  # Search components
  │   ├── search-bar.tsx
  │   ├── search-filters.tsx
  │   ├── search-results.tsx
  │   └── document-card.tsx
  ├── citations/               # Citation components
  │   ├── citation-graph.tsx
  │   ├── citation-list.tsx
  │   └── authority-chain.tsx
  ├── research/                # Research components
  │   ├── research-task-card.tsx
  │   ├── research-result.tsx
  │   ├── confidence-gauge.tsx
  │   └── gap-detector.tsx
  ├── monitor/                 # Monitor components
  │   ├── rule-card.tsx
  │   ├── rule-form.tsx
  │   ├── alert-card.tsx
  │   └── alert-badge.tsx
  ├── invention/               # LexRadar invention components
  │   ├── invention-card.tsx
  │   ├── score-radar.tsx
  │   ├── score-bars.tsx
  │   └── invention-detail.tsx
  ├── disclosure/              # Disclosure components
  │   ├── disclosure-editor.tsx
  │   ├── lhp-section-tabs.tsx
  │   ├── grounding-panel.tsx
  │   └── prior-art-evidence.tsx
  ├── bundle/                  # Filing bundle components
  │   ├── bundle-form.tsx
  │   ├── bundle-card.tsx
  │   └── disclosure-selector.tsx
  ├── handoff/                 # Handoff components
  │   ├── handoff-card.tsx
  │   ├── handoff-form.tsx
  │   └── status-timeline.tsx
  ├── settings/                # Settings components
  │   ├── team-table.tsx
  │   ├── api-key-manager.tsx
  │   ├── billing-card.tsx
  │   └── jurisdiction-toggle.tsx
  ├── shared/                  # Shared reusable components
  │   ├── loading-state.tsx
  │   ├── error-boundary.tsx
  │   ├── empty-state.tsx
  │   ├── pagination.tsx
  │   ├── data-table.tsx
  │   ├── status-badge.tsx
  │   ├── date-range-picker.tsx
  │   ├── jurisdiction-badge.tsx
  │   ├── correlation-id-display.tsx
  │   └── tenant-context.tsx
  └── forms/                   # Form components
      ├── controlled-input.tsx
      ├── multi-select.tsx
      ├── tag-input.tsx
      ├── rich-text-editor.tsx
      └── file-uploader.tsx
```

---

## Layout Components

### `AppShell`

**File:** `components/layout/app-shell.tsx`  
**Type:** Server Component (layout)  
**Props:**
```typescript
interface AppShellProps {
  children: React.ReactNode;
}
```

**Layout:**
```
┌─────────────────────────┐
│ Header                  │
├────────┬────────────────┤
│ Sidebar│ Main Content   │
│        │                │
│        │                │
│        │                │
└────────┴────────────────┘
```

**Features:**
- Sidebar collapsible (mobile: drawer)
- Header sticky with tenant name, search, notifications, user menu
- Breadcrumbs auto-generated from route
- Main content scrollable

---

### `Sidebar`

**File:** `components/layout/sidebar.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface SidebarProps {
  navigationItems: NavItem[];
  tenantTier: "SOLO" | "FIRM" | "ENTERPRISE";
}

interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  requiredPermission?: string;
  badge?: number;
  children?: NavItem[];
}
```

**Features:**
- Collapsible sections (LexCore, LexRadar, Settings)
- Active state highlighting
- Permission-based visibility (hides items user cannot access)
- Badge counts (monitor alerts, pending handoffs)
- Keyboard shortcut hints (e.g., "Ctrl+K” for search)

---

### `Header`

**File:** `components/layout/header.tsx`  
**Type:** Client Component  
**Features:**
- Tenant name + logo
- Global search trigger (Command palette)
- Notifications bell with unread count
- User avatar + menu (Clerk `<UserButton>`)
- Breadcrumb navigation

---

## Search Components

### `SearchBar`

**File:** `components/search/search-bar.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface SearchBarProps {
  onSearch: (query: string, filters: SearchFilters) => void;
  loading?: boolean;
  initialQuery?: string;
  placeholder?: string;
}

interface SearchFilters {
  jurisdiction?: string;
  bodyOfLaw?: "STATUTE" | "REGULATION" | "CASE" | "ALL";
  dateFrom?: Date;
  dateTo?: Date;
}
```

**Features:**
- Input with debounce (300ms)
- Filter panel (dropdown)
- "AI Research Mode" toggle (triggers research_task)
- Keyboard shortcut: `/` to focus
- Recent searches dropdown (localStorage)

---

### `DocumentCard`

**File:** `components/search/document-card.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface DocumentCardProps {
  document: LegalDocument;
  query: string;  // For highlighting
  onCiteClick: (docId: string) => void;
  onViewClick: (docId: string) => void;
}
```

**Features:**
- Title with citation (clickable)
- Jurisdiction badge (`<JurisdictionBadge>`)
- Body of law badge
- Summary snippet with query term highlighting
- Relevance score (progress bar)
- "View Document" button
- "Get Citations" button
- Hover: show quick actions

---

### `SearchResults`

**File:** `components/search/search-results.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface SearchResultsProps {
  results: SearchResult[];
  query: string;
  loading: boolean;
  total: number;
  page: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onSortChange: (sort: string) => void;
}
```

**Features:**
- Result count + query display
- Sort options (relevance, date, citation count)
- Grid/list toggle
- DocumentCard list
- Pagination (`<Pagination>`)
- Loading skeleton state

---

## Citation Components

### `CitationGraph`

**File:** `components/citations/citation-graph.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface CitationGraphProps {
  graph: CitationGraphData;
  onNodeClick: (docId: string) => void;
  maxDepth: number;
}
```

**Features:**
- Interactive D3.js force-directed graph
- Nodes: documents (size = authority score, color = overruled status)
- Edges: citation relationships (forward/backward)
- Zoom, pan, drag
- Click node → navigate to document
- Legend: forward citations, backward citations, overruled cases
- Depth slider (1-5)

---

### `CitationList`

**File:** `components/citations/citation-list.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface CitationListProps {
  citations: Citation[];
  direction: "forward" | "backward" | "both";
  onCiteClick: (docId: string) => void;
}
```

**Features:**
- Tabbed: Forward / Backward / Both
- Sortable: authority score, date, depth
- Overruled cases highlighted (red badge)
- Paginated list

---

## Research Components

### `ResearchTaskCard`

**File:** `components/research/research-task-card.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface ResearchTaskCardProps {
  task: ResearchTask;
  onView: (taskId: string) => void;
  onReRun: (taskId: string) => void;
  onDelete: (taskId: string) => void;
}
```

**Features:**
- Question (truncated, expandable)
- Status badge (PENDING/RUNNING/COMPLETED/FAILED)
- Confidence score (if completed, gauge)
- Gap detected warning (yellow badge)
- Created date
- Actions: View, Re-run, Delete
- Progress bar (if RUNNING)

---

### `ConfidenceGauge`

**File:** `components/research/confidence-gauge.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface ConfidenceGaugeProps {
  score: number;  // 0-100
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
}
```

**Features:**
- Circular progress gauge (SVG)
- Color: red (< 60), yellow (60-80), green (> 80)
- Label: "Low", "Moderate", "High", "Very High"
- Animated on mount

---

### `GapDetector`

**File:** `components/research/gap-detector.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface GapDetectorProps {
  gaps: ResearchGap[];
  onSearchGap: (gapQuery: string) => void;
}
```

**Features:**
- Banner: "Gaps detected in research"
- List of gaps with severity (low/medium/high)
- Each gap: description + "Search for this" button
- Links to create monitor rule from gap

---

## Monitor Components

### `RuleCard`

**File:** `components/monitor/rule-card.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface RuleCardProps {
  rule: MonitorRule;
  alertCount: number;
  onEdit: (ruleId: string) => void;
  onPause: (ruleId: string) => void;
  onDelete: (ruleId: string) => void;
  onViewAlerts: (ruleId: string) => void;
}
```

**Features:**
- Rule name
- Jurisdiction tags
- Keywords (tag chips)
- Status badge (ACTIVE/PAUSED/ARCHIVED)
- Unacknowledged alert count (red badge if > 0)
- Last triggered date
- Quick actions: Edit, Pause/Resume, Delete, View Alerts

---

### `AlertCard`

**File:** `components/monitor/alert-card.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface AlertCardProps {
  alert: MonitorAlert;
  onAcknowledge: (alertId: string) => void;
  onViewDocument: (docId: string) => void;
}
```

**Features:**
- Alert title (document name)
- Rule name (link to rule)
- Trigger reason (keyword match, new document, amendment)
- Document snippet
- Severity badge (low/medium/high)
- Created date
- "Acknowledge" button
- "View Document" button

---

## Invention Components

### `InventionCard`

**File:** `components/invention/invention-card.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface InventionCardProps {
  invention: InventionCandidate;
  onView: (inventionId: string) => void;
  onScore: (inventionId: string) => void;
  onDisclose: (inventionId: string) => void;
  viewMode: "grid" | "list";
}
```

**Features:**
- Title (clickable)
- Source icon + link (GitHub, Jira, Notion)
- Detection date
- Status badge
- Score bars (6 dimensions in list view, radar in grid view)
- Composite score (large number with gauge)
- Actions: View, Score Now, Generate Disclosure

---

### `ScoreRadar`

**File:** `components/invention/score-radar.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface ScoreRadarProps {
  scores: PatentabilityScores;
  size?: "sm" | "md" | "lg";
}

interface PatentabilityScores {
  novelty: number;
  nonobviousness: number;
  utility: number;
  enablement: number;
  scope: number;
  evidence: number;
}
```

**Features:**
- Recharts RadarChart
- 6 axes (one per dimension)
- Fill opacity 0.3
- Reference line at 0.7 (threshold)
- Tooltip on hover (dimension name + score)
- Composite score displayed in center

---

### `ScoreBars`

**File:** `components/invention/score-bars.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface ScoreBarsProps {
  scores: PatentabilityScores;
}
```

**Features:**
- 6 horizontal bars (one per dimension)
- Color: red (< 0.5), yellow (0.5-0.7), green (> 0.7)
- Label + score value on right
- Animated width on mount

---

## Disclosure Components

### `DisclosureEditor`

**File:** `components/disclosure/disclosure-editor.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface DisclosureEditorProps {
  disclosure: Disclosure;
  onSave: (sectionId: string, content: string) => void;
  editableSections: string[];
}
```

**Features:**
- Tab navigation (16 LHP sections)
- Rich text editor (TipTap) for editable sections
- Read-only sections (plain text rendering)
- Auto-save indicator (saving / saved / error)
- Grounding score badge
- Status badge
- "Request Attorney Review" button (when APPROVED)

---

### `LhpSectionTabs`

**File:** `components/disclosure/lhp-section-tabs.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface LhpSectionTabsProps {
  sections: LhpSection[];
  activeSection: string;
  onSectionChange: (sectionId: string) => void;
}
```

**Features:**
- Horizontal scrollable tabs (16 sections)
- Active tab highlighted
- Section status indicator (editable/read-only)
- Section numbering

---

### `GroundingPanel`

**File:** `components/disclosure/grounding-panel.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface GroundingPanelProps {
  score: number;
  sources: GroundingSource[];
}
```

**Features:**
- Score display (gauge)
- Sources list with expandable items
- Source: title, URL, relevance snippet
- Color: red (< 0.70), yellow (0.70-0.85), green (> 0.85)
- "View Source" links

---

## Bundle Components

### `BundleForm`

**File:** `components/bundle/bundle-form.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface BundleFormProps {
  disclosures: Disclosure[];  // APPROVED only
  onSubmit: (bundle: BundleCreate) => void;
}
```

**Features:**
- Name input
- Patent type selector (PROVISIONAL / NON_PROVISIONAL / PCT)
- Disclosure multi-select with drag-and-drop ordering
- Disclosure role: PRIMARY / SECONDARY / REFERENCE
- Preview panel
- Submit / Cancel

---

### `BundleCard`

**File:** `components/bundle/bundle-card.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface BundleCardProps {
  bundle: FilingBundle;
  onDownload: (bundleId: string) => void;
  onArchive: (bundleId: string) => void;
}
```

**Features:**
- Bundle name
- Patent type badge
- Status badge (DRAFT/READY/SUBMITTED/ARCHIVED)
- Disclosures count
- Package size (MB)
- Created date
- Actions: Download, View, Archive

---

## Handoff Components

### `HandoffCard`

**File:** `components/handoff/handoff-card.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface HandoffCardProps {
  handoff: HandoffDelivery;
  onResend: (handoffId: string) => void;
  onRevoke: (handoffId: string) => void;
  onViewReview: (handoffId: string) => void;
}
```

**Features:**
- Disclosure title
- Attorney name + email
- Status badge (DELIVERED/OPENED/IN_PROGRESS/APPROVED/REJECTED/REQUESTED_CHANGES)
- Portal URL (copy button)
- Expires countdown (red if < 24h)
- Reviewed at (if applicable)
- Actions: Resend, Revoke, View Review

---

### `StatusTimeline`

**File:** `components/handoff/status-timeline.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface StatusTimelineProps {
  events: StatusEvent[];
}

interface StatusEvent {
  status: string;
  timestamp: Date;
  actor?: string;
  notes?: string;
}
```

**Features:**
- Vertical timeline
- Each event: status badge, timestamp, actor, notes
- Active event highlighted
- Animated on mount

---

## Settings Components

### `TeamTable`

**File:** `components/settings/team-table.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface TeamTableProps {
  members: TeamMember[];
  onChangeRole: (userId: string, role: string) => void;
  onRemove: (userId: string) => void;
  onInvite: (email: string, role: string) => void;
}
```

**Features:**
- TanStack Table v8 data table
- Columns: Name, Email, Role, Last Login, Status, Actions
- Role dropdown (admin/editor/viewer)
- Remove button with confirmation
- Invite form (email + role)
- Pending invitations section

---

### `ApiKeyManager`

**File:** `components/settings/api-key-manager.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface ApiKeyManagerProps {
  keys: ApiKey[];
  onCreate: (name: string, scopes: string[]) => void;
  onRevoke: (keyId: string) => void;
  onRegenerate: (keyId: string) => void;
}
```

**Features:**
- Key list table
- Columns: Name, Scopes, Created, Last Used, Expires, Status, Actions
- Create key modal (name + scopes multi-select)
- Copy key button (shows only once after creation)
- Revoke button with confirmation
- Regenerate button (shows new key)
- Usage stats per key

---

### `BillingCard`

**File:** `components/settings/billing-card.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface BillingCardProps {
  billing: BillingInfo;
  onUpgrade: (tier: string) => void;
  onCancel: () => void;
}
```

**Features:**
- Current plan display (SOLO/FIRM/ENTERPRISE)
- Usage stats: API calls, research tasks, monitor rules (progress bars)
- Upgrade/downgrade options (plan comparison)
- Payment method (Stripe Elements)
- Invoice history table
- Cancel subscription button (confirmation modal)

---

### `JurisdictionToggle`

**File:** `components/settings/jurisdiction-toggle.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface JurisdictionToggleProps {
  jurisdictions: Jurisdiction[];
  activeCodes: string[];
  onToggle: (code: string, active: boolean) => void;
}
```

**Features:**
- Grid of jurisdiction cards
- Each card: flag, name, coverage % (progress bar), document count
- Toggle switch (activate/deactivate)
- Active count summary
- Coverage chart (Recharts bar chart)

---

## Shared Components

### `DataTable`

**File:** `components/shared/data-table.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface DataTableProps<TData> {
  data: TData[];
  columns: ColumnDef<TData>[];
  pagination: PaginationState;
  sorting: SortingState;
  onPaginationChange: (pagination: PaginationState) => void;
  onSortingChange: (sorting: SortingState) => void;
  loading?: boolean;
}
```

**Features:**
- TanStack Table v8 wrapper
- Sortable headers
- Pagination controls
- Row actions dropdown
- Loading skeleton rows
- Empty state

---

### `StatusBadge`

**File:** `components/shared/status-badge.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface StatusBadgeProps {
  status: string;
  variant?: "default" | "outline" | "secondary";
  size?: "sm" | "md" | "lg";
}
```

**Features:**
- Color mapping for common statuses:
  - ACTIVE/DELIVERED/COMPLETED/APPROVED → green
  - PENDING/PREPARING/DELIVERING → yellow
  - PAUSED/OPENED/IN_PROGRESS → blue
  - FAILED/REJECTED/ERROR → red
  - ARCHIVED/CANCELED → gray
- Small dot indicator
- Optional pulse animation for active statuses

---

### `JurisdictionBadge`

**File:** `components/shared/jurisdiction-badge.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface JurisdictionBadgeProps {
  code: string;
  name: string;
  size?: "sm" | "md";
}
```

**Features:**
- Small flag icon (emoji or SVG)
- Jurisdiction name (abbreviated if sm)
- Color-coded by region (US = blue, EU = yellow, etc.)

---

### `LoadingState`

**File:** `components/shared/loading-state.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface LoadingStateProps {
  message?: string;
  fullPage?: boolean;
  count?: number;  // Skeleton count
}
```

**Features:**
- Skeleton cards (shimmer effect)
- Optional message below
- Full page: centered with logo
- Inline: inline skeleton rows

---

### `EmptyState`

**File:** `components/shared/empty-state.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}
```

**Features:**
- Centered layout
- Large icon (gray)
- Title + description
- Optional action button

---

### `CorrelationIdDisplay`

**File:** `components/shared/correlation-id-display.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface CorrelationIdDisplayProps {
  correlationId: string;
  visible?: boolean;  // Hidden by default, shown in error states or debug mode
}
```

**Features:**
- Small monospace text
- Copy button
- Only visible in error states or when debug mode enabled
- Helps support/debugging

---

### `TenantContext`

**File:** `components/shared/tenant-context.tsx`  
**Type:** Client Component (Context Provider)  
**Features:**
- React Context for current tenant
- Tenant ID, name, tier, active jurisdictions
- Used by all domain-specific components
- Fetched once at AppShell mount
- Updated on tenant switch

```typescript
interface TenantContextType {
  tenantId: string;
  name: string;
  tier: "SOLO" | "FIRM" | "ENTERPRISE";
  activeJurisdictions: string[];
  features: string[];  // Feature flags based on tier
}
```

---

## Form Components

### `RichTextEditor`

**File:** `components/forms/rich-text-editor.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface RichTextEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  minHeight?: string;
}
```

**Features:**
- TipTap editor
- Toolbar: bold, italic, underline, lists, headings
- Auto-save debounce (30s)
- Character count
- Max length warning
- Disabled state for read-only

---

### `TagInput`

**File:** `components/forms/tag-input.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface TagInputProps {
  tags: string[];
  onChange: (tags: string[]) => void;
  placeholder?: string;
  maxTags?: number;
  validator?: (tag: string) => boolean;
}
```

**Features:**
- Input that creates tags on comma or enter
- Tag chips with remove button
- Duplicate prevention
- Max tags limit
- Optional validator (e.g., email format)

---

### `MultiSelect`

**File:** `components/forms/multi-select.tsx`  
**Type:** Client Component  
**Props:**
```typescript
interface MultiSelectProps {
  options: Option[];
  selected: string[];
  onChange: (selected: string[]) => void;
  placeholder?: string;
  searchable?: boolean;
}
```

**Features:**
- Dropdown with checkboxes
- Search filter (if searchable)
- Selected count badge
- "Select All" / "Clear All"
- Grouped options (e.g., by region for jurisdictions)

---

## shadcn/ui Components Used

All base UI components from shadcn/ui registry:

| Component | Purpose | Location |
|-----------|---------|----------|
| Button | All actions | `ui/button.tsx` |
| Input | Text inputs | `ui/input.tsx` |
| Select | Dropdowns | `ui/select.tsx` |
| Dialog | Modals | `ui/dialog.tsx` |
| Card | Content containers | `ui/card.tsx` |
| Badge | Status indicators | `ui/badge.tsx` |
| Tabs | Section navigation | `ui/tabs.tsx` |
| Table | Data display | `ui/table.tsx` |
| Toast | Notifications | `ui/toast.tsx`, `ui/toaster.tsx`, `ui/use-toast.ts` |
| Skeleton | Loading states | `ui/skeleton.tsx` |
| Dropdown Menu | Actions menu | `ui/dropdown-menu.tsx` |
| Avatar | User images | `ui/avatar.tsx` |
| Command | Command palette | `ui/command.tsx` |
| Popover | Tooltips/popups | `ui/popover.tsx` |
| Sheet | Mobile sidebar | `ui/sheet.tsx` |
| Separator | Dividers | `ui/separator.tsx` |
| Scroll Area | Scrollable regions | `ui/scroll-area.tsx` |
| Tooltip | Hover hints | `ui/tooltip.tsx` |
| Calendar | Date picker | `ui/calendar.tsx` |
| Form | Form wrapper (RHF + Zod) | `ui/form.tsx` |
| Label | Form labels | `ui/label.tsx` |
| Textarea | Multi-line input | `ui/textarea.tsx` |
| Checkbox | Boolean inputs | `ui/checkbox.tsx` |
| Radio Group | Single selection | `ui/radio-group.tsx` |
| Switch | Toggle inputs | `ui/switch.tsx` |
| Slider | Range inputs | `ui/slider.tsx` |
| Progress | Progress bars | `ui/progress.tsx` |
| Accordion | Collapsible sections | `ui/accordion.tsx` |
| Collapsible | Toggle visibility | `ui/collapsible.tsx` |
| Menubar | Top navigation | `ui/menubar.tsx` |
| Navigation Menu | Header nav | `ui/navigation-menu.tsx` |
| Toggle Group | Button groups | `ui/toggle-group.tsx` |
| Alert | Info/warning banners | `ui/alert.tsx` |
| Alert Dialog | Confirmation dialogs | `ui/alert-dialog.tsx` |
| Hover Card | Preview cards | `ui/hover-card.tsx` |
| Resizable | Split panes | `ui/resizable.tsx` |
| Sonner | Toast alternative | `ui/sonner.tsx` |

---

## Component Conventions

### Naming
- PascalCase for component names
- Suffix with domain: `RuleCard`, `InventionCard`
- Shared components in `shared/` directory

### File Structure
```
components/
  ├── [domain]/
  │   ├── component-name.tsx      # Component
  │   ├── component-name.test.tsx # Tests
  │   └── index.ts                # Barrel export
```

### Props
- Always use TypeScript interfaces
- Destructure props in function parameters
- Optional props use `?:` with sensible defaults

### State Management
- Server Components: fetch data via async props
- Client Components: use `useState`, `useSWR` for cache
- Form state: React Hook Form + Zod resolver

### Error Handling
- `ErrorBoundary` wraps all route segments
- `ErrorState` component for API errors
- `CorrelationIdDisplay` for debugging

### Accessibility
- All interactive elements keyboard accessible
- ARIA labels on all buttons without visible text
- Focus management in modals and dialogs
- Color contrast ratio ≥ 4.5:1

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-29 | Initial component library | C06 frontend component definition |
