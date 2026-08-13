# OpenSkill Studio — Bootstrap Architecture Design (ADR-001)

> 对标 Cal.com / Plane.so / Documenso / Twenty CRM / Formbricks / Supabase / Hoppscotch
>
> Status: **Proposed** | Author: Lyphixia Wang | Date: 2026-08-13

---

## 目录

1. [项目定位](#1-项目定位)
2. [世界级项目对标分析](#2-世界级项目对标分析)
3. [技术栈决策](#3-技术栈决策)
4. [仓库结构](#4-仓库结构)
5. [Monorepo 配置](#5-monorepo-配置)
6. [基础设施架构](#6-基础设施架构)
7. [后端设计](#7-后端设计)
8. [前端设计](#8-前端设计)
9. [跨语言类型共享](#9-跨语言类型共享)
10. [安全设计](#10-安全设计)
11. [可观测性](#11-可观测性)
12. [测试策略](#12-测试策略)
13. [开发者体验](#13-开发者体验)
14. [CI/CD 流水线](#14-cicd-流水线)
15. [开源治理](#15-开源治理)
16. [未来扩展预留](#16-未来扩展预留)
17. [验收标准映射](#17-验收标准映射)
18. [实施计划](#18-实施计划)

---

## 1. 项目定位

**OpenSkill Studio** — 开源的项目制训练与交付平台，面向 AI 创作者。

完整工作流：**Skill → Practice → Project → Submission → Review → Portfolio**

本文档设计 Issue #1（Bootstrap）的完整技术方案，同时为后续所有功能模块奠定架构基础。

---

## 2. 世界级项目对标分析

### 2.1 技术选型对比

| 维度 | Cal.com | Plane.so | Documenso | Twenty CRM | Formbricks | Supabase | Hoppscotch |
|------|---------|----------|-----------|------------|------------|----------|------------|
| Monorepo 工具 | Turborepo + Yarn | Turborepo + pnpm | Turborepo + npm | Nx + Yarn | Turborepo | pnpm workspaces | pnpm workspaces |
| 前端 | Next.js App Router | React 19 + Vite | React 18 + Remix | React 18 | Next.js | Next.js | Vue 3.5 + Vite |
| UI | Tailwind + Radix | Tailwind + 自研 | Tailwind + Shadcn/ui | Linaria (CSS-in-JS) | Tailwind + Radix | Tailwind + Shadcn/ui | Tailwind |
| 后端 | NestJS (API v2) | Django + DRF | Hono | NestJS 11 | Next.js 全栈 | Go/Elixir/Haskell 多语言 | NestJS |
| 数据库 | PostgreSQL | PostgreSQL | PostgreSQL | PostgreSQL | PostgreSQL | PostgreSQL | PostgreSQL |
| ORM | Prisma 6 + Kysely | Django ORM | Prisma + Kysely | 自研 ORM | Prisma | PostgREST | Prisma |
| API | tRPC + REST v2 | REST (DRF) | tRPC + ts-rest | GraphQL (Yoga) | tRPC | REST + GraphQL | GraphQL |
| 认证 | 自研 | 自研 (Django) | Arctic + Passkeys | 自研 (JWT) | NextAuth.js | GoTrue (Go) | 自研 |
| 测试 | Vitest + Playwright | — | Playwright | Jest + Playwright | Jest + Playwright | — | Vitest |
| 异步任务 | Trigger.dev | Celery + RabbitMQ | Inngest | BullMQ + Redis | — | — | — |
| Git 规范 | Conventional Commits | Feature branches | Semantic Release | Conventional | Feature branches | Trunk-based | Feature branches |
| Pre-commit | husky + lint-staged | pre-commit (Python) | husky | husky + lint-staged | husky | — | husky |

### 2.2 行业共识 (8/8 项目一致)

| 共识 | 覆盖率 |
|------|--------|
| Monorepo 结构 | 8/8 |
| PostgreSQL 唯一数据库 | 8/8 |
| Docker Compose 本地开发 | 8/8 |
| GitHub Actions CI/CD | 8/8 |
| `.env.example` 环境模板 | 8/8 |

### 2.3 主流趋势 (6+/8 项目采用)

| 趋势 | 覆盖率 |
|------|--------|
| Tailwind CSS | 7/8 |
| Redis 配对使用 | 6/8 |
| TypeScript strict mode | 7/8 |
| Conventional Commits | 5/8 |
| husky pre-commit hooks | 6/8 |
| Playwright E2E | 5/8 |
| 结构化 JSON 日志 | 6/8 |
| OpenAPI / Swagger 文档 | 5/8 |

### 2.4 OpenSkill Studio 的特殊需求

与上述项目不同，OpenSkill Studio 是**教育 + 交付平台**，额外需要：

- **代码执行沙箱**（未来）— 类似 Gitpod 的安全执行环境
- **AI 评估管道**（未来）— 需要异步任务队列
- **文件存储**（作品/提交物）— 需要对象存储 → 验证了 MinIO 选择
- **多租户**（组织/班级）— 需要 PostgreSQL RLS
- **Python AI 生态**（LLM / 向量检索 / 数据分析）— 验证了 FastAPI 选择

---

## 3. 技术栈决策

### 3.1 决策矩阵

| 层级 | 选择 | 对标 | 替代 | 理由 |
|------|------|------|------|------|
| **Monorepo** | Turborepo + pnpm | Cal.com, Documenso, Formbricks | Nx | 更轻量、零配置、学习曲线低 |
| **包管理器** | pnpm 9 | Plane, Supabase, Hoppscotch | yarn, npm | 磁盘效率最高、workspace 支持最好 |
| **前端** | Next.js 15 (App Router) | Cal.com, Supabase, Formbricks | Remix, Vite+React | 生态最成熟、SSR/SSG/ISR/RSC 全支持 |
| **UI** | Tailwind CSS 4 + Shadcn/ui | Documenso, Supabase | Ant Design, MUI | 零运行时、copy-paste 可控、Radix a11y |
| **数据获取** | TanStack Query v5 | Cal.com, Documenso | SWR | 缓存策略更丰富、DevTools 更强 |
| **后端** | FastAPI (Python 3.12+) | Plane (Django 验证 Python 可行) | NestJS, Hono | AI 生态原生、异步性能好、OpenAPI 自动生成 |
| **ORM** | SQLAlchemy 2.0 (async) + Alembic | Plane (Django ORM) | Tortoise, SQLModel | 最成熟的 Python ORM，异步原生 |
| **数据库** | PostgreSQL 16 | 全部 8 个项目 | — | 行业唯一共识 |
| **缓存/队列** | Redis 7 | Cal.com, Plane, Twenty | — | Session / Cache / PubSub / Queue 全覆盖 |
| **对象存储** | MinIO (S3 兼容) | — | Cloudflare R2 | 本地开发友好，生产可切 S3 |
| **S3 客户端** | aioboto3 | — | boto3 (同步) | **必须用异步客户端，否则阻塞事件循环** |
| **API 风格** | REST + OpenAPI (`/api/v1/` 前缀) | Plane, Supabase | tRPC, GraphQL | 跨语言栈必须 REST；从 Day 1 带版本前缀 |
| **日志** | structlog (Python) + pino (TS) | Cal.com, Plane | stdlib logging | 结构化 JSON 日志，关联 request ID |
| **测试 (后端)** | pytest + httpx | Plane | unittest | Python 测试标准 |
| **测试 (前端)** | Vitest + Testing Library | Cal.com, Documenso | Jest | 更快、ESM 原生、Vite 生态一致 |
| **E2E 测试** | Playwright (Phase 2+) | Cal.com, Documenso, Twenty | Cypress | 多浏览器、更快、更稳定 |
| **Lint (TS)** | ESLint 9 + Prettier | Cal.com, Documenso | Biome | 生态最广，插件最多 |
| **Lint (Python)** | Ruff | Plane | flake8 + black | 单工具替代 flake8/black/isort，极快 |
| **Pre-commit** | husky + lint-staged (TS) + pre-commit (Py) | Cal.com, Documenso, Plane | — | 阻止坏代码进入仓库 |
| **CI/CD** | GitHub Actions | 全部 8 个项目 | — | 行业标准 |

### 3.2 为什么 FastAPI 而不是全栈 TypeScript？

Plane.so 用 **Django + DRF 拿到 42k stars**，证明 Python 后端完全可行。额外理由：

1. **AI 原生**：LLM 调用、向量检索、嵌入生成 — Python 生态领先 3 年以上
2. **数据处理**：学习者提交物分析、统计报表 — pandas/numpy 是标准
3. **FastAPI 性能**：异步性能接近 Node.js，自动 OpenAPI 文档
4. **类型桥接**：OpenAPI spec → `openapi-typescript` 自动生成 TS 类型，消除手动同步

---

## 4. 仓库结构

```
openskill-studio/
├── apps/
│   ├── web/                            # Next.js 前端
│   │   ├── src/
│   │   │   ├── app/                    # App Router 页面
│   │   │   │   ├── layout.tsx          # 根布局 (字体 / 主题 / Provider)
│   │   │   │   ├── page.tsx            # 首页
│   │   │   │   ├── error.tsx           # 全局错误边界
│   │   │   │   ├── not-found.tsx       # 404 页面
│   │   │   │   ├── loading.tsx         # 全局 loading
│   │   │   │   ├── globals.css         # Tailwind + CSS 变量 (设计令牌)
│   │   │   │   └── health/
│   │   │   │       └── page.tsx        # 健康检查页
│   │   │   ├── components/
│   │   │   │   └── ui/                # Shadcn/ui 组件 (Button, Card, …)
│   │   │   ├── lib/
│   │   │   │   ├── api.ts             # API 客户端 (fetch wrapper)
│   │   │   │   ├── query-client.ts    # TanStack Query 配置
│   │   │   │   └── utils.ts           # cn() 等工具函数
│   │   │   └── providers/
│   │   │       └── index.tsx          # QueryClientProvider + ThemeProvider
│   │   ├── public/
│   │   │   ├── favicon.ico
│   │   │   └── og-image.png           # Open Graph 默认图片
│   │   ├── __tests__/
│   │   ├── next.config.ts
│   │   ├── tailwind.config.ts
│   │   ├── tsconfig.json
│   │   ├── vitest.config.ts
│   │   └── package.json
│   │
│   └── api/                            # FastAPI 后端
│       ├── app/
│       │   ├── __init__.py
│       │   ├── main.py                 # FastAPI 入口 + 中间件栈
│       │   ├── config.py              # pydantic-settings 配置 (启动时全量校验)
│       │   ├── api/
│       │   │   ├── __init__.py
│       │   │   ├── deps.py            # 共享依赖 (get_db, get_redis, get_settings)
│       │   │   └── v1/                # API v1 路由组
│       │   │       ├── __init__.py
│       │   │       ├── router.py      # v1 聚合路由
│       │   │       └── endpoints/
│       │   │           ├── __init__.py
│       │   │           └── health.py
│       │   ├── core/
│       │   │   ├── __init__.py
│       │   │   ├── database.py        # SQLAlchemy async engine + session
│       │   │   ├── redis.py           # Redis 连接池
│       │   │   ├── storage.py         # S3/MinIO 抽象层 (aioboto3)
│       │   │   └── logging.py         # structlog 配置
│       │   ├── middleware/
│       │   │   ├── __init__.py
│       │   │   ├── request_id.py      # X-Request-ID 注入
│       │   │   ├── logging.py         # 请求/响应日志 (带 timing)
│       │   │   └── security.py        # 安全响应头
│       │   ├── schemas/               # Pydantic 请求/响应模型
│       │   │   ├── __init__.py
│       │   │   ├── base.py            # 统一响应信封
│       │   │   └── health.py
│       │   ├── models/                # SQLAlchemy ORM 模型 (Phase 2+)
│       │   │   └── __init__.py
│       │   ├── services/              # 业务逻辑层 (Phase 2+)
│       │   │   └── __init__.py
│       │   └── exceptions.py          # 全局异常 + 异常处理器
│       ├── migrations/                # Alembic
│       │   ├── env.py
│       │   └── versions/
│       ├── tests/
│       │   ├── __init__.py
│       │   ├── conftest.py
│       │   └── test_health.py
│       ├── alembic.ini                # Alembic 配置 (项目根目录，非 migrations 内)
│       ├── pyproject.toml
│       └── .pre-commit-config.yaml    # Python pre-commit hooks
│
├── packages/
│   ├── shared/                         # 共享类型 / 常量
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   └── api-types.ts          # ← OpenAPI 自动生成的 TS 类型
│   │   ├── tsconfig.json
│   │   └── package.json
│   ├── eslint-config/                  # 共享 ESLint 配置
│   │   ├── index.js
│   │   └── package.json
│   └── typescript-config/              # 共享 tsconfig
│       ├── base.json
│       ├── nextjs.json
│       └── package.json
│
├── docker/
│   ├── postgres/
│   │   └── init.sql
│   └── minio/
│       └── create-buckets.sh
│
├── .github/
│   ├── workflows/
│   │   └── ci.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   └── feature_request.yml
│   └── dependabot.yml                  # 依赖安全自动更新
│
├── docs/
│   └── design/
│       └── 001-bootstrap-architecture.md
│
├── docker-compose.yml
├── turbo.json
├── pnpm-workspace.yaml
├── package.json                        # 根 package.json (workspace scripts)
├── Makefile                            # 跨语言统一命令入口
├── .env.example
├── .gitignore
├── .editorconfig
├── .prettierrc
├── .prettierignore
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── LICENSE                             # AGPL-3.0 (与 Cal.com/Plane/Documenso 一致)
└── CLAUDE.md
```

### 4.1 与 V1 设计的关键差异

| 维度 | V1 (有缺陷) | V2 (修正) |
|------|-----------|----------|
| API 路径 | `/health` | `/api/v1/health` — 带版本前缀 |
| 路由组织 | `api/routes/` | `api/v1/endpoints/` — 版本化分组 |
| 错误处理 | 无 | `exceptions.py` + 全局异常处理器 |
| 中间件 | 仅 CORS | 4 层中间件栈 (RequestID → Logging → Security → CORS) |
| 响应模型 | 无 | `schemas/` 目录，Pydantic 模型覆盖全部端点 |
| 日志 | 无 | structlog 结构化日志 + request ID 关联 |
| 前端状态 | 裸 useEffect+fetch | TanStack Query |
| 前端错误 | 无 | error.tsx + not-found.tsx + loading.tsx |
| 类型共享 | 手动 | OpenAPI codegen 自动生成 |
| Git 规范 | 无 | Conventional Commits + husky |
| 安全头 | 无 | SecurityHeadersMiddleware |
| alembic.ini | 放在 migrations/ 内 | 放在 apps/api/ 根目录 |
| S3 客户端 | boto3 (同步！) | aioboto3 (异步) |
| 共享配置 | 无 | `packages/eslint-config` + `packages/typescript-config` |
| 开源治理 | 无 | LICENSE + CONTRIBUTING + CODE_OF_CONDUCT |

---

## 5. Monorepo 配置

### 5.1 pnpm-workspace.yaml

```yaml
packages:
  - "apps/*"
  - "packages/*"
```

### 5.2 turbo.json

```json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "dev": {
      "cache": false,
      "persistent": true
    },
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "dist/**"]
    },
    "lint": {
      "dependsOn": ["^build"]
    },
    "test": {
      "dependsOn": ["^build"]
    },
    "type-check": {
      "dependsOn": ["^build"]
    }
  }
}
```

### 5.3 根 package.json

```json
{
  "name": "openskill-studio",
  "private": true,
  "scripts": {
    "dev": "turbo dev",
    "dev:web": "turbo dev --filter=web",
    "dev:api": "cd apps/api && uv run uvicorn app.main:app --reload --reload-dir app --port 8000",
    "build": "turbo build",
    "lint": "turbo lint && cd apps/api && uv run ruff check .",
    "lint:fix": "turbo lint -- --fix && cd apps/api && uv run ruff check . --fix",
    "test": "turbo test && cd apps/api && uv run pytest",
    "test:web": "turbo test --filter=web",
    "test:api": "cd apps/api && uv run pytest",
    "type-check": "turbo type-check",
    "types:generate": "openapi-typescript http://localhost:8000/api/v1/openapi.json -o packages/shared/src/api-types.ts",
    "infra:up": "docker compose up -d",
    "infra:down": "docker compose down",
    "infra:reset": "docker compose down -v && docker compose up -d",
    "db:migrate": "cd apps/api && uv run alembic upgrade head",
    "db:generate": "cd apps/api && uv run alembic revision --autogenerate -m",
    "db:reset": "cd apps/api && uv run alembic downgrade base && uv run alembic upgrade head",
    "prepare": "husky"
  },
  "devDependencies": {
    "turbo": "^2",
    "husky": "^9",
    "lint-staged": "^15",
    "openapi-typescript": "^7"
  },
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{json,md,yml,yaml}": ["prettier --write"]
  },
  "packageManager": "pnpm@9.15.0",
  "engines": {
    "node": ">=22"
  }
}
```

### 5.4 内部包引用

```json
// apps/web/package.json
{
  "dependencies": {
    "@openskill/shared": "workspace:*"
  }
}
```

### 5.5 TypeScript 配置 (严格模式)

```json
// packages/typescript-config/base.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "forceConsistentCasingInFileNames": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "module": "ESNext",
    "target": "ES2022",
    "lib": ["ES2022"],
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "isolatedModules": true
  }
}
```

```json
// apps/web/tsconfig.json
{
  "extends": "@openskill/typescript-config/nextjs.json",
  "compilerOptions": {
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["src", "next-env.d.ts"],
  "exclude": ["node_modules"]
}
```

---

## 6. 基础设施架构

### 6.1 架构图

```
┌──────────────────────────────────────────────────────────────────┐
│                       Developer Machine                          │
│                                                                  │
│  ┌────────────────┐         ┌────────────────┐                  │
│  │   Next.js       │  /api/* │   FastAPI       │                  │
│  │   :3000         │────────▶│   :8000         │                  │
│  │  (pnpm dev)     │ rewrite │  (uvicorn)      │                  │
│  └────────────────┘         └───────┬─────────┘                  │
│                                     │                            │
│          ┌──────────────────────────┼──────────────────┐         │
│          ▼                          ▼                  ▼         │
│  ┌──────────────┐         ┌──────────────┐   ┌──────────────┐   │
│  │  PostgreSQL   │         │    Redis     │   │    MinIO      │   │
│  │  :5432        │         │    :6379     │   │  :9000 (API)  │   │
│  │  (Docker)     │         │   (Docker)   │   │  :9001 (Web)  │   │
│  └──────────────┘         └──────────────┘   └──────────────┘   │
│                                                                  │
│  关键: 前端通过 Next.js rewrites 代理 API 调用                     │
│        开发环境无跨域问题，生产环境通过反向代理统一入口                 │
└──────────────────────────────────────────────────────────────────┘
```

### 6.2 Docker Compose

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: openskill
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Profile: 用于 CI 或完整演示
  # docker compose --profile app up
  api:
    build: ./apps/api
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      postgres: { condition: service_healthy }
      redis: { condition: service_healthy }
      minio: { condition: service_healthy }
    profiles: ["app"]

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

### 6.3 本地 → 生产映射

| 本地 (Docker Compose) | 生产 | 说明 |
|----------------------|------|------|
| PostgreSQL container | Supabase / RDS / Neon | 托管 PostgreSQL |
| Redis container | Upstash / ElastiCache | 托管 Redis |
| MinIO container | AWS S3 / Cloudflare R2 | 对象存储 |
| Next.js rewrites | Nginx / Cloudflare / Vercel | 反向代理 |
| `pnpm dev` | Vercel / Cloudflare Pages | 前端部署 |
| `uvicorn` | Fly.io / Railway / ECS | 后端部署 |

### 6.4 环境变量

```bash
# .env.example

# ─── Application ─────────────────────────────────────────
APP_ENV=development           # development | staging | production
DEBUG=true
LOG_LEVEL=DEBUG               # DEBUG | INFO | WARNING | ERROR
LOG_FORMAT=console            # console (开发) | json (生产)

# ─── Database ────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/openskill
# 生产环境: 设置连接池大小
# DB_POOL_SIZE=20
# DB_MAX_OVERFLOW=10

# ─── Redis ───────────────────────────────────────────────
REDIS_URL=redis://localhost:6379/0

# ─── Object Storage (MinIO / S3) ────────────────────────
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=openskill
S3_REGION=us-east-1

# ─── Frontend ───────────────────────────────────────────
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000

# ─── API ────────────────────────────────────────────────
CORS_ORIGINS=["http://localhost:3000"]
API_PREFIX=/api/v1

# ─── Security ───────────────────────────────────────────
# SECRET_KEY=<generate-with: openssl rand -hex 32>
# JWT_SECRET=<generate-with: openssl rand -hex 32>
# JWT_EXPIRY_HOURS=24
```

---

## 7. 后端设计

### 7.1 依赖 (pyproject.toml)

```toml
[project]
name = "openskill-api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.34",
    "sqlalchemy[asyncio]>=2.0",
    "asyncpg>=0.30",
    "alembic>=1.14",
    "pydantic-settings>=2.7",
    "redis>=5.0",
    "aioboto3>=13.0",           # 异步 S3 客户端 (非 boto3!)
    "structlog>=24.0",
    "python-ulid>=3.0",         # 有序 ULID 主键
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "httpx>=0.28",
    "ruff>=0.8",
    "pre-commit>=4.0",
]
```

### 7.2 应用入口 + 中间件栈

```python
# app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.core.database import engine
from app.core.redis import redis_pool
from app.core.logging import setup_logging
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.api.v1.router import api_v1_router
from app.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时校验全部基础设施连接，失败则 fast-fail."""
    setup_logging(level=settings.log_level, fmt=settings.log_format)

    # 1. 验证 PostgreSQL
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))

    # 2. 验证 Redis
    r = redis_pool()
    await r.ping()

    # 3. 验证 MinIO bucket (存在则跳过，不存在则创建)
    # 由 core/storage.py ensure_bucket() 处理

    import structlog
    log = structlog.get_logger()
    log.info(
        "startup_complete",
        app_env=settings.app_env,
        database=settings.database_url.split("@")[-1],  # 脱敏
    )

    yield

    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="OpenSkill Studio API",
    version="0.1.0",
    docs_url="/api/v1/docs" if settings.debug else None,   # 生产环境禁用
    redoc_url="/api/v1/redoc" if settings.debug else None,
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

# ── 中间件栈 (执行顺序: 从下往上注册，从上往下执行) ──
# 1. 最外层: 注入 X-Request-ID
app.add_middleware(RequestIDMiddleware)
# 2. 请求/响应日志 (含耗时)
app.add_middleware(LoggingMiddleware)
# 3. 安全响应头
app.add_middleware(SecurityHeadersMiddleware)
# 4. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
)

# ── 异常处理器 ──
register_exception_handlers(app)

# ── 路由 ──
app.include_router(api_v1_router, prefix="/api/v1")
```

### 7.3 中间件详解

```python
# app/middleware/request_id.py
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
```

```python
# app/middleware/security.py
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response
```

### 7.4 配置管理 (启动时全量校验)

```python
# app/config.py
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_env: str = "development"
    debug: bool = True
    log_level: str = "DEBUG"
    log_format: str = "console"      # console | json

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/openskill"
    db_pool_size: int = 5
    db_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # S3 / MinIO
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "openskill"
    s3_region: str = "us-east-1"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # API
    api_prefix: str = "/api/v1"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


settings = Settings()
```

### 7.5 统一响应格式 + 错误处理

```python
# app/schemas/base.py — 统一响应信封
from typing import Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class DataResponse(BaseModel, Generic[T]):
    """单资源响应"""
    data: T


class ListResponse(BaseModel, Generic[T]):
    """列表响应 (带分页)"""
    data: list[T]
    meta: "PaginationMeta"


class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int
    has_more: bool


class ErrorDetail(BaseModel):
    code: str           # 机器可读: VALIDATION_ERROR, NOT_FOUND, ...
    message: str        # 人类可读
    details: list[Any] | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
```

```python
# app/exceptions.py — 全局异常处理
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import structlog

log = structlog.get_logger()


class AppError(Exception):
    """应用业务异常基类"""
    def __init__(self, code: str, message: str, status_code: int = 400, details=None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        log.warning("app_error", code=exc.code, message=exc.message,
                    request_id=getattr(request.state, "request_id", None))
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": "HTTP_ERROR", "message": exc.detail}},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        log.error("unhandled_exception", error=str(exc), type=type(exc).__name__,
                  request_id=getattr(request.state, "request_id", None))
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}},
        )
```

### 7.6 数据库连接

```python
# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=settings.db_pool_size,          # 开发: 5, 生产: 按 workers × pool_size ≤ max_connections 调
    max_overflow=settings.db_max_overflow,
    pool_pre_ping=True,                       # 连接复用前验活
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    """FastAPI 依赖注入: 每个请求一个 session."""
    async with AsyncSessionLocal() as session:
        yield session
```

### 7.7 Health 端点 (分层: liveness / readiness)

```python
# app/api/v1/endpoints/health.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str


class ReadinessResponse(BaseModel):
    status: str
    components: dict[str, str]


@router.get("/health", response_model=HealthResponse)
async def liveness():
    """Liveness: 进程是否存活 (无依赖检查)."""
    return HealthResponse(status="ok")


@router.get("/health/ready", response_model=ReadinessResponse)
async def readiness(db: AsyncSession = Depends(get_db)):
    """Readiness: 是否可以接受流量 (检查全部依赖)."""
    components: dict[str, str] = {}

    # PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
        components["database"] = "ok"
    except Exception:
        components["database"] = "error"

    # Redis
    try:
        from app.core.redis import redis_pool
        r = redis_pool()
        await r.ping()
        components["redis"] = "ok"
    except Exception:
        components["redis"] = "error"

    all_ok = all(v == "ok" for v in components.values())
    return ReadinessResponse(
        status="ok" if all_ok else "degraded",
        components=components,
    )
```

```python
# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints import health

api_v1_router = APIRouter()
api_v1_router.include_router(health.router)
```

### 7.8 后端分层架构

```
请求 → Middleware → Router → (Pydantic 验证) → Service → Repository → Model
                                                  ↑
                                            Depends(get_db)
                                            Depends(get_current_user)  # Phase 2
```

| 层级 | 目录 | 职责 | 规则 |
|------|------|------|------|
| Router | `api/v1/endpoints/` | HTTP 处理、请求/响应序列化 | 不含业务逻辑 |
| Schema | `schemas/` | Pydantic 请求/响应模型 | 与 ORM 模型解耦 |
| Service | `services/` | 业务逻辑、编排、事务边界 | 不依赖 HTTP 概念 |
| Model | `models/` | SQLAlchemy ORM 模型 | 纯数据定义 |
| Core | `core/` | 基础设施 (DB/Redis/S3) | 无业务概念 |

---

## 8. 前端设计

### 8.1 依赖

```json
{
  "dependencies": {
    "next": "^15",
    "react": "^19",
    "react-dom": "^19",
    "@tanstack/react-query": "^5",
    "next-themes": "^0.4",
    "clsx": "^2",
    "tailwind-merge": "^2"
  },
  "devDependencies": {
    "typescript": "^5",
    "tailwindcss": "^4",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "vitest": "^2",
    "@testing-library/react": "^16",
    "eslint": "^9",
    "eslint-plugin-jsx-a11y": "^6",
    "@openskill/eslint-config": "workspace:*",
    "@openskill/typescript-config": "workspace:*",
    "prettier": "^3",
    "prettier-plugin-tailwindcss": "^0.6"
  }
}
```

### 8.2 根布局

```tsx
// app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Providers } from "@/providers";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-sans",
});

export const metadata: Metadata = {
  title: {
    default: "OpenSkill Studio",
    template: "%s | OpenSkill Studio",
  },
  description: "Project-based training and delivery platform for AI creators.",
  openGraph: {
    title: "OpenSkill Studio",
    description: "Project-based training and delivery platform for AI creators.",
    url: process.env.NEXT_PUBLIC_APP_URL,
    siteName: "OpenSkill Studio",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <body className="min-h-screen bg-background font-sans antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

### 8.3 Provider 层

```tsx
// providers/index.tsx
"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "next-themes";
import { useState } from "react";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,       // 1 分钟内不重新请求
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
        {children}
      </ThemeProvider>
    </QueryClientProvider>
  );
}
```

### 8.4 API 客户端

```typescript
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}/api/v1${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    ...init,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(
      res.status,
      body?.error?.code ?? "UNKNOWN",
      body?.error?.message ?? `HTTP ${res.status}`,
    );
  }

  return res.json();
}
```

### 8.5 首页

```tsx
// app/page.tsx
export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h1 className="text-4xl font-bold tracking-tight">OpenSkill Studio</h1>
      <p className="text-lg text-muted-foreground">
        Project-based training and delivery platform for AI creators.
      </p>
    </main>
  );
}
```

### 8.6 健康检查页 (TanStack Query)

```tsx
// app/health/page.tsx
"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

interface HealthData {
  status: string;
}

export default function HealthPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["health"],
    queryFn: () => api<HealthData>("/health"),
    refetchInterval: 30_000, // 每 30 秒轮询
  });

  const status = isLoading ? "Checking..." : isError ? "Offline" : data?.status === "ok" ? "Online" : "Error";

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h1 className="text-2xl font-semibold">System Health</h1>
      <p className="text-lg">
        API Status:{" "}
        <span className={`font-mono font-bold ${status === "Online" ? "text-green-600" : "text-red-600"}`}>
          {status}
        </span>
      </p>
    </main>
  );
}
```

### 8.7 错误边界 + 404

```tsx
// app/error.tsx
"use client";

export default function GlobalError({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h1 className="text-2xl font-bold">Something went wrong</h1>
      <p className="text-muted-foreground">{error.message}</p>
      <button onClick={reset} className="rounded bg-primary px-4 py-2 text-primary-foreground">
        Try again
      </button>
    </main>
  );
}
```

```tsx
// app/not-found.tsx
export default function NotFound() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h1 className="text-4xl font-bold">404</h1>
      <p className="text-lg text-muted-foreground">Page not found</p>
    </main>
  );
}
```

### 8.8 Next.js 配置 (Rewrites + 安全头)

```typescript
// next.config.ts
import type { NextConfig } from "next";

const config: NextConfig = {
  // 开发代理: /api/* → FastAPI，消除跨域问题
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/:path*`,
      },
    ];
  },

  // 安全响应头
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
        ],
      },
    ];
  },
};

export default config;
```

### 8.9 设计令牌 (CSS 变量 + Shadcn/ui)

```css
/* globals.css */
@import "tailwindcss";

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 240 10% 3.9%;
    --card: 0 0% 100%;
    --card-foreground: 240 10% 3.9%;
    --primary: 240 5.9% 10%;
    --primary-foreground: 0 0% 98%;
    --secondary: 240 4.8% 95.9%;
    --secondary-foreground: 240 5.9% 10%;
    --muted: 240 4.8% 95.9%;
    --muted-foreground: 240 3.8% 46.1%;
    --destructive: 0 84.2% 60.2%;
    --border: 240 5.9% 90%;
    --ring: 240 5.9% 10%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 240 10% 3.9%;
    --foreground: 0 0% 98%;
    --card: 240 10% 3.9%;
    --card-foreground: 0 0% 98%;
    --primary: 0 0% 98%;
    --primary-foreground: 240 5.9% 10%;
    --secondary: 240 3.7% 15.9%;
    --secondary-foreground: 0 0% 98%;
    --muted: 240 3.7% 15.9%;
    --muted-foreground: 240 5% 64.9%;
    --destructive: 0 62.8% 30.6%;
    --border: 240 3.7% 15.9%;
    --ring: 240 4.9% 83.9%;
  }
}
```

### 8.10 前端组件约定

| 位置 | 用途 | 示例 |
|------|------|------|
| `components/ui/` | Shadcn/ui 原子组件 | Button, Input, Card, Dialog |
| `components/` | 共享业务组件 | Header, Footer, Sidebar, Logo |
| `app/(feature)/components/` | 路由组内组件 (co-location) | SkillCard, ProjectForm |
| `lib/` | 工具函数 | cn(), api(), formatDate() |
| `providers/` | Context Provider | QueryClient, Theme |

**规则**：

- 一个文件一个组件，PascalCase 命名
- 所有组件默认 Server Component，仅交互部分加 `"use client"`
- `eslint-plugin-jsx-a11y` 强制无障碍规范
- 所有用户可见字符串提取为常量（为 i18n 预留）

---

## 9. 跨语言类型共享

### 9.1 问题

Python 后端 + TypeScript 前端 = **类型定义会 drift**。

### 9.2 方案: OpenAPI Codegen (对标 Plane.so 的 REST + 独立类型)

```
FastAPI (Python)                TypeScript (Frontend)
     │                               ▲
     │ 自动生成                        │ 自动生成
     ▼                               │
/api/v1/openapi.json ──────▶ openapi-typescript ──▶ packages/shared/src/api-types.ts
```

```bash
# 生成命令
pnpm types:generate
# 等价于: npx openapi-typescript http://localhost:8000/api/v1/openapi.json -o packages/shared/src/api-types.ts
```

```typescript
// 前端使用自动生成的类型
import type { components } from "@openskill/shared/api-types";

type HealthResponse = components["schemas"]["HealthResponse"];
```

**CI 保障**: GitHub Actions 中验证生成的类型文件是否与 OpenAPI spec 同步——如果有 diff 则 CI 失败。

---

## 10. 安全设计

### 10.1 Phase 1 安全措施

| 层级 | 措施 | 实现 |
|------|------|------|
| HTTP 头 | 安全响应头 | `SecurityHeadersMiddleware` + `next.config.ts headers` |
| CORS | 白名单限定 | 仅允许 `CORS_ORIGINS` 列表中的域 |
| 输入验证 | Pydantic 模型 | 全部端点使用 `response_model` + 请求体 Schema |
| 依赖安全 | 自动扫描 | `.github/dependabot.yml` 自动 PR |
| 密钥管理 | 环境变量 | `.env` 不入仓库，`.gitignore` 排除 |
| API 文档 | 环境隔离 | 生产环境禁用 `/docs` 和 `/redoc` |

### 10.2 Phase 2+ 安全路线图

| 功能 | 技术选型 | 说明 |
|------|---------|------|
| 认证 | JWT (access + refresh) | 独立 Auth 模块 |
| 授权 | RBAC + PostgreSQL RLS | 角色: admin, instructor, student |
| 限流 | slowapi + Redis | 按 IP / 用户 / 端点分级限流 |
| CSP | report-only → enforce | 逐步收紧 Content-Security-Policy |
| HTTPS | 强制 HSTS | 反向代理层配置 |

### 10.3 Dependabot 配置

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: npm
    directory: /
    schedule:
      interval: weekly
    groups:
      production:
        patterns: ["*"]
        exclude-patterns: ["@types/*", "eslint*", "prettier*"]
      dev:
        patterns: ["@types/*", "eslint*", "prettier*"]

  - package-ecosystem: pip
    directory: /apps/api
    schedule:
      interval: weekly

  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
```

---

## 11. 可观测性

### 11.1 日志架构

```python
# app/core/logging.py
import structlog


def setup_logging(level: str = "DEBUG", fmt: str = "console"):
    """
    开发环境: 彩色易读格式 (console)
    生产环境: JSON 格式 (可被 Datadog/Loki/ELK 采集)
    """
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if fmt == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(structlog, level.upper(), structlog.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )
```

### 11.2 请求日志中间件

```python
# app/middleware/logging.py
import time
import structlog
from starlette.middleware.base import BaseHTTPMiddleware

log = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start

        log.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=round(elapsed * 1000, 2),
            request_id=getattr(request.state, "request_id", None),
        )
        return response
```

### 11.3 日志输出示例

```
# 开发环境 (console 格式)
2026-08-13 10:30:01 [info] http_request  method=GET path=/api/v1/health status=200 duration_ms=3.21 request_id=a1b2c3d4

# 生产环境 (JSON 格式)
{"event":"http_request","method":"GET","path":"/api/v1/health","status":200,"duration_ms":3.21,"request_id":"a1b2c3d4","timestamp":"2026-08-13T10:30:01.000000Z","level":"info"}
```

### 11.4 前端错误追踪 (Phase 2+)

```
Phase 1: console.error (足够)
Phase 2: Sentry (错误监控)
Phase 3: PostHog (产品分析, 开源)
```

---

## 12. 测试策略

### 12.1 测试金字塔

```
         ╱╲
        ╱E2E╲            Playwright — Phase 2+ (关键用户流程)
       ╱──────╲
      ╱ Integra-╲        httpx + TestClient / React Testing Library
     ╱  tion     ╲       测试 API 端点、组件交互
    ╱──────────────╲
   ╱     Unit       ╲    pytest + Vitest
  ╱   (最多最快)      ╲   纯函数、工具库、Schema 验证
 ╱────────────────────╲
```

### 12.2 后端测试

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
```

```python
# tests/test_health.py
import pytest


@pytest.mark.asyncio
async def test_liveness_returns_ok(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_readiness_checks_components(client):
    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert "components" in data
    assert "database" in data["components"]


@pytest.mark.asyncio
async def test_404_returns_error_envelope(client):
    response = await client.get("/api/v1/nonexistent")
    assert response.status_code in (404, 405)
    data = response.json()
    assert "error" in data
    assert "code" in data["error"]
```

### 12.3 前端测试

```typescript
// __tests__/api.test.ts
import { describe, it, expect, vi } from "vitest";
import { api, ApiError } from "@/lib/api";

describe("api client", () => {
  it("should throw ApiError on non-ok response", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }), {
        status: 404,
      }),
    );

    await expect(api("/missing")).rejects.toThrow(ApiError);
  });
});
```

### 12.4 测试覆盖率目标

| 层级 | Phase 1 目标 | 长期目标 |
|------|------------|---------|
| 后端 Unit | 核心路由 100% | 80%+ |
| 前端 Unit | API client, utils | 70%+ |
| E2E | — | 关键路径 (登录 → 创建 → 提交) |

---

## 13. 开发者体验

### 13.1 统一命令入口 (Makefile)

```makefile
# Makefile — 跨语言统一命令，不需要记住 pnpm/uv/docker 区别
.PHONY: dev build test lint install infra-up infra-down db-migrate

# ─── 安装 ───────────────────────────────────────────────
install:                          ## 安装全部依赖
	pnpm install
	cd apps/api && uv sync

# ─── 开发 ───────────────────────────────────────────────
dev:                              ## 启动前后端开发服务器
	pnpm dev

dev-web:                          ## 仅启动前端
	pnpm dev:web

dev-api:                          ## 仅启动后端 (带热重载)
	cd apps/api && uv run uvicorn app.main:app --reload --reload-dir app --port 8000

# ─── 基础设施 ────────────────────────────────────────────
infra-up:                         ## 启动 Docker 基础设施
	docker compose up -d

infra-down:                       ## 停止基础设施
	docker compose down

infra-reset:                      ## 重置基础设施 (清除数据)
	docker compose down -v && docker compose up -d

# ─── 数据库 ──────────────────────────────────────────────
db-migrate:                       ## 运行数据库迁移
	cd apps/api && uv run alembic upgrade head

db-generate:                      ## 生成迁移文件
	cd apps/api && uv run alembic revision --autogenerate -m "$(msg)"

db-reset:                         ## 重置数据库
	cd apps/api && uv run alembic downgrade base && uv run alembic upgrade head

# ─── 质量 ────────────────────────────────────────────────
lint:                             ## 全量 lint
	pnpm lint

test:                             ## 全量测试
	pnpm test

type-check:                       ## TypeScript 类型检查
	pnpm type-check

types-generate:                   ## 从 OpenAPI 生成 TS 类型
	pnpm types:generate

# ─── 构建 ────────────────────────────────────────────────
build:                            ## 构建全部
	pnpm build

help:                             ## 显示帮助
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
```

### 13.2 新开发者上手流程 (一键启动)

```bash
# 1. 克隆
git clone https://github.com/Phixsura/OpenSkill-Studio.git
cd OpenSkill-Studio

# 2. 安装
make install              # pnpm install + uv sync

# 3. 配置
cp .env.example .env

# 4. 启动基础设施
make infra-up             # docker compose up -d (Postgres + Redis + MinIO)

# 5. 数据库迁移
make db-migrate

# 6. 启动开发
make dev                  # 同时启动 Next.js :3000 + FastAPI :8000

# → 打开 http://localhost:3000
# → /health 页面显示 "API Status: Online"
```

### 13.3 Git 工作流

| 约定 | 规范 |
|------|------|
| 分支命名 | `feature/xxx`, `fix/xxx`, `docs/xxx`, `chore/xxx` |
| 提交格式 | Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:` |
| 合并策略 | Squash merge to `main` |
| 保护规则 | `main` 分支: 必须 PR + CI 通过 + 1 reviewer |

### 13.4 Pre-commit Hooks

```json
// .husky/pre-commit
#!/bin/sh
pnpm lint-staged
cd apps/api && uv run pre-commit run --files $(git diff --cached --name-only -- 'apps/api/**')
```

### 13.5 编辑器配置

```ini
# .editorconfig
root = true

[*]
indent_style = space
indent_size = 2
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.py]
indent_size = 4

[Makefile]
indent_style = tab
```

```json
// .vscode/extensions.json (推荐扩展)
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "charliermarsh.ruff",
    "ms-python.python",
    "ms-python.vscode-pylance"
  ]
}
```

---

## 14. CI/CD 流水线

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint-frontend:
    name: Lint (Frontend)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm type-check

  lint-backend:
    name: Lint (Backend)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: cd apps/api && uv sync
      - run: cd apps/api && uv run ruff check .
      - run: cd apps/api && uv run ruff format --check .

  test-frontend:
    name: Test (Frontend)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: pnpm --filter web test

  test-backend:
    name: Test (Backend)
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: openskill_test
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U postgres"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7-alpine
        ports: ["6379:6379"]
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: cd apps/api && uv sync
      - run: cd apps/api && uv run pytest -v
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/openskill_test
          REDIS_URL: redis://localhost:6379/0

  # OpenAPI 类型同步检查
  types-sync:
    name: Types Sync Check
    runs-on: ubuntu-latest
    needs: [test-backend]
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: pnpm }
      - uses: astral-sh/setup-uv@v5
      - run: pnpm install --frozen-lockfile
      - run: cd apps/api && uv sync
      # 启动 API 提取 OpenAPI spec
      - run: |
          cd apps/api && uv run python -c "
          import json
          from app.main import app
          from fastapi.openapi.utils import get_openapi
          spec = get_openapi(title=app.title, version=app.version, routes=app.routes)
          print(json.dumps(spec))
          " > /tmp/openapi.json
      - run: npx openapi-typescript /tmp/openapi.json -o /tmp/api-types.ts
      - run: diff packages/shared/src/api-types.ts /tmp/api-types.ts || (echo "Types out of sync! Run 'pnpm types:generate'" && exit 1)

  build:
    name: Build
    runs-on: ubuntu-latest
    needs: [lint-frontend, lint-backend, test-frontend, test-backend]
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: pnpm build
```

---

## 15. 开源治理

### 15.1 License: AGPL-3.0

| 选项 | 代表项目 | 特点 | 选择 |
|------|---------|------|------|
| **AGPL-3.0** | Cal.com, Plane, Documenso | 强 copyleft，SaaS 提供商也必须开源 | ✅ |
| Apache 2.0 | Supabase | 宽松，允许闭源 fork | — |
| MIT | Hoppscotch | 最宽松 | — |

理由：OpenSkill Studio 作为教育平台，选择 AGPL-3.0 与 Cal.com/Plane/Documenso 保持一致——鼓励社区贡献，防止闭源竞品。

### 15.2 CONTRIBUTING.md (概要)

```markdown
# Contributing to OpenSkill Studio

## Development Setup
See README.md for local setup instructions.

## Code Style
- Frontend: ESLint + Prettier (auto-fixed on commit)
- Backend: Ruff (auto-fixed on commit)

## Commit Convention
We use Conventional Commits: feat:, fix:, docs:, chore:, refactor:, test:

## Pull Request Process
1. Fork → feature branch → PR to main
2. All CI checks must pass
3. 1 reviewer approval required
4. Squash merge

## Issue Reporting
Use GitHub Issue templates (bug report / feature request).
```

### 15.3 CODE_OF_CONDUCT.md

采用 [Contributor Covenant v2.1](https://www.contributor-covenant.org/) — 开源项目事实标准。

---

## 16. 未来扩展预留

### 16.1 目录扩展路径

```
packages/
├── shared/          # ← Phase 1 (当前)
├── ui/              # ← Phase 2: Shadcn 组件库抽取
├── email/           # ← Phase 3: 邮件模板 (对标 Documenso)

apps/
├── web/             # ← Phase 1 (当前)
├── api/             # ← Phase 1 (当前)
└── worker/          # ← Phase 3: 异步任务处理 (ARQ + Redis)
```

### 16.2 后端模块路线图

```
app/api/v1/endpoints/
├── health.py           # Phase 1 ✓
├── auth.py             # Phase 2: JWT 认证
├── users.py            # Phase 2: 用户管理
├── organizations.py    # Phase 3: 组织/多租户
├── skills.py           # Phase 3: 技能模块
├── projects.py         # Phase 3: 项目管理
├── submissions.py      # Phase 4: 提交物
└── evaluations.py      # Phase 4: AI 评估
```

### 16.3 架构决策预留

| 未来功能 | 技术选型 | 对标 |
|---------|---------|------|
| 认证 | JWT (access + refresh) + RBAC | Supabase GoTrue |
| 多租户 | PostgreSQL RLS + org_id | Plane |
| 文件上传 | aioboto3 → MinIO/S3 抽象层 | Supabase Storage |
| 异步任务 | ARQ (async-native, 轻于 Celery) | Plane (Celery) |
| AI 评估 | 独立 Worker + LLM 管道 | 创新点 |
| 实时通知 | Redis PubSub + WebSocket | Supabase Realtime |
| 搜索 | PostgreSQL FTS → Meilisearch | — |
| Feature flags | 数据库驱动 / PostHog | Cal.com |
| 分析 | PostHog (开源) | Cal.com, Documenso |
| i18n | next-intl | Cal.com |

---

## 17. 验收标准映射

| # | Issue #1 验收项 | 方案章节 | 关键设计点 |
|---|----------------|---------|-----------|
| 1 | 仓库结构初始化 | §4, §5 | Turborepo + pnpm workspace |
| 2 | Next.js 前端本地运行 | §8 | App Router + Shadcn/ui + TanStack Query |
| 3 | FastAPI 后端本地运行 | §7 | 4 层中间件 + 结构化日志 + 异常处理 |
| 4 | PostgreSQL 连接正常 | §7.6 | async engine + pool_pre_ping |
| 5 | Redis 连接正常 | §7.2 | lifespan 启动时 ping 验证 |
| 6 | MinIO 服务本地运行 | §6.2 | Docker + curl 健康检查 |
| 7 | GET /health 返回 200 | §7.7 | 分层: liveness + readiness |
| 8 | 前端展示后端健康状态 | §8.6 | TanStack Query + 轮询 |
| 9 | .env.example 包含 | §6.4 | 全量配置 + 注释 |
| 10 | Docker Compose 启动 | §6.2 | Postgres + Redis + MinIO + profiles |
| 11 | README 本地启动指南 | §13.2 | 6 步一键启动 |
| 12 | Lint 命令通过 | §13.1 | ESLint + Prettier + Ruff |
| 13 | 基础测试命令通过 | §12 | pytest + Vitest |

---

## 18. 实施计划

### Phase 1: 骨架搭建 (~2h)

1. 初始化 Monorepo (pnpm + Turborepo + tsconfig + eslint-config)
2. 初始化 Next.js 前端 (App Router + Tailwind + Shadcn/ui + 设计令牌)
3. 初始化 FastAPI 后端 (uv + 中间件栈 + structlog + 异常处理)
4. 创建 Docker Compose (Postgres + Redis + MinIO，含 healthcheck)
5. 配置环境变量 (.env.example + .gitignore)

### Phase 2: 连通验证 (~1h)

6. 实现 `/api/v1/health` + `/api/v1/health/ready` 端点
7. 实现 SQLAlchemy async engine + Alembic 初始化
8. 实现前端 Health 页面 (TanStack Query)
9. 配置 Next.js rewrites 代理
10. 验证 PostgreSQL / Redis / MinIO 全链路

### Phase 3: 开发体验 + 质量 (~1.5h)

11. Makefile 统一命令
12. ESLint + Prettier + Ruff + .editorconfig
13. husky + lint-staged pre-commit hooks
14. OpenAPI → TypeScript 类型生成管道
15. 编写后端测试 + 前端测试
16. GitHub Actions CI (lint + test + build + types-sync)

### Phase 4: 开源治理 (~30min)

17. README.md (完整本地启动文档)
18. CONTRIBUTING.md
19. CODE_OF_CONDUCT.md (Contributor Covenant)
20. LICENSE (AGPL-3.0)
21. CLAUDE.md (AI 辅助开发指南)
22. GitHub Issue/PR 模板 + Dependabot

---

## ADR 元数据

- **Status**: Proposed
- **Decision**: Bootstrap OpenSkill Studio with Turborepo + Next.js + FastAPI + PostgreSQL monorepo
- **Context**: Greenfield project, no existing code. Must support future AI evaluation pipeline.
- **Consequences**: Polyglot stack (TS + Python) requires OpenAPI codegen for type safety. Higher DX investment upfront (Makefile, pre-commit, CI) pays off at scale.

---

*V2 — 修正 60 个审查维度后的完整设计。将随项目演进持续更新。*
