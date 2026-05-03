---
name: lexcore-lexradar-build-setup
description: Build setup guide for LexCore + LexRadar based on team skills matrix. Use when setting up development environment, onboarding new team members, or configuring build pipeline according to required skill levels for backend, frontend, DevOps, ML/AI, security, data engineering, blockchain, and legal domain expertise.
license: MIT
metadata:
  author: LexCore + LexRadar Architecture Team
  version: "2.0.0"
  framework: Microsoft Skills Format v2.0
  source: microsoft/skills marketplace
---

# Build Setup Guide — LexCore + LexRadar

> **Date:** 2026-05-02  
> **Purpose:** Execute build setup based on updated skills requirements  
> **Scope:** Full system (L0-L7)  
> **Format:** Based on Microsoft Skills Format v2.0 from microsoft/skills marketplace

## Quick Start

This guide provides build setup instructions aligned with the team skills matrix. Follow these steps to set up the development environment according to the required skill levels.

## Prerequisites

Based on the skills matrix, ensure the following prerequisites are installed:

### For Backend Engineers (Python 3.12+)
- Python 3.12+ (required by pyproject.toml)
- pip 25.1.1+
- virtualenv or venv
- Docker 29.4.1+ (for local development stack)

### For Frontend Engineers (Next.js 14+)
- Node.js 18+ (LTS recommended)
- npm or pnpm or yarn
- TypeScript 5+

### For DevOps Engineers (Kubernetes, AWS, Terraform)
- Docker 29.4.1+
- Docker Compose (or `docker compose` plugin)
- kubectl (for Kubernetes deployments)
- Terraform 1.5+
- AWS CLI (for AWS deployments)

### For All Engineers
- Git 2.30+
- Make (for Makefile commands)
- curl (for API testing)

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/stackconsult/lex-planning-files.git
cd "lex planning files"
```

### 2. Backend Setup (Python 3.12+)

#### Option A: Using Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv backend/venv

# Activate virtual environment
source backend/venv/bin/activate  # On Linux/Mac
# or
backend\venv\Scripts\activate  # On Windows

# Install dependencies
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

#### Option B: Using UV (Faster)

```bash
# Install UV (Python package installer)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies with UV
cd backend
uv pip install -r requirements.txt
```

### 3. Frontend Setup (Next.js 14+)

```bash
cd frontend
npm install
# or
pnpm install
# or
yarn install
```

### 4. Local Development Stack (Docker Compose)

Start the required services:

```bash
# Start all services
make dev
# or
docker compose up -d

# Start only database and dependencies
make db-up
# or
docker compose up -d postgres redis qdrant vault

# Start with monitoring
docker compose --profile monitoring up -d
```

### 5. Database Migrations

```bash
# Run Alembic migrations
make migrate
# or
cd backend && alembic upgrade head

# Generate new migration
make migrate-gen msg="description"
# or
cd backend && alembic revision --autogenerate -m "description"

# Rollback migration
make migrate-down
# or
cd backend && alembic downgrade -1
```

## Build Commands

### Backend

```bash
# Run tests
make test
make test-unit
make test-int
make test-cov

# Code quality
make lint
make lint-fix
make format
make typecheck

# Development server
cd backend && uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
# Development server
cd frontend && npm run dev

# Build for production
cd frontend && npm run build

# Run tests
cd frontend && npm test

# Lint
cd frontend && npm run lint
```

### Infrastructure

```bash
# Terraform plan
cd infra/terraform && terraform plan

# Terraform apply
cd infra/terraform && terraform apply

# Kubernetes apply
cd infra/k8s && kubectl apply -f .

