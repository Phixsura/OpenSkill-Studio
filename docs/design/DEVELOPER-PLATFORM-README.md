# OpenSkill Developer Platform

> Build apps, connectors, and extensions for OpenSkill Studio

## Overview

The OpenSkill Developer Platform enables third-party developers to extend the platform without modifying core code. Build custom connectors, workflow adapters, UI extensions, analytics tools, and automation apps that integrate seamlessly with OpenSkill Studio.

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Developer Portal (Web UI)                       │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌───────┐ │
│  │Create│ │Build │ │Test  │ │Review│ │Publish│ │
│  │App   │ │Code  │ │Local │ │Queue │ │Market │ │
│  └──────┘ └──────┘ └──────┘ └──────┘ └───────┘ │
└─────────────────────────────────────────────────┘
        │           │           │
        ▼           ▼           ▼
┌───────────────────────────────────────────┐
│  Platform API (60+ endpoints)              │
│  ┌────────┐ ┌────────┐ ┌────────────────┐ │
│  │OAuth2  │ │API Keys│ │Event Dispatch  │ │
│  │Flow    │ │osk_app_│ │35 event types  │ │
│  └────────┘ └────────┘ └────────────────┘ │
│  ┌────────┐ ┌────────┐ ┌────────────────┐ │
│  │Sandbox │ │Manifest│ │Conformance     │ │
│  │Runtime │ │Validate│ │Suite           │ │
│  └────────┘ └────────┘ └────────────────┘ │
└───────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────┐
│  Database (13 tables)                      │
│  developer_accounts, developer_apps,       │
│  app_versions, app_installations,          │
│  app_api_keys, app_event_subscriptions,    │
│  app_automation_rules, app_secrets,        │
│  app_ui_extensions, sandbox_executions,    │
│  app_review_submissions, app_signing_keys, │
│  app_webhook_deliveries                    │
└───────────────────────────────────────────┘
```

## App Categories

| Category | Icon | Description |
|----------|------|-------------|
| Connector | 🔌 | LMS, HRIS, CRM integrations |
| Workflow Adapter | ⚡ | AI provider adapters |
| UI Extension | 🖥️ | Dashboard cards, panels |
| Analytics | 📊 | Reporting and insights |
| Automation | 🤖 | Event-driven workflows |
| Content Pack | 📦 | Skill & workflow bundles |
| Ecosystem Source | 🌐 | External data sources |

## App Lifecycle

```
draft → testing → submitted → approved → published → deprecated → revoked
```

## SDKs

### TypeScript (`@openskill/sdk`)
- API client with typed resources
- Extension SDK for iframe UI extensions (postMessage protocol)
- Full TypeScript types for all entities

### Python (`openskill-sdk`)
- Async httpx-based API client
- ProviderAdapter base class for workflow adapters
- EcosystemSourceAdapter for data sources

## Permission System

42 granular scopes organized by category:
- `read:*` / `write:*` — data access
- `subscribe:events` — event subscriptions
- `extend:ui` — UI extensions
- `run:background_jobs` — sandbox execution
- `export:analytics` — data export

## Event System

35 canonical event types across 10 categories:
- Organization, Cohort, Project, Submission
- Pack, Workflow, Talent, Marketplace
- Evaluation, App

Events delivered via HMAC-SHA256 signed webhooks with exponential backoff retry.

## Security

- Sandbox: subprocess isolation with CPU/memory/time limits
- SSRF: DNS resolution + IP range blocking on all outbound calls
- OAuth2: authorization code flow with scope validation
- API Keys: SHA-256 hashed, scoped, revocable
- Secrets: Fernet encrypted, write-only
- Manifest: validated against 42 scopes + blocked networks
- Conformance: 10-check automated validation suite
- Review: automated + human review before publishing

## API Reference

### Developer Accounts (5 endpoints)
### Apps (10 endpoints)
### Versions (3 endpoints)
### API Keys (3 endpoints)
### Installations (6 endpoints)
### Secrets (3 endpoints)
### Event Subscriptions (3 endpoints)
### Automation Rules (3 endpoints)
### Observability (8 endpoints)
### Marketplace (2 endpoints)
### OAuth 2.0 (2 endpoints)
### Developer Tools (7 endpoints)
### Batch Operations (3 endpoints)
### Admin (4 endpoints)

Total: 60+ endpoints

## Tests

227 integration tests covering:
- Full E2E lifecycle (25-step flow)
- Schema validation (25 manifest scenarios)
- Security (SSRF, IDOR, auth, scopes)
- Compatibility checking (semver, breaking changes)
- Batch operations (multi-org upgrade, version pinning)
- OAuth flow (authorize, token, scopes)
- Analytics and observability
