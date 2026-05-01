-- LexCore + LexRadar — pgvector Indexes
-- Build System: Unified Build System v2
-- Chunk: C03 — Data Model + Storage
-- Horde: HORDE-SCHEMA
-- Date: 2026-04-29
-- Schema Version: v0.1.0-foundation
-- Prerequisites: 001_initial_schema.sql and 002_rls_policies.sql must be executed first

-- ============================================================
-- HNSW INDEX ON LEGAL_CHUNKS (LexCore)
-- ============================================================
-- Hybrid search: pgvector HNSW index for approximate nearest neighbor
-- on 1536-dimensional OpenAI text-embedding-3-large vectors.
-- Cosine similarity is used for semantic relevance.

CREATE INDEX legal_chunks_embedding_hnsw_cosine_idx
ON legal_chunks
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 100);

-- ============================================================
-- GIN INDEX ON LEGAL_CHUNKS CONTENT (LexCore)
-- ============================================================
-- Full-text search fallback using PostgreSQL tsvector/tsquery.
-- Hybrid search combines HNSW (cosine) + GIN (full-text) + re-rank.

CREATE INDEX legal_chunks_content_gin_idx
ON legal_chunks
USING gin (to_tsvector('english', content));

-- ============================================================
-- PARTIAL INDEX ON LEGAL_CHUNKS (FILTERED BY CHUNK TYPE)
-- ============================================================
-- Section-level chunks are the most important for document overview.
-- Filtered index improves search when only section-level context is needed.

CREATE INDEX legal_chunks_section_embedding_idx
ON legal_chunks
USING hnsw (embedding vector_cosine_ops)
WHERE chunk_type = 'SECTION'
WITH (m = 16, ef_construction = 100);

-- ============================================================
-- COMPOSITE INDEX: LEGAL_CHUNKS (TENANT + DOCUMENT)
-- ============================================================
-- Speeds up queries that fetch all chunks for a specific document
-- within a tenant. Combined with HNSW for hybrid search.

CREATE INDEX legal_chunks_tenant_doc_type_idx
ON legal_chunks(tenant_id, document_id, chunk_type);

-- ============================================================
-- COMPOSITE INDEX: LEGAL_CHUNKS (TENANT + EMBEDDING SEARCH)
-- ============================================================
-- Speeds up tenant-scoped HNSW search by narrowing search space first.
-- PostgreSQL planner uses this before entering the HNSW index.

CREATE INDEX legal_chunks_tenant_embedding_idx
ON legal_chunks(tenant_id, id)
INCLUDE (chunk_index, chunk_type, content);

-- ============================================================
-- GIN INDEX ON LEGAL_DOCUMENTS METADATA (LexCore)
-- ============================================================
-- JSONB metadata may contain jurisdiction-specific fields, source
-- identifiers, or custom tags. GIN index enables efficient querying.

CREATE INDEX legal_documents_metadata_gin_idx
ON legal_documents
USING gin (metadata);

-- ============================================================
-- NOTE: PRIOR_ART TABLE EMBEDDINGS
-- ============================================================
-- Prior art embeddings are stored in Qdrant (not PostgreSQL) per
-- C02 architecture decision (ADR-001). PostgreSQL stores the metadata
-- and relational structure; Qdrant stores the vectors for similarity
-- search across 7 prior art sources.
--
-- If in the future prior art embeddings are moved to PostgreSQL,
-- add the following (commented out for reference):
--
-- CREATE INDEX prior_art_embedding_hnsw_cosine_idx
-- ON prior_art
-- USING hnsw (embedding vector_cosine_ops)
-- WITH (m = 16, ef_construction = 100);

-- ============================================================
-- DOCUMENT SEARCH — COMPOSITE GIN INDEX
-- ============================================================
-- Combined full-text search across title + citation + summary
-- for fast document listing and search-before-chunk-search.

CREATE INDEX legal_documents_search_gin_idx
ON legal_documents
USING gin (to_tsvector('english', coalesce(title, '') || ' ' || coalesce(citation, '') || ' ' || coalesce(summary, '')));

-- ============================================================
-- QUERY CACHE SEARCH
-- ============================================================
-- Fast lookup by tenant + fingerprint for cache hit detection.

CREATE INDEX query_cache_tenant_fingerprint_lookup_idx
ON query_cache(tenant_id, query_fingerprint)
WHERE expires_at > now();

-- ============================================================
-- MONITOR RULES SEARCH
-- ============================================================
-- Active rules lookup for scheduled monitoring tasks.

CREATE INDEX monitor_rules_active_tenant_idx
ON monitor_rules(tenant_id, status)
WHERE status = 'ACTIVE';

-- ============================================================
-- INVENTION CANDIDATES SEARCH
-- ============================================================
-- Composite index for scoring pipeline queries.

CREATE INDEX invention_candidates_tenant_status_score_idx
ON invention_candidates(tenant_id, status, composite_score DESC NULLS LAST);

-- ============================================================
-- DISCLOSURES SEARCH
-- ============================================================
-- Status-filtered search for disclosure dashboard.

CREATE INDEX disclosures_tenant_status_created_idx
ON disclosures(tenant_id, status, created_at DESC);

-- ============================================================
-- ATTORNEY REVIEWS SEARCH
-- ============================================================
-- Expiring reviews lookup for reminder notifications.

CREATE INDEX attorney_reviews_expiring_idx
ON attorney_reviews(tenant_id, expires_at)
WHERE status IN ('PENDING', 'IN_PROGRESS') AND expires_at < now() + interval '24 hours';

-- ============================================================
-- INDEX MAINTENANCE NOTES
-- ============================================================
-- Rebuild HNSW index after bulk ingestion:
--   REINDEX INDEX legal_chunks_embedding_hnsw_cosine_idx;
--
-- Monitor index bloat:
--   SELECT schemaname, tablename, indexname, pg_size_pretty(pg_relation_size(indexrelid))
--   FROM pg_stat_user_indexes
--   WHERE schemaname = 'public' AND tablename IN ('legal_chunks', 'legal_documents');
--
-- Vacuum and analyze after large ingestion batches:
--   VACUUM ANALYZE legal_chunks;
--   VACUUM ANALYZE legal_documents;
--
-- Tune HNSW ef_search at query time for latency/accuracy tradeoff:
--   SET hnsw.ef_search = 200;  -- higher = more accurate, slower
--   Default: 40 (tuned for 95% recall at < 100ms)

-- ============================================================
-- END OF 003_pgvector_indexes.sql
-- ============================================================
