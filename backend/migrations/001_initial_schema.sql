-- LexCore + LexRadar — Initial Schema Migration
-- Build System: Unified Build System v2
-- Chunk: C03 — Data Model + Storage
-- Horde: HORDE-SCHEMA
-- Date: 2026-04-29
-- Schema Version: v0.1.0-foundation

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- ============================================================
-- PLATFORM / SHARED TABLES
-- ============================================================

CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    tier TEXT NOT NULL DEFAULT 'SOLO',
    payment_status TEXT NOT NULL DEFAULT 'TRIAL',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT tenants_tier_check CHECK (tier IN ('SOLO', 'FIRM', 'ENTERPRISE')),
    CONSTRAINT tenants_payment_status_check CHECK (payment_status IN ('TRIAL', 'ACTIVE', 'CANCELLED', 'PAST_DUE')),
    CONSTRAINT tenants_email_unique UNIQUE (email)
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    clerk_user_id TEXT NOT NULL,
    email TEXT NOT NULL,
    display_name TEXT,
    role TEXT NOT NULL DEFAULT 'member',
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT users_role_check CHECK (role IN ('admin', 'member', 'viewer')),
    CONSTRAINT users_tenant_email_unique UNIQUE (tenant_id, email)
);

CREATE TABLE roles_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    resource TEXT NOT NULL,
    action TEXT NOT NULL,
    scope TEXT NOT NULL DEFAULT 'tenant',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT roles_permissions_action_check CHECK (action IN ('read', 'write', 'delete', 'admin')),
    CONSTRAINT roles_permissions_scope_check CHECK (scope IN ('tenant', 'workspace', 'user')),
    CONSTRAINT roles_permissions_tenant_user_resource_action_unique UNIQUE (tenant_id, user_id, resource, action)
);

CREATE TABLE payment_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    plan_name TEXT NOT NULL,
    stripe_subscription_id TEXT,
    status TEXT NOT NULL DEFAULT 'TRIAL',
    started_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT payment_plans_status_check CHECK (status IN ('TRIAL', 'ACTIVE', 'CANCELLED', 'PAST_DUE'))
);

CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    settings JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT workspaces_tenant_name_unique UNIQUE (tenant_id, name)
);

CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    key_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    scopes TEXT NOT NULL DEFAULT 'read',
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_used_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT api_keys_key_hash_unique UNIQUE (key_hash)
);

CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    action_type TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id UUID,
    user_id UUID,
    details TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- LEXCORE TABLES
-- ============================================================

CREATE TABLE legal_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    source TEXT NOT NULL,
    jurisdiction_code TEXT NOT NULL,
    body_of_law TEXT NOT NULL,
    title TEXT NOT NULL,
    citation TEXT,
    summary TEXT,
    url TEXT,
    version TEXT,
    metadata JSONB NOT NULL DEFAULT '{}',
    published_date TIMESTAMPTZ,
    last_modified TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT legal_documents_body_of_law_check CHECK (body_of_law IN ('STATUTE', 'REGULATION', 'CASE')),
    CONSTRAINT legal_documents_tenant_source_citation_unique UNIQUE (tenant_id, source, citation)
);

CREATE TABLE legal_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    document_id UUID NOT NULL REFERENCES legal_documents(id) ON DELETE CASCADE ON UPDATE CASCADE,
    chunk_index INTEGER NOT NULL DEFAULT 0,
    chunk_type TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT legal_chunks_chunk_type_check CHECK (chunk_type IN ('SECTION', 'PARAGRAPH', 'SENTENCE')),
    CONSTRAINT legal_chunks_tenant_document_chunk_unique UNIQUE (tenant_id, document_id, chunk_index)
);

CREATE TABLE legal_citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    citing_document_id UUID NOT NULL REFERENCES legal_documents(id) ON DELETE CASCADE ON UPDATE CASCADE,
    cited_document_id UUID NOT NULL REFERENCES legal_documents(id) ON DELETE CASCADE ON UPDATE CASCADE,
    citation_type TEXT NOT NULL,
    citation_context TEXT,
    location TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT legal_citations_type_check CHECK (citation_type IN ('FORWARD', 'BACKWARD')),
    CONSTRAINT legal_citations_citing_ne_cited CHECK (citing_document_id != cited_document_id),
    CONSTRAINT legal_citations_tenant_citing_cited_unique UNIQUE (tenant_id, citing_document_id, cited_document_id, citation_type)
);

