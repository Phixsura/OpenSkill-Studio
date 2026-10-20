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
	cd apps/api && uv run uvicorn app.main:app --no-server-header --reload --reload-dir app --port 8000 &
	pnpm dev:web

dev-web:                          ## Start frontend only
	pnpm dev:web

dev-api:                          ## Start backend only (hot reload)
	cd apps/api && uv run uvicorn app.main:app --no-server-header --reload --reload-dir app --port 8000

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

e2e-intg: ## Live-API E2E for the integration fabric (starts its own uvicorn on :8443)
	cd apps/api && (lsof -tiTCP:8443 -sTCP:LISTEN | xargs kill -9 2>/dev/null; sleep 0.3; \
		APP_ENV=test EGRESS_ALLOW_PRIVATE=true uv run uvicorn app.main:app --no-server-header --port 8443 & \
		echo $$! > /tmp/intg-e2e-uvicorn.pid; \
		until curl -sf http://localhost:8443/api/v1/health >/dev/null 2>&1 || \
			! kill -0 $$(cat /tmp/intg-e2e-uvicorn.pid) 2>/dev/null; do sleep 0.5; done; \
		APP_ENV=test EGRESS_ALLOW_PRIVATE=true E2E_INTG_API=http://localhost:8443/api/v1 \
			PYTHONPATH=. uv run python tests/e2e_integration_lifecycle.py; \
		status=$$?; kill $$(cat /tmp/intg-e2e-uvicorn.pid) 2>/dev/null; \
		rm -f /tmp/intg-e2e-uvicorn.pid; exit $$status)

e2e-intg-scale: ## Fabric scale smoke: 300 SCIM users + 400 mesh deliveries (uvicorn :8443)
	cd apps/api && (lsof -tiTCP:8443 -sTCP:LISTEN | xargs kill -9 2>/dev/null; sleep 0.3; \
		APP_ENV=test EGRESS_ALLOW_PRIVATE=true uv run uvicorn app.main:app --no-server-header --port 8443 & \
		echo $$! > /tmp/intg-scale-uvicorn.pid; \
		until curl -sf http://localhost:8443/api/v1/health >/dev/null 2>&1 || \
			! kill -0 $$(cat /tmp/intg-scale-uvicorn.pid) 2>/dev/null; do sleep 0.5; done; \
		APP_ENV=test EGRESS_ALLOW_PRIVATE=true E2E_INTG_API=http://localhost:8443/api/v1 \
			PYTHONPATH=. uv run python tests/e2e_scale_smoke.py; \
		status=$$?; kill $$(cat /tmp/intg-scale-uvicorn.pid) 2>/dev/null; \
		rm -f /tmp/intg-scale-uvicorn.pid; exit $$status)

e2e-intg-fuzz: ## Fabric hostile-input fuzz: 250 reqs, asserts zero 5xx (uvicorn :8443)
	cd apps/api && (lsof -tiTCP:8443 -sTCP:LISTEN | xargs kill -9 2>/dev/null; sleep 0.3; \
		APP_ENV=test uv run uvicorn app.main:app --no-server-header --port 8443 & \
		echo $$! > /tmp/intg-fuzz-uvicorn.pid; \
		until curl -sf http://localhost:8443/api/v1/health >/dev/null 2>&1 || \
			! kill -0 $$(cat /tmp/intg-fuzz-uvicorn.pid) 2>/dev/null; do sleep 0.5; done; \
		APP_ENV=test E2E_INTG_API=http://localhost:8443/api/v1 \
			PYTHONPATH=. uv run python tests/e2e_fuzz_fabric.py; \
		status=$$?; kill $$(cat /tmp/intg-fuzz-uvicorn.pid) 2>/dev/null; \
		rm -f /tmp/intg-fuzz-uvicorn.pid; exit $$status)

