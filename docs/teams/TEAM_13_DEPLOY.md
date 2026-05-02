# Team 13: Staging Deployment Team — Role Analysis & Execution Plan

## Role Definition
**Lead**: Deployment Lead / SRE
**Mission**: Staging environment deployment with zero-downtime validation. Prepares production-ready artifacts without touching production.

## Capability Matrix
| Capability | Metric | Target | Instrument |
|------------|--------|--------|----------|
| Docker build | Image build success | 100% | `docker build` |
| Container health | Container starts and responds | PASS | `docker run + curl` |
| K8s manifest validity | YAML schema valid | 100% | `kubectl apply --dry-run=client` |
| Environment config | Staging env vars defined | 100% | File existence |
| Service readiness | All services report ready | 100% | Health check endpoints |
| Artifact integrity | Docker image digest signed | SHA-256 | `docker images --digests` |

## Core Functions
1. **Container Build**: Build Docker image from validated source (post HORDE-AUDIT PASS)
2. **Manifest Validation**: Validate K8s YAML without cluster apply
3. **Environment Configuration**: Staging-specific env vars, secrets placeholders
4. **Health Check Definition**: Define readiness/liveness probes for all services
5. **Rollback Artifacts**: Tag and sign pre-deployment image for instant rollback

## Execution Micro-Chunks (Validated Completion)

### Micro-Chunk 1: Context Pre-Load from HORDE-AUDIT
**Action**: Read HORDE_AUDIT_REPORT.md gate decision; abort if BLOCKED
**Input**: `docs/execution/HORDE_AUDIT_REPORT.md`
**Metric**: Gate decision == "PASS"
**Output**: Deployment authorization flag
**Validation Gate**: `assert gate_decision == "PASS"`
**Transfer Control**: Auth flag + commit hash → Micro-Chunk 2

### Micro-Chunk 2: Dockerfile Validation
**Action**: Verify Dockerfile exists, syntax valid, base image specified
**Input**: `backend/Dockerfile`
**Metric**: Dockerfile parseable; FROM image specified
**Output**: Dockerfile validation report
**Validation Gate**: `assert dockerfile_exists and base_image_defined`
**Transfer Control**: Dockerfile report → Micro-Chunk 3

### Micro-Chunk 3: Staging Environment Config
**Action**: Create staging environment file with non-production credentials
**Input**: `.env.staging` template
**Metric**: All required env vars present; no production secrets
**Output**: `.env.staging` file
**Validation Gate**: `assert env_vars_count >= 8 and no_prod_secrets`
**Transfer Control**: Env config → Micro-Chunk 4

### Micro-Chunk 4: K8s Manifest Dry-Run
**Action**: Validate K8s manifests with client-side dry-run
**Input**: `k8s/*.yaml`
**Metric**: All manifests parseable; no schema errors
**Output**: Manifest validation report
**Validation Gate**: `assert manifest_errors == 0`
**Transfer Control**: Manifest report → Micro-Chunk 5

### Micro-Chunk 5: Health Check Specification
**Action**: Define readiness/liveness probes for API, workers, Redis, PostgreSQL
**Input**: Service definitions
**Metric**: Every service has /health/live and /health/ready endpoints defined
**Output**: Health check specification document
**Validation Gate**: `assert health_endpoints >= 4`
**Transfer Control**: Health spec → Micro-Chunk 6

### Micro-Chunk 6: Staging Deployment Report
**Action**: Aggregate all artifacts; tag staging release; generate deployment report
**Metric**: All artifacts validated; release tagged `staging-v{N}`
**Output**: `docs/execution/STAGING_DEPLOY_REPORT.md`
**Validation Gate**: `assert all_chunks_validated and release_tagged`
**Transfer Control**: Staging report → P2-09 Security Team

## Deliverables
- `.env.staging` — staging environment configuration
- `docs/execution/STAGING_DEPLOY_REPORT.md` — signed deployment readiness report
- Health check specification
- Staging release tag

## Current Status
- Dockerfile: exists, needs validation
- K8s manifests: created (deployment, HPA, monitoring)
- Terraform: Redis module configured
- GitHub Actions: workflows defined
- Deployment script: stub created
