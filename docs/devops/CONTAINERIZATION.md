# CONTAINERIZATION.md — LexCore + LexRadar Container Specifications

> **Build System:** Unified Build System v2 | **Chunk:** C07 — DevOps + CI/CD | **Horde:** HORDE-DEVOPS

---

## Overview

All workloads run as containers orchestrated by EKS. Three primary images: API (FastAPI), Frontend (Next.js), and Worker (Celery). Multi-stage Dockerfiles minimize image size and attack surface. Images are built via GitHub Actions, pushed to ECR, and deployed via Helm.

**Registry:** AWS ECR (private)  
**Runtime:** containerd on Amazon Linux 2023 EKS nodes  
**Scanning:** Amazon Inspector + Trivy on every build  
**Base Images:** Official `python:3.12-slim`, `node:20-alpine`  

---

## API Container

### Dockerfile

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim AS builder

WORKDIR /app
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY api/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim AS production
WORKDIR /app
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 && rm -rf /var/lib/apt/lists/*

COPY --chown=appuser:appgroup api/ ./

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Spec

| Property | Value |
|----------|-------|
| Base image | `python:3.12-slim` |
| Builder stage | Compiles C extensions, installs dependencies |
| Production stage | Minimal runtime, no build tools |
| User | `appuser` (UID 999), non-root |
| Port | 8000 |
| Health check | `GET /health` every 30s |
| Entrypoint | `uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4` |

### Kubernetes Deployment (API)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lexcore-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: lexcore-api
  template:
    metadata:
      labels:
        app: lexcore-api
    spec:
      serviceAccountName: lexcore-api-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 999
        fsGroup: 999
      containers:
      - name: api
        image: "${ECR_REGISTRY}/lexcore-api:${IMAGE_TAG}"
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8000
          name: http
        envFrom:
        - secretRef:
            name: lexcore-api-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
        volumeMounts:
        - name: tmp
          mountPath: /tmp
      volumes:
      - name: tmp
        emptyDir: {}
```

---

## Frontend Container

### Dockerfile

```dockerfile
# syntax=docker/dockerfile:1
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:20-alpine AS production
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => r.statusCode === 200 ? process.exit(0) : process.exit(1))" || exit 1
USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]
```

### Spec

| Property | Value |
|----------|-------|
| Base image | `node:20-alpine` |
| Output mode | Next.js `output: 'standalone'` |
| User | `nextjs` (UID 1001), non-root |
| Port | 3000 |
| Health check | `GET /api/health` every 30s |

### Kubernetes Deployment (Frontend)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lexcore-frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: lexcore-frontend
  template:
    metadata:
      labels:
        app: lexcore-frontend
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        fsGroup: 1001
      containers:
      - name: frontend
        image: "${ECR_REGISTRY}/lexcore-frontend:${IMAGE_TAG}"
        ports:
        - containerPort: 3000
          name: http
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "https://api.lexcore.com"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

## Worker Container

### Dockerfile

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim AS builder
WORKDIR /app
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY api/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim AS production
WORKDIR /app
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 && rm -rf /var/lib/apt/lists/*
COPY --chown=appuser:appgroup api/ ./
USER appuser
CMD ["celery", "-A", "tasks", "worker", "-Q", "${CELERY_QUEUE}", "-c", "${CELERY_CONCURRENCY}"]
```

### Spec

| Property | Value |
|----------|-------|
| Base image | `python:3.12-slim` |
| User | `appuser` (UID 999) |
| Entrypoint | `celery -A tasks worker -Q ${CELERY_QUEUE} -c ${CELERY_CONCURRENCY}` |
| Queue env | `CELERY_QUEUE` (default, ingestion, search, research, patent, monitor, email, evaluation, blockchain) |
| Concurrency env | `CELERY_CONCURRENCY` (default 4) |

### Kubernetes Deployment (Worker — Patent Queue)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: celery-patent-worker
spec:
  replicas: 2
  selector:
    matchLabels:
      app: celery-patent-worker
  template:
    metadata:
      labels:
        app: celery-patent-worker
    spec:
      serviceAccountName: celery-worker-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 999
        fsGroup: 999
      containers:
      - name: worker
        image: "${ECR_REGISTRY}/lexcore-worker:${IMAGE_TAG}"
        env:
        - name: CELERY_QUEUE
          value: "patent"
        - name: CELERY_CONCURRENCY
          value: "4"
        envFrom:
        - secretRef:
            name: lexcore-api-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          exec:
            command:
            - /bin/sh
            - -c
            - "celery -A tasks inspect ping -d celery@$HOSTNAME || exit 1"
          initialDelaySeconds: 60
          periodSeconds: 30
          timeoutSeconds: 10
```

---

## Security Hardening

| Control | Implementation |
|---------|---------------|
| Non-root user | `runAsUser: 999` / `1001` |
| Read-only root FS | `readOnlyRootFilesystem: true` |
| Drop all capabilities | `capabilities: { drop: [ALL] }` |
| No privilege escalation | `allowPrivilegeEscalation: false` |
| Distroless/minimal base | `python:3.12-slim`, `node:20-alpine` |
| No secrets in image | Secrets injected via K8s External Secrets Operator |
| Image scanning | Trivy + Amazon Inspector on every build |
| SBOM generation | Syft generates SBOM, stored in ECR |

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-30 | Initial containerization spec | C07 DevOps definition |
