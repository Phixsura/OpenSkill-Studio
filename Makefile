.PHONY: dev build test test-eco lint install infra-up infra-down db-migrate help

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

e2e-exp: ## Live-API E2E for the experimentation platform (starts its own uvicorn on :8442)
	cd apps/api && (APP_ENV=test uv run uvicorn app.main:app --port 8442 & \
		echo $$! > /tmp/exp-e2e-uvicorn.pid; \
		until curl -sf http://localhost:8442/api/v1/health >/dev/null 2>&1 || \
			! kill -0 $$(cat /tmp/exp-e2e-uvicorn.pid) 2>/dev/null; do sleep 0.5; done; \
		PYTHONPATH=. uv run python tests/e2e_experiment_lifecycle.py; \
		status=$$?; kill $$(cat /tmp/exp-e2e-uvicorn.pid) 2>/dev/null; \
		rm -f /tmp/exp-e2e-uvicorn.pid; exit $$status)

test-exp: ## Run the experimentation-platform suites (ADR-017, needs infra-up + db-migrate)
	cd apps/api && uv run pytest tests/test_exp_spec_validation.py tests/test_exp_assignment_pure.py \
		tests/test_exp_assignment_db.py tests/test_exp_metrics_db.py tests/test_exp_guardrails_db.py \
		tests/test_exp_analysis.py tests/test_exp_analysis_db.py tests/test_exp_decisions_db.py \
		tests/test_exp_integrations_db.py tests/test_exp_e2e_flow.py tests/test_exp_endpoints_nodb.py \
		tests/test_exp_identity_api.py \
		tests/test_exp_web_parity.py tests/test_exp_holdouts_db.py tests/test_exp_fuzz.py \
		-q --timeout=600 --timeout-method=thread

test:                             ## Run all tests
	pnpm test

test-eco:                         ## Ecosystem-intelligence subset (issue #35; ~90s, needs infra-up)
	cd apps/api && uv run pytest tests/ -q -k "eco"

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
