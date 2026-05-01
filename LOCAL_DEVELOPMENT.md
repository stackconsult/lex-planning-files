# LexCore + LexRadar — Local Development Guide

> **Schema Version:** v0.1.0-foundation
> **Last Updated:** 2026-04-29

---

## Quick Start

```bash
# 1. Clone repository
git clone <repository-url>
cd lexcore

# 2. Start local development stack
docker-compose up -d

# 3. Run database migrations
docker-compose --profile migrate up migrate

# 4. API is available at http://localhost:8000
# 5. API docs at http://localhost:8000/docs (development only)
# 6. Grafana dashboards at http://localhost:3000 (admin/admin)
# 7. Prometheus at http://localhost:9090
```

---

## Services

| Service | Port | Purpose | Credentials |
|---------|------|---------|-------------|
| API | 8000 | FastAPI application | JWT via `/v1/auth/token` |
| PostgreSQL | 5432 | Primary database with pgvector | lexcore / lexcore_dev_password |
| Redis | 6379 | Caching, sessions, job queue | (no auth in dev) |
| Qdrant | 6333 | Vector database for embeddings | (no auth in dev) |
| Vault | 8200 | Secrets management, BYOK | dev-token-only-for-local |
| Prometheus | 9090 | Metrics collection | (no auth) |
| Grafana | 3000 | Dashboards and visualization | admin / admin |

---

## Environment Variables

Copy `.env.example` to `.env` and customize:

```env
LEXCORE_ENVIRONMENT=development
LEXCORE_DATABASE_URL=postgresql+asyncpg://lexcore:lexcore_dev_password@localhost:5432/lexcore
LEXCORE_REDIS_URL=redis://localhost:6379/0
LEXCORE_QDRANT_URL=http://localhost:6333
LEXCORE_VAULT_ADDR=http://localhost:8200
LEXCORE_VAULT_TOKEN=dev-token-only-for-local
LEXCORE_JWT_SECRET=change-me-in-production
LEXCORE_LOG_LEVEL=DEBUG
```

---

## Database Migrations

```bash
# Run migrations (one-off)
docker-compose --profile migrate up migrate

# Create new migration (requires local Python + alembic)
cd backend/
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

---

## Testing

```bash
# Run all tests (inside Docker or locally with Python 3.12)
docker-compose exec api pytest

# Run specific test suite
docker-compose exec api pytest tests/unit/
docker-compose exec api pytest tests/integration/

# Run security tests
docker-compose exec api pytest tests/security/

# Run with coverage
docker-compose exec api pytest --cov=src --cov-report=html
```

---

## API Usage

```bash
# Get JWT token
curl -X POST http://localhost:8000/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your_api_key"}'

# Use MCP get_capabilities
curl http://localhost:8000/v1/mcp/get_capabilities \
  -H "Authorization: Bearer <token>"

# Search legal documents
curl -X POST http://localhost:8000/v1/mcp/search_legal \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"query": "privacy law california", "top_k": 10}'

# List inventions
curl http://localhost:8000/v1/lexradar/inventions \
  -H "Authorization: Bearer <token>"
```

---

## Monitoring

- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3000 (login: admin/admin)
  - LexCore API Overview dashboard
  - Database & Cache dashboard
  - Security & Compliance dashboard
  - SLOs & SLIs dashboard

---

## Security Notes

> ⚠️ **WARNING:** This local development stack uses weak credentials and disables security features. **Never use in production.**

- JWT secret: `local-dev-secret-change-in-production`
- Vault token: `dev-token-only-for-local`
- PostgreSQL password: `lexcore_dev_password`
- Grafana password: `admin`

Before production deployment:
1. Change all secrets
2. Enable TLS/HTTPS
3. Configure proper CORS origins
4. Set up proper authentication backends
5. Enable Vault production mode (HA cluster)
6. Configure AWS/GCP/Azure credentials
7. Set up proper logging and alerting

---

## Troubleshooting

```bash
# View logs
docker-compose logs -f api

# Restart a service
docker-compose restart api

# Reset database (WARNING: destroys all data)
docker-compose down -v
docker-compose up -d
docker-compose --profile migrate up migrate

# Check service health
curl http://localhost:8000/health/ready
curl http://localhost:8000/health/live
```

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│  FastAPI    │────▶│  PostgreSQL │
│  (Browser)  │     │    API      │     │  + pgvector │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  Redis   │ │  Qdrant  │ │  Vault   │
        │  Cache   │ │ Vectors  │ │  Secrets │
        └──────────┘ └──────────┘ └──────────┘
```
