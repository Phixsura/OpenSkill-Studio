# PR #28 — Adversarial Review Summary (Issue #27)

**Branch:** `feature/saas-commercialization` (stacked on `feature/workflow-pack-runtime`)
**Scope:** SaaS Commercialization Control Plane — tenants, plans/entitlements,
metering, rating/FX, credits/budgets, billing (manual/mock/Stripe), partners &
revenue share, paid marketplace, client portal, white-label/domains/blueprints,
platform ops console (ADR-014).
**Status at time of writing:** NOT merged — awaiting explicit approval.
**Regression baseline:** full control-plane suite 337 passed (16 `test_cp_*`
files; one known cross-file event-loop teardown flake passes in isolation);
product suites (evaluation / skill_packs / installations / organizations /
projects) 214 passed; ruff check + format clean.
**E2E re-run post-remediation:** `e2e_commercial_lifecycle.py` 52/52 against a
fresh live API and `browser_e2e_commercial.mjs` 19/19 (zero JS console errors),
with the API log monitored throughout — **zero 500s, zero tracebacks**; the
only error-level log lines were the intentional `cp_rating_no_cost_rate`
alerts added by R91-100-H12.
**Full UI-driven browser E2E:** new `browser_e2e_full_lifecycle.mjs` drives the
issue-§12.4 chain through the actual UI — provision wizard, platform console
ops, MarketplacePanel credit purchase, invoice pages, §37 trace drawer,
settlement state machine, client-portal guest decision flow, audit explorer —
**60/60 checks, zero 500s, zero JS errors**. It caught one real frontend bug:
the platform tenant-detail page parsed the API's `{tenant, organizations}`
response as a flat object, crashing StatusBadge (`undefined.replace`) and
unmounting the entire page — the page had never rendered. Fixed + StatusBadge
hardened to render null on missing status.

Every defect below was **verified against the real code** (finder + independent
adversarial verifier, then personally re-confirmed before fixing), fixed with a
regression test, and **guard-proven** where the failure mode is silent (revert
fix → test fails → restore → passes).

---

## 1. How to read this

The review ran as successive adversarial rounds **R1 → R100**. Early rounds
(R1–R40) probed the freshly-built control plane surface by surface; the middle
campaign (R41–R80) ran themed deep-dives (billing correctness, rating math,
credit concurrency, revenue-share currency, impersonation, outbox resilience);
the final campaign (R81–R100) was two 10-dimension finder+verifier sweeps over
the whole PR (35 + 38 confirmed findings). In total **~230 confirmed defects
were fixed across 43 remediation commits**.

Money handling dominated: this PR moves real money through five subsystems
(rating → credits → invoicing → revenue share → settlement), and **the largest
defect class by far is money-correctness (~80 findings)** — wrong amounts,
wrong currencies, double-charges, silent losses. The classes below are the
reusable lessons.

---

## 2. Defect classes (confirmed + fixed)

### 2.1 Money correctness — currency (the #1 recurring bug shape)

Every place an amount crossed a subsystem boundary was a chance to mix
currencies or minor-unit scales. Confirmed instances:

- **Stripe sends lowercase currency codes** (`'jpy'`) but `minor_multiplier`'s
  dict lookup used uppercase keys, falling through to ×100 — a JPY 1 000 top-up
  credited **JPY 100 000 (100×)** (R81[0], CRITICAL).
- **Seller rev-share accrued in the buyer's currency** while seller statements
  sum in the platform currency unconverted — a KRW 1 040 000 sale settled as
  **USD 1 040 000** (R88[9], CRITICAL; R56[22] had fixed only the partner
  branch — same bug, two branches).
- Partner accruals in buyer currency with no FX, summed into one statement
  (R56[22]); credit-note reversal bases unconverted (R56[28]);
  `fixed_amount_per_seat` interpreting $5.00 as ¥500 on a JPY invoice
  (R56[26]); `percentage_of_margin` double-converting a platform-currency base
  (R56[21]).
- `cost_plus_*` computed billable from the **cost-rate currency** but labeled
  and FX-converted it as the **policy currency** (R52[6], CRITICAL).
- Tenant AI-budget ceiling hardcoded `currency="USD"` — never fired for any
  non-USD tenant (R32/C5); same hardcoding in the eval-settings budget
  write-through (R63-3); run-cost estimate in USD cents held against a
  tenant-currency balance (R51[4]).