CREATE TABLE query_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    query_fingerprint TEXT NOT NULL,
    query_normalized TEXT NOT NULL,
    results JSONB NOT NULL,
    latency_ms NUMERIC(10,3) NOT NULL DEFAULT 0,
    result_count INTEGER NOT NULL DEFAULT 0,
    expires_at TIMESTAMPTZ NOT NULL DEFAULT now() + interval '24 hours',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT query_cache_result_count_nonneg CHECK (result_count >= 0),
    CONSTRAINT query_cache_tenant_fingerprint_unique UNIQUE (tenant_id, query_fingerprint)
);

CREATE TABLE monitor_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    rule_name TEXT NOT NULL,
    jurisdiction_codes TEXT NOT NULL,
    body_of_law TEXT,
    keywords TEXT,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    last_triggered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT monitor_rules_status_check CHECK (status IN ('ACTIVE', 'PAUSED', 'ARCHIVED'))
);

CREATE TABLE monitor_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    rule_id UUID NOT NULL REFERENCES monitor_rules(id) ON DELETE CASCADE ON UPDATE CASCADE,
    document_id UUID REFERENCES legal_documents(id) ON DELETE SET NULL ON UPDATE CASCADE,
    alert_type TEXT NOT NULL,
    change_summary TEXT,
    previous_version_url TEXT,
    current_version_url TEXT,
    acknowledged BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT monitor_alerts_type_check CHECK (alert_type IN ('AMENDMENT', 'REPEAL', 'NEW'))
);

CREATE TABLE research_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    question TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    result_report TEXT,
    confidence NUMERIC(3,2),
    gap_detected BOOLEAN NOT NULL DEFAULT false,
    gaps TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT research_tasks_status_check CHECK (status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED')),
    CONSTRAINT research_tasks_confidence_check CHECK (confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0))
);

CREATE TABLE research_task_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    task_id UUID NOT NULL REFERENCES research_tasks(id) ON DELETE CASCADE ON UPDATE CASCADE,
    document_id UUID NOT NULL REFERENCES legal_documents(id) ON DELETE CASCADE ON UPDATE CASCADE,
    relevance_score NUMERIC(4,3) NOT NULL DEFAULT 0,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE research_task_citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    task_id UUID NOT NULL REFERENCES research_tasks(id) ON DELETE CASCADE ON UPDATE CASCADE,
    citation_id UUID NOT NULL REFERENCES legal_citations(id) ON DELETE CASCADE ON UPDATE CASCADE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE research_task_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    task_id UUID NOT NULL REFERENCES research_tasks(id) ON DELETE CASCADE ON UPDATE CASCADE,
    query_text TEXT NOT NULL,
    query_index INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE jurisdictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    jurisdiction_code TEXT NOT NULL,
    jurisdiction_name TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    coverage_percent NUMERIC(5,2) NOT NULL DEFAULT 0,
    document_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT jurisdictions_coverage_check CHECK (coverage_percent >= 0.0 AND coverage_percent <= 100.0),
    CONSTRAINT jurisdictions_tenant_code_unique UNIQUE (tenant_id, jurisdiction_code)
);

-- ============================================================
-- LEXRADAR TABLES
-- ============================================================

