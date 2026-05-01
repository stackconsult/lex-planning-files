# ERD — Entity Relationship Diagram

> **Build System:** Unified Build System v2  
> **Chunk:** C03 — Data Model + Storage  
> **Horde:** HORDE-SCHEMA  
> **Control Plane:** ENGINEERING  

---

## LexCore Domain (10 Tables)

```mermaid
erDiagram
    tenants ||--o{ legal_documents : "tenant-scoped"
    tenants ||--o{ query_cache : "tenant-scoped"
    tenants ||--o{ monitor_rules : "tenant-scoped"
    tenants ||--o{ research_tasks : "tenant-scoped"
    tenants ||--o{ audit_log : "tenant-scoped"
    tenants ||--o{ api_keys : "tenant-scoped"
    tenants ||--o{ workspaces : "tenant-scoped"
    tenants ||--o{ jurisdictions : "tenant-scoped"
    tenants ||--o{ monitor_alerts : "tenant-scoped"

    legal_documents ||--o{ legal_chunks : "parent-document"
    legal_documents ||--o{ legal_citations : "citing-document"
    legal_documents ||--o{ legal_citations : "cited-document"
    legal_documents ||--o{ monitor_rules : "monitored-document"

    monitor_rules ||--o{ monitor_alerts : "rule-triggered"
    research_tasks ||--o{ research_task_documents : "task-document"
    research_tasks ||--o{ research_task_citations : "task-citation"
    research_tasks ||--o{ research_task_queries : "task-query"

    query_cache ||--|| legal_documents : "cached-result"

    tenants {
        uuid id PK
        text name
        text email
        text tier "SOLO|FIRM|ENTERPRISE"
        text payment_status
        timestamp created_at
        timestamp updated_at
    }

    legal_documents {
        uuid id PK
        uuid tenant_id FK
        text source
        text jurisdiction_code
        text body_of_law "STATUTE|REGULATION|CASE"
        text title
        text citation
        text summary
        text url
        text version
        jsonb metadata
        timestamp published_date
        timestamp last_modified
        timestamp created_at
        timestamp updated_at
    }

    legal_chunks {
        uuid id PK
        uuid tenant_id FK
        uuid document_id FK
        int chunk_index
        text chunk_type "SECTION|PARAGRAPH|SENTENCE"
        text content
        vector_1536 embedding
        timestamp created_at
    }

    legal_citations {
        uuid id PK
        uuid tenant_id FK
        uuid citing_document_id FK
        uuid cited_document_id FK
        text citation_type "FORWARD|BACKWARD"
        text citation_context
        text location
        timestamp created_at
    }

    query_cache {
        uuid id PK
        uuid tenant_id FK
        text query_fingerprint
        text query_normalized
        jsonb results
        float latency_ms
        int result_count
        timestamp expires_at
        timestamp created_at
        timestamp updated_at
    }

    monitor_rules {
        uuid id PK
        uuid tenant_id FK
        text rule_name
        text jurisdiction_codes
        text body_of_law "STATUTE|REGULATION|CASE"
        text keywords
        text status "ACTIVE|PAUSED|ARCHIVED"
        timestamp last_triggered_at
        timestamp created_at
        timestamp updated_at
    }

    monitor_alerts {
        uuid id PK
        uuid tenant_id FK
        uuid rule_id FK
        uuid document_id FK
        text alert_type "AMENDMENT|REPEAL|NEW"
        text change_summary
        text previous_version_url
        text current_version_url
        boolean acknowledged
        timestamp created_at
        timestamp updated_at
    }

    research_tasks {
        uuid id PK
        uuid tenant_id FK
        text question
        text status "PENDING|RUNNING|COMPLETED|FAILED"
        text result_report
        float confidence
        boolean gap_detected
        text gaps
        timestamp started_at
        timestamp completed_at
        timestamp created_at
        timestamp updated_at
    }

    research_task_documents {
        uuid id PK
        uuid tenant_id FK
        uuid task_id FK
        uuid document_id FK
        float relevance_score
        int sort_order
        timestamp created_at
    }

    research_task_citations {
        uuid id PK
        uuid tenant_id FK
        uuid task_id FK
        uuid citation_id FK
        int sort_order
        timestamp created_at
    }

    research_task_queries {
        uuid id PK
        uuid tenant_id FK
        uuid task_id FK
        text query_text
        int query_index
        timestamp created_at
    }

    jurisdictions {
        uuid id PK
        uuid tenant_id FK
        text jurisdiction_code
        text jurisdiction_name
        boolean is_active
        float coverage_percent
        int document_count
        timestamp created_at
        timestamp updated_at
    }

    audit_log {
        uuid id PK
        uuid tenant_id FK
        text action_type
        text entity_type
        uuid entity_id
        uuid user_id
        text details
        timestamp created_at
    }

    api_keys {
        uuid id PK
        uuid tenant_id FK
        text key_hash
        text name
        text scopes
        boolean is_active
        timestamp last_used_at
        timestamp expires_at
        timestamp created_at
        timestamp updated_at
    }

    workspaces {
        uuid id PK
        uuid tenant_id FK
        text name
        text description
        jsonb settings
        timestamp created_at
        timestamp updated_at
    }
```