# Kubernetes status
kubectl get pods -n lexcore
```

## Skill-Specific Setup

### For Backend Engineers (Intermediate+)

**Required Skills:**
- Python 3.12+ (Advanced)
- FastAPI 0.110+ (Advanced)
- async/await (Advanced)
- PostgreSQL (Advanced)
- pgvector (Intermediate)
- Redis (Intermediate)
- Celery (Advanced)

**Setup Steps:**
1. Complete backend installation (Step 2)
2. Review `backend/src/api/main.py` for FastAPI structure
3. Review `backend/src/core/db_session.py` for RLS implementation
4. Review `backend/src/api/services/` for service layer patterns
5. Run `make typecheck` to verify type hints
6. Run `make test` to verify tests pass

**Learning Resources:**
- FastAPI: https://fastapi.tiangolo.com/tutorial/
- PostgreSQL: https://www.postgresql.org/docs/
- pgvector: https://github.com/pgvector/pgvector
- Celery: https://docs.celeryproject.org/

### For Frontend Engineers (Intermediate+)

**Required Skills:**
- Next.js 14+ (Advanced)
- TypeScript (Advanced)
- React (Advanced)
- Tailwind CSS (Intermediate)
- React Query (Intermediate)
- Clerk (Intermediate)

**Setup Steps:**
1. Complete frontend installation (Step 3)
2. Review `frontend/` directory structure
3. Review Clerk integration documentation
4. Run `npm run dev` to start development server
5. Review component library (Shadcn/UI)

**Learning Resources:**
- Next.js: https://nextjs.org/docs
- TypeScript: https://www.typescriptlang.org/docs/
- React Query: https://tanstack.com/query/latest
- Tailwind: https://tailwindcss.com/docs
- Clerk: https://clerk.com/docs

### For DevOps Engineers (Advanced)

**Required Skills:**
- Kubernetes (EKS) (Advanced)
- Terraform (Advanced)
- Docker (Intermediate)
- AWS (Advanced)
- CI/CD (Advanced)
- Prometheus (Intermediate)
- Grafana (Intermediate)

**Setup Steps:**
1. Complete local development stack setup (Step 4)
2. Review `docker-compose.yml` for service configuration
3. Review `infra/terraform/` for infrastructure as code
4. Review `infra/k8s/` for Kubernetes manifests
5. Start monitoring stack: `docker compose --profile monitoring up -d`
6. Access Grafana at http://localhost:3000 (admin/admin)

**Learning Resources:**
- Kubernetes: https://kubernetes.io/docs/
- Terraform: https://developer.hashicorp.com/terraform/docs
- AWS: https://docs.aws.amazon.com/
- Prometheus: https://prometheus.io/docs/
- Grafana: https://grafana.com/docs/

### For ML/AI Engineers (Intermediate+)

**Required Skills:**
- Python (Advanced)
- OpenAI API (Intermediate)
- Embeddings (Intermediate)
- Vector databases (Intermediate)
- LLM integration (Intermediate)
- Prompt engineering (Intermediate)
- Qdrant (Intermediate)

**Setup Steps:**
1. Complete backend installation (Step 2)
2. Review embedding integration in ingestion workers
3. Review Qdrant configuration in `docker-compose.yml`
4. Test vector search via MCP tools
5. Review prompt templates for disclosure generation

**Learning Resources:**
- OpenAI API: https://platform.openai.com/docs/
- Embeddings: https://platform.openai.com/docs/guides/embeddings
- Qdrant: https://qdrant.tech/documentation/
- Vector Search: https://www.pinecone.io/learn/vector-database/

### For Security Engineers (Intermediate+)

**Required Skills:**
- JWT (Intermediate)
- OAuth 2.0 (Intermediate)
- SAML (Intermediate)
- Encryption (Intermediate)
- PostgreSQL RLS (Intermediate)
- BYOK (Intermediate)
- Compliance (Intermediate)

**Setup Steps:**
1. Review authentication middleware in `backend/src/api/main.py`
2. Review RLS policies in `backend/migrations/002_rls_policies.sql`
3. Review Vault configuration in `docker-compose.yml`
4. Review JWT implementation in `backend/src/core/`
5. Test tenant isolation across layers

**Learning Resources:**
- JWT: https://jwt.io/introduction
- OAuth 2.0: https://oauth.net/2/
- PostgreSQL RLS: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- Vault: https://developer.hashicorp.com/vault/docs

### For Data Engineers (Intermediate+)

**Required Skills:**
- PostgreSQL (Advanced)
- ETL (Intermediate)
- Data modeling (Intermediate)
- Indexing (Intermediate)
- Migration management (Intermediate)

**Setup Steps:**
1. Review database schema in `docs/03-data/ERD.md`
2. Review migrations in `backend/migrations/`
3. Review connection pool config in `docs/03-data/CONNECTION_POOL_CONFIG.md`
4. Run `make migrate` to apply migrations
5. Review indexing strategy in `backend/migrations/003_pgvector_indexes.sql`

**Learning Resources:**
- PostgreSQL: https://www.postgresql.org/docs/
- Alembic: https://alembic.sqlalchemy.org/
- Data Modeling: https://www.databasestar.com/data-modeling/

### For Blockchain Engineers (Intermediate+)

**Required Skills:**
- Polygon (Intermediate)
- Smart contracts (Intermediate)
- Web3.py (Intermediate)
- Cryptography (Intermediate)
- IP anchoring (Intermediate)

**Setup Steps:**
1. Review blockchain integration in `backend/src/`
2. Review Polygon configuration
3. Test IP anchoring flow
4. Review smart contract deployment
5. Verify blockchain anchoring with BAM Genesis Hash

**Learning Resources:**
- Polygon: https://docs.polygon.technology/
- Web3.py: https://web3py.readthedocs.io/
- Smart Contracts: https://docs.soliditylang.org/

### For Legal Domain Experts (Intermediate+)

**Required Skills:**
- Patent law (Intermediate)
- Legal document parsing (Intermediate)
- Jurisdiction mapping (Intermediate)
- Citation analysis (Intermediate)

**Setup Steps:**
1. Review legal source connectors in L0
2. Review document parsing in ingestion workers
3. Review jurisdiction mapping in database schema
4. Review citation analysis in LexRadar agents
5. Test legal document ingestion flow

**Learning Resources:**
- Patent Law: Internal training materials
- Legal Document Parsing: Documentation in `docs/`

## Verification Steps

### Backend Verification

```bash
# Check Python version
python3 --version  # Should be 3.12+

