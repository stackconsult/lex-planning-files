# Ledger Module Governance

> **Chunk:** C42 — Phase 3 Ledger + Auto  
> **Horde:** HORDE-LEDGER  
> **Status:** PRODUCTION_READY

## Overview

Immutable proof layer for IP content hashing. Only SHA-256 hashes stored on-chain, never raw IP content (IP-G1 guardrail).

## Components

### Proof Layer
- SHA-256 hashing for IP content
- Immutable proof records
- Hash verification

## Guardrails

- IP-G1: Only SHA-256 hash on-chain, never IP content
- LEDGER-CRIT-01: SHA-256 hash matching file content

## Tests

- test_proof_layer.py: 14 tests covering all functions
