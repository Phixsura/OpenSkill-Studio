# ADR-016 — OpenSkill Developer Platform: Extension SDK, Sandboxed Apps & Connector Marketplace

**Status:** Accepted  
**Date:** 2026-10-22  
**Relates to:** ADR-009 (Skill Pack Registry), ADR-010 (Workflow Packs), ADR-011 (Provider Capability), ADR-014 (SaaS Commercialization), Issue #44

---

## Context

OpenSkill Studio's growth depends on first-party development. A real ecosystem needs third parties to extend the platform without modifying core code — custom skill types, evaluation rubrics, LMS/HRIS/CRM connectors, workflow adapters, UI widgets, and marketplace distribution.

Industry leaders (Shopify, Atlassian Forge, GitHub Apps, Stripe Apps, Figma, Slack, Salesforce, Zapier, Notion Workers) converge on a common architecture: **declarative manifest → scoped permissions → sandboxed runtime → marketplace distribution**.

---

## Decision

### Part A — Developer Organization & App Model

#### Entities

```
DeveloperAccount
  ├── id: ULID
  ├── owner_user_id: FK(users)
  ├── org_id: FK(organizations) — nullable, for org-owned dev accounts
  ├── display_name: str(100)
  ├── slug: str(60) — unique, URL-safe
  ├── website_url: str(500) — nullable
  ├── support_email: str(255)
  ├── verified: bool — platform-verified publisher
  ├── status: enum(active, suspended, revoked)
  ├── created_at, updated_at

DeveloperApp
  ├── id: ULID
  ├── developer_id: FK(developer_accounts)
  ├── name: str(100)
  ├── slug: str(60) — unique within developer
  ├── description: text
  ├── icon_url: str(500)
  ├── homepage_url: str(500)
  ├── privacy_policy_url: str(500) — required for public
  ├── category: enum(connector, workflow_adapter, ui_extension,
  │     analytics, automation, content_pack, ecosystem_source)
  ├── visibility: enum(private, unlisted, public)
  ├── status: enum(draft, testing, submitted, approved,
  │     published, deprecated, revoked)
  ├── manifest: JSONB — capability manifest (see Part D)
  ├── oauth_client_id: str(64) — auto-generated
  ├── oauth_client_secret_hash: str — bcrypt
  ├── redirect_uris: JSONB — array of allowed URIs
  ├── webhook_url: str(500) — app-level webhook endpoint
  ├── webhook_secret_hash: str
  ├── created_at, updated_at

AppVersion
  ├── id: ULID
  ├── app_id: FK(developer_apps)
  ├── version: str(20) — semver
  ├── manifest: JSONB — frozen at publish
  ├── changelog: text
  ├── content_hash: str(64) — SHA-256
  ├── signature: str — publisher signature
  ├── review_status: enum(pending, approved, rejected, revoked)
  ├── review_notes: text
  ├── reviewed_by: FK(users) — nullable
  ├── reviewed_at: timestamp
  ├── min_platform_version: str(10)
  ├── created_at

AppInstallation
  ├── id: ULID
  ├── app_id: FK(developer_apps)
  ├── app_version_id: FK(app_versions)
  ├── org_id: FK(organizations)
  ├── tenant_id: FK(tenant_accounts) — nullable
  ├── installed_by: FK(users)
  ├── status: enum(active, suspended, uninstalled)
  ├── granted_permissions: JSONB — subset of manifest permissions
  ├── config: JSONB — tenant-specific config values
  ├── pinned_version: bool — false = auto-update
  ├── created_at, updated_at, uninstalled_at

AppApiKey
  ├── id: ULID
  ├── app_id: FK(developer_apps)
  ├── installation_id: FK(app_installations) — nullable
  ├── key_prefix: str(8) — "osk_app_"
  ├── key_hash: str — SHA-256
  ├── scopes: JSONB — granted API scopes
  ├── rate_limit_tier: enum(standard, elevated, unlimited)
  ├── last_used_at: timestamp
  ├── expires_at: timestamp — nullable
  ├── revoked_at: timestamp — nullable
  ├── created_at
```

#### App Lifecycle State Machine

