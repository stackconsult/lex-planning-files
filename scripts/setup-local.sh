#!/bin/bash
# LexCore + LexRadar — Local Development Setup
# Run once after cloning repository

set -euo pipefail

echo "=== LexCore Local Development Setup ==="

# Check dependencies
echo "Checking dependencies..."
command -v docker >/dev/null 2>&1 || { echo "Docker required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "docker-compose required but not installed. Aborting." >&2; exit 1; }

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.example .env
fi

# Start infrastructure
echo "Starting infrastructure (PostgreSQL, Redis, Qdrant, Vault)..."
docker-compose up -d postgres redis qdrant vault

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
sleep 5
until docker-compose exec postgres pg_isready -U lexcore -d lexcore; do
    echo "  PostgreSQL not ready yet, waiting..."
    sleep 2
done

# Run migrations
echo "Running database migrations..."
cd backend
alembic upgrade head

# Done
echo ""
echo "=== Setup complete ==="
echo "Services:"
echo "  API:        http://localhost:8000"
echo "  PostgreSQL: localhost:5432 (lexcore/lexcore_dev_password)"
echo "  Redis:      localhost:6379"
echo "  Qdrant:     http://localhost:6333"
echo "  Vault:      http://localhost:8200"
echo "  Grafana:    http://localhost:3000 (admin/admin)"
echo ""
echo "Next steps:"
echo "  make dev          # Start full stack"
echo "  make test         # Run tests"
echo "  make migrate      # Run migrations"