e2e-intg-appwide: ## App-wide OpenAPI hostile sweep (~4k reqs), zero unexplained 5xx (uvicorn :8443)
	cd apps/api && (lsof -tiTCP:8443 -sTCP:LISTEN | xargs kill -9 2>/dev/null; sleep 0.3; \
		APP_ENV=test uv run uvicorn app.main:app --no-server-header --port 8443 & \
		echo $$! > /tmp/intg-appwide-uvicorn.pid; \
		until curl -sf http://localhost:8443/api/v1/health >/dev/null 2>&1 || \
			! kill -0 $$(cat /tmp/intg-appwide-uvicorn.pid) 2>/dev/null; do sleep 0.5; done; \
		APP_ENV=test E2E_INTG_API=http://localhost:8443/api/v1 \
			PYTHONPATH=. uv run python tests/e2e_fuzz_appwide.py; \
		status=$$?; kill $$(cat /tmp/intg-appwide-uvicorn.pid) 2>/dev/null; \
		rm -f /tmp/intg-appwide-uvicorn.pid; exit $$status)

e2e-intg-scim-conformance: ## scim2-tester conformance run, zero hard failures (uvicorn :8443)
	cd apps/api && (lsof -tiTCP:8443 -sTCP:LISTEN | xargs kill -9 2>/dev/null; sleep 0.3; \
		APP_ENV=test uv run uvicorn app.main:app --no-server-header --port 8443 & \
		echo $$! > /tmp/intg-scimconf-uvicorn.pid; \
		until curl -sf http://localhost:8443/api/v1/health >/dev/null 2>&1 || \
			! kill -0 $$(cat /tmp/intg-scimconf-uvicorn.pid) 2>/dev/null; do sleep 0.5; done; \
		APP_ENV=test E2E_INTG_API=http://localhost:8443/api/v1 \
			PYTHONPATH=. uv run python tests/e2e_scim_conformance.py; \
		status=$$?; kill $$(cat /tmp/intg-scimconf-uvicorn.pid) 2>/dev/null; \
		rm -f /tmp/intg-scimconf-uvicorn.pid; exit $$status)

e2e-intg-latency: ## Hot-endpoint latency tripwire (p95 ceiling; uvicorn :8443)
	cd apps/api && (lsof -tiTCP:8443 -sTCP:LISTEN | xargs kill -9 2>/dev/null; sleep 0.3; \
		APP_ENV=test uv run uvicorn app.main:app --no-server-header --port 8443 & \
		echo $$! > /tmp/intg-lat-uvicorn.pid; \
		until curl -sf http://localhost:8443/api/v1/health >/dev/null 2>&1 || \
			! kill -0 $$(cat /tmp/intg-lat-uvicorn.pid) 2>/dev/null; do sleep 0.5; done; \
		APP_ENV=test E2E_INTG_API=http://localhost:8443/api/v1 \
			PYTHONPATH=. uv run python tests/e2e_latency_smoke.py; \
		status=$$?; kill $$(cat /tmp/intg-lat-uvicorn.pid) 2>/dev/null; \
		rm -f /tmp/intg-lat-uvicorn.pid; exit $$status)

# R578: shared recipe for epic live-E2E suites (own uvicorn on :8443).
# EGRESS=1 adds EGRESS_ALLOW_PRIVATE=true (suites that create webhook sinks;
# on VPN fake-IP DNS even example.com resolves private).
define run_e2e
	cd apps/api && (lsof -tiTCP:8443 -sTCP:LISTEN | xargs kill -9 2>/dev/null; sleep 0.3; \
		APP_ENV=test $(2) uv run uvicorn app.main:app --no-server-header --port 8443 & \
		echo $$! > /tmp/e2e-epic-uvicorn.pid; \
		until curl -sf http://localhost:8443/api/v1/health >/dev/null 2>&1 || \
			! kill -0 $$(cat /tmp/e2e-epic-uvicorn.pid) 2>/dev/null; do sleep 0.5; done; \
		APP_ENV=test $(2) E2E_INTG_API=http://localhost:8443/api/v1 \
			E2E_EXP_API=http://localhost:8443/api/v1 E2E_API=http://localhost:8443/api/v1 \
			PYTHONPATH=. uv run python tests/$(1).py; \
		status=$$?; kill $$(cat /tmp/e2e-epic-uvicorn.pid) 2>/dev/null; \
		rm -f /tmp/e2e-epic-uvicorn.pid; exit $$status)