```
draft ──► testing ──► submitted ──► approved ──► published
  │          │            │                         │
  │          │            ▼                         ▼
  │          │        rejected ──► draft        deprecated
  │          │                                      │
  ▼          ▼                                      ▼
(delete)  (delete)                              revoked
```

- `draft`: Developer building, no installations allowed
- `testing`: Developer + designated test orgs can install
- `submitted`: Under platform review
- `approved`: Review passed, developer can publish
- `published`: Available per visibility (private/unlisted/public)
- `deprecated`: Existing installs work, no new installs
- `revoked`: Kill switch — all installations suspended

---

### Part B — Public API & OAuth2

#### API Key Authentication

```
Authorization: Bearer osk_app_XXXXXXXXXXXX
```

Keys scoped to installation (org-bound) or app-global (developer tools). SHA-256 hashed storage, `osk_app_` prefix for grep-ability. Rate limits: 1000 req/hour standard, 5000 elevated.

#### OAuth2 Authorization Code Flow

```
GET /api/v1/oauth/authorize?
    client_id=<app.oauth_client_id>&
    redirect_uri=<registered_uri>&
    scope=read:cohorts write:projects subscribe:events&
    state=<csrf_token>&
    response_type=code

POST /api/v1/oauth/token
    grant_type=authorization_code&
    code=<auth_code>&
    client_id=<client_id>&
    client_secret=<client_secret>&
    redirect_uri=<redirect_uri>

Response: { access_token, refresh_token, expires_in, scope, token_type }
```

#### API Versioning

Public API lives at `/api/v1/` (existing). Breaking changes require version bump. Deprecation header: `Sunset: <date>`, `Deprecation: true`. 6-month deprecation window.

