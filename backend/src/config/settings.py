"""Application configuration for LexCore + LexRadar API.

Loaded from environment variables with sensible defaults.
"""

import os
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "LexCore + LexRadar"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost/lexcore"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_POOL_SIZE: int = 10
    
    # Vector Database (Qdrant)
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    
    # Vault
    VAULT_ADDR: str = "http://localhost:8200"
    VAULT_TOKEN: str = ""
    VAULT_NAMESPACE: str = ""
    
    # JWT
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 100
    RATE_LIMIT_BURST: int = 150
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Polygon (Blockchain)
    POLYGON_RPC_URL: str = "https://polygon-rpc.com"
    POLYGON_PRIVATE_KEY: str = ""
    POLYGON_CHAIN_ID: int = 137
    
    # S3
    S3_BUCKET_LEGAL_DOCS: str = "lexcore-legal-docs"
    S3_BUCKET_FILING_BUNDLES: str = "lexradar-filing-bundles"
    AWS_REGION: str = "us-east-1"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Monitoring
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""
    PROMETHEUS_PORT: int = 9090
    
    # BAM (Binary Action Matrix)
    BAM_GENESIS_HASH: str = "a96893482a3e79e75437ed19c21be1c9f618633c88cd5102f1e2d020035ade96"
    
    # Security
    BYOK_ENABLED: bool = True
    ENCRYPTION_ALGORITHM: str = "AES-256-GCM"
    
    # Feature Flags
    ENABLE_MCP_TOOLS: bool = True
    ENABLE_INGEST_PIPELINE: bool = True
    ENABLE_MONITORING: bool = True
    
    class Config:
        env_prefix = "LEXCORE_"
        case_sensitive = True


settings = Settings()
