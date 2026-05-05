# CI/CD Pipeline Governance

> **Chunk:** C02 — Phase 0 Foundation  
> **Horde:** HORDE-INFRA  
> **Status:** PRODUCTION_READY

## Overview

GitHub Actions workflows for CI/CD automation with security scanning and staged deployments.

## Pipelines

### CI (ci.yml)
- Trigger: Push/PR
- Stages: Code quality, secret scan, dependency audit, tests, security scan, build
- Gate: All stages pass before merge

### Deploy Dev (deploy-dev.yml)
- Trigger: Push to main
- Stages: DB migration, K8s deploy, smoke test
- Environment: lexcore-dev

### Deploy Prod (deploy-prod.yml)
- Trigger: Manual approval
- Stages: DB migration, canary (10% → 100%), fitness check, promote/rollback
- Environment: lexcore-prod

## Security

- GitHub Secrets for credentials
- pip-audit, npm audit, trivy scanning
- gitleaks, bandit, semgrep
- Zero HIGH/CRITICAL CVEs required

## Quality Gates

- Code quality: black, isort, flake8, mypy strict
- Coverage: 80% minimum
- Tests: 100% pass rate
- Security: Zero secrets, zero HIGH CVEs

## Deployment Strategy

- Dev: Automatic rolling update
- Prod: Manual canary with fitness score (0.90 min)
- Auto-rollback on error rate > 1%

## Governance

- Never overwrite: Additive changes only
- Always append: New stages/jobs added
- Track changes: Git commits with format `ci-cd: [Team H] Chunk {N}: {description}`
- No bloat: Remove unused jobs

## Change History

| Date | Change | Chunk | Team |
|------|--------|-------|------|
| 2026-05-05 | Governance documentation added | Chunk 3 | HORDE-INFRA |