#### Standard Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1698000000
X-Request-Id: <ulid>
Idempotency-Key: <client-provided>  (on POST/PATCH)
```

---

### Part C — Extension Capability Manifest

Every app declares capabilities in `manifest.json`:

```json
{
  "schema_version": "1.0",
  "app": {
    "name": "Acme LMS Connector",
    "slug": "acme-lms",
    "version": "1.2.0",
    "category": "connector",
    "min_platform_version": "1.0.0"
  },
  "permissions": [
    "read:organizations",
    "read:cohorts",
    "read:cohort_members",
    "write:project_results",
    "read:skill_progress",
    "subscribe:events"
  ],
  "scopes": {
    "data": ["cohorts", "projects", "submissions", "skills"],
    "events": ["submission.completed", "cohort.member_added"],
    "ui": ["dashboard_card", "cohort_tool"],
    "capabilities": ["connector", "background_job"]
  },
  "oauth": {
    "redirect_uris": ["https://acme.example.com/callback"],
    "token_endpoint_auth_method": "client_secret_post"
  },
  "sandbox": {
    "runtime": "nodejs20",
    "memory_mb": 128,
    "timeout_seconds": 30,
    "network": {
      "allowed_hosts": ["api.acme-lms.com"],
      "egress_policy": "allowlist"
    }
  },
  "ui_extensions": [
    {
      "surface": "dashboard_card",
      "title": "LMS Sync Status",
      "entry": "ui/dashboard-card.html",
      "viewport": { "width": 400, "height": 300 }
    }
  ],
  "event_subscriptions": ["submission.completed", "cohort.member_added", "project.published"],
  "secrets": [
    { "key": "LMS_API_KEY", "description": "Acme LMS API key", "required": true },
    { "key": "LMS_WEBHOOK_SECRET", "description": "Webhook signing key" }
  ],
  "config_schema": {
    "type": "object",
    "properties": {
      "lms_base_url": { "type": "string", "format": "uri" },
      "sync_interval_minutes": { "type": "integer", "minimum": 5, "maximum": 1440, "default": 60 }
    },
    "required": ["lms_base_url"]
  }
}
```

#### Permission Taxonomy (42 scopes)

| Category      | Permissions                                                                      |
| ------------- | -------------------------------------------------------------------------------- |
| Organizations | `read:organizations`, `write:organizations`                                      |
| Members       | `read:members`, `write:members`                                                  |
| Cohorts       | `read:cohorts`, `write:cohorts`, `read:cohort_members`                           |
| Projects      | `read:projects`, `write:projects`, `read:submissions`, `write:project_results`   |
| Skills        | `read:skills`, `write:skills`, `read:skill_progress`                             |
| Packs         | `read:packs`, `write:packs`, `read:installations`                                |
| Workflows     | `read:workflows`, `write:workflows`, `read:workflow_runs`, `write:workflow_runs` |
| Providers     | `read:providers`, `write:providers`, `read:credentials`                          |
| Talent        | `read:talent`, `write:talent`, `read:passports`, `read:opportunities`            |
| Evaluation    | `read:evaluations`, `write:evaluations`                                          |
| Matching      | `read:matching`, `write:matching`                                                |
| Marketplace   | `read:marketplace`, `write:marketplace_listings`                                 |
| Events        | `subscribe:events`                                                               |
| UI            | `extend:ui`                                                                      |
| Analytics     | `read:analytics`, `export:analytics`                                             |
| Admin         | `read:settings`, `write:settings`                                                |
| Users         | `read:users`, `read:user_profiles`                                               |
| Background    | `run:background_jobs`                                                            |

---

### Part D — Sandboxed Runtime

Third-party code **never** runs in the main API process.

#### Architecture: Subprocess Isolation

```
┌─────────────────────────────────────┐
│  OpenSkill API (FastAPI)            │
│  ┌───────────────┐                  │
│  │ Sandbox       │  spawn/manage    │
│  │ Manager       │◄────────────────┐│
│  └───────┬───────┘                 ││
│          │ subprocess.Popen        ││
│          ▼                         ││
│  ┌───────────────────┐             ││
│  │ Sandbox Worker    │   stdin/out  ││
│  │ (isolated proc)   │◄───────────►││
│  │ ┌───────────────┐ │   JSON-RPC  ││
│  │ │ App Code      │ │             ││
│  │ │ (user script) │ │             ││
│  │ └───────────────┘ │             ││
│  │ CPU: cgroup limit │             ││
│  │ MEM: 128MB max    │             ││
│  │ NET: egress policy│             ││
│  │ TIME: 30s timeout │             ││
│  └───────────────────┘             │
└─────────────────────────────────────┘
```

#### Sandbox Constraints

| Resource       | Limit                                    | Enforcement                       |
| -------------- | ---------------------------------------- | --------------------------------- |
| CPU time       | 5s default, 30s max                      | `resource.setrlimit` / cgroup     |
| Memory         | 128MB default, 512MB max                 | `resource.setrlimit` / cgroup     |
| Execution time | 30s default, 300s max                    | `asyncio.wait_for`                |
| Network egress | Allowlist only                           | iptables / proxy                  |
| Filesystem     | Read-only `/app`, writable `/tmp` (10MB) | mount namespace                   |
| DB access      | None — API calls only                    | No credentials in env             |
| Secrets        | Injected by reference, write-only        | `OPENSKILL_SECRET_<KEY>` env vars |
| Concurrency    | 1 execution per installation at a time   | Queue + lock                      |

#### Execution Model

```python
# Sandbox manager interface
class SandboxManager:
    async def execute(
        self,
        app_version_id: str,
        installation_id: str,
        function_name: str,
        payload: dict,
        *,
        timeout_seconds: int = 30,
        memory_mb: int = 128,
    ) -> SandboxResult:
        """Execute a function in the app's sandbox."""

@dataclass
class SandboxResult:
    success: bool
    output: dict | None
    logs: list[LogEntry]
    duration_ms: int
    memory_peak_mb: float
    error: str | None
```

#### Communication Protocol (JSON-RPC over stdin/stdout)

```json
// Manager → Sandbox
{"jsonrpc": "2.0", "method": "execute", "params": {
    "function": "on_submission_completed",
    "event": {"type": "submission.completed", "data": {...}},
    "config": {"lms_base_url": "https://..."},
    "api_base_url": "https://api.openskill.dev/api/v1",
    "api_token": "<scoped_short_lived_token>"
}, "id": 1}