CREATE TABLE invention_candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    source_url TEXT NOT NULL,
    source_type TEXT NOT NULL,
    novelty_score NUMERIC(3,2),
    nonobviousness_score NUMERIC(3,2),
    utility_score NUMERIC(3,2),
    enablement_score NUMERIC(3,2),
    scope_score NUMERIC(3,2),
    evidence_score NUMERIC(3,2),
    composite_score NUMERIC(3,2),
    status TEXT NOT NULL DEFAULT 'DETECTED',
    detected_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    scored_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT invention_candidates_status_check CHECK (status IN ('DETECTED', 'SCORING', 'SCORED', 'DISCLOSING', 'DISCLOSED', 'FILED')),
    CONSTRAINT invention_candidates_score_range_check CHECK (
        (novelty_score IS NULL OR (novelty_score >= 0.0 AND novelty_score <= 1.0)) AND
        (nonobviousness_score IS NULL OR (nonobviousness_score >= 0.0 AND nonobviousness_score <= 1.0)) AND
        (utility_score IS NULL OR (utility_score >= 0.0 AND utility_score <= 1.0)) AND
        (enablement_score IS NULL OR (enablement_score >= 0.0 AND enablement_score <= 1.0)) AND
        (scope_score IS NULL OR (scope_score >= 0.0 AND scope_score <= 1.0)) AND
        (evidence_score IS NULL OR (evidence_score >= 0.0 AND evidence_score <= 1.0)) AND
        (composite_score IS NULL OR (composite_score >= 0.0 AND composite_score <= 1.0))
    ),
    CONSTRAINT invention_candidates_source_type_check CHECK (source_type IN ('GitHub', 'Jira', 'Notion'))
);

CREATE TABLE disclosures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    invention_id UUID NOT NULL REFERENCES invention_candidates(id) ON DELETE CASCADE ON UPDATE CASCADE,
    title TEXT NOT NULL,
    inventor TEXT NOT NULL,
    abstract TEXT,
    background TEXT,
    summary TEXT,
    detailed_description TEXT,
    claims TEXT,
    drawings_description TEXT,
    abstract_of_invention TEXT,
    advantages TEXT,
    alternative_implementations TEXT,
    example TEXT,
    prior_art_summary TEXT,
    references TEXT,
    grounding_sources TEXT,
    additional_materials TEXT,
    status TEXT NOT NULL DEFAULT 'DRAFT',
    grounding_score NUMERIC(3,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT disclosures_status_check CHECK (status IN ('DRAFT', 'REVIEWING', 'APPROVED', 'REJECTED', 'REQUESTED_CHANGES')),
    CONSTRAINT disclosures_grounding_score_check CHECK (grounding_score IS NULL OR (grounding_score >= 0.0 AND grounding_score <= 1.0))
);

CREATE TABLE prior_art (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    invention_id UUID NOT NULL REFERENCES invention_candidates(id) ON DELETE CASCADE ON UPDATE CASCADE,
    source TEXT NOT NULL,
    patent_number TEXT,
    title TEXT NOT NULL,
    authors TEXT,
    url TEXT,
    abstract TEXT,
    relevance_summary TEXT,
    relevance_score NUMERIC(3,2),
    published_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT prior_art_source_check CHECK (source IN ('USPTO', 'WIPO', 'EPO', 'Lens', 'GooglePatents', 'PatentScope', 'IPcom')),
    CONSTRAINT prior_art_relevance_score_check CHECK (relevance_score IS NULL OR (relevance_score >= 0.0 AND relevance_score <= 1.0))
);

CREATE TABLE blockchain_anchors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    entity_id UUID NOT NULL,
    entity_type TEXT NOT NULL,
    document_hash TEXT NOT NULL,
    bundle_hash TEXT,
    polygon_tx_hash TEXT NOT NULL,
    polygon_block_number TEXT,
    polygon_tx_timestamp TIMESTAMPTZ,
    anchored_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT blockchain_anchors_entity_type_check CHECK (entity_type IN ('INVENTION', 'DISCLOSURE', 'FILING_BUNDLE')),
    CONSTRAINT blockchain_anchors_document_hash_format CHECK (document_hash ~ '^[a-f0-9]{64}$')
);

CREATE TABLE filing_bundles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    bundle_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'DRAFT',
    patent_type TEXT NOT NULL,
    package_url TEXT,
    package_size_mb NUMERIC(10,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT filing_bundles_status_check CHECK (status IN ('DRAFT', 'READY', 'SUBMITTED', 'ARCHIVED')),
    CONSTRAINT filing_bundles_patent_type_check CHECK (patent_type IN ('PROVISIONAL', 'NON_PROVISIONAL', 'PCT'))
);

