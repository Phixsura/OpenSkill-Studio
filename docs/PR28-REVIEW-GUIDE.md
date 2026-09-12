# PR #28 Review Guide — SaaS Commercialization Control Plane (#27)

A 30-minute entry point for reviewing a 390-file / ~94k-line PR.
The full round-by-round audit ledger lives in `PR28-REVIEW-SUMMARY.md`;
the design record is `design/014-saas-commercialization-control-plane.md`.

## 1. Shape of the change

Everything commercial lives in **`apps/api/app/controlplane/`** (~22k LOC):
`models/` (12 modules, all `cp_*` tables), `services/` (19), `api/` (14
routers), `worker.py` (transactional outbox), `facade.py`.

**The one seam to scrutinize**: product code may import ONLY
`app.controlplane.facade` (grep proves it; the single documented exception
is the provisioning orchestrator, which by design drives product services).
If the facade's 11 functions look right, the blast radius of the control
plane on the existing product is exactly those call sites.

Frontend: `apps/web/src/app/(dashboard)/{tenant,partner,platform}/…`,
standalone `client/` portal, `lib/cp.ts` money helpers, white-label theming
via `site-context.ts`.

## 2. Read in this order (suggested)

1. `docs/design/014-…` — decisions + **Known limitations (v1, deliberate)**
   (read this list first; it pre-answers most "why not X" questions).
2. `app/controlplane/facade.py` — the product↔commercial contract.
3. Migrations `cp01 … cp23` in order — each has a real downgrade; `cp01`
   backfills `organizations.tenant_id` NOT NULL (197k orgs, verified live).
4. Money invariants, one file each:
   - `services/credits.py` — append-only ledger, `balance_after`, FOR UPDATE
     - DB CHECK; reserve → settle/release.
   - `services/rating.py` — frozen cost/sell/FX snapshots; historical margin
     never recomputed from today's tables.
   - `services/billing.py` — `close_period_and_invoice` (the 900-line core:
     gap-free numbering, proration segments, credit auto-apply uses
     AVAILABLE = balance − holds).
   - `services/revenue_share.py` — natural-key idempotent accrual;
     statements FOR UPDATE against finalize races.
5. Security surfaces: `services/client_portal.py` (guest tokens hashed,
   §32), `services/domains.py` (Host never trusted, IDNA normalization),
   `api/deps.py` platform-role gates, `middleware/api_metering.py`.

## 3. What the verification actually proves

| Layer             | Evidence                                                                                                                                                                                                                                                                    |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Unit/DB           | backend 2557 green (CI coverage gate 90% passed at 90.44%); web 543 across 116 files — every page and every component has direct tests                                                                                                                                      |
| Mutation          | ~450 mutants across all 14 cp services + facade + worker + adapters + web money/theme libs; 22 test gaps found and killed during the audit; every surviving mutant has an in-module disposition (equivalence proof / schema-unique structural argument / accepted residual) |
| Live E2E          | 664 checks re-run on the branch tip 2026-09-12/13: commercial lifecycle 52, adversarial 178 (all §39 bullets), smoke 148, concurrency 17, product lifecycle 68, workflow lifecycle 49, browser 152 — zero 500s, zero console errors                                         |
| Issue conformance | all 39 sections re-audited bullet-by-bullet; Part N's 25 API groups checked against the live OpenAPI spec (373 paths)                                                                                                                                                       |
| CI                | first-ever full pipeline green (and again on the follow-up commit)                                                                                                                                                                                                          |

## 4. Where human judgment is still needed

These are decisions, not defects — the machine checks can't settle them:

- **§33 self-service signup — now BUILT (R535)**: the earlier "deferred"
  note was wrong (standalone org creation always auto-minted a TRIAL
  tenant); the abuse gates are now in the minting branch — kill-switch,
  opt-in verified-email gate (default off; production should enable it,
  see .env.example), per-user cap 20 with a FOR UPDATE race lock.
  Decide: enable the email gate at launch? Is cap 20 right for you?
- **v1 money policies** (all ADR-documented): non-credit refunds return as
  platform credit (no provider-side refund API yet); settle-over-hold floors
  at balance ≥ 0 with the shortfall logged, no debt rows; promo-credit
  expiry is not lot-tracked FIFO.
- **No automated dunning**: PAST_DUE keeps consuming until ops act.
- **`included_quota_then_overage` concurrent-rating window**: benign
  (undercharge, never overcharge) — accepted for v1.
- **The `-s ours` merge of main** (commit 2c30ba5): main's only new commit
  was the squash of parent PR #22, byte-identical to this branch's ancestor
  (tree hash verified unchanged). Confirm you're comfortable with that
  resolution before merging.

## 5. Running it yourself

```bash
make infra-up && make db-migrate && make dev-api   # + make dev-web
cd apps/api
APP_ENV=test PYTHONPATH=. uv run python tests/e2e_commercial_lifecycle.py  # 52 checks
APP_ENV=test PYTHONPATH=. uv run python tests/e2e_adversarial.py          # 178 checks
node tests/browser_e2e_commercial.mjs                                     # needs :3000
```

`make lint` now runs ruff check **and** `ruff format --check` (the CI gate
that the first pipeline run exposed as missing locally).

## 6. One-line history

R1–R190: adversarial hardening to fixpoint (~610 fixes, 17 criticals).
R191–R500: mutation-verified test hardening of every page/service.
R501–R533: bullet-level issue audit (22 more test-gap kills), live E2E
re-verification, PR consolidation onto main, first green CI.
