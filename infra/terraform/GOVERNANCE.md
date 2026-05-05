# Terraform Infrastructure Governance

> **Chunk:** C02 — Phase 0 Foundation  
> **Horde:** HORDE-INFRA  
> **Control Plane:** OPERATIONS  
> **Status:** PRODUCTION_READY

## Overview

This directory contains Terraform Infrastructure as Code (IaC) for LexCore + LexRadar deployment on AWS. All infrastructure is defined declaratively with state management via S3 and DynamoDB.

## Architecture Components

### Compute
- **EKS Cluster:** Kubernetes 1.28 with managed node groups
  - General purpose: t3.large (3-10 nodes)
  - Compute intensive: c5.2xlarge (2-5 nodes) with taints
  - GPU: p3.2xlarge (1-3 nodes) with taints (optional)

### Networking
- **VPC:** 10.0.0.0/16 with 3 AZs
  - Private subnets: 10.0.1.0/24, 10.0.2.0/24, 10.0.3.0/24
  - Public subnets: 10.0.101.0/24, 10.0.102.0/24, 10.0.103.0/24
  - NAT Gateway: Single in dev, multi-AZ in prod
  - ALB: HTTPS (443) with WAF protection

### Storage
- **S3 Buckets:**
  - lexcore-legal-docs-{env}-{account}: Raw legal documents
  - lexradar-filing-bundles-{env}-{account}: Patent filing bundles
  - lexcore-terraform-state: Terraform state backend
- **Redis:** ElastiCache Redis 7 with encryption and logging
- **PostgreSQL:** Neon (managed via Neon provider, not in this Terraform)

### Security
- **WAF:** AWSManagedRulesCommonRuleSet
- **Security Groups:** Restrictive, principle of least privilege
- **IAM:** IRSA for service accounts, least access policies
- **Encryption:** AES-256 for S3, TLS for Redis

### State Management
- **Backend:** S3 with DynamoDB locking
- **State File:** infrastructure/terraform.tfstate
- **Lock Table:** terraform-locks

## Deployment Workflow

### Prerequisites
```bash
# Install Terraform >= 1.6.0
# Configure AWS credentials
aws configure

# Set environment variables
export TF_VAR_environment=dev
export TF_VAR_aws_account_id=123456789012
export TF_VAR_neon_api_key=xxx
```

### Initialization
```bash
terraform init
```

### Planning
```bash
terraform plan -out=tfplan
```

### Application
```bash
terraform apply tfplan
```

### Validation
```bash
# Format check
terraform fmt -check

# Validate syntax
terraform validate

# Security scan (if tflint available)
tflint --config .tflint.hcl
```

## Governance Rules

### Never Overwrite
- All changes must be additive or explicitly destructive
- Use `terraform plan` to review changes before apply
- State is sacred - never manually modify resources

### Always Append
- New resources added via new Terraform code
- Variable additions must have defaults
- Output additions for new resources

### Track Changes
- Every Terraform change must be committed to git
- Commit message format: `infra: [Team H] Chunk {N}: {description}`
- State changes must be reviewed in PR

### No Bloat
- Remove unused resources via Terraform (not manual deletion)
- Keep modules focused and single-purpose
- Avoid over-engineering - use AWS managed services

## Module Structure

```
terraform/
├── main.tf              # Root configuration
├── variables.tf         # Input variables
├── outputs.tf           # Output values
├── modules/             # Reusable modules
│   └── redis/          # Redis module
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── GOVERNANCE.md        # This file
```

## Environment Strategy

### Dev
- Single NAT Gateway (cost optimization)
- No GPU nodes
- Minimum node counts
- Development-only features enabled

### Staging
- Multi-AZ NAT Gateway
- No GPU nodes
- Production-like configuration
- Integration testing environment

### Production
- Multi-AZ NAT Gateway
- GPU nodes enabled (if needed)
- Maximum node counts
- Full monitoring and alerting
- BYOK for encryption keys

## Cost Optimization

- **Dev:** Single NAT gateway, no GPU, minimum nodes
- **Staging:** Multi-AZ but no GPU
- **Production:** Full HA with optional GPU
- **S3 Lifecycle:** Transition to GLACIER after 90 days, expire after 7 years
- **Redis:** cache.m6g.large (balance of cost/performance)

## Security Controls

### Network
- Private subnets for all workloads
- ALB as only public entry point
- WAF rules for common attacks
- Security groups restrict to minimum required ports

### IAM
- IRSA for pod-level permissions
- Least privilege policies
- No hardcoded credentials
- Secrets via AWS Secrets Manager

### Encryption
- S3: AES-256 server-side
- Redis: At-rest and in-transit encryption
- EBS: KMS-managed encryption keys
- TLS 1.3 for all external communication

## Monitoring

### CloudWatch
- Redis slow log and engine log
- EKS metrics via CloudWatch agent
- ALB access logs
- WAF metrics

### Alerts
- High error rates
- High latency
- Security events
- Cost anomalies

## Disaster Recovery

- **Backups:** S3 versioning enabled
- **State:** Terraform state in S3 with versioning
- **RPO:** < 5 minutes (state)
- **RTO:** < 15 minutes (infrastructure recreation)

## Change History

| Date | Change | Chunk | Team |
|------|--------|-------|------|
| 2026-05-05 | Governance documentation added | Chunk 2 | HORDE-INFRA |

## References

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
- [AWS Security Hub](https://docs.aws.amazon.com/securityhub/)
