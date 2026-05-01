-- LexCore + LexRadar — Row Level Security Policies
-- Build System: Unified Build System v2
-- Chunk: C03 — Data Model + Storage
-- Horde: HORDE-SCHEMA
-- Date: 2026-04-29
-- Schema Version: v0.1.0-foundation
-- Prerequisites: 001_initial_schema.sql must be executed first

-- ============================================================
-- RLS ENABLEMENT
-- ============================================================
-- Force RLS on all tenant-scoped tables. This ensures the app role (which
-- bypasses RLS if not forced) still respects row-level policies.

ALTER TABLE tenants FORCE ROW LEVEL SECURITY;
ALTER TABLE users FORCE ROW LEVEL SECURITY;
ALTER TABLE roles_permissions FORCE ROW LEVEL SECURITY;
ALTER TABLE payment_plans FORCE ROW LEVEL SECURITY;
ALTER TABLE workspaces FORCE ROW LEVEL SECURITY;
ALTER TABLE api_keys FORCE ROW LEVEL SECURITY;
ALTER TABLE audit_log FORCE ROW LEVEL SECURITY;
ALTER TABLE legal_documents FORCE ROW LEVEL SECURITY;
ALTER TABLE legal_chunks FORCE ROW LEVEL SECURITY;
ALTER TABLE legal_citations FORCE ROW LEVEL SECURITY;
ALTER TABLE query_cache FORCE ROW LEVEL SECURITY;
ALTER TABLE monitor_rules FORCE ROW LEVEL SECURITY;
ALTER TABLE monitor_alerts FORCE ROW LEVEL SECURITY;
ALTER TABLE research_tasks FORCE ROW LEVEL SECURITY;
ALTER TABLE research_task_documents FORCE ROW LEVEL SECURITY;
ALTER TABLE research_task_citations FORCE ROW LEVEL SECURITY;
ALTER TABLE research_task_queries FORCE ROW LEVEL SECURITY;
ALTER TABLE jurisdictions FORCE ROW LEVEL SECURITY;
ALTER TABLE invention_candidates FORCE ROW LEVEL SECURITY;
ALTER TABLE disclosures FORCE ROW LEVEL SECURITY;
ALTER TABLE prior_art FORCE ROW LEVEL SECURITY;
ALTER TABLE blockchain_anchors FORCE ROW LEVEL SECURITY;
ALTER TABLE filing_bundles FORCE ROW LEVEL SECURITY;
ALTER TABLE disclosures_filing_bundles FORCE ROW LEVEL SECURITY;
ALTER TABLE attorney_reviews FORCE ROW LEVEL SECURITY;

-- ============================================================
-- TENANT ISOLATION FUNCTION
-- ============================================================
-- Returns the current tenant_id from the session context variable.
-- All RLS policies reference this function.

CREATE OR REPLACE FUNCTION current_app_tenant_id()
RETURNS UUID AS $$
BEGIN
    RETURN NULLIF(current_setting('app.tenant_id', true), '')::UUID;
EXCEPTION WHEN OTHERS THEN
    RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================
-- GENERIC TENANT ISOLATION POLICIES (FOR ALL TENANT-SCOPED TABLES)
-- ============================================================

-- tenants: Users can only see their own tenant record
CREATE POLICY tenants_isolation ON tenants
    FOR ALL TO app_role
    USING (id = current_app_tenant_id());

-- users: Users can see users within their tenant
CREATE POLICY users_isolation ON users
    FOR ALL TO app_role
    USING (tenant_id = current_app_tenant_id());

-- roles_permissions: Scoped to tenant
CREATE POLICY roles_permissions_isolation ON roles_permissions
    FOR ALL TO app_role
    USING (tenant_id = current_app_tenant_id());

-- payment_plans: Scoped to tenant
CREATE POLICY payment_plans_isolation ON payment_plans
    FOR ALL TO app_role
    USING (tenant_id = current_app_tenant_id());

-- workspaces: Scoped to tenant
CREATE POLICY workspaces_isolation ON workspaces
    FOR ALL TO app_role
    USING (tenant_id = current_app_tenant_id());

-- api_keys: Scoped to tenant (admin role restriction enforced in app layer)
CREATE POLICY api_keys_isolation ON api_keys
    FOR ALL TO app_role
    USING (tenant_id = current_app_tenant_id());

-- audit_log: Scoped to tenant, read-only
CREATE POLICY audit_log_isolation ON audit_log
    FOR SELECT TO app_role
    USING (tenant_id = current_app_tenant_id());

-- audit_log: No UPDATE or DELETE allowed for any role
CREATE POLICY audit_log_no_update ON audit_log
    FOR UPDATE TO app_role
    USING (false);