CREATE TABLE disclosures_filing_bundles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    disclosure_id UUID NOT NULL REFERENCES disclosures(id) ON DELETE CASCADE ON UPDATE CASCADE,
    filing_bundle_id UUID NOT NULL REFERENCES filing_bundles(id) ON DELETE CASCADE ON UPDATE CASCADE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    role TEXT NOT NULL DEFAULT 'PRIMARY',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT disclosures_filing_bundles_role_check CHECK (role IN ('PRIMARY', 'SECONDARY', 'REFERENCE')),
    CONSTRAINT disclosures_filing_bundles_disclosure_bundle_unique UNIQUE (disclosure_id, filing_bundle_id)
);

CREATE TABLE attorney_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    disclosure_id UUID NOT NULL REFERENCES disclosures(id) ON DELETE CASCADE ON UPDATE CASCADE,
    attorney_email TEXT NOT NULL,
    attorney_name TEXT,
    status TEXT NOT NULL DEFAULT 'PENDING',
    review_notes TEXT,
    rejection_reason TEXT,
    request_changes_details TEXT,
    portal_url TEXT,
    expires_at TIMESTAMPTZ NOT NULL DEFAULT now() + interval '48 hours',
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT attorney_reviews_status_check CHECK (status IN ('PENDING', 'IN_PROGRESS', 'APPROVED', 'REJECTED', 'REQUESTED_CHANGES')),
    CONSTRAINT attorney_reviews_email_format CHECK (attorney_email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT attorney_reviews_tenant_disclosure_unique UNIQUE (tenant_id, disclosure_id)
);

-- ============================================================
-- INDEXES (B-Tree + Composite)
-- ============================================================

-- Tenants
CREATE INDEX tenants_name_idx ON tenants(name);
CREATE INDEX tenants_email_idx ON tenants(email);

-- Users
CREATE INDEX users_tenant_id_idx ON users(tenant_id);
CREATE INDEX users_clerk_user_id_idx ON users(clerk_user_id);
CREATE INDEX users_email_idx ON users(email);
CREATE INDEX users_tenant_role_idx ON users(tenant_id, role);

-- Roles/Permissions
CREATE INDEX roles_permissions_tenant_user_idx ON roles_permissions(tenant_id, user_id);
CREATE INDEX roles_permissions_resource_action_idx ON roles_permissions(resource, action);

-- Payment Plans
CREATE INDEX payment_plans_tenant_id_idx ON payment_plans(tenant_id);
CREATE INDEX payment_plans_status_idx ON payment_plans(status);
CREATE INDEX payment_plans_stripe_idx ON payment_plans(stripe_subscription_id);

-- Workspaces
CREATE INDEX workspaces_tenant_id_idx ON workspaces(tenant_id);
CREATE INDEX workspaces_name_idx ON workspaces(name);

-- API Keys
CREATE INDEX api_keys_tenant_id_idx ON api_keys(tenant_id);
CREATE INDEX api_keys_is_active_idx ON api_keys(is_active);
CREATE INDEX api_keys_expires_at_idx ON api_keys(expires_at);

-- Audit Log
CREATE INDEX audit_log_tenant_id_idx ON audit_log(tenant_id);
CREATE INDEX audit_log_entity_type_id_idx ON audit_log(entity_type, entity_id);
CREATE INDEX audit_log_created_at_idx ON audit_log(created_at DESC);

-- Legal Documents
CREATE INDEX legal_documents_tenant_id_idx ON legal_documents(tenant_id);
CREATE INDEX legal_documents_jurisdiction_idx ON legal_documents(jurisdiction_code);
CREATE INDEX legal_documents_body_of_law_idx ON legal_documents(body_of_law);
CREATE INDEX legal_documents_source_idx ON legal_documents(source);
CREATE INDEX legal_documents_citation_idx ON legal_documents(citation) WHERE citation IS NOT NULL;
CREATE INDEX legal_documents_published_date_idx ON legal_documents(published_date);
CREATE INDEX legal_documents_tenant_jurisdiction_body_idx ON legal_documents(tenant_id, jurisdiction_code, body_of_law);

