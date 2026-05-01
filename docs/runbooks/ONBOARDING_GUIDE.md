# ONBOARDING_GUIDE.md — LexCore + LexRadar Developer Onboarding

> **Build System:** Unified Build System v2 | **Chunk:** C10 — Runbooks | **Horde:** HORDE-LOG

---

## Overview

This guide provides step-by-step instructions for new developers joining the LexCore + LexRadar project. It covers local development setup, architecture overview, and contribution guidelines.

**Prerequisites:** Python 3.12, Node 20, Docker, AWS CLI, kubectl  
**Onboarding Duration:** 2-3 days (self-paced)  

---

## Day 1: Environment Setup

### 1. Clone Repository

```bash
git clone git@github.com:lexcore/lexcore.git
cd lexcore
```

### 2. Install Dependencies

**Backend (Python):**
```bash
cd api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**Frontend (Node):**
```bash
cd frontend
npm install
```

### 3. Start Local Stack

```bash
# From project root
docker-compose up -d

# Wait for services to be ready
./scripts/wait-for-services.sh
```

### 4. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit with your values
# - DATABASE_URL (use local Docker)
# - REDIS_URL (use local Docker)
# - OPENAI_API_KEY (your key)
# - CLERK_SECRET_KEY (from Clerk dashboard)
```

### 5. Run Migrations

```bash
cd api
alembic upgrade head
```

### 6. Verify Setup

```bash
# Backend health check
curl http://localhost:8000/health

# Frontend health check
curl http://localhost:3000/api/health
```

---

## Day 2: Architecture Deep Dive

### Read Key Documentation

**In this order:**
1. `docs/spec/PRODUCT_SPEC.md` — What we're building
2. `docs/architecture/SYSTEM_LAYERS.md` — System architecture
3. `docs/services/SERVICE_CATALOG.md` — Service layer
4. `docs/api/API_SPEC.md` — API endpoints
5. `docs/frontend/SCREEN_MAP.md` — Frontend screens

### Review Codebase Structure

```
lexcore/
├── api/                    # FastAPI backend
│   ├── app/
│   │   ├── core/          # Config, security
│   │   ├── models/        # SQLAlchemy models
│   │   ├── repositories/  # Data access layer
│   │   ├── services/      # Business logic
│   │   ├── agents/        # AI agents
│   │   └── workers/       # Celery tasks
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   └── main.py
│
├── frontend/              # Next.js frontend
│   ├── src/
│   │   ├── app/          # App Router pages
│   │   ├── components/   # React components
│   │   ├── lib/          # Utilities
│   │   └── hooks/        # Custom hooks
│   └── tests/
│
├── schema/               # Database schema
│   ├── migrations/
│   └── erd.md
│
└── docs/                 # Documentation
```

### Run Local Development

**Backend:**
```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

**Workers:**
```bash
celery -A app.workers worker -Q ingestion,patent -l info
```

---

## Day 3: First Contribution

### 1. Pick a Good First Issue

Check GitHub Issues labeled `good first issue`

### 2. Create Feature Branch

```bash
git checkout -b feature/my-feature
```

### 3. Make Changes

- Write code
- Add tests
- Update documentation

### 4. Run Tests

```bash
# Backend
pytest api/tests/ -v --cov

# Frontend
npm test

# E2E
npx playwright test
```

### 5. Commit and Push

```bash
git add .
git commit -m "feat: add my feature"
git push origin feature/my-feature
```

### 6. Open Pull Request

- Fill out PR template
- Link to issue
- Request review

---

## Development Guidelines

### Code Style

**Python:** Black, Ruff, mypy  
**TypeScript:** ESLint, Prettier  
**Commit:** Conventional Commits (feat, fix, docs, refactor, test)

### Testing

- Unit tests for all business logic
- Integration tests for service boundaries
- E2E tests for critical paths
- Coverage ≥ 80%

### Security

- No secrets in code
- Use environment variables
- Validate all inputs
- Follow RLS policies
- No agent-to-agent imports (AGT-G1)

### Documentation

- Docstrings for all functions
- Update README for new features
- Add inline comments for complex logic
- Keep architecture docs in sync

---

## Troubleshooting

### Database Connection Failed

```bash
# Check Docker containers
docker-compose ps

# Restart stack
docker-compose restart

# Check logs
docker-compose logs postgres
```

### Frontend Build Errors

```bash
# Clear Next.js cache
rm -rf .next
npm run build
```

### Worker Not Processing Tasks

```bash
# Check worker logs
celery -A app.workers inspect active

# Restart worker
pkill -f celery
celery -A app.workers worker -Q ingestion
```

---

## Resources

**Internal:**
- Slack: #lexcore-dev
- Confluence: LexCore Knowledge Base
- Jira: LexCore Project Board

**External:**
- FastAPI Docs: https://fastapi.tiangolo.com
- Next.js Docs: https://nextjs.org/docs
- Celery Docs: https://docs.celeryq.dev

---

## Questions?

**Contact:**
- Engineering Lead: eng-lead@lexcore.com
- DevOps: devops@lexcore.com
- On-call: on-call@lexcore.com (PagerDuty)

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-30 | Initial onboarding guide | C10 Runbooks definition |
