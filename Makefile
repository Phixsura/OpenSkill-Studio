.PHONY: dev build test lint install infra-up infra-down db-migrate help

# ─── Install ─────────────────────────────────────────────
install:                          ## Install all dependencies
	pnpm install
	cd apps/api && uv sync

# ─── Development ─────────────────────────────────────────
dev:                              ## Start frontend + backend dev servers (2 terminals needed)
	@echo "Run in separate terminals:"
	@echo "  make dev-web   → http://localhost:3000"
	@echo "  make dev-api   → http://localhost:8000"
	@echo ""
	@echo "Or use: make dev-all (requires background jobs)"

dev-all:                          ## Start both servers (frontend foreground, API background)
	cd apps/api && uv run uvicorn app.main:app --reload --reload-dir app --port 8000 &
	pnpm dev:web

dev-web:                          ## Start frontend only
	pnpm dev:web

dev-api:                          ## Start backend only (hot reload)
	cd apps/api && uv run uvicorn app.main:app --reload --reload-dir app --port 8000

dev-worker:                       ## Start control-plane worker (outbox + crons)
	cd apps/api && uv run arq app.controlplane.worker.WorkerSettings

# ─── Infrastructure ──────────────────────────────────────
infra-up:                         ## Start Docker infrastructure
	docker compose up -d

infra-down:                       ## Stop infrastructure
	docker compose down

infra-reset:                      ## Reset infrastructure (clear data)
	docker compose down -v && docker compose up -d

# ─── Database ────────────────────────────────────────────
db-migrate:                       ## Run database migrations
	cd apps/api && uv run alembic upgrade head

db-generate:                      ## Generate migration file
	cd apps/api && uv run alembic revision --autogenerate -m "$(msg)"

db-reset:                         ## Reset database
	cd apps/api && uv run alembic downgrade base && uv run alembic upgrade head

db-seed:                          ## Create initial admin user (set ADMIN_EMAIL, ADMIN_PASSWORD)
	cd apps/api && uv run python -m app.cli create-admin

# ─── Quality ─────────────────────────────────────────────
lint:                             ## Lint all code
	pnpm lint

lint-fix:                         ## Fix lint issues
	pnpm lint:fix

test:                             ## Run all tests
	pnpm test

type-check:                       ## TypeScript type check
	pnpm type-check

types-generate:                   ## Generate TS types from OpenAPI
	pnpm types:generate

# ─── Build ───────────────────────────────────────────────
build:                            ## Build all packages
	pnpm build

help:                             ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
