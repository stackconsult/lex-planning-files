# DEPLOYMENT_RUNBOOK.md — LexCore + LexRadar Deployment Procedures

> **Build System:** Unified Build System v2 | **Chunk:** C10 — Runbooks | **Horde:** HORDE-LOG

---

## Overview

This runbook provides step-by-step procedures for deploying LexCore + LexRadar to staging and production environments. All deployments follow the CI/CD pipeline defined in C07.

**Deployment Method:** GitHub Actions → Helm → EKS  
**Environments:** dev, staging, production  
**Strategy:** Blue-green deployment with canary rollout  

---

## Prerequisites

**Before deploying to any environment, verify:**
- [ ] All tests pass (unit, integration, E2E)
- [ ] Code coverage ≥ 80%
- [ ] Security scans pass (Trivy, Bandit, npm audit)
- [ ] HORDE-AUDIT gate is PASS
- [ ] Release notes documented
- [ ] Backward compatibility verified (for breaking changes)
- [ ] Rollback plan documented

---

## Deploy to Staging

### Trigger

**Automatic:** Merge to `main` branch  
**Manual:** GitHub Actions → Deploy to Staging (workflow_dispatch)

### Steps

1. **Build and Scan Images**
   ```bash
   # Verify images built successfully
   aws ecr describe-images --repository-name lexcore-api --image-ids imageTag=$SHA
   aws ecr describe-images --repository-name lexcore-frontend --image-ids imageTag=$SHA
   aws ecr describe-images --repository-name lexcore-worker --image-ids imageTag=$SHA
   ```

2. **Verify Image Scans**
   ```bash
   # Check Trivy scan results
   aws ecr describe-image-scan-findings --repository-name lexcore-api --image-id imageTag=$SHA
   # Verify no HIGH/CRITICAL vulnerabilities
   ```

3. **Deploy via Helm**
   ```bash
   # Update kubeconfig
   aws eks update-kubeconfig --region us-east-1 --name staging-lexcore
   
   # Deploy
   helm upgrade --install lexcore ./helm/lexcore \
     --namespace staging \
     --set image.tag=$SHA \
     --set environment=staging \
     --wait \
     --timeout 10m
   ```

4. **Verify Deployment**
   ```bash
   # Check rollout status
   kubectl rollout status deployment/lexcore-api -n staging --timeout=5m
   kubectl rollout status deployment/lexcore-frontend -n staging --timeout=5m
   
   # Check pod health
   kubectl get pods -n staging
   
   # Run smoke tests
   npm run test:smoke -- --base-url=https://staging.lexcore.com
   ```

5. **Post-Deploy Verification**
   - [ ] API health checks pass (`/health`, `/health/ready`)
   - [ ] Frontend loads successfully
   - [ ] Workers are processing tasks
   - [ ] Database migrations applied successfully
   - [ ] No error spikes in logs
   - [ ] Metrics within baseline

### Rollback (if needed)

```bash
# Rollback to previous Helm release
helm rollback lexcore 0 --namespace staging

# Verify
kubectl rollout status deployment/lexcore-api -n staging
```

---

## Deploy to Production

### Trigger

**Manual only:** Create GitHub Release with tag (e.g., `v1.0.0`)  
**Approval:** Requires 2 approvals (Engineering Lead, DevOps Lead)

### Pre-Deploy Checklist

- [ ] Staging deployment successful
- [ ] Staging smoke tests pass
- [ ] Staging E2E tests pass
- [ ] Performance benchmarks met
- [ ] Security review complete
- [ ] Compliance review complete
- [ ] Customer-facing documentation updated
- [ ] Release notes published
- [ ] On-call engineer notified
- [ ] Maintenance window scheduled (for major releases)

### Steps

1. **Promote Images to Production Tag**
   ```bash
   # Tag staging SHA as production
   aws ecr tag-resource --resource-arn $STAGING_IMAGE_ARN --tag production
   ```

