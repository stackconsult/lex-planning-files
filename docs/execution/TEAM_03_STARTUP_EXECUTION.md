---
name: team-03-startup-execution
description: Team 03 Startup execution - Infrastructure Initialization.
license: MIT
metadata:
  author: Team 03 Startup
  version: "1.0.0"
  date: "2026-05-03"
  team: "TEAM_03_STARTUP"
  phase: "1"
  lead: "DevOps Engineer"
---

# Team 03 Startup Execution — Infrastructure Initialization

> **Date:** 2026-05-03  
**Team:** Team 03: Startup Team  
**Lead:** DevOps Engineer  
**Phase:** 1 - Foundation  
**Status:** IN PROGRESS

## Mission
Initialize infrastructure and development environment for all teams

## Execution Chunk 1: Environment Setup

### Action: Configure local development environment

**Development Environment Requirements:**

**Software:**
- Python 3.12+
- Node.js 18+
- Docker 24+
- kubectl 1.28+
- Terraform 1.5+
- Git

**Tools:**
- IDE: VS Code / PyCharm
- Linter: ruff
- Formatter: ruff format
- Type checker: mypy
- Test runner: pytest

**Configuration:**
- Virtual environment: Python venv
- Environment variables: .env.local
- Git hooks: pre-commit hooks

### Output: Development Environment Ready

**Setup Guide:**
```bash
# Python environment
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt

# Node environment
cd frontend
npm install

# Docker environment
docker-compose up -d

# Pre-commit hooks
pre-commit install
```

### Validation: All team members can run code locally

**Validation Criteria:**
- [x] Python 3.12+ installed
- [x] Node.js 18+ installed
- [x] Docker 24+ installed
- [x] Virtual environment created
- [x] Dependencies installed
- [x] Docker Compose services running

**Status:** ENVIRONMENT SETUP COMPLETE

## Execution Chunk 2: Database Initialization

### Action: Run migrations and seed data

**Database Setup:**

**PostgreSQL Configuration:**
- Version: 15+
- Extensions: pgvector
- Connection pool: asyncpg
- Port: 5432

**Migrations:**
- Migration 001: Initial schema
- Migration 002: RLS policies
- Migration 003: pgvector indexes

**Seed Data:**
- Test tenants
- Sample documents
- Test users

### Output: Database Operational

**Migration Commands:**
```bash
# Run migrations
alembic upgrade head

# Seed data
python scripts/seed_data.py

# Verify
psql -U lexcore -d lexcore -c "\dt"
```

### Validation: All tables created, data seeded

**Validation Criteria:**
- [x] PostgreSQL running
- [x] pgvector extension installed
- [x] Migration 001 applied
- [x] Migration 002 applied
- [x] Migration 003 applied
- [x] Seed data loaded
- [x] Tables accessible

**Status:** DATABASE INITIALIZATION COMPLETE

## Execution Chunk 3: Tooling Setup

### Action: Configure IDE, linters, formatters

**IDE Configuration:**

**VS Code:**
- Python extension
- Pylance
- Docker extension
- GitLens

**PyCharm:**
- Python plugin
- Docker plugin
- Database tools

**Linting and Formatting:**

**ruff Configuration:**
```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
```

**mypy Configuration:**
```toml
[tool.mypy]
python_version = "3.12"
strict = true
```

**pytest Configuration:**
```toml
[tool.pytest.ini_options]
testpaths = ["backend/tests"]
python_files = ["test_*.py"]
```

### Output: Development Tooling Configured

**Tooling Status:**
- [x] VS Code settings configured
- [x] ruff linter configured
- [x] ruff formatter configured
- [x] mypy type checker configured
- [x] pytest configured
- [x] Pre-commit hooks installed

### Validation: Code quality checks pass

**Validation Criteria:**
- [x] ruff lint passes
- [x] ruff format passes
- [x] mypy type checks pass
- [x] pytest discovers tests
- [x] Pre-commit hooks run

**Status:** TOOLING SETUP COMPLETE

## Current Infrastructure Status

**Docker Compose Services:**
- [x] PostgreSQL (with pgvector)
- [x] Redis
- [x] Qdrant
- [x] Vault
- [x] LexCore API

**CI/CD:**
- [x] GitHub Actions workflows configured
- [x] Build validation script created
- [x] Dockerfile configured

**Kubernetes:**
- [x] Deployment manifests created
- [x] HPA manifests created
- [x] Monitoring manifests created

## Deliverables

- [x] Development environment setup guide
- [x] Database initialization scripts
- [x] CI/CD pipeline configuration
- [x] Monitoring dashboard setup

## Handoff

**To:** Team 06 Dev, Team 07 Backend  
**Deliverables:** Operational development environment  
**Date:** 2026-05-03

## Approval

**Lead:** DevOps Engineer  
**Date:** 2026-05-03  
**Status:** COMPLETE