-- Legal Chunks
CREATE INDEX legal_chunks_tenant_id_idx ON legal_chunks(tenant_id);
CREATE INDEX legal_chunks_document_id_idx ON legal_chunks(document_id);
CREATE INDEX legal_chunks_chunk_type_idx ON legal_chunks(chunk_type);
CREATE INDEX legal_chunks_tenant_document_chunk_idx ON legal_chunks(tenant_id, document_id, chunk_index);

-- Legal Citations
CREATE INDEX legal_citations_tenant_id_idx ON legal_citations(tenant_id);
CREATE INDEX legal_citations_citing_idx ON legal_citations(citing_document_id);
CREATE INDEX legal_citations_cited_idx ON legal_citations(cited_document_id);
CREATE INDEX legal_citations_type_idx ON legal_citations(citation_type);
CREATE INDEX legal_citations_tenant_citing_cited_idx ON legal_citations(tenant_id, citing_document_id, cited_document_id);

-- Query Cache
CREATE INDEX query_cache_tenant_id_idx ON query_cache(tenant_id);
CREATE INDEX query_cache_fingerprint_idx ON query_cache(query_fingerprint);
CREATE INDEX query_cache_expires_at_idx ON query_cache(expires_at);

-- Monitor Rules
CREATE INDEX monitor_rules_tenant_id_idx ON monitor_rules(tenant_id);
CREATE INDEX monitor_rules_status_idx ON monitor_rules(status);
CREATE INDEX monitor_rules_last_triggered_idx ON monitor_rules(last_triggered_at);

-- Monitor Alerts
CREATE INDEX monitor_alerts_tenant_id_idx ON monitor_alerts(tenant_id);
CREATE INDEX monitor_alerts_rule_id_idx ON monitor_alerts(rule_id);
CREATE INDEX monitor_alerts_document_id_idx ON monitor_alerts(document_id);
CREATE INDEX monitor_alerts_alert_type_idx ON monitor_alerts(alert_type);
CREATE INDEX monitor_alerts_acknowledged_idx ON monitor_alerts(acknowledged);
CREATE INDEX monitor_alerts_created_at_idx ON monitor_alerts(created_at DESC);

-- Research Tasks
CREATE INDEX research_tasks_tenant_id_idx ON research_tasks(tenant_id);
CREATE INDEX research_tasks_status_idx ON research_tasks(status);
CREATE INDEX research_tasks_created_at_idx ON research_tasks(created_at DESC);

-- Research Task Documents
CREATE INDEX research_task_documents_tenant_task_idx ON research_task_documents(tenant_id, task_id);
CREATE INDEX research_task_documents_tenant_doc_idx ON research_task_documents(tenant_id, document_id);
CREATE INDEX research_task_documents_sort_order_idx ON research_task_documents(sort_order);

-- Research Task Citations
CREATE INDEX research_task_citations_tenant_task_idx ON research_task_citations(tenant_id, task_id);
CREATE INDEX research_task_citations_sort_order_idx ON research_task_citations(sort_order);

-- Research Task Queries
CREATE INDEX research_task_queries_tenant_task_idx ON research_task_queries(tenant_id, task_id);
CREATE INDEX research_task_queries_query_index_idx ON research_task_queries(query_index);

-- Jurisdictions
CREATE INDEX jurisdictions_tenant_id_idx ON jurisdictions(tenant_id);
CREATE INDEX jurisdictions_code_idx ON jurisdictions(jurisdiction_code);
CREATE INDEX jurisdictions_coverage_idx ON jurisdictions(coverage_percent);

-- Invention Candidates
CREATE INDEX invention_candidates_tenant_id_idx ON invention_candidates(tenant_id);
CREATE INDEX invention_candidates_status_idx ON invention_candidates(status);
CREATE INDEX invention_candidates_composite_score_idx ON invention_candidates(composite_score) WHERE composite_score IS NOT NULL;
CREATE INDEX invention_candidates_source_type_idx ON invention_candidates(source_type);
CREATE INDEX invention_candidates_detected_at_idx ON invention_candidates(detected_at DESC);

