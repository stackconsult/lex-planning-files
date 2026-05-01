# CICD_PIPELINES.md — LexCore + LexRadar CI/CD Pipelines

> **Build System:** Unified Build System v2 | **Chunk:** C07 — DevOps + CI/CD | **Horde:** HORDE-DEVOPS

---

## Overview

Continuous Integration and Deployment (CI/CD) is managed via GitHub Actions. Three primary pipelines:
1. **Build & Test** — PR validation, unit tests, integration tests, security scans
2. **Deploy** — Build images, push to ECR, deploy to EKS (staging/production)
3. **Release** — Tag, changelog, rollback artifacts, post-deployment verification

**Source Control:** GitHub (monorepo)  
**CI/CD Platform:** GitHub Actions  
**Artifact Registry:** AWS ECR  
**Deployment:** Helm charts via `helm upgrade` to EKS  
**GitOps:** ArgoCD (future consideration)

---

## Pipeline Architecture

```
Developer pushes to branch
  → PR opened
    → [Build & Test Pipeline]
      → Lint, type check, unit tests
      → Security scan (Trivy, Bandit, npm audit)
      → Integration tests (Docker Compose)
      → Schema validation
      → Coverage report (> 80%)
      → Post PR comment with results
  → PR merged to main
    → [Build & Test Pipeline] (re-run on main)
    → [Deploy Pipeline — Staging]
      → Build API, Frontend, Worker images
      → Trivy container scan + SBOM
      → Push to ECR with SHA tag
      → Deploy to staging EKS via Helm
      → Smoke tests
      → HORDE-AUDIT quick gate (L1 + L3)
  → Tag release (vX.Y.Z)
    → [Deploy Pipeline — Production]
      → Promote staging image SHA to prod tag
      → Blue-green deployment (Helm)
      → Canary rollout (10% → 50% → 100%)
      → Smoke tests + synthetic monitoring
      → Post-deployment verification
      → Notify on success / alert on failure
      → Automatic rollback on failure
```

---

## Workflow 1: Build & Test

### Triggers
- `push` to any branch (excluding `main` for deploy steps)
- `pull_request` to `main`
- `workflow_dispatch` (manual)

### Jobs

| Job | Runner | Purpose | Timeout |
|-----|--------|---------|---------|
| `lint-and-typecheck` | ubuntu-latest | Black, ruff, mypy, ESLint, tsc | 5 min |
| `unit-tests-api` | ubuntu-latest | Pytest (api/) with coverage | 10 min |
| `unit-tests-frontend` | ubuntu-latest | Jest (frontend/) with coverage | 10 min |
| `integration-tests` | ubuntu-latest | Docker Compose full stack test | 15 min |
| `security-scan` | ubuntu-latest | Trivy fs, Bandit, npm audit, truffleHog | 10 min |
| `schema-validation` | ubuntu-latest | Alembic dry-run, SQL lint | 5 min |
| `coverage-report` | ubuntu-latest | Combine coverage, upload to Codecov | 2 min |

### Integration Test Job

```yaml
integration-tests:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    
    - name: Start services
      run: docker compose -f docker-compose.test.yml up -d --wait
      
    - name: Run API tests
      run: docker compose -f docker-compose.test.yml exec api pytest tests/integration/
      
    - name: Run frontend tests
      run: docker compose -f docker-compose.test.yml exec frontend npm run test:ci
      
    - name: Run E2E tests
      run: docker compose -f docker-compose.test.yml exec playwright npx playwright test
      
    - name: Cleanup
      if: always()
      run: docker compose -f docker-compose.test.yml down -v
```

### Security Scan Job

```yaml
security-scan:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    
    - name: Trivy filesystem scan
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        severity: 'HIGH,CRITICAL'
        exit-code: '1'
        
    - name: Bandit (Python)
      run: bandit -r api/ -f json -o bandit-report.json || true
      
    - name: npm audit (Frontend)
      run: cd frontend && npm audit --audit-level=high
      
    - name: Secret scan
      run: truffleHog git file://. --since-commit HEAD --only-verified --fail
      
    - name: Dependency review
      uses: actions/dependency-review-action@v4
```

---

## Workflow 2: Deploy to Staging

### Triggers
- `push` to `main` (after PR merge)
- `workflow_dispatch` (manual)

### Jobs