- Stripe's zero-decimal currency set is larger than JPY/KRW — minor-unit
  convention mismatch on both webhook credit and checkout amounts (R75[3]).
- Platform dashboard summed JPY minor (×1) with USD cents (×100) into one MRR
  number (R48[31]).
- Missing FX must **block, not vanish**: cross-currency accrual with no rate
  returned `None` — the outbox success signal — and the accrual was marked done
  and lost forever (R35/C24, CRITICAL). Inverse-FX quantized 1/rate of a
  hyperinflated rate to 0, rating conversions at zero (R61-3).

**Lesson:** an amount is not a number — it is (amount, currency, scale).
Normalize case at every external boundary, snapshot FX at decision time, and
make "conversion impossible" a blocking state, never a silent zero or a
swallowed success.

### 2.2 Money correctness — double-charge / never-charge / lost credit

- **Deferred downgrades were recorded but never applied** — the tenant was
  billed the old, higher plan **every period, forever** (R41[0], CRITICAL).
- Immediate plan change double-charged the delta (full new-plan line + proration
  net, R41[1]); immediate seat increase likewise (R41[2]); plan-line truncation
  ignored on immediate cancel — full interval billed for a truncated period
  (R82[2]).
- **Credit-settled usage billed again on the period invoice** (settle left rows
  `rated`, R38/C11, CRITICAL); the settle-vs-close race charged the same row
  from credit AND invoice (R80[1]); `pending_licenses` unlocked read double-
  invoiced licenses (R91-100-H8).
- `void_invoice` permanently lost the applied credit while re-billing the usage
  at full price (R42/43[8], CRITICAL); voiding an older invoice rewound
  already-invoiced (even paid) periods into re-billing (R82[3]); void never
  reversed the partner accrual — void + re-invoice paid the partner twice
  (R56[24]).
- Credit notes: capped per-note not per-invoice, so N notes refunded N× the
  invoice (R42/43[10]); a note on a still-OPEN invoice minted spendable credit
  while the debt remained (R42/43[12]); a note exceeding `amount_due` silently
  dropped the collected portion (R88[10]); **refunding an invoice-billed
  purchase whose invoice was still open minted credit for money never received**
  (R88[11], CRITICAL).
- Never-charge holes: budgets were **never enforced on workflow runs** — the
  primary costed path (R63-1, CRITICAL); evaluation spend bypassed credit
  enforcement entirely (R67[4]); zero-estimate runs skipped the reserve call
  (R31/C13); failed evaluations that consumed real tokens were never metered
  (R49[40]); `expire_promotional` expired the full face value of a
  partially-spent lot — over-debit (R91-100-H10); per-event ROUND_HALF_UP
  dropped every sub-half-minor charge to zero, zeroing cheap-token billing and
  margins (R75[1], R75[2]); `cost_plus_fixed` under-billed partial blocks until
  ⌈qty/per⌉ (R7).
- Reversal math: negative-quantity events re-applied `minimum_fee`, flipping a
  credit into a charge (R52[7]); tier selection by signed quantity made
  reversals not mirror the original (R52[8]/[9]); same-timestamp reversals
  missed `included_quota` prior-usage (R52[10]).
- Seats: archived orgs' members billed as overage forever (R68[2]); ACTIVE
  member rows of a deleted org held tenant seat quota forever (R68[1]);
  add-then-promote bypassed the seat gate (R27/C0).

### 2.3 Concurrency & races (FOR UPDATE, guarded UPDATE, idempotency)

- **ORM identity-map stale read under FOR UPDATE**: `SELECT ... FOR UPDATE`
  acquired the lock but returned a cached pre-lock copy (R51[0], CRITICAL) —
  every locked re-read now uses `populate_existing=True`. This single pattern
  recurred in statements (R73[8]), close-period (R80[4]), and settle (R80[1]).
- TOCTOU blind writes → guarded conditional UPDATEs: `void_rated` overwrote a
  concurrently-invoiced row (R73[6]); the FX-unblock path resurrected
  ops-voided rows (R73[7]); double-click checkout created a **real second
  recurring Stripe subscription** with no platform record (R64-17).
- Seat-quota TOCTOU across orgs → tenant-scoped `pg_advisory_xact_lock`
  (R68[3]); org-count check-then-insert (R74[3]); slug-race 500s →
  SAVEPOINT-isolated insert with suffix fallback (R68[4]).
- `cancel_run` settled while a provider call was mid-flight, missing its usage —
  terminal handler now defers while any step lease is live (R66[3]).