endef

e2e-talent: ## Talent lifecycle live E2E (64 checks; uvicorn :8443)
	$(call run_e2e,e2e_talent_lifecycle,)

e2e-commercial: ## Commercialization lifecycle live E2E (uvicorn :8443)
	$(call run_e2e,e2e_commercial_lifecycle,)

e2e-core: ## Core platform lifecycle live E2E (uvicorn :8443)
	$(call run_e2e,e2e_lifecycle,)

e2e-smoke: ## App-wide smoke live E2E (148 checks; uvicorn :8443)
	$(call run_e2e,e2e_smoke,)

e2e-workflow: ## Workflow-pack lifecycle live E2E (uvicorn :8443)
	$(call run_e2e,e2e_workflow_lifecycle,)

e2e-experiments: ## Experimentation lifecycle live E2E (uvicorn :8443; private egress for sinks)
	$(call run_e2e,e2e_experiment_lifecycle,EGRESS_ALLOW_PRIVATE=true)

e2e-concurrency: ## Cross-epic concurrency probe (uvicorn :8443)
	$(call run_e2e,e2e_concurrency_probe,)

e2e-live-all: ## EVERY epic's live E2E + all fabric suites, sequentially (shared dev DB)
	$(MAKE) e2e-core
	$(MAKE) e2e-smoke
	$(MAKE) e2e-commercial
	$(MAKE) e2e-workflow
	$(MAKE) e2e-experiments
	$(MAKE) e2e-talent
	$(MAKE) e2e-concurrency
	$(MAKE) e2e-intg-all
	@echo "ALL LIVE E2E SUITES OK"

e2e-intg-all: ## Every fabric live-HTTP suite, SEQUENTIALLY (shared dev DB — never run these concurrently)
	$(MAKE) e2e-intg
	$(MAKE) e2e-intg-scale
	$(MAKE) e2e-intg-fuzz
	$(MAKE) e2e-intg-appwide
	$(MAKE) e2e-intg-scim-conformance
	$(MAKE) e2e-intg-latency
	$(MAKE) e2e-intg-storm
	$(MAKE) e2e-intg-races
	$(MAKE) e2e-intg-adversarial
	@echo "ALL FABRIC LIVE SUITES OK"

e2e-intg-adversarial: ## Hostile-actor battery: 178 checks, strict zero-5xx (uvicorn :8443, NO egress flag)
	cd apps/api && (lsof -tiTCP:8443 -sTCP:LISTEN | xargs kill -9 2>/dev/null; sleep 0.3; \
		APP_ENV=test uv run uvicorn app.main:app --no-server-header --port 8443 & \
		echo $$! > /tmp/intg-adv-uvicorn.pid; \
		until curl -sf http://localhost:8443/api/v1/health >/dev/null 2>&1 || \
			! kill -0 $$(cat /tmp/intg-adv-uvicorn.pid) 2>/dev/null; do sleep 0.5; done; \
		APP_ENV=test E2E_INTG_API=http://localhost:8443/api/v1 \
			PYTHONPATH=. uv run python tests/e2e_adversarial.py; \
		status=$$?; kill $$(cat /tmp/intg-adv-uvicorn.pid) 2>/dev/null; \
		rm -f /tmp/intg-adv-uvicorn.pid; exit $$status)

