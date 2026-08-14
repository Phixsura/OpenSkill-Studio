# OpenSkill Studio

> Open-source project-based training and delivery platform for AI creators.

**Skill → Practice → Project → Submission → Review → Portfolio**

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)
[![CI](https://github.com/Phixsura/OpenSkill-Studio/actions/workflows/ci.yml/badge.svg)](https://github.com/Phixsura/OpenSkill-Studio/actions)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, React 19, Tailwind CSS 4, TanStack Query |
| Backend | FastAPI, Python 3.12+, SQLAlchemy 2.0, asyncpg |
| Database | PostgreSQL 16 |
| Cache/Queue | Redis 7 |
| Object Storage | MinIO (S3-compatible) |
| Monorepo | Turborepo + pnpm |

## Local Development

### Prerequisites

- [Node.js](https://nodejs.org/) ≥ 22
- [pnpm](https://pnpm.io/) ≥ 9
- [Python](https://python.org/) ≥ 3.12
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Docker](https://www.docker.com/) + Docker Compose

### Setup

```bash
# 1. Clone
git clone https://github.com/Phixsura/OpenSkill-Studio.git
cd OpenSkill-Studio

# 2. Install dependencies
make install              # pnpm install + uv sync

# 3. Configure environment
cp .env.example .env

# 4. Start infrastructure
make infra-up             # PostgreSQL + Redis + MinIO

# 5. Generate & run database migrations
cd apps/api && uv run alembic revision --autogenerate -m "initial" && cd ../..
make db-migrate

# 6. Start development
make dev                  # Next.js :3000 + FastAPI :8000
```

Open [http://localhost:3000](http://localhost:3000) — you should see the OpenSkill Studio homepage.

Visit [http://localhost:3000/health](http://localhost:3000/health) to verify frontend ↔ backend communication.

### Available Commands

```bash
make help                 # Show all commands
make dev                  # Start all dev servers
make dev-web              # Start frontend only
make dev-api              # Start backend only
make infra-up             # Start Docker services
make infra-down           # Stop Docker services
make infra-reset          # Reset all data
make db-migrate           # Run migrations
make lint                 # Lint all code
make test                 # Run all tests
make build                # Build for production
```

## Project Structure

```
openskill-studio/
├── apps/
│   ├── web/              # Next.js frontend
│   └── api/              # FastAPI backend
├── packages/
│   ├── shared/           # Shared types & constants
│   ├── eslint-config/    # Shared ESLint config
│   └── typescript-config/# Shared tsconfig
├── docker/               # Docker init scripts
├── docs/design/          # Architecture Decision Records
├── docker-compose.yml    # Local infrastructure
├── Makefile              # Unified commands
└── CLAUDE.md             # AI development guide
```

## Documentation

Architecture decisions are documented in [`docs/design/`](docs/design/):

- [ADR-001: Bootstrap Architecture](docs/design/001-bootstrap-architecture.md)
- [ADR-002: Auth & Users](docs/design/002-auth-and-users.md)
- [ADR-003: Organizations & Multitenancy](docs/design/003-organizations-and-multitenancy.md)
- [ADR-004: Skills & Practice](docs/design/004-skills-and-practice.md)
- [ADR-005: Projects & Submissions](docs/design/005-projects-and-submissions.md)
- [ADR-006: AI Evaluation Pipeline](docs/design/006-ai-evaluation-pipeline.md)
- [ADR-007: Portfolio & Public Page](docs/design/007-portfolio-and-public-page.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[AGPL-3.0](LICENSE) — same license as Cal.com, Plane, and Documenso.