---

## LexRadar Domain (8 Tables)

```mermaid
erDiagram
    tenants ||--o{ invention_candidates : "tenant-scoped"
    tenants ||--o{ disclosures : "tenant-scoped"
    tenants ||--o{ prior_art : "tenant-scoped"
    tenants ||--o{ blockchain_anchors : "tenant-scoped"
    tenants ||--o{ filing_bundles : "tenant-scoped"
    tenants ||--o{ attorney_reviews : "tenant-scoped"
    tenants ||--o{ disclosures_filing_bundles : "tenant-scoped"

    invention_candidates ||--o{ disclosures : "candidate-to-disclosure"
    invention_candidates ||--o{ prior_art : "candidate-prior-art"
    invention_candidates ||--o{ blockchain_anchors : "candidate-proof"

    disclosures ||--o{ disclosures_filing_bundles : "disclosure-filing"
    disclosures ||--o{ attorney_reviews : "disclosure-review"
    filing_bundles ||--o{ disclosures_filing_bundles : "bundle-filing"
    disclosures ||--o{ blockchain_anchors : "disclosure-proof"
    filing_bundles ||--o{ blockchain_anchors : "bundle-proof"

    tenants {
        uuid id PK
        text name
        text email
        text tier "SOLO|FIRM|ENTERPRISE"
        text payment_status
        timestamp created_at
        timestamp updated_at
    }

    invention_candidates {
        uuid id PK
        uuid tenant_id FK
        text title
        text description
        text source_url
        text source_type "GitHub|Jira|Notion"
        float novelty_score
        float nonobviousness_score
        float utility_score
        float enablement_score
        float scope_score
        float evidence_score
        float composite_score
        text status "DETECTED|SCORING|SCORED|DISCLOSING|DISCLOSED|FILED"
        timestamp detected_at
        timestamp scored_at
        timestamp created_at
        timestamp updated_at
    }

    disclosures {
        uuid id PK
        uuid tenant_id FK
        uuid invention_id FK
        text title
        text inventor
        text abstract
        text background
        text summary
        text detailed_description
        text claims
        text drawings_description
        text abstract_of_invention
        text advantages
        text alternative_implementations
        text example
        text prior_art_summary
        text references
        text grounding_sources
        text additional_materials
        text status "DRAFT|REVIEWING|APPROVED|REJECTED|REQUESTED_CHANGES"
        float grounding_score
        timestamp created_at
        timestamp updated_at
    }

    prior_art {
        uuid id PK
        uuid tenant_id FK
        uuid invention_id FK
        text source "USPTO|WIPO|EPO|Lens|GooglePatents|PatentScope|IPcom"
        text patent_number
        text title
        text authors
        text url
        text abstract
        text relevance_summary
        float relevance_score
        timestamp published_date
        timestamp created_at
        timestamp updated_at
    }

    blockchain_anchors {
        uuid id PK
        uuid tenant_id FK
        uuid entity_id
        text entity_type "INVENTION|DISCLOSURE|FILING_BUNDLE"
        text document_hash "SHA-256"
        text bundle_hash "SHA-256"
        text polygon_tx_hash
        text polygon_block_number
        timestamp polygon_tx_timestamp
        timestamp anchored_at
        timestamp created_at
        timestamp updated_at
    }

    filing_bundles {
        uuid id PK
        uuid tenant_id FK
        text bundle_name
        text status "DRAFT|READY|SUBMITTED|ARCHIVED"
        text patent_type "PROVISIONAL|NON_PROVISIONAL|PCT"
        text package_url
        float package_size_mb
        timestamp created_at
        timestamp updated_at
    }

    disclosures_filing_bundles {
        uuid id PK
        uuid tenant_id FK
        uuid disclosure_id FK
        uuid filing_bundle_id FK
        int sort_order
        text role "PRIMARY|SECONDARY|REFERENCE"
        timestamp created_at
        timestamp updated_at
    }

    attorney_reviews {
        uuid id PK
        uuid tenant_id FK
        uuid disclosure_id FK
        text attorney_email
        text attorney_name
        text status "PENDING|IN_PROGRESS|APPROVED|REJECTED|REQUESTED_CHANGES"
        text review_notes
        text rejection_reason
        text request_changes_details
        text portal_url
        timestamp expires_at
        timestamp reviewed_at
        timestamp created_at
        timestamp updated_at
    }
```

---

## Shared / Platform Tables (6 Tables)