2. **Blue-Green Deployment**
   ```bash
   # Update kubeconfig
   aws eks update-kubeconfig --region us-east-1 --name production-lexcore
   
   # Deploy to blue environment (no traffic)
   helm upgrade --install lexcore-blue ./helm/lexcore \
     --namespace production \
     --set image.tag=$PRODUCTION_TAG \
     --set environment=production \
     --set deployment.color=blue \
     --wait
   ```

3. **Verify Blue Environment**
   ```bash
   # Check blue pods
   kubectl get pods -n production -l color=blue
   
   # Run smoke tests against blue
   npm run test:smoke -- --base-url=https://blue.lexcore.com
   ```

4. **Canary Rollout (10% → 50% → 100%)**
   ```bash
   # 10% traffic to blue
   kubectl patch virtualservice lexcore-api -p '{"spec":{"http":[{"route":[{"destination":{"host":"lexcore-green","weight":90}},{"destination":{"host":"lexcore-blue","weight":10}}]}]}'
   
   # Wait 5 minutes, monitor metrics
   sleep 300
   
   # 50% traffic to blue
   kubectl patch virtualservice lexcore-api -p '{"spec":{"http":[{"route":[{"destination":{"host":"lexcore-green","weight":50}},{"destination":{"host":"lexcore-blue","weight":50}}]}]}'
   
   # Wait 5 minutes, monitor metrics
   sleep 300
   
   # 100% traffic to blue
   kubectl patch virtualservice lexcore-api -p '{"spec":{"http":[{"route":[{"destination":{"host":"lexcore-blue","weight":100}}]}]}'
   ```

5. **Post-Deploy Verification**
   - [ ] Error rate < 0.1%
   - [ ] P95 latency < 2× baseline
   - [ ] No alert firing
   - [ ] User-reported issues = 0
   - [ ] Database queries performing normally
   - [ ] Workers processing tasks normally

6. **Promote Blue to Green**
   ```bash
   # Update service selector
   kubectl patch service lexcore-api -p '{"spec":{"selector":{"color":"blue"}}}'
   
   # Scale down green (after 24 hours)
   kubectl scale deployment lexcore-green --replicas=0 -n production
   ```

### Automatic Rollback Conditions

If any condition occurs during canary, automatic rollback triggers:
- Error rate > 1% for 2 minutes
- P95 latency > 2× baseline for 5 minutes
- Any critical health check fails
- HORDE-AUDIT gate BLOCKED

```bash
# Automatic rollback command (executed by CI)
helm rollback lexcore 0 --namespace production
kubectl patch virtualservice lexcore-api -p '{"spec":{"http":[{"route":[{"destination":{"host":"lexcore-green","weight":100}}]}]}'
```

---

## Database Migrations

### Run Migrations

```bash
# Via Alembic
alembic upgrade head

# Verify
alembic current
```

### Rollback Migrations

```bash
# Rollback to previous version
alembic downgrade -1

# Verify
alembic current
```

### Migration Checklist

- [ ] Migration script reviewed
- [ ] Migration tested in staging
- [ ] Rollback script tested
- [ ] Data backup taken before migration
- [ ] Migration time window scheduled
- [ ] Application compatible with new schema

---

## Post-Deploy Tasks

**Within 1 hour:**
- [ ] Verify all dashboards green
- [ ] Check alert channels for false positives
- [ ] Update deployment log
- [ ] Notify stakeholders

**Within 24 hours:**
- [ ] Monitor for late-appearing issues
- [ ] Review performance metrics
- [ ] Address any customer feedback
- [ ] Document any issues encountered

---

## Emergency Deployment

**For critical fixes only:**

1. **Bypass standard gates** (requires Engineering Director approval)
2. **Deploy directly to production** (skip canary)
3. **Deploy during off-peak hours** (if possible)
4. **On-site engineer available** for rollback

**Post-emergency:**
- [ ] Root cause analysis
- [ ] Process improvement
- [ ] Post-mortem within 24 hours

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-30 | Initial deployment runbook | C10 Runbooks definition |
