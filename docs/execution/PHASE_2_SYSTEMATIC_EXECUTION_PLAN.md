# Phase 2 IP Pipeline - Systematic Execution Plan

> **Domain:** legal-patent
> **Status:** READY_FOR_EXECUTION
> **Date:** 2026-05-05
> **Execution Pattern:** Quasi-Coder (mini-chunks, validate, commit, push)

## Overview

Phase 2 builds the IP Pipeline with 24 agents across 4 teams. Systematic chunking to avoid RAM throttling on Chromebook.

## Team Assignments

### Team C: Agents & Grounding (HORDE-AGENTS)
**Primary Skills:**
- Agent orchestration
- Grounding verification
- Citation management
- No direct imports enforcement (AGT-G1 guardrail)

**Assigned Chunks:**
- Chunk 9: Router Agent
- Chunk 10: Search Agent
- Chunk 11: Analysis Agent
- Chunk 12: Draft Agent
- Chunk 13: Ingest Agent
- Chunk 14: Monitor Agent
- Chunk 15: Cite Agent
- Chunk 16: Scanner Agent
- Chunk 17: Detector Agent
- Chunk 18: PriorArt Agent
- Chunk 19: Scorer Agent
- Chunk 20: Discloser Agent
- Chunk 21: Ledger Agent
- Chunk 22: Grounding Verification
- Chunk 23: Citation Management
- Chunk 24: No Direct Imports Enforcement

### Team D: Prior Art & Ingest (HORDE-INGEST)
**Primary Skills:**
- Prior art fetching
- API integration (USPTO, EPO, Google Patents)
- Data pipelines
- Vector embeddings

**Assigned Chunks:**
- Chunk 25: USPTO Connector
- Chunk 26: EPO Connector
- Chunk 27: Google Patents Connector
- Chunk 28: Legal Source Connectors (9 sources)
- Chunk 29: Ingestion Workers
- Chunk 30: Vector Embeddings
- Chunk 31: Quality Validation

### Team B: API & MCP Tools (HORDE-API)
**Primary Skills:**
- FastAPI implementation
- MCP tools development
- JWT authentication
- Rate limiting

**Assigned Chunks:**
- Chunk 32: API Routes Enhancement
- Chunk 33: MCP Tools Implementation
- Chunk 34: Authentication Integration
- Chunk 35: Rate Limiting Enhancement

### Team E: Scoring & Evaluation (HORDE-SCORE)
**Primary Skills:**
- Scoring model calibration
- GroundingJudge ≥ 0.85
- ToolCallJudge ≥ 0.90
- Quality assessment

**Assigned Chunks:**
- Chunk 36: Scoring Model Calibration
- Chunk 37: GroundingJudge Implementation
- Chunk 38: ToolCallJudge Implementation
- Chunk 39: LHP Section Drafting (10 sections)

## Execution Protocol

1. **Execute chunk** (1-2 files max)
2. **Validate guardrails** (AGT-G1, IP-G7, SEC-G2)
3. **Commit with structured message**
4. **Push to remote**
5. **Continue to next chunk**

## Guardrails

- **AGT-G1**: No agent imports another agent directly
- **IP-G7**: No auto-submission to patent offices
- **SEC-G2**: BYOK: LexRadar never holds plaintext decryption key
- **GroundingJudge**: ≥ 0.85
- **ToolCallJudge**: ≥ 0.90

## Gate Criteria

- All 24 agents built
- Grounding ≥ 0.85
- All 10 LHP sections draftable
- Zero critical findings
- Test coverage ≥ 80%