// Sandbox → Manager (API call via proxy)
{"jsonrpc": "2.0", "method": "api_call", "params": {
    "method": "GET",
    "path": "/api/v1/orgs/{org_id}/cohorts",
    "query": {"limit": 50}
}, "id": 2}

// Manager → Sandbox (API response)
{"jsonrpc": "2.0", "result": {"data": [...]}, "id": 2}

// Sandbox → Manager (final result)
{"jsonrpc": "2.0", "result": {"status": "ok", "data": {...}}, "id": 1}
```

---

### Part E — UI Extension Points

#### Defined Surfaces

| Surface ID             | Location             | Max Size | Description              |
| ---------------------- | -------------------- | -------- | ------------------------ |
| `dashboard_card`       | Org dashboard        | 400×300  | Summary card widget      |
| `project_sidebar`      | Project detail page  | 320×∞    | Contextual project tools |
| `cohort_tool`          | Cohort management    | 800×600  | Cohort-level tools       |
| `submission_panel`     | Submission review    | 400×∞    | Extra submission info    |
| `registry_detail`      | Pack/workflow detail | 800×400  | Registry extension info  |
| `settings_page`        | Org settings         | ∞×∞      | Full config page         |
| `client_portal_widget` | Client portal        | 600×400  | Client-facing widget     |
| `operator_console`     | Platform admin       | 800×600  | Operator tools           |

#### Isolation: Sandboxed iframe

```html
<!-- Host page renders: -->
<iframe
  src="/api/v1/apps/{app_id}/ui/{surface_id}?installation={id}&token={short_lived}"
  sandbox="allow-scripts allow-forms"
  referrerpolicy="no-referrer"
  style="border:none; width:400px; height:300px;"
></iframe>
```

- **No** `allow-same-origin` — prevents DOM/cookie/token escape
- **No** `allow-top-navigation` — prevents redirect hijack
- Communication via `postMessage` with origin validation
- Short-lived tokens (5 min) scoped to surface + installation

#### Host ↔ Extension SDK (postMessage API)

```typescript
// Extension SDK (runs inside iframe)
import { OpenSkillExtension } from "@openskill/extension-sdk";

const ext = new OpenSkillExtension();

// Read platform data (scoped to granted permissions)
const cohorts = await ext.api.cohorts.list({ limit: 10 });

// Resize the extension viewport
ext.ui.resize({ height: 500 });

// Navigate host to a platform page
ext.ui.navigate("/dashboard/orgs/{orgId}/cohorts/{cohortId}");

// Show a toast notification in the host
ext.ui.toast({ message: "Sync complete!", type: "success" });

// Listen for host events
ext.on("context_changed", (ctx) => {
  // ctx.orgId, ctx.userId, ctx.surface, ctx.entityId
});
```

---

### Part F — Event Subscriptions & Automation API

#### Canonical Event Types (extending existing webhook events)

```
# Organization lifecycle
org.created, org.updated, org.member_added, org.member_removed

# Cohort lifecycle
cohort.created, cohort.updated, cohort.member_added, cohort.member_removed

# Project/Submission
project.created, project.published, project.archived
submission.created, submission.completed, submission.graded

# Packs
pack.published, pack.installed, pack.updated, pack.uninstalled, pack.forked

# Workflows
workflow.run_started, workflow.run_completed, workflow.run_failed
workflow.step_completed, workflow.review_submitted

# Talent
talent.capability_verified, talent.credential_issued, talent.credential_revoked
talent.application_submitted, talent.application_stage_changed
talent.offer_created, talent.placement_started

# Marketplace
marketplace.listing_published, marketplace.purchase_completed
marketplace.license_granted, marketplace.license_revoked

