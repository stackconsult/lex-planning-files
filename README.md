# LexCore + LexRadar

Legal intelligence platform for patent detection, prior art search, and regulatory monitoring.

## Architecture

- **Backend**: Python FastAPI with async service layer
- **Workers**: Celery for ingest, LexRadar IP detection, and monitoring
- **Database**: PostgreSQL + pgvector for embeddings, with RLS-enforced tenant isolation
- **Blockchain**: Polygon for IP anchoring (SHA-256 hashed bundles)
- **ML**: Hyper-efficient data flow with token efficiency tracking and pattern forensic consistency

## Quick Start

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run build validation
python scripts/validate_build.py

# Run predictability validation
python scripts/validate_predictability.py

# Run HORDE-AUDIT
python scripts/horde_audit.py
```

## Service Layer

| Domain | Routes | Service | Methods |
|---|---|---|---|
| MCP | 7 | `mcp_service.py` | 7 tools |
| LexCore | 5 | `lexcore_service.py` | 5 operations |
| LexRadar | 6 | `lexradar_service.py` | 6 IP operations |

## Validation

- **Token efficiency**: 41.9% reduction (target 40%)
- **Pattern forensic consistency**: 100%
- **Predictability curve R²**: 0.9449

## Documentation

- `docs/teams/` — 17 team execution plans
- `docs/execution/BUILD_JOURNAL.md` — incremental build log
- `docs/execution/HORDE_AUDIT_REPORT.md` — latest audit gate