```mermaid
erDiagram
    tenants ||--o{ users : "tenant-members"
    tenants ||--o{ roles_permissions : "tenant-roles"
    tenants ||--o{ audit_log : "tenant-audit"

    users ||--o{ roles_permissions : "user-roles"
    tenants ||--o{ payment_plans : "tenant-payment"

    tenants {
        uuid id PK
        text name
        text email
        text tier "SOLO|FIRM|ENTERPRISE"
        text payment_status
        timestamp created_at
        timestamp updated_at
    }

    users {
        uuid id PK
        uuid tenant_id FK
        text clerk_user_id
        text email
        text display_name
        text role "admin|member|viewer"
        boolean is_active
        timestamp last_login_at
        timestamp created_at
        timestamp updated_at
    }

    roles_permissions {
        uuid id PK
        uuid tenant_id FK
        uuid user_id FK
        text resource "legal_documents|monitor_rules|invention_candidates|disclosures|filing_bundles"
        text action "read|write|delete|admin"
        text scope "tenant|workspace|user"
        timestamp created_at
        timestamp updated_at
    }

    payment_plans {
        uuid id PK
        uuid tenant_id FK
        text plan_name "SOLO|FIRM|ENTERPRISE"
        text stripe_subscription_id
        text status "ACTIVE|CANCELLED|PAST_DUE|TRIAL"
        timestamp started_at
        timestamp expires_at
        timestamp created_at
        timestamp updated_at
    }

    audit_log {
        uuid id PK
        uuid tenant_id FK
        text action_type
        text entity_type
        uuid entity_id
        uuid user_id
        text details
        timestamp created_at
    }
```

---

## Cross-Domain References

| From Table | To Table | Foreign Key | Relationship | Cascade |
|------------|----------|-------------|--------------|---------|
| legal_documents | tenants | tenant_id | many-to-one | ON DELETE CASCADE |
| legal_chunks | legal_documents | document_id | many-to-one | ON DELETE CASCADE |
| legal_chunks | tenants | tenant_id | many-to-one | ON DELETE CASCADE |
| legal_citations | legal_documents (citing) | citing_document_id | many-to-one | ON DELETE CASCADE |
| legal_citations | legal_documents (cited) | cited_document_id | many-to-one | ON DELETE CASCADE |
| legal_citations | tenants | tenant_id | many-to-one | ON DELETE CASCADE |
| query_cache | tenants | tenant_id | many-to-one | ON DELETE CASCADE |
| monitor_rules | tenants | tenant_id | many-to-one | ON DELETE CASCADE |
| monitor_alerts | monitor_rules | rule_id | many-to-one | ON DELETE CASCADE |
| monitor_alerts | legal_documents | document_id | many-to-one | ON DELETE SET NULL |
| monitor_alerts | tenants | tenant_id | many-to-one | ON DELETE CASCADE |
| research_tasks | tenants | tenant_id | many-to-one | ON DELETE CASCADE |
| research_task_documents | research_tasks | task_id | many-to-one | ON DELETE CASCADE |
| research_task_documents | legal_documents | document_id | many-to-one | ON DELETE CASCADE |
| research_task_documents | tenants | tenant_id | many-to-one | ON DELETE CASCADE |
| research_task_citations | research_tasks | task_id | many-to-one | ON DELETE CASCADE |
| research_task_citations | legal_citations | citation_id | many-to-one | ON DELETE CASCADE |
| research_task_citations | tenants | tenant_id | many-to-one | ON DELETE CASCADE |
| research_task_queries | research_tasks | task_id | many-to-one | ON DELETE CASCADE |
| research_task_queries | tenants | tenant_id | many-to-one | ON DELETE CASCADE |
| jurisdictions | tenants | tenant_id | many-to-one | ON DELETE CASCADE |
| audit_log | tenants | tenant_id | many-to-one | ON DELETE CASCADE |
| api_keys | tenants | tenant_id | many-to-one | ON DELETE CASCADE |
| workspaces | tenants | tenant_id | many-to-one | ON DELETE CASCADE |
| users | tenants | tenant_id | many-to-one | ON DELETE CASCADE |
| roles_permissions | tenants | tenant_id | many-to-one | ON DELETE CASCADE |
| roles_permissions | users | user_id | many-to-one | ON DELETE CASCADE |
| payment_plans | tenants | tenant_id | many-to-one | ON DELETE CASCADE |
| invention_candidates | tenants | tenant_id | many-to-one | ON DELETE CASCADE |
| disclosures | invention_candidates | invention_id | many-to-one | ON DELETE CASCADE |
| disclosures | tenants | tenant_id | many-to-one | ON DELETE CASCADE |
| prior_art | invention_candidates | invention_id | many-to-one | ON DELETE CASCADE |
| prior_art | tenants | tenant_id | many-to-one | ON DELETE CASCADE |
| blockchain_anchors | tenants | tenant_id | many-to-one | ON DELETE CASCADE |
| filing_bundles | tenants | tenant_id | many-to-one | ON DELETE CASCADE |
| disclosures_filing_bundles | disclosures | disclosure_id | many-to-one | ON DELETE CASCADE |
| disclosures_filing_bundles | filing_bundles | filing_bundle_id | many-to-one | ON DELETE CASCADE |
| disclosures_filing_bundles | tenants | tenant_id | many-to-one | ON DELETE CASCADE |
| attorney_reviews | disclosures | disclosure_id | many-to-one | ON DELETE CASCADE |
| attorney_reviews | tenants | tenant_id | many-to-one | ON DELETE CASCADE |

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-29 | Initial ERD | C03 data model definition — LexCore 10 tables, LexRadar 8 tables, Platform 6 tables |