# Evaluation
evaluation.completed, evaluation.failed
```

#### Event Delivery

Apps receive events via:

1. **Webhook HTTP POST** — HMAC-SHA256 signed, retry with exponential backoff (3 attempts: 10s, 60s, 300s)
2. **Sandbox invocation** — For apps with sandbox runtime, events trigger function execution directly

#### Automation Rules API

```json
{
  "id": "rule_01JARX...",
  "app_installation_id": "inst_01JAR...",
  "name": "Sync completed submissions to LMS",
  "trigger": {
    "event": "submission.graded",
    "filter": {
      "field": "data.grade",
      "operator": "gte",
      "value": 70
    }
  },
  "action": {
    "type": "webhook",
    "url": "https://acme-lms.com/api/grade-sync",
    "method": "POST",
    "headers": { "Authorization": "Bearer {{secrets.LMS_API_KEY}}" },
    "body_template": {
      "student_id": "{{event.data.user_id}}",
      "course_id": "{{config.lms_course_id}}",
      "grade": "{{event.data.grade}}"
    }
  },
  "enabled": true,
  "max_executions_per_hour": 100
}
```

No arbitrary scripting — actions are bounded: `webhook`, `sandbox_function`, `api_call`, `notification`.

---

### Part G — Provider & Workflow Adapter SDK

Formalizes the existing ADR-011 `ProviderAdapterBase` for third-party use:

```python
from openskill_sdk import ProviderAdapter, Capability, HealthCheck

class AcmeVideoAdapter(ProviderAdapter):
    """Third-party video generation adapter."""

    name = "acme-video"
    display_name = "Acme Video Generator"
    version = "1.0.0"

    capabilities = [
        Capability(
            key="text_to_video",
            input_schema={"prompt": "string", "duration_seconds": "integer"},
            output_schema={"video_url": "string", "duration": "number"},
            pricing={"unit": "second", "cost_per_unit": 0.05},
        )
    ]

    async def execute(self, capability, inputs, config, credentials):
        # credentials injected by reference, never visible to adapter code
        api_key = credentials["ACME_API_KEY"]
        result = await self.http.post(
            f"{config['base_url']}/generate",
            json=inputs,
            headers={"Authorization": f"Bearer {api_key}"}
        )
        return {
            "video_url": result["url"],
            "duration": result["duration"],
            "__usage__": {"seconds": result["duration"]}
        }

    async def health_check(self) -> HealthCheck:
        return HealthCheck(status="healthy", latency_ms=120)

    retry_policy = {"max_attempts": 3, "backoff": "exponential"}
    idempotency = True  # safe to retry with same idempotency_key
```

---

### Part H — Ecosystem Source Adapter SDK

Extends ADR-015 ecosystem intelligence for third-party data sources:

```python
from openskill_sdk import EcosystemSourceAdapter, SourceType

class AcmeTalentSource(EcosystemSourceAdapter):
    name = "acme-talent-db"
    source_type = SourceType.TALENT_DIRECTORY
    version = "1.0.0"

    async def fetch_records(self, config, credentials, *, since=None, limit=100):
        """Pull talent records from external source."""
        # SSRF protection enforced by sandbox network policy
        # Parser versioning tracked by platform
        ...

    async def validate_config(self, config):
        """Validate source configuration before activation."""
        ...

    provenance_tracking = True
    ingestion_rate_limit = 1000  # records per hour
```

---

### Part I — Component Authoring Toolchain (CLI)

```bash
# Initialize a new app project
openskill init --category connector --name "my-lms-connector"

# Validate manifest against schema
openskill validate

# Run local tests with mock platform
openskill test

# Package for distribution
openskill package
# → my-lms-connector-1.0.0.osk (signed tarball)

# Publish to registry
openskill publish --visibility unlisted

