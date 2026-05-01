-- Base seed data for LexCore + LexRadar
-- Schema Version: v0.1.0-foundation
-- Phase: P1 Core Build - schema-01

-- Insert default tenant types and subscription tiers
-- These are reference data, not actual tenant records

-- Note: Actual tenant records will be created during onboarding
-- This seed data is for reference/configuration only

-- Default system roles (for reference)
-- Roles are: admin, member, viewer
-- These are enforced in the users.role CHECK constraint

-- Default subscription tiers (for reference)
-- Tiers are: SOLO, FIRM, ENTERPRISE
-- These are enforced in the tenants.tier CHECK constraint

-- Default payment statuses (for reference)
-- Statuses: TRIAL, ACTIVE, CANCELLED, PAST_DUE
-- These are enforced in the tenants.payment_status CHECK constraint

-- Default document body_of_law types (for reference)
-- Types: STATUTE, REGULATION, CASE
-- These are enforced in the legal_documents.body_of_law CHECK constraint

-- Default chunk types (for reference)
-- Types: SECTION, PARAGRAPH, SENTENCE
-- These are enforced in the legal_chunks.chunk_type CHECK constraint

-- Default citation types (for reference)
-- Types: FORWARD, BACKWARD
-- These are enforced in the legal_citations.citation_type CHECK constraint

-- Default monitor rule statuses (for reference)
-- Statuses: ACTIVE, PAUSED, ARCHIVED
-- These are enforced in the monitor_rules.status CHECK constraint

-- Default monitor alert types (for reference)
-- Types: AMENDMENT, REPEAL, NEW
-- These are enforced in the monitor_alerts.alert_type CHECK constraint

-- Default research task statuses (for reference)
-- Statuses: PENDING, RUNNING, COMPLETED, FAILED
-- These are enforced in the research_tasks.status CHECK constraint

-- Default invention candidate statuses (for reference)
-- Statuses: DETECTED, SCORING, SCORED, DISCLOSING, DISCLOSED, FILED
-- These are enforced in the invention_candidates.status CHECK constraint

-- Default invention source types (for reference)
-- Types: GitHub, Jira, Notion
-- These are enforced in the invention_candidates.source_type CHECK constraint

-- Default disclosure statuses (for reference)
-- Statuses: DRAFT, REVIEWING, APPROVED, REJECTED, REQUESTED_CHANGES
-- These are enforced in the disclosures.status CHECK constraint

-- Default prior art sources (for reference)
-- Sources: USPTO, WIPO, EPO, Lens, GooglePatents, PatentScope, IPcom
-- These are enforced in the prior_art.source CHECK constraint

-- Default blockchain anchor entity types (for reference)
-- Types: INVENTION, DISCLOSURE, FILING_BUNDLE
-- These are enforced in the blockchain_anchors.entity_type CHECK constraint

-- Default filing bundle statuses (for reference)
-- Statuses: DRAFT, READY, SUBMITTED, ARCHIVED
-- These are enforced in the filing_bundles.status CHECK constraint

-- Default filing bundle patent types (for reference)
-- Types: PROVISIONAL, NON_PROVISIONAL, PCT
-- These are enforced in the filing_bundles.patent_type CHECK constraint

-- Default disclosures_filing_bundles roles (for reference)
-- Roles: PRIMARY, SECONDARY, REFERENCE
-- These are enforced in the disclosures_filing_bundles.role CHECK constraint

-- Default attorney review statuses (for reference)
-- Statuses: PENDING, IN_PROGRESS, APPROVED, REJECTED, REQUESTED_CHANGES
-- These are enforced in the attorney_reviews.status CHECK constraint

-- Default user roles (for reference)
-- Roles: admin, member, viewer
-- These are enforced in the users.role CHECK constraint

-- Default roles_permissions actions (for reference)
-- Actions: read, write, delete, admin
-- These are enforced in the roles_permissions.action CHECK constraint

-- Default roles_permissions scopes (for reference)
-- Scopes: tenant, workspace, user
-- These are enforced in the roles_permissions.scope CHECK constraint