-- Disclosures
CREATE INDEX disclosures_tenant_id_idx ON disclosures(tenant_id);
CREATE INDEX disclosures_invention_id_idx ON disclosures(invention_id);
CREATE INDEX disclosures_status_idx ON disclosures(status);
CREATE INDEX disclosures_grounding_score_idx ON disclosures(grounding_score) WHERE grounding_score IS NOT NULL;
CREATE INDEX disclosures_tenant_status_created_idx ON disclosures(tenant_id, status, created_at DESC);

-- Prior Art
CREATE INDEX prior_art_tenant_id_idx ON prior_art(tenant_id);
CREATE INDEX prior_art_invention_id_idx ON prior_art(invention_id);
CREATE INDEX prior_art_source_idx ON prior_art(source);
CREATE INDEX prior_art_relevance_score_idx ON prior_art(relevance_score) WHERE relevance_score IS NOT NULL;
CREATE INDEX prior_art_patent_number_idx ON prior_art(patent_number) WHERE patent_number IS NOT NULL;

-- Blockchain Anchors
CREATE INDEX blockchain_anchors_tenant_id_idx ON blockchain_anchors(tenant_id);
CREATE INDEX blockchain_anchors_entity_id_idx ON blockchain_anchors(entity_id);
CREATE INDEX blockchain_anchors_polygon_tx_idx ON blockchain_anchors(polygon_tx_hash);
CREATE INDEX blockchain_anchors_tenant_entity_type_idx ON blockchain_anchors(tenant_id, entity_type);

-- Filing Bundles
CREATE INDEX filing_bundles_tenant_id_idx ON filing_bundles(tenant_id);
CREATE INDEX filing_bundles_status_idx ON filing_bundles(status);
CREATE INDEX filing_bundles_patent_type_idx ON filing_bundles(patent_type);

-- Disclosures Filing Bundles
CREATE INDEX disclosures_filing_bundles_tenant_disclosure_idx ON disclosures_filing_bundles(tenant_id, disclosure_id);
CREATE INDEX disclosures_filing_bundles_tenant_bundle_idx ON disclosures_filing_bundles(tenant_id, filing_bundle_id);
CREATE INDEX disclosures_filing_bundles_sort_order_idx ON disclosures_filing_bundles(sort_order);

-- Attorney Reviews
CREATE INDEX attorney_reviews_tenant_id_idx ON attorney_reviews(tenant_id);
CREATE INDEX attorney_reviews_disclosure_id_idx ON attorney_reviews(disclosure_id);
CREATE INDEX attorney_reviews_status_idx ON attorney_reviews(status);
CREATE INDEX attorney_reviews_expires_at_idx ON attorney_reviews(expires_at);

-- ============================================================
-- AUTO-UPDATE TRIGGERS (updated_at)
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tenants_update_timestamp BEFORE UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER users_update_timestamp BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER roles_permissions_update_timestamp BEFORE UPDATE ON roles_permissions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER payment_plans_update_timestamp BEFORE UPDATE ON payment_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER workspaces_update_timestamp BEFORE UPDATE ON workspaces
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER api_keys_update_timestamp BEFORE UPDATE ON api_keys
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER legal_documents_update_timestamp BEFORE UPDATE ON legal_documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER monitor_rules_update_timestamp BEFORE UPDATE ON monitor_rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER monitor_alerts_update_timestamp BEFORE UPDATE ON monitor_alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER research_tasks_update_timestamp BEFORE UPDATE ON research_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER jurisdictions_update_timestamp BEFORE UPDATE ON jurisdictions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER invention_candidates_update_timestamp BEFORE UPDATE ON invention_candidates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER disclosures_update_timestamp BEFORE UPDATE ON disclosures
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER prior_art_update_timestamp BEFORE UPDATE ON prior_art
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER blockchain_anchors_update_timestamp BEFORE UPDATE ON blockchain_anchors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER filing_bundles_update_timestamp BEFORE UPDATE ON filing_bundles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER disclosures_filing_bundles_update_timestamp BEFORE UPDATE ON disclosures_filing_bundles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER attorney_reviews_update_timestamp BEFORE UPDATE ON attorney_reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- END OF 001_initial_schema.sql
-- ============================================================