CREATE POLICY audit_log_no_delete ON audit_log
    FOR DELETE TO app_role
    USING (false);

-- ============================================================
-- LEXCORE DOMAIN RLS POLICIES
-- ============================================================

CREATE POLICY legal_documents_isolation ON legal_documents
    FOR ALL TO app_role
    USING (tenant_id = current_app_tenant_id());

CREATE POLICY legal_chunks_isolation ON legal_chunks
    FOR ALL TO app_role
    USING (tenant_id = current_app_tenant_id());

CREATE POLICY legal_citations_isolation ON legal_citations
    FOR ALL TO app_role
    USING (tenant_id = current_app_tenant_id());

CREATE POLICY query_cache_isolation ON query_cache
    FOR ALL TO app_role
    USING (tenant_id = current_app_tenant_id());

CREATE POLICY monitor_rules_isolation ON monitor_rules
    FOR ALL TO app_role
    USING (tenant_id = current_app_tenant_id());

CREATE POLICY monitor_alerts_isolation ON monitor_alerts
    FOR ALL TO app_role
    USING (tenant_id = current_app_tenant_id());

CREATE POLICY research_tasks_isolation ON research_tasks
    FOR ALL TO app_role
    USING (tenant_id = current_app_tenant_id());

CREATE POLICY research_task_documents_isolation ON research_task_documents
    FOR ALL TO app_role
    USING (tenant_id = current_app_tenant_id());

CREATE POLICY research_task_citations_isolation ON research_task_citations
    FOR ALL TO app_role
    USING (tenant_id = current_app_tenant_id());

CREATE POLICY research_task_queries_isolation ON research_task_queries
    FOR ALL TO app_role
    USING (tenant_id = current_app_tenant_id());

CREATE POLICY jurisdictions_isolation ON jurisdictions
    FOR ALL TO app_role
    USING (tenant_id = current_app_tenant_id());

-- ============================================================
-- LEXRADAR DOMAIN RLS POLICIES
-- ============================================================

CREATE POLICY invention_candidates_isolation ON invention_candidates
    FOR ALL TO app_role
    USING (tenant_id = current_app_tenant_id());

CREATE POLICY disclosures_isolation ON disclosures
    FOR ALL TO app_role
    USING (tenant_id = current_app_tenant_id());

CREATE POLICY prior_art_isolation ON prior_art
    FOR ALL TO app_role
    USING (tenant_id = current_app_tenant_id());

CREATE POLICY blockchain_anchors_isolation ON blockchain_anchors
    FOR ALL TO app_role
    USING (tenant_id = current_app_tenant_id());

CREATE POLICY filing_bundles_isolation ON filing_bundles
    FOR ALL TO app_role
    USING (tenant_id = current_app_tenant_id());

CREATE POLICY disclosures_filing_bundles_isolation ON disclosures_filing_bundles
    FOR ALL TO app_role
    USING (tenant_id = current_app_tenant_id());

CREATE POLICY attorney_reviews_isolation ON attorney_reviews
    FOR ALL TO app_role
    USING (tenant_id = current_app_tenant_id());

-- ============================================================
-- ATTENDEE / APP USER SETUP
-- ============================================================
-- The app connects as a role with limited privileges. RLS enforces
-- that it can only see data for the tenant set in session context.

CREATE ROLE app_role WITH LOGIN PASSWORD 'app_role_password_here';

GRANT USAGE ON SCHEMA public TO app_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_role;

-- Note: Production should use Vault to inject the app_role password,
-- rotate it regularly, and grant only the specific table permissions
-- required by each service (principle of least privilege).

-- ============================================================
-- RLS VERIFICATION FUNCTION
-- ============================================================
-- Call this to verify RLS is active on all tables.

CREATE OR REPLACE FUNCTION verify_rls_enabled()
RETURNS TABLE (
    table_name TEXT,
    rls_enabled BOOLEAN,
    force_rls_enabled BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT c.relname::TEXT,
           c.relrowsecurity AS rls_enabled,
           c.relforcerowsecurity AS force_rls_enabled
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relkind = 'r'
      AND n.nspname = 'public'
      AND c.relname IN (
          'tenants','users','roles_permissions','payment_plans','workspaces',
          'api_keys','audit_log','legal_documents','legal_chunks','legal_citations',
          'query_cache','monitor_rules','monitor_alerts','research_tasks',
          'research_task_documents','research_task_citations','research_task_queries',
          'jurisdictions','invention_candidates','disclosures','prior_art',
          'blockchain_anchors','filing_bundles','disclosures_filing_bundles',
          'attorney_reviews'
      );
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- END OF 002_rls_policies.sql
-- ============================================================