- Row locks held across minutes-long LLM calls — commit before the provider
  call (R13 pattern; evaluation R91-100-H5, export-to-S3 R81-90-m6).
- Idempotent-retry lottery: retrying an accepted run 403'd when the run itself
  consumed the last quota slot (R74[2]); purchase idempotency needed a
  pending-purchase resume path (R44[17]).

### 2.4 Authorization / tenancy

- **Idempotency keys are tenant-scoped state**: three separate global-namespace
  collisions disclosed or charged across tenants — purchases (R72[2]), credit
  ops (R51[5]), usage ingestion (R70[42]).
- **Impersonation**: privileged-target check ran only at grant creation —
  promote-after-grant escalated (R54-1); revoke left minted tokens valid 15 min
  — now swept (R59-5); the read-only guard parsed `Bearer` case-sensitively
  while FastAPI doesn't — full write bypass (R71); same casing gap skipped API
  metering (R71).
- **Paid content turning free**: the install gate filtered `status=='active'`,
  so delist/suspend removed the gate entirely and nullified refund revocation
  (R44[16]); a licensed buyer could repackage a paid pack's skills into their
  own pack and resell (R91-100-H1); public registry badges leaked
  private/partner_only listings' existence and price (R25) and later the
  underlying archived/private product (R86[7]).
- **Financial internals**: platform_support could read cost/margin snapshots
  via dashboard + trace endpoints — restricted to billing_admin/admin (R48[30]);
  partner CSV exposed the platform margin via `percentage_of_margin` bases
  (R60-39).
- Blueprint escalation: a partner admin could author platform-only entitlement
  overrides into a blueprint and provision them (R46[25]).
- **Production fail-open default**: `domain_verifier` defaulted to `mock`
  (always verifies) — zero domain-ownership verification in a default deploy
  (R83[4]).
- Consumption mask fired only on SUSPENDED, not CANCELLED/ARCHIVED (R49[35]);
  portal member principal skipped `user.is_active` (R69[2]).

### 2.5 Ops resilience (outbox / worker / Redis)

- One handler DB error poisoned the whole claimed outbox batch (R38); a product
  service's `session.rollback()` inside a handler SAVEPOINT rolled back the
  root batch (R57-1); one 50-message batch transaction exceeded arq's 300s
  job_timeout → rollback-and-retry livelock — now claim-once, commit-per-message
  (R89[12]).
- The sync Stripe SDK was called inline in async code — one slow round-trip
  froze the entire event loop (R89[13]) → `asyncio.to_thread`.
- **Prod compose had no arq worker at all** — the outbox was never drained in
  production: no rating, no invoices, no accruals (R91-100-H2); Redis had no
  persistence and an eviction policy that could drop idempotency/rate-limit
  keys (R91-100-H3).
- Unknown outbox topic retried forever at attempts=0 — now dead-letters
  (R91-100-m15); provider pushes on plan change had no retry — moved into the
  outbox (R91-100-H4); usage emission without a savepoint aborted the caller's
  transaction (R77[1]).
- Metering flush: hourly flush deleted the very Redis buckets the daily quota
  sums — unlimited API for the price of one hour (R53-1); flush dropped buckets
  it couldn't attribute (R57-3).

### 2.6 State machines & integrity

- `require_tenant_active` fired only at `create_run` — a run parked at a review
  gate for up to 30 days resumed provider spending after suspension (R66[1]);
  cancelled/archived tenants kept white-label domains resolving (R83[5]).
- Portal: approve/final-accept accepted DRAFT submissions (R69[1]);
  resubmit-after-revision reused the same version, so the decision idempotency
  key never changed (R87[8]); request-revision missing `_assert_decidable`
  (R81-90-M10).
- Trial-expiry cron could suspend a tenant **mid-Stripe-checkout** (R54-2);
  FX rates were permanently immutable — an open-ended rate blocked its pair
  forever (R61-1); Stripe API 2025-03+ moved `subscription` into
  `parent.subscription_details` — paid/failed webhooks silently no-opped
  (R64-19).
- Rule activation retired **other countries'** active rules (country missing
  from the dimension filter, R35/C26, CRITICAL); rev-share accrual silently
  dropped SUSPENDED partners' earnings permanently (R35/C28).

### 2.7 Untrusted-input 500s

