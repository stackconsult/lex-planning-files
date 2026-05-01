# LexCore + LexRadar — Unified Build System v2
# Common commands for all HORDE teams

.PHONY: help dev test lint format migrate db-up db-down clean

help:
	@echo "Available commands:"
	@echo "  make dev          Start local development stack (docker-compose up -d)"
	@echo "  make db-up        Start database and dependencies"
	@echo "  make db-down      Stop database and dependencies"
	@echo "  make migrate      Run Alembic migrations"
	@echo "  make migrate-down Rollback one migration"
	@echo "  make test         Run all tests"
	@echo "  make test-unit    Run unit tests"
	@echo "  make test-int     Run integration tests"
	@echo "  make lint         Run ruff linter"
	@echo "  make format       Run ruff formatter"
	@echo "  make typecheck    Run mypy type checker"
	@echo "  make clean        Remove build artifacts and containers"

# Development

dev:
	docker-compose up -d

db-up:
	docker-compose up -d postgres redis qdrant vault

db-down:
	docker-compose down

migrate:
	cd backend && alembic upgrade head

migrate-down:
	cd backend && alembic downgrade -1

migrate-gen:
	cd backend && alembic revision --autogenerate -m "$(msg)"

# Testing

test:
	cd backend && pytest -v

test-unit:
	cd backend && pytest tests/unit -v

test-int:
	cd backend && pytest tests/integration -v

test-cov:
	cd backend && pytest --cov=src --cov-report=html --cov-report=term

# Code Quality

lint:
	cd backend && ruff check src tests

lint-fix:
	cd backend && ruff check --fix src tests

format:
	cd backend && ruff format src tests

typecheck:
	cd backend && mypy src

# Cleanup

clean:
	docker-compose down -v
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend -type f -name '*.pyc' -delete 2>/dev/null || true
	find backend -type f -name '*.pyo' -delete 2>/dev/null || true
	find backend -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	find backend -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