# Run local dev server with webhook tunnel
openskill dev --tunnel
```

The CLI is implemented as a Python package (`openskill-cli`) that mirrors server-side validation. Package format: `.osk` — a signed gzip tarball containing `manifest.json`, source code, and content hash.

---

### Part J — App Review & Supply-chain Security

#### Automated Checks (on submit)

1. Manifest schema validation
2. Permission minimality check (warn on unused declared permissions)
3. Dependency vulnerability scan (npm audit / pip-audit)
4. Secret scanning (detect hardcoded credentials, API keys)
5. Prohibited network destination check (known malicious domains)
6. Content hash verification (matches declared hash)
7. License metadata validation (SPDX identifier required)
8. Size limits (50MB package, 5MB per file)

#### Human Review (for public apps)

- Platform reviewers check business logic, data handling, UX
- Review decision: `approved`, `rejected` (with notes)
- Published apps are signed with platform key

#### Emergency Controls

```python
# Kill switch — immediately suspend all installations
await app_service.revoke_app(app_id, reason="security_incident")
# → Sets app.status = revoked
# → Sets all installations.status = suspended
# → Emits app.revoked event
# → Blocks all sandbox executions
# → Blocks all API key authentication
```

---

### Part K — Signing & Provenance

- **Content hash**: SHA-256 of package contents (deterministic)
- **Publisher signature**: Ed25519 signing key registered to DeveloperAccount
- **Platform signature**: Platform co-signs approved versions
- **Installation record**: Pins `app_version_id` + content_hash + provenance chain

```
AppVersion.content_hash = SHA-256(package_contents)
AppVersion.signature = Ed25519_sign(developer_key, content_hash)
AppInstallation.app_version_id → frozen manifest + hash
```

---

### Part L — Extension Marketplace

Reuses ADR-014 `MarketplaceListing` / `MarketplacePurchase` / `LicenseGrant`:

- **Product types** extended: `app`, `connector`, `workflow_adapter`, `ui_extension` (in addition to existing `skill_pack`, `workflow_pack`, `learning_path`)
- **Offer types**: `free`, `paid`, `private`, `partner_only`, `included_with_plan`
- **Revenue share**: Reuses partner economics from ADR-014
- **Listing metadata**: Screenshots, demo video, documentation URL, support URL, changelog

---

### Part M — Observability

#### Developer Dashboard

- Install count (total, active, by org)
- API usage (requests/day, by endpoint)
- Error rate and top errors
- Webhook delivery success rate and lag
- Sandbox execution duration (p50, p95, p99)
- Permission-denied events
- Version adoption (% on latest)

#### Tenant Dashboard

- Installed apps list with status
- Per-app API usage
- Per-app error log
- Permission audit trail

#### Platform Operator Dashboard

- Total apps, installs, active developers
- Abuse detection (anomalous API usage)
- Review queue metrics
- Sandbox resource consumption

---

### Part N — Backward Compatibility

- **API versioning**: Semantic versioning with deprecation headers
- **Manifest schema versioning**: `schema_version` field, backward-compatible evolution
- **Conformance test suite**: Platform provides test harness that apps can run against
- **Breaking change policy**: 6-month deprecation window, migration guides

---

## Database Schema

### New Tables

```
developer_accounts        — Publisher identity
developer_apps            — App registration + OAuth client
app_versions              — Immutable versioned releases
app_installations         — Per-org install record
app_api_keys              — Scoped API credentials
app_event_subscriptions   — Per-installation event subscriptions
app_automation_rules      — Event → action rules
app_secrets               — Per-installation secret storage (Fernet)
app_ui_extensions         — UI surface registrations
sandbox_executions        — Execution log (duration, memory, status)
app_review_submissions    — Review queue entries
app_signing_keys          — Developer Ed25519 public keys
```

### Indexes

```sql
CREATE UNIQUE INDEX ix_dev_accounts_slug ON developer_accounts(slug);
CREATE UNIQUE INDEX ix_dev_apps_dev_slug ON developer_apps(developer_id, slug);
CREATE UNIQUE INDEX ix_app_versions_app_ver ON app_versions(app_id, version);
CREATE UNIQUE INDEX ix_app_installs_app_org ON app_installations(app_id, org_id)
    WHERE status = 'active';
CREATE INDEX ix_app_api_keys_prefix ON app_api_keys(key_prefix);
CREATE INDEX ix_sandbox_exec_install ON sandbox_executions(installation_id, created_at);
CREATE INDEX ix_app_event_subs_event ON app_event_subscriptions(event_type);
```

---

## Consequences

- Third parties can build, test, and distribute extensions without core code changes
- Sandbox isolation prevents resource abuse and data leaks
- Manifest-declared permissions enable tenant-level approval
- Reuses existing marketplace/billing infrastructure from ADR-014
- Platform can emergency-revoke compromised apps
- CLI toolchain enables local development with parity to production
