# ADR-014: SaaS Commercialization Control Plane

**Status**: Accepted
**Issue**: [#27 — SaaS Commercialization Control Plane](https://github.com/Phixsura/OpenSkill-Studio/issues/27)
**Depends on**: ADR-002 (auth), ADR-003 (orgs), ADR-009/010 (registries), ADR-011 (providers)

## Context

OpenSkill Studio had a complete product layer (orgs, cohorts, projects,
evaluation, skill/workflow pack registries, provider abstraction, matching)
but no commercial layer: no notion of a paying customer, no metering, no
billing, no partner economics, no white-label delivery, no external client
access. Issue #27 adds all of it as a **control plane** that wraps the
product without entangling it.

## Decision 1 — Hard package boundary (`app/controlplane/`)

All commercial code lives in `app/controlplane/{models,schemas,services,api}`.
Product code imports **only** `app.controlplane.facade`:

```
get_tenant_for_org · require_tenant_active · record_audit
get_effective_entitlements · check_quota · require_feature
emit_usage · check_storage_quota · check_install_license
```

Control-plane code may import product **models**, never product **services**
— with one documented exception: the provisioning orchestrator
(`services/provisioning.py`) imports `OrgService`/installation services,
because provisioning IS orchestration of product operations.

## Decision 2 — TenantAccount above Organization

`TenantAccount` is the commercial owner; every `Organization` carries a
`tenant_id NOT NULL` FK (RESTRICT). The backfill migration
(`cp01a0000001`) created one DIRECT tenant per pre-existing org (197k+ on
the dev dataset), resolved owners from org OWNER members (fallback
`created_by`), and wrote non-expiring "migration grandfathering"
entitlement overrides wherever existing usage already exceeded community
defaults — existing users feel nothing.

Lifecycle: `TRIAL → ACTIVE → PAST_DUE → SUSPENDED → CANCELLED → ARCHIVED`
via a `TENANT_TRANSITIONS` map; every transition is a guarded conditional
UPDATE (`WHERE status = :expected`, 0 rows → 409). Self-serve org creation
auto-creates a TRIAL tenant (school-plan entitlements for
`settings.trial_days`, downgrade to community on expiry via worker cron).
Suspension blocks **consumption** (runs, evaluations, uploads, purchases,
provider connections, guest links, checkout) and never blocks reads,
invoice viewing or payments — self-service recovery stays open.

## Decision 3 — Transactional outbox + arq worker

Every cross-domain financial reaction goes through `cp_outbox`: the
business write INSERTs the message in the same transaction; a separate arq
worker polls with `FOR UPDATE SKIP LOCKED`, dispatches per-topic handlers,
retries with exponential backoff (`available_at = now + 30s·2^attempts`)
and dead-letters at `settings.outbox_max_attempts`. All handlers are
idempotent (natural keys / `ON CONFLICT` / guarded UPDATE). The poll
compares `available_at <= DB now()` — the DB clock, not the app clock
(clock-skew made fresh messages invisible otherwise).

Topics: `usage.recorded`, `fx.rate_created`, `run.terminal`,
`period.close_due`, `invoice.finalized`, `purchase.paid`,
`purchase.refunded`, `credit_note.applied`, `provision.run`. Tests drive
`process_outbox_once(db)` directly — no Redis/arq needed.

## Decision 4 — Money and immutability

- Amounts: `BigInteger` **minor units** + `CHAR(3)` currency; zero-decimal
  currencies via `CURRENCY_MINOR` ({JPY:1, KRW:1}, default 100).
- Quantities `Numeric(18,6)`, unit/FX rates `Numeric(18,8)`.
- Append-only ledgers: usage events, credit ledger (with
  `balance_after_minor` so the ledger replays), rev-share entries, audit.
  Corrections are explicit adjustment rows (`adjustment_of_id`).
- Economics frozen as JSONB snapshots at decision time: rating stores
  cost/sell/FX snapshots; purchases store `economics_snapshot`; accruals
  store `rule_snapshot`. Changing a rate/policy/rule NEVER rewrites
  history (regression-tested).

## Decision 5 — Entitlements

`ENTITLEMENT_DEFS` (15 keys) is the single registry. Effective =
plan-version defaults (TRIAL → school; fallback community) + non-expired
overrides + suspension mask (consumption bools forced false; display
entitlements like active domains stay). Redis cache `cp:ent:{tenant}`
TTL 60s, fail-to-DB. Numeric limits are hard except `max_storage_gb`
(soft — never breaks an in-flight upload). Seat counting: monthly sweep
events + live count; "active learner" = active org member with STUDENT
role (login activity not considered).

## Decision 6 — Metering → rating → invoicing

- `emit_usage` is same-transaction with the business write,
  `ON CONFLICT (idempotency_key) DO NOTHING` (partial unique index needs
  `index_where` for inference). 13 usage types with canonical units.
  Failed runs meter too (`metadata.status=failed`) — pricing may exclude
  them via `exclude_failed`.
- Rating ladder: exact provider+model → provider wildcard → capability →
  offering fallback → no-rate (cost 0, reconciliation-visible). Sell
  policy specificity: tenant > partner > plan > global (seeded cost+50%
  fallback). Missing FX → `status=blocked` → unblocked by
  `fx.rate_created`. NULL margin never blocks billing.
- Invoicing: period close via hourly scan → outbox; invoice assembles
  plan lines (proration segments), seat overage (max(actual peak,
  reserved)), usage lines (consumption window: `occurred_at <
  period_end`, rated rows marked `invoiced`), license lines, credit
  application. Finalize = sequence `FOR UPDATE` + guarded draft→open (one
  winner, no number gaps). Post-finalize corrections via CreditNote only.
- API metering middleware: Redis hourly buckets, **fail-open** on Redis
  outage (infra alert, not platform kill), hourly flush to usage events.

## Decision 7 — Billing providers

`BillingProviderBase` registry mirroring the provider-adapter pattern:
**manual** (remote ops 409), **mock** (deterministic refs, HMAC-signed
webhooks forgeable by tests via `sign_mock_event`), **stripe** (thin
wrapper — parameter assembly + response mapping, zero logic branches;
unit-tested with a monkeypatched stripe module; real
`Webhook.construct_event`). Webhook receiver: signature verify (fail →
401, not stored) → `ON CONFLICT` replay guard → handler; unknown events
ignored with 200. No card data anywhere (schema-asserted).

## Decision 8 — Partners and revenue share

Rules are versioned and immutable once active (activating v(n+1) retires
v(n); accrued entries never recomputed). Accrual on `invoice.finalized` /
`purchase.paid` with natural-key idempotency
`(source_type, source_id, beneficiary, partner, org)`. Entries convert to
the beneficiary's currency at accrual (FX snapshot) so statements are
single-currency. Statement flow: draft → finalized → approved →
paid_externally (guarded, audited); late adjustments land in the next
period's opening. Partner tenant lists expose commercial metadata only
(name/status/plan/created) — no usage or revenue detail.

## Decision 9 — Marketplace licensing

Listings snapshot the platform commission at create. Purchases freeze the
full economics split. License grants derive tenant/org **only from the
purchase row** (IDOR-proof by construction). The install gate
(`facade.check_install_license`) wires into both installation services +
upgrade paths: free/no-listing pass; own product passes; private →
uniform 404; included_with_plan → plan-key check + lazy grant;
paid/partner_only → covering grant (seat occupancy approximated by org
active-student count). Suspended/cancelled sellers can't sell; TRIAL
sellers can (listing creation already gates on the `paid_marketplace`
entitlement). **Revocation blocks new installs/upgrades only** — installed
content, imported skills and learner progress are never touched.

## Decision 10 — Client portal

Two channels: guest links (sha256-hashed tokens shown once, optional
email binding, ≤90d expiry, uniform 401 on every failure mode) and member
accounts (`ClientPortalMember`). Guest JWTs are `type=client_guest` —
structurally rejected by the product `get_current_user` (reverse
isolation). Portal endpoints whitelist every response field (brief hides
budget/brand-guidelines/constraints); clients see only
`ClientShare`-whitelisted submissions and `client_visible` comments.
Final-accept is a partial-unique row (one per project) wrapped in
`begin_nested` (IntegrityError → 409 without poisoning the session).

## Decision 11 — White-label

Branding is a closed token set (6 hex colors + radius enum + plain-text
strings + https-only URLs) — no HTML/JS anywhere; SVG uploads rejected.
Domains: normalize (lower/IDNA/port-scheme strip) → reserved rejection →
pending_verification → verify (adapter: DnsTxt real / Mock in dev, which
also issues `ok-`-prefixed tokens so the E2E flow completes without DNS)
→ activate (entitlement-gated) → disable. `site-context` resolves
**ACTIVE domains only** by exact match on an explicit query param — the
backend never trusts the Host header. Frontend: middleware tags
non-platform hosts with `x-tenant-host`; the root layout injects
validated theme tokens as CSS variables (hex→HSL re-guarded); the auth
layout swaps name/tagline/legal links. TLS via adapter (Null default —
terminates at the proxy; Mock for tests; real ACME out of scope).

## Decision 12 — Blueprints and provisioning

`BlueprintConfig` is strict pydantic (`extra="forbid"`) so
users/credentials/submissions keys are **structurally impossible** —
provisioning can configure, never copy runtime data (issue §8 red line;
zero-learner-rows asserted in tests). `TenantProvisionRun` is a resumable
step machine executed by the `provision.run` outbox handler; steps record
`done` and are skipped on resume; the org slug comes from the run's
unique `requested_slug` (name-template slugs collide across runs).
Exports build a whitelist-constructed JSON bundle (never `SELECT *`) —
credentials, cost fields and token hashes excluded structurally.

## Decision 13 — Ops console and traceability

`/platform/dashboard` aggregates tenants/MRR/usage economics/credits/
liabilities/GMV/attention in one round trip. The §37 acceptance chains:
`/platform/trace/invoice-lines/{id}` walks line → invoice → every
RatedUsage row (frozen snapshots) → usage-event provider refs;
`/platform/trace/settlement-entries/{id}` walks entry (rule snapshot) →
source invoice/purchase (economics snapshot) → statement. These responses
carry internal cost/margin — platform roles only; the tenant-facing
rated-usage response is a field-whitelisted constructor
(`TENANT_RATED_FIELDS`), substring-asserted against leaks.

## Known limitations (v1, deliberate)

- `included_quota_then_overage` has a benign concurrent-rating window
  (undercharge never overcharge).
- Promo-credit expiry is not lot-tracked FIFO (min(face, balance)).
- Settle-over-hold floors at balance ≥ 0; shortfall recorded, no debt rows.
- Seat-limited license occupancy is approximated by org student count.
- Provider-retry deduped executions still meter (reconciliation corrects).
- No automated dunning suspension; PAST_DUE keeps consuming until ops act.
- Rev-share periods are UTC months; tenant tz applies to billing/budgets.

## Verification

- ~180 control-plane tests across 16 files: per-domain DB suites,
  pure-logic suites, outbox infra (atomicity/backoff/dead-letter/SKIP
  LOCKED), backfill invariants, and `test_cp_adversarial.py` covering all
  17 issue-§39 bullets by name.
- `tests/e2e_commercial_lifecycle.py`: 52-check live-API chain (partner →
  blueprint → provision → domain → subscription → paid listing → credit
  purchase → license-gated install → rating → invoice → accrual →
  settlement → both trace chains → client portal), zero 500s.
- `tests/browser_e2e_commercial.mjs`: 19-check Playwright pass over the
  commercial frontend (tenant tabs, trial banner, feature gates, client
  portal, platform guard), zero console errors, zero API 500s.