| Job | Runner | Purpose | Timeout |
|-----|--------|---------|---------|
| `build-images` | ubuntu-latest | Build API, Frontend, Worker images | 15 min |
| `scan-images` | ubuntu-latest | Trivy container scan, generate SBOM | 10 min |
| `push-to-ecr` | ubuntu-latest | Tag with SHA, push to ECR | 5 min |
| `deploy-staging` | ubuntu-latest | Helm upgrade to staging namespace | 10 min |
| `smoke-tests` | ubuntu-latest | Verify staging endpoints, health checks | 5 min |
| `audit-gate` | ubuntu-latest | HORDE-AUDIT quick gate (L1 + L3) | 15 min |

### Build Images Job

```yaml
build-images:
  runs-on: ubuntu-latest
  strategy:
    matrix:
      image: [api, frontend, worker]
  steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
      
    - name: Build image
      uses: docker/build-push-action@v5
      with:
        context: .
        file: docker/${{ matrix.image }}/Dockerfile
        tags: |
          lexcore-${{ matrix.image }}:${{ github.sha }}
          lexcore-${{ matrix.image }}:latest
        cache-from: type=gha
        cache-to: type=gha,mode=max
        push: false
        load: true
        
    - name: Save image artifact
      run: docker save lexcore-${{ matrix.image }}:${{ github.sha }} | gzip > ${{ matrix.image }}.tar.gz
      
    - uses: actions/upload-artifact@v4
      with:
        name: ${{ matrix.image }}-image
        path: ${{ matrix.image }}.tar.gz
```

### Scan Images Job

```yaml
scan-images:
  needs: build-images
  runs-on: ubuntu-latest
  strategy:
    matrix:
      image: [api, frontend, worker]
  steps:
    - name: Download image artifact
      uses: actions/download-artifact@v4
      with:
        name: ${{ matrix.image }}-image
        
    - name: Load image
      run: docker load < ${{ matrix.image }}.tar.gz
      
    - name: Trivy image scan
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'lexcore-${{ matrix.image }}:${{ github.sha }}'
        format: 'sarif'
        output: 'trivy-${{ matrix.image }}.sarif'
        severity: 'HIGH,CRITICAL'
        exit-code: '1'
        
    - name: Generate SBOM
      uses: anchore/sbom-action@v0
      with:
        image: 'lexcore-${{ matrix.image }}:${{ github.sha }}'
        format: 'spdx-json'
        output-file: 'sbom-${{ matrix.image }}.spdx.json'
        
    - uses: actions/upload-artifact@v4
      with:
        name: scan-results-${{ matrix.image }}
        path: |
          trivy-${{ matrix.image }}.sarif
          sbom-${{ matrix.image }}.spdx.json
```

### Deploy to Staging Job

```yaml
deploy-staging:
  needs: [scan-images, push-to-ecr]
  runs-on: ubuntu-latest
  environment: staging
  steps:
    - uses: actions/checkout@v4
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
        
    - name: Update kubeconfig
      run: aws eks update-kubeconfig --region us-east-1 --name staging-lexcore
      
    - name: Deploy via Helm
      run: |
        helm upgrade --install lexcore ./helm/lexcore \
          --namespace staging \
          --set image.tag=${{ github.sha }} \
          --set environment=staging \
          --wait \
          --timeout 10m
          
    - name: Verify deployment
      run: |
        kubectl rollout status deployment/lexcore-api -n staging --timeout=5m
        kubectl rollout status deployment/lexcore-frontend -n staging --timeout=5m
```

---

## Workflow 3: Deploy to Production

### Triggers
- `release` published (GitHub Release)
- `workflow_dispatch` (manual, requires approval)

### Jobs

| Job | Runner | Purpose | Timeout |
|-----|--------|---------|---------|
| `promote-images` | ubuntu-latest | Re-tag staging SHA as prod, push to ECR | 5 min |
| `blue-green-deploy` | ubuntu-latest | Deploy to blue environment, verify | 10 min |
| `canary-rollout` | ubuntu-latest | 10% → 50% → 100% traffic shift | 20 min |
| `smoke-tests` | ubuntu-latest | Synthetic monitoring, critical path tests | 10 min |
| `verify-and-switch` | ubuntu-latest | Promote green, drain blue | 5 min |
| `notify` | ubuntu-latest | Slack notification, update status page | 2 min |
| `rollback-on-failure` | ubuntu-latest | Automatic rollback if any job fails | — |

### Canary Rollout Job

