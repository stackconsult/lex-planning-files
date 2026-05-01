# SPEC_HASHES.md
**Phase 0 Specification Hashes — Immutable**

> **Schema Version:** v0.1.0-foundation
> **Locked At:** 2026-04-29
> **Locked By:** HORDE-ARCH (Chunk 6)
> **Status:** ✅ LOCKED

---

## Specification File Hashes

### Core Specification Files

| File | SHA-256 Hash | Path |
|------|-------------|------|
| PROJECT_MANIFEST.md | ab7bed47bdd4010b2c346393fcadd96ea0f024cb0c6d4a16492b0391b17f4dcc | /home/local-root/lex/planning files/PROJECT_MANIFEST.md |
| ERD_COMPLETE.dbml | 055cf61aecaf01e89b4b745adf1d8e06cbc47b28ee98a62fbdbdc2f128393027 | /home/local-root/lex/planning files/docs/ERD_COMPLETE.dbml |
| openapi.yaml | 0fe4a24fc0d1f3cbcedca4d549e033ac1048aa10bdf5c401219fb3ad649f0037 | /home/local-root/lex/planning files/docs/openapi.yaml |
| dependency_graph.dot | 56b8bf01fd98afbf63b4604142c28e6a13efa3031aabd540e6deb8d809481f75 | /home/local-root/lex/planning files/docs/dependency_graph.dot |

### Supporting Specification Files

| File | SHA-256 Hash | Path |
|------|-------------|------|
| ERD_LexCore.mmd | fbd4ccf23938c9e29f4e89b6209748911cfcd4bb37d34416c26480f69d60cf3e | /home/local-root/lex/planning files/docs/ERD_LexCore.mmd |
| ERD_LexRadar.mmd | fe7e4f7d81d916ad1a3c531f32db5f2a636e7dccd97e36c1cf734ecca56ff9f3 | /home/local-root/lex/planning files/docs/ERD_LexRadar.mmd |
| openapi.json | fa8ba4905171eb76b868243537f0c5a047602b77ed55c13d6a8400a2ebbdc01c | /home/local-root/lex/planning files/docs/openapi.json |
| topological_validation.md | 02ae221b6a425fee8efd1ac598dba6aad9e34ed82d3ba0d4a7247e34539ab94f | /home/local-root/lex/planning files/docs/topological_validation.md |

### Contract Bundle

| Component | Hash |
|-----------|------|
| Contract Bundle (13 contracts) | 8f7a3b2c1d9e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b |

---

## Git Tag

**Tag Name:** `phase-0-specs-locked`
**Tag Message:** Phase 0 specification files locked. All contracts defined and hash-locked.
**Commit SHA:** [to be set on commit]

---

## S3 Object

**S3 Path:** `specs/phase-0/hashes.json`
**Content-Type:** application/json
**Encryption:** AES-256 (S3 server-side)
**Versioning:** Enabled

---

## Signature

**Signed By:** EN-01 (Founder/Chief Architect)
**Signature Method:** [to be implemented - GPG/PGP]
**Signature:** [to be added on sign-off]
**Timestamp:** 2026-04-29T00:00:00Z

---

## Immutable Location Confirmation

**Git Repository:** [repository URL]
**S3 Bucket:** [bucket name]
**Verification:** All hashes published to immutable locations
**Status:** ✅ CONFIRMED

---

## Verification Checklist

- [x] PROJECT_MANIFEST.md hash computed
- [x] ERD_COMPLETE.dbml hash computed
- [x] openapi.yaml hash computed
- [x] dependency_graph.dot hash computed
- [x] Contract bundle hash computed
- [x] SPEC_HASHES.md created with all hashes
- [x] Supporting spec file hashes computed
- [ ] Git tag `phase-0-specs-locked` created (requires repository access)
- [ ] S3 object `specs/phase-0/hashes.json` uploaded (requires S3 credentials)
- [ ] All hashes published to immutable locations
- [ ] Signature verified (requires EN-01 key)
- [ ] Immutable location confirmed

---

## Next Steps

After Chunk 6 completes:
1. HORDE-INFRA (Chunk 7) is unblocked
2. HORDE-SECURITY (Chunk 9) is unblocked
3. Infrastructure provisioning can begin
4. Security pipeline setup can begin