The R1 sweep bounded every money/rate/quantity field to its actual column
constraint; later rounds closed the exotic residue: asyncpg client-side
`DataError` with no SQLSTATE (BIGINT overflow, R1; timestamptz encoder
`OverflowError` on year-1+14:00 datetimes → SQLSTATEs 22000/22008 added to the
backstop, R76[1]); `decimal.InvalidOperation` escaping pydantic (R58[34]);
`per_quantity=0` dead-lettering a tenant's entire rating pipeline (R52[12]);
21-digit page numbers overflowing int64 OFFSET across 11 endpoints (R29);
pydantic `ValidationError` raised **outside** request-model parsing is not
wrapped by FastAPI — blueprint validation 500'd (R91-100-H14); JSONB depth
bricks via portal comment regions (R58[33]); non-ASCII webhook signature
header crashing `hmac.compare_digest` (R64-20); tier_rules accepting
NaN/Infinity (R91-100-H13).

### 2.8 Injection & content safety

- **CRLF header injection**: branding `email_from_name` and org `name` both
  flow into email headers — new `reject_header_str` (blocks
  `\x00-\x1f\x7f`) at both sites (R91-100-m7/m8).
- ILIKE metacharacters unescaped in platform search (R91-100-m11).
- Domain handling: stdlib IDNA is IDNA2003 → UTS46 via `idna` package
  (R81-90-M3); stale `pending_verification` rows squatted hostnames forever
  (R81-90-M2); unauthenticated site-context endpoint rate-limited (R81-90-M4).

### 2.9 Pagination / cache / distribution

- Entitlement cache invalidated **before** commit re-cached stale entitlements
  for the full TTL — revoked features stayed on (R55-1) → 5s dirty tombstone;
  the API-quota secondary cache was never invalidated (R55-2); quota
  re-population raced the tombstone (R91-100-m2).
- Offset pagination on tx-fixed `now()` timestamps duplicated/skipped rows —
  every control-plane list now chains the ULID id tiebreaker (R90[14]); five
  endpoints had hidden fixed LIMITs with fabricated `total`/`has_more` (R76[3]);
  fx-rates/recon-reports had fake pagination (R81-90-M17).

---

## 3. Feature completion (in-scope gaps, not bugs)

- **R49[36]:** learning-path licenses were purchasable but unredeemable — wired
  ADR-014 §8.5 cross-org fork install end-to-end.
- **R62-2:** `external_price_ref` (the one ADR-designated mutable field) had no
  write path — Stripe subscription checkout was unreachable.
- **R44[22]:** `bill_via_invoice` was stored but unwired — invoice-billed
  purchases now deliver immediately and charge at period close.
- **R64-16:** `change_plan` never pushed to Stripe — provider kept invoicing the
  old price forever.
- **R60 audit sweep:** subscription start/cancel, tenant member changes, rule
  retirement, purchase mark-paid, domain delete, tenant country/timezone
  changes — all now audited.
- **R91-100-m16:** webhook-events ops list endpoint.

---

## 4. Convergence

The final campaign (R81–R100) ran as two independent 10-dimension
finder+verifier workflows over the full PR surface. R81–R90 confirmed 35
findings (1 critical — the seller-currency statement bug), R91–R100 confirmed
38 (0 critical, 15 high). The last sweep's highs were dominated by
second-order issues (a missing worker in prod compose, lock-scope refinements,
logging gaps) rather than new money-loss classes — the same convergence shape
that closed PR #22.

### Known out-of-scope (documented, not fixed in this PR)

- **issue-18 stale-read-write debt** in pre-existing product services (fix
  pattern established in PR #22's R70) — tracked separately.
- **Cross-file pytest event-loop teardown flake**: one test intermittently
  fails with `RuntimeError` when 16 DB suites share a session; passes in
  isolation. Infrastructure, not product.
- **included_quota_then_overage concurrent-rating window**: both raters may see
  "within quota" → undercharge-never-overcharge; accepted for v1 (ADR-014).

---

## 5. Bottom line

- **~230 confirmed defects fixed across 43 remediation commits** (R1–R100),
  on top of the 12-phase feature delivery.
- 12 critical money-loss bugs found and fixed, including three that billed or
  credited at 100×/wrong-currency scale and two that billed customers forever.
- Every fix carries a regression test; silent-failure fixes are guard-proven;
  each batch was committed with full per-finding traceability.
- Full control-plane + product regression green; ruff clean.

**Recommendation:** the PR is in a strong, well-verified state. Remaining
decision is the reviewer's: merge, or continue with further rounds.