e2e-intg-races: ## Duplicate-create race probes: 8x parallel identical creates, losers must 4xx (uvicorn :8443)
	cd apps/api && (lsof -tiTCP:8443 -sTCP:LISTEN | xargs kill -9 2>/dev/null; sleep 0.3; \
		APP_ENV=test uv run uvicorn app.main:app --no-server-header --port 8443 & \
		echo $$! > /tmp/intg-races-uvicorn.pid; \
		until curl -sf http://localhost:8443/api/v1/health >/dev/null 2>&1 || \
			! kill -0 $$(cat /tmp/intg-races-uvicorn.pid) 2>/dev/null; do sleep 0.5; done; \
		APP_ENV=test E2E_INTG_API=http://localhost:8443/api/v1 \
			PYTHONPATH=. uv run python tests/e2e_race_probe.py; \
		status=$$?; kill $$(cat /tmp/intg-races-uvicorn.pid) 2>/dev/null; \
		rm -f /tmp/intg-races-uvicorn.pid; exit $$status)

e2e-intg-storm: ## Fabric concurrency storm: 20 workers mixed CRUD, zero 5xx (uvicorn :8443)
	cd apps/api && (lsof -tiTCP:8443 -sTCP:LISTEN | xargs kill -9 2>/dev/null; sleep 0.3; \
		APP_ENV=test uv run uvicorn app.main:app --no-server-header --port 8443 & \
		echo $$! > /tmp/intg-storm-uvicorn.pid; \
		until curl -sf http://localhost:8443/api/v1/health >/dev/null 2>&1 || \
			! kill -0 $$(cat /tmp/intg-storm-uvicorn.pid) 2>/dev/null; do sleep 0.5; done; \
		APP_ENV=test E2E_INTG_API=http://localhost:8443/api/v1 \
			PYTHONPATH=. uv run python tests/e2e_storm_fabric.py; \
		status=$$?; kill $$(cat /tmp/intg-storm-uvicorn.pid) 2>/dev/null; \
		rm -f /tmp/intg-storm-uvicorn.pid; exit $$status)

e2e-intg-browser: ## Fabric browser journey (needs web on :3000 + api on :8000, APP_ENV=test)
	cd apps/api && node tests/browser_e2e_integrations.mjs

e2e-intg-a11y: ## Fabric axe-core WCAG 2.1 A/AA audit (needs web :3000 + api :8000, APP_ENV=test)
	cd apps/api && node tests/browser_a11y_integrations.mjs

drills: ## Run every fabric operational drill sequentially (infra up required; ~15 min)
	cd apps/api && for f in redis_drill minio_drill crash_drill migration_drill \
		ratelimit_drill slow_sink_drill backup_restore_drill explain_audit soak_drill \
		idempotency_drill compose_env_drill; do \
		echo "== $$f =="; uv run python tests/drills/$$f.py || exit 1; \
	done
	@echo "ALL DRILLS OK"


test-intg: ## Run the integration-fabric suites (ADR-018, needs infra-up + db-migrate)
	cd apps/api && uv run pytest tests/test_integrations_core.py tests/test_integrations_db.py \
		tests/test_integrations_events_db.py tests/test_integrations_sso_db.py \
		tests/test_integrations_saml_db.py tests/test_integrations_scim_db.py \
		tests/test_integrations_sync_db.py tests/test_integrations_roster_db.py \
		tests/test_integrations_lti_db.py tests/test_integrations_ags_db.py \
		tests/test_integrations_import_db.py tests/test_integrations_export_db.py \
		tests/test_integrations_health_db.py tests/test_integrations_push_db.py \
		tests/test_integrations_races_db.py tests/test_integrations_properties.py \
		tests/test_integrations_acceptance_db.py tests/test_web_api_contract.py \
		tests/test_schema_drift_guard_db.py \
		tests/test_ops_doc_contract.py -q

e2e-exp: ## Live-API E2E for the experimentation platform (starts its own uvicorn on :8442)
	cd apps/api && (APP_ENV=test uv run uvicorn app.main:app --no-server-header --port 8442 & \
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
		tests/test_exp_webhooks_db.py \
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
