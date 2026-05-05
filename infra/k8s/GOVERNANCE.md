# Kubernetes Manifests Governance

> **Chunk:** C02 — Phase 0 Foundation  
> **Horde:** HORDE-INFRA  
> **Control Plane:** OPERATIONS  
> **Status:** PRODUCTION_READY

## Overview

This directory contains Kubernetes manifests for LexCore + LexRadar deployment on EKS. All manifests follow Kubernetes best practices with security hardening, observability, and scalability.

## Namespace Strategy

### Application Namespaces
- **lexcore-dev:** Development environment
- **lexcore-staging:** Staging environment
- **lexcore-prod:** Production environment

All application namespaces have `istio-injection: enabled` for service mesh.

### System Namespaces
- **monitoring:** Prometheus, Grafana, Loki, Alertmanager
- **security:** Security tools, pod security policies enforced

## Deployment Architecture

### API Deployment (lexcore-api)
- **Replicas:** 3 (minimum for HA)
- **Strategy:** RollingUpdate with maxSurge=1, maxUnavailable=0
- **Security:**
  - runAsNonRoot: true
  - runAsUser: 1000
  - fsGroup: 1000
  - seccompProfile: RuntimeDefault
  - readOnlyRootFilesystem: true
  - capabilities: drop ALL
- **Probes:**
  - Liveness: /health/live (30s initial, 10s period)
  - Readiness: /health/ready (5s initial, 5s period)
- **Resources:**
  - Requests: 512Mi memory, 250m CPU
  - Limits: 2Gi memory, 1000m CPU
- **Affinity:**
  - Pod anti-affinity to spread across nodes
  - Topology spread constraints for AZ distribution

### Service Configuration
- **Type:** ClusterIP (internal only)
- **Port:** 80 → 8000 (container)
- **ServiceAccount:** IRSA for AWS resource access

## Horizontal Pod Autoscaling

### HPA Configuration
- **Min Replicas:** 3
- **Max Replicas:** 20
- **Metrics:**
  - CPU: 70% utilization
  - Memory: 80% utilization
- **Scale Up:**
  - Stabilization: 60s
  - Max 100% or 4 pods per 15s
- **Scale Down:**
  - Stabilization: 300s
  - Max 10% per 60s

### Pod Disruption Budget
- **Min Available:** 2 pods
- Ensures HA during voluntary disruptions

## Monitoring Stack

### Prometheus
- Scrapes metrics from all pods with `prometheus.io/scrape: true`
- Port: 8000
- Path: /metrics
- Retention: 15 days

### Grafana
- Dashboards for API, database, cache, vector search
- Alerting integration with Alertmanager
- User authentication via OAuth

### Loki
- Log aggregation from all pods
- Structured JSON logs (structlog)
- Retention: 30 days

### Alertmanager
- Critical alerts: error rate > 1%, P95 latency > 500ms
- Routes to Slack, PagerDuty
- Silencing and inhibition rules

## Governance Rules

### Never Overwrite
- All manifest changes must be additive or explicitly versioned
- Use kubectl apply --dry-run to review changes
- Never manually edit running resources

### Always Append
- New resources added via new YAML files
- New labels/annotations added to existing resources
- New configmaps/secrets for new configurations

### Track Changes
- Every manifest change must be committed to git
- Commit message format: `k8s: [Team H] Chunk {N}: {description}`
- PR required for production changes

### No Bloat
- Remove unused resources via kubectl delete (not manual)
- Keep manifests focused and single-purpose
- Use Helm charts for complex applications (future)

## Deployment Workflow

### Validation
```bash
# Dry-run apply
kubectl apply --dry-run=client -f namespace.yaml
kubectl apply --dry-run=client -f api-deployment.yaml
kubectl apply --dry-run=client -f hpa.yaml

# Validate syntax
kubectl apply --validate=true --dry-run=client -f .

# Security scan (if kube-score available)
kube-score score *.yaml
```

### Application
```bash
# Apply in order
kubectl apply -f namespace.yaml
kubectl apply -f monitoring/
kubectl apply -f api-deployment.yaml
kubectl apply -f hpa.yaml
```

### Verification
```bash
# Check deployment status
kubectl rollout status deployment/lexcore-api -n lexcore-prod

# Check pods
kubectl get pods -n lexcore-prod -l app=lexcore-api

# Check HPA
kubectl get hpa -n lexcore-prod
```

## Security Controls

### Pod Security
- Restricted pod security policies on security namespace
- No privileged containers
- No host network or host PID
- Read-only root filesystem
- Drop all capabilities

### Network Policies
- Default deny all ingress/egress
- Allow only required traffic
- Namespace isolation enforced

### Secrets Management
- Secrets via Kubernetes secrets (IRSA for AWS)
- No secrets in manifests
- Vault integration for sensitive data
- Secret rotation policy

## Observability

### Metrics
- HTTP request rate, error rate, latency
- Container resource usage
- Custom business metrics
- HPA scaling events

### Logging
- Structured JSON logs
- Correlation ID propagation
- No PII in logs
- Log level: INFO (prod), DEBUG (dev)

### Tracing
- OpenTelemetry integration
- Distributed tracing across services
- Span context propagation
- Jaeger UI for trace analysis

## Disaster Recovery

- **Backups:** etcd backups via EKS
- **State:** Stateless applications (state in external services)
- **RPO:** < 5 minutes (etcd)
- **RTO:** < 10 minutes (deployment)

## Change History

| Date | Change | Chunk | Team |
|------|--------|-------|------|
| 2026-05-05 | Governance documentation added | Chunk 3 | HORDE-INFRA |

## References

- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [HPA Best Practices](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