```yaml
canary-rollout:
  needs: blue-green-deploy
  runs-on: ubuntu-latest
  steps:
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
        
    - name: Update kubeconfig
      run: aws eks update-kubeconfig --region us-east-1 --name production-lexcore
      
    - name: Phase 1 — 10% traffic
      run: |
        kubectl patch service lexcore-api -p '{"spec":{"selector":{"version":"green"}}}'
        kubectl patch virtualservice lexcore-api -p '{"spec":{"http":[{"route":[{"destination":{"host":"lexcore-api-blue","weight":90}},{"destination":{"host":"lexcore-api-green","weight":10}}]}]}'
      
    - name: Wait and monitor (5 min)
      run: sleep 300
      
    - name: Phase 2 — 50% traffic
      run: |
        kubectl patch virtualservice lexcore-api -p '{"spec":{"http":[{"route":[{"destination":{"host":"lexcore-api-blue","weight":50}},{"destination":{"host":"lexcore-api-green","weight":50}}]}]}'
      
    - name: Wait and monitor (5 min)
      run: sleep 300
      
    - name: Phase 3 — 100% traffic
      run: |
        kubectl patch virtualservice lexcore-api -p '{"spec":{"http":[{"route":[{"destination":{"host":"lexcore-api-green","weight":100}}]}]}'
        kubectl patch service lexcore-api -p '{"spec":{"selector":{"version":"green"}}}'
```

---

## Helm Chart Structure

```
helm/
  lexcore/
    Chart.yaml
    values.yaml
    values-staging.yaml
    values-production.yaml
    templates/
      _helpers.tpl
      deployment-api.yaml
      deployment-frontend.yaml
      deployment-worker.yaml
      service.yaml
      ingress.yaml
      hpa.yaml                      # Horizontal Pod Autoscaler
      pdb.yaml                      # Pod Disruption Budget
      serviceaccount.yaml
      externalsecret.yaml
      configmap.yaml
```

### Key Helm Values

```yaml
# helm/lexcore/values.yaml (excerpt)
image:
  repository: "123456789012.dkr.ecr.us-east-1.amazonaws.com/lexcore"
  tag: "latest"
  pullPolicy: IfNotPresent

replicaCount:
  api: 3
  frontend: 3
  worker: 2

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

resources:
  api:
    requests:
      memory: "512Mi"
      cpu: "250m"
    limits:
      memory: "2Gi"
      cpu: "2000m"
  frontend:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "1Gi"
      cpu: "1000m"
  worker:
    requests:
      memory: "512Mi"
      cpu: "500m"
    limits:
      memory: "2Gi"
      cpu: "2000m"

pdb:
  enabled: true
  minAvailable: 1

ingress:
  enabled: true
  className: alb
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTPS":443}]'
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-east-1:123456789012:certificate/...
```

---

## Environment Promotion Strategy

| Stage | Trigger | Tests | Gate |
|-------|---------|-------|------|
| **Dev** | Push to feature branch | Unit tests, lint | PR approval (1 reviewer) |
| **Staging** | Merge to `main` | Integration, E2E, security scan | Automated smoke tests |
| **Canary** | Release tag | Synthetic monitoring | Error rate < 0.1%, latency P95 < 500ms |
| **Production** | Canary success | Full regression | Manual approval for major releases |

---

## Rollback Procedure

### Automatic Rollback Conditions
- Error rate > 1% for 2 minutes
- P95 latency > 2× baseline for 5 minutes
- Any critical health check fails
- HORDE-AUDIT gate BLOCKED

### Rollback Command

```bash
# Rollback to previous Helm release
helm rollback lexcore 0 --namespace production

# Or rollback to specific revision
helm rollback lexcore 42 --namespace production

# Verify rollback
kubectl rollout status deployment/lexcore-api -n production
```

### Rollback Checklist
1. Identify failure cause from logs/metrics
2. Revert PR if code change caused failure
3. Verify previous version health
4. Post-mortem within 24 hours

---

## Required GitHub Secrets

| Secret | Description | Used By |
|--------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS IAM access key | Deploy workflows |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key | Deploy workflows |
| `ECR_REGISTRY` | ECR registry URI | Build, deploy |
| `KUBECONFIG_STAGING` | Staging kubeconfig | Deploy staging |
| `KUBECONFIG_PRODUCTION` | Production kubeconfig | Deploy production |
| `SLACK_WEBHOOK_URL` | Slack notification | All deploy workflows |
| `CODECOV_TOKEN` | Codecov upload token | Build & Test |
| `SNYK_TOKEN` | Snyk vulnerability scan | Security scan |
| `GITHUB_TOKEN` | Auto-generated, PR comments | Build & Test |

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-30 | Initial CI/CD pipeline specification | C07 DevOps definition |