# Check dependencies
cd backend
pip list

# Run type checker
make typecheck

# Run linter
make lint

# Run tests
make test

# Start development server
uvicorn src.api.main:app --reload
```

### Frontend Verification

```bash
# Check Node.js version
node --version  # Should be 18+

# Check dependencies
cd frontend
npm list

# Run linter
npm run lint

# Start development server
npm run dev
```

### Infrastructure Verification

```bash
# Check Docker
docker --version  # Should be 29.4.1+

# Check Docker Compose
docker compose version

# Start services
docker compose up -d postgres redis qdrant vault

# Check services
docker compose ps

# Check logs
docker compose logs postgres
docker compose logs redis
docker compose logs qdrant
docker compose logs vault
```

## Troubleshooting

### Python Virtual Environment Issues

**Problem:** `ensurepip is not available`

**Solution:**
```bash
# Install python3-venv
sudo apt install python3.13-venv  # On Debian/Ubuntu
# or
brew install python3-venv  # On macOS

# Recreate virtual environment
python3 -m venv backend/venv
```

### Docker Permission Issues

**Problem:** `permission denied while trying to connect to the docker API`

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again
# or
newgrp docker
```

### PostgreSQL Connection Issues

**Problem:** Cannot connect to PostgreSQL

**Solution:**
```bash
# Check PostgreSQL container status
docker compose ps postgres

# Check PostgreSQL logs
docker compose logs postgres

# Restart PostgreSQL
docker compose restart postgres
```

### Redis Connection Issues

**Problem:** Cannot connect to Redis

**Solution:**
```bash
# Check Redis container status
docker compose ps redis

# Check Redis logs
docker compose logs redis

# Test Redis connection
docker compose exec redis redis-cli ping
```

### Qdrant Connection Issues

**Problem:** Cannot connect to Qdrant

**Solution:**
```bash
# Check Qdrant container status
docker compose ps qdrant

# Check Qdrant logs
docker compose logs qdrant

# Test Qdrant connection
curl http://localhost:6333/healthz
```

## Next Steps

After completing the build setup:

1. **For Backend Engineers:** Start implementing features following the service layer pattern
2. **For Frontend Engineers:** Start building UI components using Shadcn/UI
3. **For DevOps Engineers:** Configure CI/CD pipeline in GitHub Actions
4. **For ML/AI Engineers:** Start optimizing embedding strategies
5. **For Security Engineers:** Implement additional security controls
6. **For Data Engineers:** Optimize database queries and indexes
7. **For Blockchain Engineers:** Test IP anchoring flow end-to-end
8. **For Legal Domain Experts:** Validate legal document parsing accuracy

## Reference Documents

- `docs/architecture/TEAM_SKILLS_MATRIX.md` — Required skills for each role
- `docs/architecture/SYSTEM_LAYERS.md` — Architecture overview
- `docs/architecture/ADR/` — Architecture decision records
- `docs/03-data/ERD.md` — Database schema
- `docs/03-data/CONNECTION_POOL_CONFIG.md` — Database configuration
- `docs/api/API_SPEC.md` — API specification
- `README.md` — Project overview
- `LOCAL_DEVELOPMENT.md` — Local development guide

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review reference documents
3. Check GitHub Issues: https://github.com/stackconsult/lex-planning-files/issues
4. Contact the architecture team
