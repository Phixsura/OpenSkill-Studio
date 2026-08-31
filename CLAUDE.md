# CLAUDE.md — AI Development Guide

## Project Overview

OpenSkill Studio is an open-source project-based training and delivery platform for AI creators.

Stack: Turborepo monorepo with Next.js (TypeScript) frontend and FastAPI (Python) backend.

## Repository Structure

```
apps/web/       — Next.js 15 frontend (App Router, Tailwind CSS 4, Shadcn/ui)
apps/api/       — FastAPI backend (SQLAlchemy, asyncpg, structlog)
  app/          — Application code (models, services, api, core, middleware)
  migrations/   — Alembic database migrations
  tests/        — pytest test suite (runs without DB via noop lifespan)
  .venv/        — Python virtual env (managed by uv, gitignored)
packages/       — Shared configs (typescript-config, eslint-config, shared types)
docker/         — Docker init scripts
docs/design/    — Architecture Decision Records (ADR)
```

## Key Commands

```bash
make install      # Install all dependencies (pnpm install + cd apps/api && uv sync)
make infra-up     # Start Docker services (Postgres, Redis, MinIO)
make db-migrate   # Run Alembic migrations (requires infra-up first)
make dev-web      # Start frontend (http://localhost:3000)
make dev-api      # Start backend (http://localhost:8000) — needs separate terminal
make lint         # Lint all code (ESLint + Ruff)
make test         # Run all tests (Vitest + pytest) — tests run WITHOUT infra
```

## Backend (Python)

- **Package manager**: [uv](https://docs.astral.sh/uv/) — config in `apps/api/pyproject.toml`
- **Virtual env**: `apps/api/.venv/` (auto-created by `uv sync`)
- **Run commands**: Always `cd apps/api && uv run <command>` or `make <target>`
- **Linter**: Ruff (`uv run ruff check .`)
- **Tests**: pytest (`uv run pytest -v`) — runs with noop lifespan, no DB needed
- **Migrations**: `make db-generate msg="description"` then `make db-migrate`

## Frontend (TypeScript)

- **Package manager**: pnpm 9 (workspace root)
- **Tests**: Vitest (`pnpm --filter web test`)
- **Type check**: `pnpm --filter web type-check`

## Conventions

- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`)
- **Frontend**: Server Components by default; `"use client"` only for interactivity
- **Backend**: Router → Schema → Service → Model layering; no business logic in routers
- **API paths**: Always under `/api/v1/`
- **IDs**: ULID (26-char, time-ordered)
- **Responses**: `{ data: T }` for single, `{ data: T[], meta: {...} }` for lists
- **Errors**: `{ error: { code: "MACHINE_CODE", message: "Human text" } }`
- **Org-scoped endpoints**: `/api/v1/orgs/{org_id}/...` — use `require_org_member()` from deps

## Design Documents

All architecture decisions are documented in `docs/design/`:
- ADR-001: Bootstrap architecture
- ADR-002: Auth & users
- ADR-003: Organizations & multitenancy
- ADR-004: Skills & practice
- ADR-005: Projects & submissions
- ADR-006: AI evaluation pipeline
- ADR-007: Portfolio & public page
- ADR-008: Cohorts, client briefs & multimodal AI evaluation
- ADR-009: Skill pack registry & versioned content distribution
- ADR-010: Workflow Packs & execution runtime
- ADR-011: Provider capability abstraction
- ADR-012: Explainable matching engine
- ADR-013: Solution composers & creator matching
- ADR-014: SaaS commercialization control plane
