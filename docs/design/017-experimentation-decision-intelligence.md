# ADR-017: Experimentation & Decision Intelligence Platform

- **Status**: Accepted — phases exp01–exp09 implemented 2026-09-30 (core loop,
  assignment/exposure, metrics+provenance, guardrails+SRM, statistical core
  incl. CUPED/mSPRT/OF/BH/Bayesian, decision registry + promotion adapters,
  six domain hooks, Experiment Console frontend, E2E). Remaining v2 items
  (§10 switchback/bandit/post-stratification analysis paths, global holdout
  groups §4.12, health-check suite §4.13 beyond SRM, hourly guardrail lane,
  launch checklist, meta-analysis priors) and the learning_paths/evaluations/
  billing/talent_outcomes metric sources are follow-up work — see
  §18 Implementation notes.
- **Issue**: #42
- **Depends on**: ADR-010 (WorkflowRun telemetry), ADR-012 (`MatchingConfig` versioned rows),
  ADR-014 (control-plane transactional outbox `enqueue`, cost ledger/rating),
  ADR-015 (talent ethics boundary), ADR-016 (facade isolation pattern, RolloutPlan,
  TelemetrySnapshot, sweep-fairness cap, enum guards, keyset pagination discipline)

## 1. Problem

Product/business decisions (curriculum ordering, rubric wording, provider bindings,
matching weights, marketplace presentation, retry policies) are made by static
configuration. We need one platform-wide experimentation layer implementing:

Hypothesis → Design → Eligibility/Randomization → Exposure → Metrics → Guardrails →
Statistical Analysis → DecisionRecord → Controlled Promotion → Long-term Outcomes.

## 2. Safety posture (non-negotiable, mirrors ADR-016 §1)

1. **Employment decisions are never randomized.** The promotion target whitelist
   contains no offer/hire/reject action; `talent_flow`-domain experiments allow
   presentation-layer (non-consequential) targets only. Enforced structurally:
   there is no talent `target_type` in `promotion_drafts`.
2. **Guardrail breach can only auto-PAUSE. There is no auto-promote code path.**
   Promotion requires a DecisionRecord + explicit approver + the target domain's
   own validations (R79/R82/R83 gates are never bypassed by an experiment).
3. **No protected/sensitive-attribute targeting.** Population rule fields are
   whitelist-validated per domain and checked against `FORBIDDEN_TARGETING_KEYS`
   (age, gender, ethnicity, disability, religion, nationality, ...).
4. **Running specs are immutable.** Only `ramp_bp` (monotonic increase) and an
   earlier `ended_at` may change, via audited amendments (`experiment_events`).
5. **Strict tenant isolation.** Org-scoped experiments only accept units belonging
   to that org → 422 `EXPERIMENT_UNIT_OUT_OF_SCOPE`; cross-tenant reads are a
   uniform 404 (no existence oracle — R89 authz class 2).
6. **Immutable exposure/audit trail.** `experiment_exposures` and
   `experiment_events` are append-only; no UPDATE/DELETE path exists.

## 3. Package layout (copies the mature `ecosystem/` shape)

```
apps/api/app/experiments/
  facade.py            # ONLY entry point for product code:
                       #   resolve_variant / record_exposure / emit_outcome
  security.py          # FORBIDDEN_TARGETING_KEYS, target whitelists, risk gates
  worker.py            # outbox topic handlers + sweeps (reuses controlplane outbox)
  schemas.py           # Pydantic, extra="forbid" (R85)
  models/  experiment.py assignment.py metric.py guardrail.py decision.py audit.py
  services/ experiments.py assignment.py layers.py metrics.py guardrails.py
            analysis.py    # pure functions, zero I/O, mutation-tested
            decisions.py promotion.py
  api/     deps.py experiments.py versions.py assignments.py metrics.py
           guardrails.py analysis.py decisions.py promotions.py layers.py
```

Mounted from `app/api/v1/router.py`. Platform routes under `/api/v1/experiments`
(platform admin or experiment owner); org routes under
`/api/v1/orgs/{org_id}/experiments` via `require_org_member(admin)`.

## 4. Data model (Part A/B/C/J)

All tables use `ulid_pk()` and timestamptz `created_at`/`updated_at`
(`server_default=func.now()`). Migrations: `exp01_core.py`, `exp02_metrics.py`,
`exp03_decisions.py` (naming follows `talentNN_`). Money/measures are `numeric`,
never float (metamorphic-money discipline).

### 4.1 `experiments`

| column                                    | type        | constraint                                                                            |
| ----------------------------------------- | ----------- | ------------------------------------------------------------------------------------- |
| id                                        | String(26)  | PK                                                                                    |
| key                                       | String(64)  | unique, `^[a-z0-9][a-z0-9_-]{2,63}$`                                                  |
| title                                     | String(200) | not null                                                                              |
| domain                                    | String(20)  | enum: learning, assessment, workflow, matching, marketplace, operational, talent_flow |
| scope_org_id                              | String(26)  | FK organizations, nullable (null = platform-wide)                                     |
| layer_key                                 | String(64)  | FK experiment_layers.key, not null                                                    |
| status                                    | String(12)  | lifecycle enum, see §5                                                                |
| current_version                           | Integer     | default 0                                                                             |
| owner_user_id                             | String(26)  | FK users, not null                                                                    |
| risk_class                                | String(8)   | low, medium, high — high requires platform-admin approval                             |
| ramp_bp                                   | Integer     | 0–10000 basis points, default 0                                                       |
| holdout_bp                                | Integer     | 0–1000                                                                                |
| started_at / ended_at / analysis_close_at | timestamptz | nullable; analysis_close_at drives Part I                                             |

Indexes: `ix_experiments_status_domain (status, domain)`, `ix_experiments_layer (layer_key)`.

### 4.2 `experiment_versions` (immutable spec)

`experiment_id` FK, `version` int, `spec` JSONB, `spec_hash` String(64)
(canonical-JSON SHA-256), `created_by`. Unique `(experiment_id, version)`.
Rows are insert-only.

`spec` schema (`ExperimentSpec`, extra="forbid"):

```json
{
  "hypothesis": "Rubric wording B reduces revision count without hurting pass rate",
  "unit_type": "user",
  "population": {
    "rules": [{ "field": "cohort_id", "op": "in", "values": ["01H..."] }],
    "exclusions": [{ "field": "user_id", "op": "in_experiment_layer", "values": ["layer-x"] }]
  },
  "variants": [
    {
      "key": "control",
      "name": "Current rubric",
      "weight_bp": 5000,
      "is_control": true,
      "config": {}
    },
    {
      "key": "treatment",
      "name": "Rubric B",
      "weight_bp": 5000,
      "is_control": false,
      "config": { "rubric_template_id": "01H..." }
    }
  ],
  "metrics": {
    "primary": ["project_approval_rate"],
    "secondary": ["revision_count", "time_to_completion_hours"],
    "guardrails": [
      { "metric_key": "eval_cost_usd", "op": "lte", "threshold": 500.0, "window_hours": 24 },
      { "metric_key": "run_failure_rate", "op": "lte", "threshold": 0.15, "window_hours": 6 }
    ]
  },
  "power": { "mde": 0.05, "alpha": 0.05, "power": 0.8, "estimated_n_per_variant": 380 },
  "design": "parallel",
  "allocation_mode": "fixed",
  "stats_engine": "frequentist",
  "sequential": "msprt",
  "variance_reduction": {
    "method": "cuped",
    "covariate_metric": "project_approval_rate",
    "lookback_days": 28
  },
  "trigger": {
    "analysis_population": "exposed",
    "note": "triggered analysis; trigger must not be affected by treatment"
  },
  "stop_policy": { "max_days": 28, "max_looks": 4 },
  "analysis_type": "randomized"
}
```

v2 spec fields:

- `design` ∈ {parallel, cluster, **switchback**}. Switchback (marketplace /
  matching interference — the DoorDash/Lyft class problem): config
  `{"switch_unit": "org|region_key", "window_minutes": 60, "washout_minutes": 10}`;
  randomization over (unit × time-window) with balanced treatment counts per
  unit; washout windows excluded from analysis; cluster-robust analysis path.
- `allocation_mode` ∈ {fixed, **bandit**}. Bandit = Thompson sampling over
  binary/continuous reward, **allowed only** for domain ∈ {marketplace,
  operational} presentation-layer configs with risk_class=low; forbidden for
  learning/assessment/matching/talent_flow (422
  `EXPERIMENT_BANDIT_DOMAIN_FORBIDDEN`). Bandit allocations update daily from
  posterior; assignments remain sticky per unit (allocation probabilities
  shift for NEW units only — no yanking experiences).
- `stats_engine` ∈ {frequentist, **bayesian**} — dual engine, GrowthBook-style.
- `sequential` ∈ {none, obrien_fleming, **msprt**} (mSPRT = always-valid
  inference; unlimited looks, no look registry needed for msprt).
- `variance_reduction` — CUPED with one pre-period covariate metric (v1);
  schema reserves a list for CUPED++-style multi-covariate later.
- `trigger.analysis_population` ∈ {assigned, exposed} — triggered analysis with
  dilution correction; the analysis warns when per-variant exposure rates
  diverge (exposure-SRM ⇒ trigger possibly affected by treatment ⇒ selection
  bias).

Validation: `sum(weight_bp) == 10000`; exactly one `is_control`; `unit_type` ∈
{user, cohort, organization, workflow_installation, project, provider_offering,
tenant}; population fields per-domain whitelisted and not in
`FORBIDDEN_TARGETING_KEYS`; `analysis_type` ∈ {randomized, observational} —
observational responses always carry `"causal_claim": false` and can never
produce a promotion draft (422 `PROMOTION_REQUIRES_RANDOMIZED`).

### 4.3 `experiment_layers` + `experiment_layer_allocations` (contamination control)

- layers: `key` PK, `domain`, `total_slices` int default 10000.
- allocations: `layer_key` FK, `experiment_id` FK, `slice_start`, `slice_end`.
  Overlap prevention: `SELECT ... FOR UPDATE` on the layer row + application-level
  interval-overlap check (chosen over an `EXCLUDE USING gist` constraint to avoid
  the `btree_gist` extension dependency). Same-layer experiments own disjoint
  slice ranges ⇒ a unit can never enter two mutually-exclusive experiments.

### 4.4 `experiment_assignments` (sticky)

`experiment_id`, `unit_type` String(24), `unit_id` String(26), `variant_key`,
`assigned_version` int, `bucket` int (0–9999), `is_holdout` bool, `assigned_at`.
Unique `(experiment_id, unit_type, unit_id)`; index `(unit_type, unit_id)`.
Writes use `INSERT ... ON CONFLICT DO NOTHING` then re-read (never
SELECT-then-INSERT — R128/R88 race class).

### 4.5 `experiment_exposures` (append-only)

`assignment_id` FK, `experiment_id` (denormalized), `occurred_at`, `context`
JSONB (surface identifiers only, **no PII bodies**), `dedup_key` String(64)
nullable + partial unique index `(experiment_id, dedup_key) WHERE dedup_key IS
NOT NULL` (idempotency). Index `(experiment_id, occurred_at)`.

### 4.6 `metric_definitions`

`key` unique, `title`, `kind` enum {binary, continuous, rate, time_to_event},
`domain`, `source_kind` enum {sql, service}, `query_version` int, `spec` JSONB,
`privacy_class` enum {aggregate_only, k_anonymous}, `direction` enum
{increase_good, decrease_good}, and v2 robustness fields: `winsorize_pct`
numeric nullable (e.g. 99.9 — clamp upper tail before aggregation),
`cap_value` numeric nullable (absolute cap), `percentile` numeric nullable
(50/95/99 → percentile metric; CI via the outer/bootstrap-free percentile
delta method). ~20 seeded definitions cover issue Part C:
learning (completion, time-to-completion, practical pass, project approval,
revision count, capability gain, placement), production (success/failure,
latency, internal cost, client acceptance, revision rate, provider reliability —
read from `WorkflowRun` and eco `TelemetrySnapshot`), commercial (conversion,
retention, ARPU, gross margin, pack adoption, partner performance — read from
control-plane rating/ledger aggregates).

### 4.7 `metric_snapshots` (provenance-backed)

`experiment_id`, `metric_key`, `variant_key`, `window_start/window_end` (UTC
day windows, aligned with eco telemetry), `n` bigint, `numerator` numeric,
`denominator` numeric, `sum_value` numeric, `sum_sq` numeric, `provenance`
JSONB `{"query_version": 3, "computed_at": "...", "source": "workflow_runs",
"row_count": 812}`. Unique `(experiment_id, metric_key, variant_key,
window_start)` — recompute is an UPSERT recorded in provenance. Analyses
default to same-`query_version` windows and flag mixes with
`SNAPSHOT_VERSION_MIXED` (warning, not error).

v2 CUPED support: additional columns `cov_sum` numeric, `cov_sum_sq` numeric,
`cov_xy_sum` numeric (pre-period covariate aggregates per variant window) —
sufficient statistics for theta estimation without raw rows. Winsorization/caps
are applied at snapshot computation time and recorded in provenance
(`"winsorize_pct": 99.9`).

### 4.8 `guardrail_events`

`experiment_id`, `guardrail_key`, `metric_key`, `observed` numeric, `threshold`
numeric, `window_start/end`, `action` enum {paused, alerted}, `auto` bool.
Index `(experiment_id, created_at)`.

### 4.9 `decision_records` (Part J, immutable)

`experiment_id`, `experiment_version`, `decision` enum {promote, reject,
inconclusive, extend}, `summary` Text, `uncertainty` JSONB (per-primary-metric
CI), `segments` JSONB, `guardrail_outcome` JSONB, `approver_user_id`,
`evidence` JSONB (links: benchmark ids, snapshot ranges, analysis result hash).
Partial unique index `(experiment_id) WHERE decision IN ('promote','reject')` —
extend/inconclusive may repeat, a terminal decision may not.

### 4.10 `promotion_drafts` (Part K)

`decision_record_id` FK, `target_type` enum whitelist {learning_path,
pack_recommendation, workflow_binding, matching_config, eco_rollout_policy,
pricing_presentation}, `target_ref` String(64), `draft_payload` JSONB, `status`
enum {draft, approved, applied, rejected}, `approved_by`, `applied_at`,
`apply_error` Text. Apply is idempotent: `applied_at` already set → 409
`PROMOTION_ALREADY_APPLIED`. Apply produces a **draft object in the target
domain** (e.g. eco RolloutPlan draft, new LearningPath version draft) — never a
direct production mutation ("never silently rewrite").

### 4.11 `experiment_events` (audit)

`experiment_id`, `actor_user_id` nullable (worker = null), `event_type`
String(40), `payload` JSONB. Every transition, amendment, ramp change,
guardrail action, and analysis look lands one row.

### 4.12 `holdout_groups` (v2 — cumulative-impact holdouts, Statsig-style)

`id`, `key` unique, `title`, `domain`, `scope_org_id` nullable, `holdout_bp`
Integer (e.g. 200 = 2%), `starts_at`, `ends_at` (typically ~6 months),
`status` enum {active, released, analyzed}. Units hashing into a holdout group
(salt `holdout:{key}`) are excluded from ALL experiments in its domain/scope
for the period; at release, aggregate metrics of holdout vs non-holdout
measure the cumulative impact of everything shipped. `experiments.holdout_bp`
(per-experiment holdout) remains for single-experiment long-term control.
Membership is computed, not stored (deterministic hash) — a
`holdout_exclusions` check runs inside `resolve_variant` step 3.

### 4.13 Health checks (v2 — implemented WITHOUT a dedicated table)

The original design called for an `experiment_health_checks` table; the
implementation records health signals through two EXISTING channels
instead (round 148 doc-honesty correction — no such table exists):
alert-style findings (SRM, exposure-SRM, interaction) land as
`guardrail_events` rows with reserved keys (`__srm__` etc., alert-only,
dedup-windowed), and analysis-time findings (pre_balance, novelty, A/A
probe verdicts, data-flow) ride the analysis `warnings` list and the
diagnostics endpoints. The console surfaces them via the diagnostics
page, the SRM banner, the detail page's guardrail-freshness line and the
round-146 list data-flow badge.

### 4.14 Quantile metrics (v3 round 124 — the quantile epoch)

Mean-based sufficient stats cannot answer "did p95 latency regress?" —
the industry-standard question (Statsig/Eppo both ship percentile
metrics). Design, three steps mirroring the §4.6 v3 epoch:

**Step 1 — spec/definition.** `metric_definitions.spec.quantiles`:
optional list of 1–3 probabilities in (0, 1) (e.g. `[0.5, 0.95]`).
Operational knob (PATCHable): it changes what is REPORTED, not what the
stored sufficient stats mean. Only continuous-kind metrics accept it.

**Step 2 — sketch.** Snapshots gain `value_histogram` JSONB (migration
exp13): a fixed base-2 log histogram over positive values —
`{"<bucket>": count}` where bucket = clamp(floor(log2(x)), -20, 43),
plus `"__zero__"` and `"__neg__"` overflow keys (counts only; quantile
estimation refuses when neg > 0 — honest for latency/cost, the target
domain). Mergeable across windows and segments by plain addition (the
same fold the covariates map uses). Sources producing per-event values
populate it ONLY when the definition requests quantiles (no silent write
amplification). ~64 buckets ≈ 2 significant digits of relative precision:
enough for a p95 regression read, tiny in storage.

**Step 2b — percentile guardrails (round 128).** A continuous definition
with the quantiles knob can set `spec.guardrail_aggregate: "p95"` (any
pNN): the guardrail window folds the sketch bucket-wise and guards
`histogram_quantile(fold, 0.95)` itself — "pause when p95 latency
regresses past X". No sketch in the window means not evaluable (skip,
never crash).

**Step 3 — math + analysis.** Pure core `histogram_quantile(hist, p)`:
cumulative-count walk, geometric interpolation inside the bucket
(sqrt(lo·hi) at the midpoint rank fraction). Distribution-free CI from
order statistics: rank bounds r± = np ± z·sqrt(np(1−p)) mapped back
through the histogram (conservative, no normality assumed — the caveat
says so). Per-variant estimates + control-vs-treatment difference with a
conservative combined CI ride the analysis result under
`quantiles: {"0.5": {...}, "0.95": {...}}`; never a decision basis on
their own (the primary comparison stays the registered engine's).

### 4.6b Auto covariate selection (v5 round 201 — design)

Multi-covariate CUPED (v3) takes an explicit covariate_metrics list. The
last deferred item, "ML-learned covariates", ships in its honest minimal
form: DATA-DRIVEN SELECTION, not learned embeddings.

**Spec.** `covariate_metrics: ["auto"]` — a reserved literal (mutually
exclusive with explicit keys; the validator rejects mixing).

**Snapshot side.** Auto folds the DEFAULT covariate for every registered
provider (a small registry AUTO_COVARIATE_DEFAULTS maps provider source
-> its canonical covariate metric key), so the stored aggregates carry
every candidate — selection can then happen at analysis time with no
extra reads.

**Analysis side.** For each candidate the pooled pre-period correlation
is computable from the stored sums alone (cov_xy_sum, cov_sum,
cov_sum_sq, sum_value/numerator, n). Candidates with |r| >= 0.1 are kept
(at most 3, strongest first, deterministic tie-break by key); the chosen
set feeds the existing multi-CUPED estimator and the run warns
CUPED_AUTO_SELECTED (with the keys) so the selection is never silent.
No candidate qualifying degrades to plain Welch with CUPED_AUTO_NONE —
honest refusal over a useless adjustment.

Three-step shape: design (this), selection core + snapshot fold +
validator (step 1-2), console surfacing of the selected keys (step 3).

### 4.15 Kaplan-Meier time-to-event (v3 rounds 181–183 — SHIPPED)

time_to_event metrics analyze as binary-at-horizon (honest caveat
attached); full KM adds censoring correctness — none of the compared
vendors ship it. Built in the proven three-step shape (core round 181,
wiring round 182, console strip round 183):

**Step 1 — pure core.** `km_curve(events: dict[int, int], censored:
dict[int, int], n0: int)` over DAY-granular counts: the product-limit
estimator S(t) = prod(1 - d_i/n_i) with Greenwood standard errors, plus
`km_compare(control, treatment)` — the survival difference at the horizon
with a normal-approximation CI from the combined Greenwood SEs
(z = diff/se; as-built — simpler than the log-rank sketch in the original
design note, and honest about being a horizon comparison rather than a
whole-curve test). Refusals: n0 < 2, no events in the arm, d > at-risk,
malformed counts; km_compare refuses when either curve is absent.

**Step 2 — analysis-time counts (REVISED, the ITS precedent).** KM counts
are cumulative-from-assignment, so per-window snapshot rows would need
latest-window (not additive) aggregation — the wrong shape for the
snapshot store. Instead the analysis computes counts ON DEMAND for
time_to_event primaries: per arm, each unit's day = (event_time -
its assigned_at).days (events) or (horizon - assigned_at).days
(censorings for units with no event), fed to km_curve/km_compare. No
migration, no fold semantics, no write amplification; the cost is one
assignment scan plus one event query per analysis run. The `km` block
rides next to the binary-at-horizon read, which stays authoritative;
console strip mirrors the ITS pattern. The event reader is
placement-based, so the knob and the analysis gate both require
source == talent_outcomes (round 188, defect #70) — other time_to_event
sources (billing retention) need their own reader before opting in.

### 4.16 Synthetic control (v3 round 193 — design)

Observational runs today carry DiD (§10 v2) and ITS (§10 v3). Synthetic
control closes the deferred list's largest item: instead of assuming
parallel trends (DiD) or modeling one interrupted series (ITS), build a
WEIGHTED COMBINATION of control-arm units whose pre-period trajectory
matches the treatment arm's, then read the post-period gap. Three-step
shape as before:

**Step 1 — pure core.** `synthetic_control(pre_treated, post_treated,
donors_pre, donors_post)` over day-granular series: simplex-constrained
weights (w_i >= 0, sum w = 1) fit by deterministic projected-gradient
descent on ||pre_treated - W . donors_pre||^2 (fixed iteration budget,
no randomness); outputs the post-period gap mean, the pre-fit RMSPE, the
post/pre RMSPE ratio (the honesty readout — a ratio near 1 means the fit
explains nothing), and a PLACEBO p: each donor is refit as a
pseudo-treated unit and p = rank of the true ratio among placebo ratios
(Abadie-style permutation inference, deterministic). Refusals: < 3 pre
points, < 2 donors, all-constant donor matrix.

**Step 2 — analysis-time series (the ITS/KM precedent).** Per-unit daily
means come from the SAME on-demand source reads ITS uses — one source
call per day with variant_units = {unit_id: [unit_id]} fans the per-unit
split out of a single query, so the cost stays 2 x ITS_DAYS calls, not
units x days. Treated series = treatment-arm mean; donor pool =
control-arm units capped at SC_MAX_DONORS = 20 (first-assigned order,
deterministic); smaller pools warn SC_DONOR_POOL_SMALL. Attaches as
`synthetic_control` on the FIRST primary of observational runs next to
`its`, association-only caveat, segment runs untouched (early return).

**Step 3 — console strip** mirroring ITS/KM: gap, placebo p, RMSPE
ratio, donor count, caveat.

### 4.17 Anonymous → login identity resolution (round 209 — design)

Every compared vendor serves pre-login traffic and carries the
assignment across login; we have neither. Honest minimal design in our
idioms:

**Unit namespace (REVISED at build).** "anonymous" is an ID NAMESPACE
normalized at the resolve boundary, NOT a spec unit type — eligibility
compares unit_type against spec.unit_type, so an unlinked anon id
resolves as a user-typed unit under its own ULID (specs stay "user";
bucketing, stickiness, holdouts and exposure dedup all work unchanged)
and its history migrates in place when the link lands.

**exp15 migration.** `experiment_identity_links(anonymous_id PK,
user_id, created_at)` — GLOBAL, one anon id links to exactly one user,
ever. Re-linking the same pair is idempotent 200; linking a taken anon
id to a DIFFERENT user is 422 EXPERIMENT_IDENTITY_CONFLICT (first link
wins — silent rebinding is identity theft). Index on user_id for the
reverse lookup.

**Link endpoint.** POST /experiments/identity-links {anonymous_id} —
authenticated; user_id is ALWAYS the caller (you can only claim your own
pre-login history; platform admin may pass an explicit user_id for
support flows). On link, every (anonymous, anon_id) assignment row
MIGRATES IN PLACE to (user, user_id) — variant, bucket, version and
assigned_at preserved (ITT timing intact, exposure FKs intact, no
duplicate roster rows). Where the user ALREADY holds a row in the same
experiment, the user row stays authoritative, the anon row is removed,
and an experiment_identity_conflict EVENT records both variants — the
audit trail is the memory, and the analysis caveat stands on the event.

**Resolution law.** resolve(anonymous, X) first follows the link: a
linked anon id serves the USER's assignments (one person, one
experience, regardless of which id the client still holds). Unlinked
anon ids resolve normally. resolve(user, U) needs no special casing —
migration moved history under the user key.

**Honesty.** Linking is treatment-independent only when login behavior
is not an outcome of the treatment — the §4.7 exposure-SRM guard
already covers the dilution class; the conflict event covers the rest.

Shipped rounds 209-225: migration exp15/exp16 (links + the privacy
CASCADE), the link service with in-place migration, both resolve paths
race-hardened (#73), exposure survival and namespace (#74/#75), the
nested-savepoint exposure retry (#76), wave 41 (21/26), the web SDK
wired into login AND register, live E2E 136 (the wall keeps growing
with each seam: full-fold, admin override).

## 5. Lifecycle state machine

```
draft → review → scheduled → running ⇄ paused → completed → analyzed
                                                → promoted | rejected | archived
any non-terminal → archived
```

- Table-driven transitions (`_ALLOWED: dict[str, frozenset[str]]`); illegal →
  422 `EXPERIMENT_INVALID_TRANSITION` (eco `RolloutService._check_transition`
  pattern).
- `review → scheduled` preconditions: full spec validation, layer slices
  allocated, `risk_class=high` needs platform admin, **guardrails non-empty**
  (mandatory except risk_class=low in marketplace/operational), and the v2
  **launch checklist** complete (structured JSONB on the review record:
  hypothesis peer-checked, power computed, metrics/guardrails reviewed, ethics
  screen for talent_flow/learning domains, rollback owner named).
- Org-level **default guardrail policies** (v2): a platform/org policy table
  auto-attaches baseline guardrails (cost ceiling, failure-rate ceiling) to
  every new experiment in scope; spec-level guardrails add to, never replace,
  policy guardrails.
- Transitions are serialized with `SELECT ... FOR UPDATE` on the experiment row
  (R396 lesson).
- `extend` keeps status `analyzed` and pushes `analysis_close_at` out; it never
  returns to running (no re-randomization, ever).

## 6. Deterministic bucketing & sticky assignment (Part B)

```python
def bucket(layer_key, unit_type, unit_id) -> int:          # layer slice
    return int(sha256(f"layer:{layer_key}:{unit_type}:{unit_id}").hexdigest()[:8], 16) % 10000

def variant_roll(exp_key, version_salt, unit_type, unit_id) -> int:   # variant point
    return int(sha256(f"variant:{exp_key}:{version_salt}:{unit_type}:{unit_id}").hexdigest()[:8], 16) % 10000
```

Two independent salts (`layer:` / `variant:`) keep layer bucket and variant
roll uncorrelated. `version_salt` = first 8 hex chars of version 1's
`spec_hash` and **never changes across versions** (re-randomization is
forbidden under the immutable-spec rule).

`facade.resolve_variant(db, *, experiment_key, unit_type, unit_id, context)
-> ResolvedVariant | None`:

1. Load experiment (30s in-memory TTL cache; determinism makes staleness safe).
   Not running → return the existing assignment if any (paused/completed keep
   serving the assigned variant until `ended_at`; pause stops NEW entries only),
   else None.
2. Existing assignment row → return it (sticky).
3. Evaluate population rules (whitelisted fields from context/domain lookups);
   ineligible → None.
4. `b = bucket(...)`; outside this experiment's slice range → None (layer
   exclusion). Ramp: local offset within slice ≥ ramp fraction → None. Ramp
   only widens eligibility; ramp-down never reassigns (protects ITT).
5. Holdout: roll < holdout_bp → write `is_holdout=True` assignment, return None.
6. Variant: cumulative `weight_bp` interval lookup on `variant_roll`.
7. `INSERT ... ON CONFLICT DO NOTHING`, then SELECT-back as truth (race-safe).
8. **Assignment ≠ exposure.** Integration points call
   `facade.record_exposure(...)` at the moment the variant actually takes
   effect (Part L exposure diagnostics depend on this split).

Resolution response example:

```json
{
  "experiment_key": "rubric-wording-b",
  "variant_key": "treatment",
  "config": { "rubric_template_id": "01H..." },
  "assigned_version": 1,
  "is_holdout": false
}
```

## 7. Integration points (facade consumers)

| Domain                     | hook                                       | unit_type             | variant.config meaning                                                                                                                               |
| -------------------------- | ------------------------------------------ | --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Learning paths (Part F)    | learning_path service, path-structure read | user / cohort         | alternative pack order / prerequisite structure id                                                                                                   |
| Rubrics (assessment)       | evaluation service, rubric-template pick   | cohort                | rubric_template_id                                                                                                                                   |
| Workflow/provider (Part G) | workflow_runtime step-binding resolution   | workflow_installation | provider_offering_id / release_id — **still passes the R82 runtime capability re-check**; experiments never exempt                                   |
| Matching (Part H)          | matching engine MatchingConfig read        | organization          | matching_config_id (existing versioned row); only soft-weight fields whitelisted — hard authorization/eligibility constraints are not experimentable |
| Registry presentation      | registry list ordering/badges              | user                  | ordering strategy key                                                                                                                                |
| Operational/cost           | eco rollout / retry policy                 | tenant                | policy parameters                                                                                                                                    |

| Pre-login surfaces (§4.17) | useAnonExperiment (web SDK) | user (anon namespace) | same as the user surface — the device-held anon id resolves through the identity link |

Facade is the only entry point (eco facade discipline). Configs returned to a
domain still pass ALL of that domain's existing validations and approval gates.

Client SDK surfaces (round 227 summary): useExperiment (authed self-serve,
§7 above), useAnonExperiment + claimAnonymousId (pre-login, §4.17 — the
claim fires on BOTH conversion points, login and register), each with the
#54 null-safe fail-safe shape and the #57 identity-stable exposure
callback.

## 8. Metrics & long-term outcomes (Part C/I)

- Worker topic `exp.compute_snapshots`: for experiments in
  running/completed/analyzed with `now < analysis_close_at`, join exposed-unit
  sets against product data per metric definition; aggregate per variant per
  UTC day window. ITT: group by assigned variant regardless of later behavior.
- `analysis_close_at` defaults to `ended_at + 90d`; time_to_event metrics
  (capability_retained_30d/90d, placement_retention, repeat-client acceptance)
  keep snapshotting after completion — only archive or close-date stops them.

## 9. Guardrails (Part D) + SRM

Sweep `sweep_experiment_guardrails` (10 min, reuses eco sweep pattern **with the
fairness cap**: take cap rows ordered by `last_checked_at` asc, stamp after
processing — the §106.26 accumulation-bomb lesson):

1. Compute each guardrail metric over its window.
2. Breach → `guardrail_events(action='paused', auto=True)` + running→paused via
   the same FOR-UPDATE state machine + owner notification. **No auto-promote
   path exists anywhere in the codebase** (asserted by a grep-level test).
3. Built-in SRM check (not disableable): chi-square of assignment counts vs
   weights; p < 0.001 → `guardrail_events(action='alerted',
guardrail_key='__srm__')` + red banner in the analysis view.

Built-in guardrail metrics: cost_usd (controlplane rating), run_failure_rate,
p95_latency_ms (WorkflowRun), complaint_count, client_rejection_rate,
security_incident (manual endpoint → immediate pause).

v2 timing: guardrail metrics get an **hourly fast-lane** aggregation (small
sufficient-stats query per running experiment); full analysis snapshots stay
daily.

v2 health-check suite (beyond SRM, persisted to `experiment_health_checks`):

- **exposure_srm** — chi-square on exposure counts per variant; divergence from
  assignment ratios flags trigger bias for triggered analyses.
- **aa_probe** — automated A/A: each layer keeps one synthetic 50/50 experiment
  with no treatment; any "significant" A/A result flags the pipeline itself.
- **pre_balance** — pre-experiment covariate balance across variants
  (standardized mean difference > 0.1 → warn).
- **novelty** — days-since-exposure cohort curve on the primary metric; effect
  decaying to zero flags novelty (Statsig-style).
- **interaction** (v2, cross-experiment): weekly pairwise scan over
  concurrently running experiments in DIFFERENT layers sharing exposed units —
  two-way contingency/regression interaction test with BH correction; a
  significant interaction warns both owners (Microsoft ExP practice). Same-layer
  pairs cannot interact by construction.

## 10. Statistical core (Part E — `services/analysis.py`, pure, zero I/O)

| case                         | method                                                                                                                                                                                                                          | output                                                                   |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| binary                       | two-proportion z + Wilson 95% CI; absolute + relative effect                                                                                                                                                                    | `{"effect": 0.031, "ci": [0.004, 0.058], "p": 0.024, "relative": 0.078}` |
| continuous                   | Welch t reconstructed from n/sum/sum_sq (no raw rows needed)                                                                                                                                                                    | mean diff + CI                                                           |
| rate                         | delta method over events/exposure_time                                                                                                                                                                                          | rate diff + CI                                                           |
| time_to_event                | windowed KM survival diff + Greenwood CI (no Cox — YAGNI)                                                                                                                                                                       | 30/90d retention diff                                                    |
| clustered (cohort/org units) | cluster-level means, then Welch t; n = cluster count (no pseudo-independence)                                                                                                                                                   | as above                                                                 |
| sequential                   | `obrien_fleming`: alpha-spending, look registry in `experiment_events`, over `max_looks` → 422 `EXPERIMENT_LOOKS_EXHAUSTED`; **`msprt` (v2, default)**: mixture SPRT always-valid CIs — peek freely, no look budget             | adjusted boundary / always-valid CI                                      |
| multiplicity                 | Benjamini-Hochberg (FDR 0.05) across secondary metrics; each carries `passes_fdr`                                                                                                                                               |                                                                          |
| **CUPED (v2)**               | theta = cov_xy/cov_var from snapshot sufficient stats; adjusted Y − θ(X − mean(X)); reported as variance-reduction % alongside unadjusted result                                                                                | tighter CI, both shown                                                   |
| **Bayesian engine (v2)**     | conjugate posteriors (Beta-Binomial for binary, Normal-inverse-gamma for continuous); reports P(beat control), expected loss, 95% credible interval; optional prior from meta-analysis corpus (§11), default weakly-informative | posterior summary                                                        |
| **post-stratification (v2)** | small-n cohort/org experiments: strata-weighted effect over pre-registered strata (org size / cohort track)                                                                                                                     | stratified estimate + CI                                                 |
| **switchback (v2)**          | (unit × window) randomization, washout excluded, cluster-robust SE over switch units, balanced design validated at spec time                                                                                                    | effect + robust CI                                                       |
| **triggered (v2)**           | exposed-only population; dilution-corrected extrapolation to assigned population shown next to triggered estimate; exposure-SRM gate                                                                                            | both estimates                                                           |
| **quasi-experiments (v2)**   | DiD (parallel-trends diagnostic plotted) and interrupted time series for `analysis_type=observational`; always `causal_claim:false`; synthetic control shipped (§4.16, rounds 193-196)                                          | effect + caveat                                                          |

- Every result includes `practical_effect` (effect size + CI); the UI leads
  with CIs, not p-values.
- Observational experiments run the same pipeline but respond with
  `"causal_claim": false` plus a caveat string, and cannot promote.
- No scipy dependency: hand-written z/t/chi-square/Beta-posterior routines with
  golden-value unit tests (constants precomputed in R). CUPED, mSPRT, Bayesian
  and post-stratification are all sufficient-statistics computations — no raw
  rows leave the snapshot layer. Bandit allocation (Thompson sampling) lives in
  `services/bandit.py`, gated per §4.2 domain whitelist.
- provider_offering units are documented as installation-clustered designs and
  automatically routed to the clustered path.

## 11. Decisions & promotion (Part J/K)

- `POST /experiments/{id}/decisions`: only in `analyzed`; body references the
  latest analysis result hash (prevents decide-before-analyze); approver is the
  caller; risk_class=high requires platform admin.
- `POST /decisions/{id}/promotion-drafts`: decision=promote only; whitelisted
  target_type; payload generated by `promotion.py` calling the target domain's
  existing validation; apply re-validates and is idempotent.
- The decision registry (`GET /decisions?domain=&decision=&q=`) is searchable
  organizational memory so questions are not silently re-tested.
- **Meta-analysis (v2, Statsig Meta-Analysis class):**
  `GET /decisions/meta?domain=` aggregates the DecisionRecord corpus — win
  rate, effect-size distribution, median lift by domain/metric — and exposes an
  empirical prior the Bayesian engine can opt into (`prior: "corpus"`).
  Observational records are excluded from priors.

## 12. API surface (all `{data}` / `{data, meta}` envelopes)

```
POST   /experiments                              409 EXPERIMENT_KEY_TAKEN
GET    /experiments?status=&domain=&cursor=      keyset (id desc; cursor key == sort key — R395)
GET    /experiments/{id}                         404 uniform
POST   /experiments/{id}/versions                draft/review only
POST   /experiments/{id}/transition              422 EXPERIMENT_INVALID_TRANSITION
PATCH  /experiments/{id}/ramp                    422 EXPERIMENT_RAMP_DECREASE
GET    /experiments/{id}/assignments?variant=&cursor=
POST   /experiments/{id}/assignments:preview     dry-run bucketing, no writes
GET    /experiments/{id}/exposures/stats         exposure funnel diagnostics
GET    /experiments/{id}/metrics?window=
POST   /experiments/{id}/analysis                registers a look; 422 EXPERIMENT_LOOKS_EXHAUSTED
GET    /experiments/{id}/guardrails/events
POST   /experiments/{id}/guardrails/incident     manual incident → immediate pause
POST   /experiments/{id}/decisions               422 DECISION_STATE_INVALID
GET    /decisions?domain=&decision=&q=
POST   /decisions/{id}/promotion-drafts          422 PROMOTION_REQUIRES_RANDOMIZED
POST   /promotion-drafts/{id}/approve|apply|reject   409 PROMOTION_ALREADY_APPLIED
GET|POST /layers ; POST /layers/{key}/allocations    409 LAYER_SLICE_OVERLAP
GET|POST /metric-definitions                     admin
```

Additional error codes: `EXPERIMENT_NOT_FOUND` (uniform 404),
`EXPERIMENT_SPEC_INVALID`, `EXPERIMENT_FORBIDDEN_TARGETING`,
`EXPERIMENT_UNIT_OUT_OF_SCOPE`, `EXPERIMENT_NO_GUARDRAILS`,
`METRIC_KEY_UNKNOWN`. Every enum query param goes through `check_enum`
(silent-empty is a lie — ADR-016 §106.6). All new routes join the route-table
auth sweep (ADR-016 §96).

## 13. Worker (reuses controlplane outbox)

Topics: `exp.compute_snapshots`, `exp.evaluate_guardrails`,
`exp.close_experiment` (ended_at reached → completed), `exp.apply_promotion`.
Sweeps: `sweep_experiment_guardrails` (10 min, fairness cap),
`sweep_experiment_windows` (daily), `sweep_experiment_closures`,
`prune_experiment_history` (exposures archived to
`experiment_exposures_archive` after 400d — audit is never deleted).
All handlers idempotent under at-least-once delivery (UPSERT / dedup_key).

## 14. Frontend (Part L — 13 pages)

Under `/dashboard/experiments/`: list (status/domain filters as URL state —
§106.21), `new/` (stepped builder: spec → variants → metrics → guardrails →
power calculator), `[experimentId]/` (overview + lifecycle actions),
`.../assignments` (diagnostics + SRM banner), `.../metrics` (snapshot matrix),
`.../analysis` (CI forest plot; observational caveat banner), `.../guardrails`,
`decisions/` (searchable registry), `decisions/[decisionId]/`, `promotions/`
(rollout monitor), `layers/`, `metrics/` (metric explorer). Domain entry
points: "Run experiment" links on workflow-pack, matching and learning-path
detail pages with prefilled domain. All lists: keyset pagination + meta totals
(§106.19) + Load-more failures surfacing in the error banner (§106.18).

## 15. Testing plan

- `test_exp_endpoints_nodb.py` — 401/403/404/422 contracts, enum guards,
  route-shadowing guard.
- `test_exp_services_db.py`, `test_exp_assignment_db.py` (concurrent
  double-resolve race, ON CONFLICT truth), `test_exp_layers_db.py` (overlap
  rejection, FOR UPDATE serialization), `test_exp_guardrails_db.py`
  (breach→paused, SRM, fairness cap starvation), `test_exp_lifecycle_db.py`
  (full illegal-transition matrix).
- `test_exp_analysis.py` — golden values vs R constants, CI coverage via Monte
  Carlo, BH and OF boundaries, clustered n assertion; **mutation testing on
  analysis.py and the bucketing core** (R136–R250 discipline: 100% on decision
  cores).
- `test_exp_properties.py` — Hypothesis: bucket uniformity (chi-square),
  stickiness idempotence, layer exclusivity, ramp monotonicity.
- `test_exp_security.py` — forbidden targeting rejected, talent targets
  structurally absent, cross-tenant 404, observational cannot promote,
  no-auto-promote grep assertion.
- `e2e_experiment_lifecycle.py` — hypothesis → run → expose → snapshot →
  analyze → decide → promotion draft appears in target domain (final
  acceptance criterion).
- Frontend `__tests__/experiments-*.test.tsx` — builder validation, URL-state
  filters, caveat rendering.

## 16. Delivery phases (each independently shippable)

1. **exp01** — models + migrations + state machine + layers + spec validation + security.py + nodb contract tests
2. **exp02** — assignment/exposure + facade resolve/record + property + race tests
3. **exp03** — metric definitions/snapshots + snapshot worker + provenance
4. **exp04** — guardrails + SRM + sweeps + pause chain
5. **exp05** — analysis pure core + analysis API + look registration (mutation clean)
6. **exp06** — decisions + promotion drafts + per-domain apply adapters
7. **exp07** — six domain integration hooks
8. **exp08** — frontend (13 pages) + tests
9. **exp09** — E2E + hardening sweep (enum guards, pagination uniformity, audit parity)
10. **exp10 (v2 stats)** — CUPED + Bayesian engine + mSPRT + winsorization/percentile metrics + triggered analysis + post-stratification (mutation clean)
11. **exp11 (v2 designs & ops)** — switchback design + scoped bandits + global holdouts + health-check suite (A/A, exposure-SRM, pre-balance, novelty, interaction) + guardrail policies + hourly fast-lane + launch checklist + meta-analysis + `useExperiment` TS hook with batched exposure endpoint
12. **v3 epochs (rounds 113–172, migrations exp10–exp14)** — scheduled
    auto-start (exp10) + per-assignment exposure dedup (exp11) +
    MULTI-COVARIATE CUPED (§4.6 v3, exp12: provider registry, joint OLS at
    1e-9 vs a per-unit oracle) + BINARY CUPED (§4.6 v4, regression-adjusted
    proportions) + QUANTILE METRICS (§4.14, exp13: log-histogram sketch,
    distribution-free CIs, percentile guardrails) + SCHEDULED RAMP PLANS
    (exp14, monotone steps via a crash-tolerant sweep) + weekly owner
    digest + look history + the export trio with console downloads + the
    #63 schedule gate + the CALIBRATION QUARTET (null alpha, power at the
    planner's exact n, sequential anytime-validity, quantile CI coverage —
    all deterministic Monte-Carlo in the main suite). Verification stack at
    this writing: mutation waves 1–35 (~1100 mutants, every module waved),
    fuzz totality, 131 full-suite certifications (latest 6946/6946), live
    E2E 106 checks, defects #1–#69 each fixed with a kill-proof.
13. **Causal-inference epochs (rounds 177–197)** — ITS (§10 v3, segmented
    OLS over on-demand daily source windows, rounds 177–180) + full
    KAPLAN-MEIER (§4.15, censoring-correct horizon block from on-demand
    assignment/placement counts, source-gated per #70, rounds 181–192) +
    SYNTHETIC CONTROL (§4.16, simplex donor weights, placebo permutation
    inference, per-unit daily fan-out, rounds 193–197) — each epoch
    design → pure core with hand oracle → analysis-time wiring pinned
    bit-for-bit against the core → console strip → mutation wave (36–39)
    with reasoned ledgers. Defects #70–#72 (wrong-source KM opt-in; the
    Explorer offering what the API refuses; a mid-wave commit shipping a
    live mutant — now an iron law). Live E2E at this item's writing: 110
    checks (136 as of round 232); certifications through 139 (6955/6955;
    151 as of round 232). Observational analyses carry the three
    blocks at ~1s wall against local Postgres (ITS 28 + SC 28 on-demand
    daily reads + KM's two queries) — informational cost, segment runs
    exempt via the early return.
14. **Identity epoch (rounds 209–215, exp15)** — anonymous→login
    resolution: the anonymous ID NAMESPACE normalized at the resolve and
    exposure boundaries, a global first-link-wins identity link (422 on
    rebinding), in-place assignment migration preserving ITT timing and
    exposure FKs, user-row-wins conflicts with audit events, the
    unauthenticated rate-limited anon resolve/exposure surfaces and the
    authenticated self link claim. Defects #73 (the link/insert race
    window, fixed on BOTH insert paths with post-insert re-checks), #74
    (conflict deletion cascading exposure audit rows away — re-pointed
    before delete) and #75 (pre-login exposures silently dropped by the
    fail-safe False) each kill-proven; wave 41 at 21/26 with the
    switchback config pin; live E2E 133 checks at the item's writing (136 as of round 232).

## 17. Known edges & explicit decisions

- Unit deletion / GDPR: assignments keep anonymous ULIDs (no PII); exposure
  context forbids PII bodies; the GDPR deletion hook excludes the unit from
  future snapshots (talent/gdpr.py pattern).
- Timezones: all UTC; window_start is always UTC midnight.
- Version bumps: allowed only in draft/review; assignments pin
  `assigned_version`; variant sets can therefore never change mid-run.
- Zero-weight variants rejected at spec validation.
- Ramp-down: refused (422 `EXPERIMENT_RAMP_DECREASE`); pausing is the correct
  lever.
- Bandit + sticky coexistence: Thompson sampling shifts allocation
  probabilities for NEW units only; existing assignments never flip (no yanked
  experiences, ITT preserved within each allocation epoch).
- Explicitly deferred (documented in the competitive analysis):
  feature-flag CDN/edge SDKs, session replay, warehouse connectors (we
  are the warehouse). Anonymous→login identity resolution SHIPPED in
  rounds 209-211 (§4.17).
- Base branch: the epic depends on the eco facade, so implementation chains on
  the issue-35 branch (PR #36) until it merges.

## 18a. Operator runbook (round 58 — what each signal means and what to do)

Every signal below is surfaced in the Console; none requires DB access.

| Signal                                                | Meaning                                                                                                                                                                                                            | First response                                                                                                                             |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `NO_RECENT_EXPOSURES` warning / stale "Last exposure" | The surface stopped recording exposures — almost always a broken host integration, not a finished experiment                                                                                                       | Check the host surface's deploy/logs; verify with POST /experiments/self/exposures on a test account; if intended, complete the experiment |
| `SAMPLE_BELOW_POWER_TARGET` / Underpowered banner     | Not enough units against the declared MDE — a "no effect" read is not evidence of absence                                                                                                                          | Keep running, raise ramp_bp, or accept a bigger MDE; never promote on an underpowered primary                                              |
| SRM alert (`__srm__` guardrail event, alert-only)     | Assignment counts deviate from spec weights — randomization or data-feed suspect                                                                                                                                   | Check recent ramp changes and layer edits; run the layer A/A probe; if unexplained, pause and investigate before trusting ANY result       |
| Exposure-SRM alert                                    | Exposure funnel imbalanced across arms — one arm's surface renders/exposes differently                                                                                                                             | Audit the host surface per arm (error rates, latency); exposure dilution biases toward null                                                |
| Guardrail auto-pause                                  | A declared guardrail breached its threshold                                                                                                                                                                        | The experiment is already safe (paused). Review the breach in Diagnostics → fix or accept → resume via transition running                  |
| `__incident__` event                                  | A human pressed the incident button                                                                                                                                                                                | Coordinate with the operator who filed it; resume only after the stated reason is addressed                                                |
| `PRE_BALANCE_SUSPECT`                                 | CUPED covariate differs across arms pre-experiment — randomization or feed broken                                                                                                                                  | Treat all effects as suspect; re-check assignment integrity (A/A probe, interaction sweep)                                                 |
| `NOVELTY_EFFECT_DECAY_SUSPECT`                        | Early-window effect much larger than late-window                                                                                                                                                                   | Extend the run; judge on the late window; don't promote a novelty spike                                                                    |
| `TRIGGERED_*` warnings                                | Exposed-only analysis population caveats                                                                                                                                                                           | Expected for triggered experiments; confirm provenance markers on snapshots                                                                |
| Interaction alert (both owners notified)              | Two same-domain experiments' assignments correlate                                                                                                                                                                 | Verify layer slices are disjoint; if they are, investigate shared upstream surfaces                                                        |
| Promotion stuck in `applying` / `apply_error` set     | Async apply failed typed and parked back to approved                                                                                                                                                               | Read apply_error on the Promotions page; fix the target-domain issue; re-apply                                                             |
| `CUPED_COVARIATES_UNAVAILABLE`                        | variance_reduction configured but NO covariate aggregates were computed — the estimate is unadjusted                                                                                                               | Check the covariate metrics' definitions (source registered? provider for multi?); lookback window may predate data                        |
| `experiment_identity_conflict` (event)                | An identity link found the user ALREADY assigned in an experiment the anon id was also assigned in — the user row stayed, the anon row (and its exposures, re-pointed) folded in; both variants are in the payload | Expected on shared/stale devices; a spike suggests clients minting fresh anon ids per session instead of persisting one                    |
| `SC_DONOR_POOL_SMALL`                                 | An observational run's synthetic control needs >= 2 control-arm donor units and >= 1 treated unit — this roster has fewer, so no block attached                                                                    | Expected on lone-arm observational rosters; assign control units if a donor-weighted counterfactual is wanted                              |
| `CLUSTERED_DESIGN_NAIVE_SE`                           | A cluster/switchback design analyzed with unit-level (naive) standard errors — intervals are too narrow when outcomes correlate within clusters                                                                    | Read effects directionally; cluster-robust SEs are a future knob — do not promote on a marginal p alone                                    |
| `SNAPSHOT_VERSION_MIXED`                              | The aggregation window mixes snapshot rows computed under different query_versions of a definition                                                                                                                 | Re-sweep the affected windows after a definition change, or read with the mixed-provenance discount                                        |
| `TRIGGERED_DILUTION_UNCORRECTED`                      | The spec asked for triggered (exposed-only) analysis but stored snapshots predate the exposed-population computation — ITT rows dilute the triggered read                                                          | Wait for fresh exposed-population windows (or re-sweep); the dilution biases toward null                                                   |
| `TRIGGERED_SNAPSHOTS_MIXED_POPULATION`                | Some windows were computed exposed-only and some ITT — the aggregate mixes populations                                                                                                                             | Same as above: re-sweep for a uniform population before trusting magnitudes                                                                |
| `CUPED_AUTO_SELECTED`                                 | The "auto" covariate spec picked data-driven covariates for this run (the chosen keys ride each comparison's cuped.covariates)                                                                                     | Nothing — informational; check cuped.covariates if the selection surprises you                                                             |
| `CUPED_AUTO_NONE`                                     | The "auto" covariate spec found NO candidate with pooled abs(r) >= 0.1 (or no covariate aggregates exist) — the run fell back to plain Welch                                                                       | Expected on sparse pre-periods; if persistent, name covariates explicitly or accept the unadjusted read                                    |
| `KM_SOURCE_UNSUPPORTED`                               | A time_to_event primary opted into KM but its source is not talent_outcomes — the placement-based event reader cannot serve it (#70)                                                                               | Strip the km knob (PATCH km=false) or wait for a per-source event reader; the binary-at-horizon read is unaffected                         |
| `CUPED_MULTI_DEGRADED`                                | A multi-covariate spec fell back to the SINGLE-covariate adjustment (missing provider or degenerate joint design)                                                                                                  | Check each covariate's source has a provider and the covariates aren't collinear; the reported CUPED line is one-covariate only            |
| Snapshot holes after an outage                        | Worker was down > SNAPSHOT_BACKFILL_DAYS-1 days                                                                                                                                                                    | Recompute manually: enqueue exp.compute_snapshots for the missing day windows                                                              |

## 18. Implementation notes (exp01–exp11; log runs newest-first)

**State at round 111 (2026-10-03):** 59 numbered defects/gaps fixed (every
fix kill-proven or branch-verified); migrations exp01–exp11; 516 exp tests,
702 web tests (every console page covered), 90-check live E2E, 16 mutation
waves (all killed or ledgered), 86 full-suite certifications all green
(latest 6896/6896). Hot path: ~3 ms new-assignment resolve, ~1 ms sticky.
Coverage: facade/deps 100%, holdouts 99%, decisions/promotion 98%, analysis
core 97%, metrics 96%, hooks/assignment/guardrails/worker/experiments
91-95% — every remaining line individually accounted for (defense-in-depth,
race fallback, or statistical sub-branch). Deliberately deferred (documented
above): full Kaplan-Meier, synthetic control, ITS (no pre-period exists),
org-side full console. (Multi-covariate CUPED left this list in rounds
113-115 — §4.6 v3.) The log below is
chronological, newest first.

Deviations from and refinements to the plan, discovered during implementation:

- **Holdout uses its own salt** (`holdout:`), independent of the variant roll —
  the plan's shared-roll formulation would have skewed variant proportions by
  removing a contiguous low range of the roll space (§6).
- **Guardrail evaluation clock is the DB's `clock_timestamp()`** — app-clock
  windows vs DB-clock `occurred_at` skew made fresh exposures invisible (the
  outbox R-fix class), and `now()` (transaction-frozen) equals same-transaction
  write stamps, which the half-open window's strict `<` excludes (§9).
- **Falsy-zero class**: `get("z") or get("t")` silently dropped sequential
  fields when z was exactly 0.0 (§10 runner).
- **Metric sources take `unit_type`** so a source never joins the wrong id
  space; mismatches return zero-sample results (§8). Wired: exposures,
  workflow_runs, projects, cost_ledger, client_briefs, registry,
  eco_telemetry. Unwired (definitions are the contract): learning_paths
  (progress is derived — needs its own aggregation), evaluations
  (review-pipeline semantics), billing, talent_outcomes.
- **Promotion apply adapters** create the target domain's own draft shape:
  inactive MatchingConfig version, draft LearningPath, UNCONFIRMED
  WorkflowStepBinding suggestion (never overwrites an existing binding —
  SAVEPOINT-guarded 409), draft eco RolloutPlan via RolloutService (eco
  hard-incompatible gate re-runs). pack_recommendation/pricing_presentation
  refuse apply (EXPERIMENT_PROMOTION_UNWIRED) — no target draft store exists.
- **Domain hooks bind to well-known surface keys** (one live experiment per
  surface); the registry hook applies its override BEFORE the cache key so
  cached pages never leak across variants; the binding hook re-runs the full
  R82 capability re-check.
- **Observational promote is refused at DECISION time** (stricter than the
  planned draft-time gate).
- **Mutation campaign** on the statistical core: 147/157 killed; the 10
  survivors are documented equivalent/accuracy-level mutants (test file
  carries the ledger).
- Org-scoped operator routes (`/orgs/{org_id}/experiments`) are still
  platform-admin only; org-admin delegation is follow-up work.

Post-implementation hardening round (same day):

- **Reads are platform-admin gated** (was: any authenticated user could read
  specs, decisions, guardrail events, assignment diagnostics — the R88-91
  authz class); a source-scan test pins that no experiments API module uses
  plain `get_current_user`.
- **Sweeps are actually scheduled**: exp_guardrail_sweep (10 min),
  exp_window_sweep (daily 00:52 UTC) and exp_closure_sweep (hourly) are
  registered in the worker cron table — previously they existed but never
  ran; a test pins the three names into `_cron_jobs()` (§96 guard class).
- **`sweep_experiment_closures`** auto-completes running experiments past
  `stop_policy.max_days` (was missing entirely — max_days was decorative).
- **Window sweep's analysis-close filter moved into SQL before the cap** —
  a closed-analysis backlog could starve live experiments out of capped
  slots (fourth accumulation-bomb shape).
- **Both arms record exposures at the decision point** — hooks previously
  exposed only treatment units, biasing every exposure-based comparison
  (control units now log an `arm: control` exposure when the default
  experience serves; invalid treatment overrides still record nothing).
- **Missing-key negative cache (60s)** on the facade hot path: surfaces
  without a live experiment cost ~zero after the first lookup and no longer
  log per-request; `ExperimentService.create` invalidates the cache
  in-process so a new surface experiment takes effect immediately.
- ADR §4.2 example previously used a non-existent population op
  (`in_experiment_layer`) — layer exclusivity is enforced by slice
  allocation, not population rules.

Hardening round 2 (same day):

- **Promotion drafts are FOR-UPDATE locked** through approve/reject/apply —
  two racing applies previously both passed the idempotency check and
  double-created the target-domain draft (race test: exactly one applied +
  one PROMOTION_ALREADY_APPLIED, exactly one new MatchingConfig version).
- **Bogus scope_org_id is a 404** — the FK violation was swallowed by the
  IntegrityError→EXPERIMENT_KEY_TAKEN mapping and misreported as a key
  conflict.
- **exposure_rate counts DISTINCT exposed units** — a raw event count pushed
  the rate past 1.0 and false-fired lte guardrails.
- **Exposures dedup per unit per UTC day** in every hook (`{unit}:{date}`
  dedup_key, matching the snapshot windows) — control-arm exposure logging
  otherwise wrote a row per page view (table-growth bomb class).
- **Spec size cap 64 KB** before parsing (oversized-input class).
- **Guardrail auto-pause notifies the experiment owner** (fail-safe: a
  notification hiccup never fails the pause — the eco_audit posture).

Hardening round 3 (same day):

- **CRITICAL — the generic transition endpoint could mint promoted/rejected**
  with user-supplied to_status, bypassing the DecisionRecord, the approver
  and the hash gate entirely (the literal `to_status="promoted"` source scan
  cannot see user input). The service now refuses those statuses outside the
  decision path (422 EXPERIMENT_DECISION_REQUIRED); the internal
  `_via_decision=True` token may only be spent by decisions.py (source-scan
  pinned); the Console routes promote/reject through the decision flow.
- **Surface keys were one-shot forever** — the global unique on
  `experiments.key` meant an archived surface experiment blocked that surface
  for the platform's lifetime. Migration exp06: key is unique among LIVE
  experiments only (partial index excluding promoted/rejected/archived);
  resolution binds to the single non-terminal experiment.
- **prune_experiment_history implemented** (was promised, missing): archived
  experiments' raw exposures older than 400 days are deleted batch-capped
  (deviation from the cold-table plan — snapshots retain the aggregates);
  registered as the exp_retention cron.
- Console nav entry is platform-role gated; the detail page no longer offers
  promote/reject buttons (decision flow hint instead).
- Documented limitation: cross-window aggregation treats unit-window
  observations as independent (repeated measures) — per-unit aggregation is
  v2 work alongside the clustered analysis paths.

Hardening round 4 (same day):

- **Window-consistent ITT denominators**: snapshot computation now pins the
  unit set to `assigned_at < window_end` — recomputing yesterday's window
  after today's enrollments previously diluted yesterday's rates with
  necessarily-zero-exposure units.
- **Preview computes against the experiment ROW, not the key** — after key
  reuse (round 3) a key-based preview on an archived experiment id bound to
  the NEWER live experiment; it also 404'd on terminal experiments.
- **Truthful provenance**: the automatic `winsorize_pct` provenance stamp is
  removed — no source applies winsorization yet, so provenance claimed an
  adjustment that never happened (application of the robustness knobs stays
  v2 work; the definition fields remain the contract).
- **Builder self-heal**: if version creation fails after the experiment row
  is created, the Console archives the spec-less orphan (which would
  otherwise hold the live-unique key hostage with no repair surface) before
  surfacing the error.

Hardening round 5 (same day):

- **Poison-spec resilience** across every stored-spec consumer. Specs are
  validated at write, but schema drift / bad data repair can make an old
  version unparseable — previously: guardrail evaluation crashed and
  dead-lettered forever while the experiment kept RUNNING WITHOUT GUARDRAILS;
  the closure sweep crashed the whole batch on one poison row; analysis,
  decisions and preview raw-500'd. Now: guardrails PAUSE the experiment with
  a `__spec_invalid__` event (an unguardable running experiment is unsafe by
  definition), sweeps skip-and-log the poison row, and the API surfaces a
  typed EXPERIMENT_SPEC_INVALID 422.
- **Terminal-set parity guard**: security.TERMINAL_STATUSES and the
  live-key partial index WHERE clause are test-pinned to the same set —
  adding a terminal status to one but not the other silently breaks key
  reuse or uniqueness.
- Reserved column note: `promotion_drafts.apply_error` is currently unused —
  synchronous applies roll back on failure; the column is reserved for a
  future async apply path.

v2 round 10 (2026-10-01, batches 3–15) — the backlog cleared in one sweep:

- **Every declared metric source wired** (batch 3): learning_paths (derived
  all-project-path completion + time-to-completion), evaluations
  (SubmissionReview verdicts), talent_outcomes (Placement, observational
  only), billing (tenant-keyed conversion/ARPU/retention/gross-margin; org
  units refused — double-count), capabilities (score-snapshot gain vs
  pre-window baseline). Unwired set pinned EMPTY; skip-not-crash re-proved
  via a ghost definition.
- **Health checks** (batch 4): PRE_BALANCE_SUSPECT (covariate Welch across
  arms — pre-experiment covariates must not differ), NOVELTY_EFFECT_DECAY
  _SUSPECT (early-half |z|>3 effect flipping/shrinking late; ≥4 windows),
  aa_probe (deterministic decile χ² layer hash-health diagnostic,
  GET /experiments/layers/{key}/aa-probe).
- **Meta-analysis corpus priors** (batch 5): analysis_look events record
  primary effects; ≥3 decided same-domain experiments on the metric yield
  {n, mean, sd} + a normal-normal shrunk_effect. Informational.
- **Async promotion apply** (batch 6): apply_async parks the draft in
  'applying' + outbox handler; typed failure → back to 'approved' with
  apply_error (retryable, consumed); crash → outbox retry; racing manual
  action wins. ?background=true on the apply route.
- **Org-admin read delegation** (batch 7): experiment_read_scope — org
  owners/admins read experiments scoped to their orgs (list SQL-filtered,
  uniform 404 outside scope); roleless users still 403; ALL writes and the
  remaining operator reads stay platform-admin (deliberate non-goal).
- **Time-stratified estimates** (batch 8): pool_stratified inverse-variance
  pooling of per-window effects on primary comparisons (enrollment-drift
  robustness); analyze_binary now exposes its pooled se.
- **Console surfacing** (batch 9): stratified/corpus-shrunk lines, health
  warnings, Apply-async button, apply_error surfaced, Holdouts tab.
- **Bandit suggestions** (batch 10): thompson_weights (seeded Beta
  Monte-Carlo) → top-level `bandit` block for allocation_mode=bandit
  experiments; ADVISORY only — no auto-apply, ever.
- **Switchback design real** (batch 11): epoch-aligned window_minutes
  buckets randomized by the v1 salt (never re-randomized); placeholder
  assignment rows keep the exposure FK + ITT roster; window computation
  attributes the roster to the window's owner variant; exposures fold onto
  it. Batch 12: washout_minutes APPLIED (head-of-window band excluded,
  provenance-stamped; whole-window washout computes nothing).
- **Verification deepened** (batches 13–15): 4 new Hypothesis totality
  contracts (pool_stratified / thompson_weights / chi2_sf /
  switchback_variant) — fuzz defect #27: pool_stratified divided by zero on
  a DENORMAL se (se*se underflows; weights now must be finite themselves);
  live E2E grew to 48 checks (holdout CRUD walls, aa-probe, delegation
  boundary); AST mutation over the new cores 33/43 killed, all 10 survivors
  verified equivalent and ledgered in-test (incl. round(chi2,3→4) being
  mathematically equivalent: chi2 = integer/200).

Round-10 continuation (same day, batches 16-32) — the marathon's second half:

- **Builder**: design/allocation dropdowns + switchback window/washout
  inputs (spec submit carries the config); DESIGNS/ALLOCATION_MODES
  parity-pinned. Console: bandit banner, segment picker, apply_error rows.
- **Triggered analysis applied** (§4.7): exposed-only rosters at snapshot
  time (as_of-pinned), provenance analysis_population=exposed;
  TRIGGERED_ANALYSIS_UNAPPLIED retired for TRIGGERED_DILUTION_UNCORRECTED
  - TRIGGERED_SNAPSHOTS_MIXED_POPULATION.
- **Self-serve surface** (§7 client-SDK class): POST /experiments/self/
  resolve + /exposures (caller IS the unit) + the useExperiment TS hook.
- **DiD for observational analyses** (§10): change-score estimate from
  per-unit covariate sufficient stats, parallel-trends caveat.
- **CUPED extended to cost_ledger**; **segment breakdowns** (§4.8,
  exp08a00008): org-dimension snapshot slices (opt-in, top-20 cap),
  run(?segment=...) informational slices that never burn looks or ground
  decisions; whole-population aggregation strictly excludes slices.
- **Defects #28–#31 (adversarial passes)**: switchback false-SRM (skip both
  SRM checks for time-randomized designs); switchback silently ignoring
  per-unit holdout_bp (now honored, sticky holdout rows); interaction
  pair-cap starvation (ISO-week rotation, §106.26); exposures-source
  numerators not intersected with the passed population (overstated every
  segment/exposed-only slice). Plus version-mixing fixed in the window
  passes and the salt truncation extracted into version_salt_of (one
  definition for resolution and window attribution).
- **Verification**: mutation waves 2-4 (holdouts/interaction 45/51, new
  sources 32/55 after fixing THREE symmetric-fixture collisions, window
  core 24/27) with every survivor classified; DiD fuzz totality; live E2E
  52 checks including the self-serve walls.

Round-10 tail (batches 33-35): feature-combination matrix pinned
(segments × switchback: slices carry the window's variant; segments ×
triggered: slice denominators = exposed ∩ org; multi-org users land in
exactly ONE slice — min org_id); CUPED extended to a third source
(workflow_runs per-installation mean latency); competitive matrix synced.

Round-10 close-out (batches 36-40): org-admin WRITE delegation
(transition + ramp via the read scope, uniform 404 outside it; decisions/
promotions/creation stay platform — direct promote re-pinned refused for
delegated writers); three-arm end-to-end (assignment reaches all arms, one
comparison per treatment, Thompson spans all arms); org-scoped holdout's
symmetric face (it DOES withhold from the org's own experiments); live E2E
grew to 57 checks (write-delegation walls over HTTP).

Round 11 (same day, adversarial continuation) — four more defects:

- **#32** self-serve resolve carried no org context, so org-scoped
  experiments were structurally unreachable from the product surface — the
  caller's primary org (min org_id) now rides along; live E2E walks the full
  delegated-operator journey (schedule w/ checklist → run → ramp →
  self-resolve) to 63 checks.
- **#33** (R88 class) holdout create's duplicate pre-check had a race
  window surfacing an unmapped IntegrityError — flush now maps to the typed
  409; two-session race test.
- **#34** (the round-3 one-shot-key lesson, holdout edition) a RELEASED
  group held its key forever — key uniqueness is now active-only
  (exp09a00009 partial index), release→recreate proven with the new band
  taking effect.
- **#35** (information boundary) after write delegation, an org operator's
  analysis would have carried the cross-org corpus prior — non-platform
  actors now run the identical analysis without the shrinkage context.
  Plus delegation consistency (batch 42): snapshots, analysis run and
  segments honor the same read scope as the operating surfaces.

Round 12: mutation wave 5 over the delegation/self-serve layer (12/13 —
require_platform_admin pinned directly, list filters as equality, keyset
cursor strictly-less-than per R395, next_cursor exactly on full pages; the
sole survivor is the unreachable service-internal limit default, ledgered);
segment-picker web tests; holdout release confirm-guard; self-exposure
dedup_key bound = column bound (#36).

Round 13: delegation reaches the diagnostic surfaces an operator actually
needs — guardrail events (an auto-paused experiment's WHY), assignment
stats, exposure funnel, dry-run preview — while incident/force-evaluate
stay platform-admin; a manifest test pins the exact scope-vs-platform
dependency count per API module (neither set can change as a drive-by).
Note: the experiments Console nav remains platform-gated — delegated org
operators work through the API until an org-side console exists.

Round 14 — defect #37 (funnel integrity): all seven invalid-override
fallback paths across the six surface hooks returned the default experience
WITHOUT an exposure — treatment units with broken overrides vanished from
the funnel, biasing exposed-only analysis and noisily tripping exposure-SRM.
Every fallback now records an arm=fallback exposure at the decision point
(per-unit-per-day deduped), making the funnel a partition again: control /
treatment / fallback.

Round 15: the builder exposes the org-segment opt-in (the spec/API
supported it since round 10 with no Console path to request it); defect
numbering audited #27–#37 consistent. Honest performance note, deferred:
resolve() costs ~3 queries per call on the hot path (experiment row, spec
version, sticky row) — industry client SDKs evaluate locally at ~0. A
process-local spec cache (invalidated by create_version/forget_missing_key)
would cut this. DONE in round 16 with a stronger design than the one
deferred: the cache entry is keyed by (experiment_id, current_version), and
specs are immutable — a version bump misses automatically, so there is NO
staleness window at all (the TTL only bounds memory for dead experiments);
poison specs are never cached, and the guardrail/analysis paths read their
own spec uncached, keeping the poison→pause safety loop untouched.
resolve() drops from ~3 to ~2 queries per call.

Round 17 — defect #38 (alert reachability): the three alert-only findings
(SRM, exposure-SRM, cross-experiment interaction) were silent outside the
Console — owners now get ONE fail-safe notification per dedup window (the
interaction alert notifies BOTH owners), same additive-never-blocking
posture as the pause notification. Round 16 shipped the version-keyed spec
cache (zero staleness, poison never cached, ~3→2 queries per resolve).

Rounds 18-19: last-mile Console inputs for org-scoped/self-expiring
holdout groups; mutation wave 6 over the six surface hooks — 13/13 killed
after one REAL gap closed: the inactive-offering branch of the binding
override had no independent test (an Or→And flip would have let a
deactivated credentialed offering keep serving an override — now pinned to
fall back with the arm=fallback exposure).

Round 20: mutation wave 7 over the decision/promotion flow — 45/45 after
killers. Fifteen survivors were flipped HTTP-status constants (the round-6
lesson recurring at scale): now ONE AST-level contract test pins the full
(error code → status) map for both services, so any flipped constant
anywhere fails a single named test. Semantic killers: omitted
uncertainty/segments/evidence default to {} (an or→and would hand None to
non-null JSONB), inconclusive never extends the close date while extend
moves it by exactly the requested days, and the corpus win-rate pool is
pinned with an ASYMMETRIC 2:1 promote:reject split plus an observational
reject that must stay excluded (the symmetric-collision lesson, third
occurrence — asymmetry is now the default fixture shape).

Round 21: mutation wave 8 over the experiments service lifecycle — 36/36
after killers. The AST status-contract pin extended to experiments.py;
semantic killers: the 64000-byte spec cap is INCLUSIVE (padded to the exact
canonical size programmatically), the guardrail-exemption matrix pinned on
all three refusing corners plus the exempt one, the high-risk schedule gate
holds against DELEGATED writers (403) while the platform admin passes the
same gate, and an equal-value ramp re-apply is not a decrease.

Round 22: mutation wave 9 — layers allocation and the worker sweeps,
30/36 → 36/36 after killers (grand total across nine waves: ~430 sites).
Killers: the allocation boundary matrix (slice_end == total_slices−1 legal,
== refused; adjacency legal; single-point overlap refused on both edges) +
the layers AST status contract; previous_utc_day pinned on a fixed instant;
analysis_close_at == now stays OUT of the window sweep; a stop_policy
elapsing EXACTLY now closes (count pinned to 1); prune retention pinned at
399-keep/401-delete — a flipped cutoff sign would have deleted EVERYTHING
archived, which is exactly the mutant that survived before the killer.

Round 23: mutation wave 10 — the analysis_service internals (108 sites,
the largest single target). Killers: a direct _compare matrix (None-laden
arms behave as zeros → insufficient_data for every kind × engine; engine
signature fields pinned; rate-bayesian extras ride exactly on sufficient
data), the version filter aggregates the HIGHEST version's VALUES (v2-only
sums, not v1+v2), novelty minimum-30 per pooled half and the one-third
ratio pinned from both sides (the exact instant is a float boundary,
ledgered), single-version runs never flag MIXED, the corpus prior takes
each experiment's LATEST look (an older wild look is ignored) and its sd is
the exact sample standard deviation. Remaining survivors ledgered:
unreachable query_version defaults, per-window None-coalesce templates
(round-6 class), float/index-exact instants.

Round 24: the experiment DETAIL page (the lifecycle-operations core UI)
had zero tests — four landed: the review checklist renders five boxes for
ethics domains / four otherwise and rides the schedule transition verbatim,
running transitions carry no checklist body, and analyzed status gates
promote/reject behind the decision flow (no buttons offered). Triple
randomized-seed fuzz pass all green.

Round 25: the ten mutation-wave configs moved from the session scratchpad
into the repo (tests/mutation_configs/ with a results README) so the
campaign is reproducible by anyone, not an artifact of one session; plus
the switchback × holdout-group combination pinned (the group check precedes
the design branch, so members are withheld from switchback enrollment too).

Rounds 26-28: live E2E re-certified at 63/63 after the full campaign; the
last two untested Console subpages (assignment diagnostics incl. the SRM
banner and dry-run preview, and the guardrail dashboard) gained behavior
tests — every Console page now has them; hygiene audit clean (zero
TODO/FIXME in the package, every noqa carries its reason); five
randomized-seed fuzz passes across the rounds all green.

Round 29: the async-apply journey certified over HTTP — park in
'applying', sync apply refused in flight (409), the outbox handler driven
inline lands the draft in 'applied' with its target-domain ref. Live E2E
now 68 checks (both runs green, idempotent against its own residue).

Round 30: guardrail ops endpoints certified over HTTP — manual evaluate,
the incident trigger's 403 wall for non-platform callers, incident →
immediate pause, the org admin SEEING the **incident** event through the
delegated diagnostics, and resuming after the drill. Live E2E 74 checks.

Round 31: a one-off 100k-unit randomization deep-check — layer-bucket
decile uniformity chi2 7.46 (p = .59) and bucket × variant-roll
independence chi2 0.73 (p = .40): the three-salt core is healthy at scale
(the resident aa_probe covers the continuous case at 2k). `make test-exp`
added so maintainers can run the 472-test experimentation suite in one
command.

Round 32: `make e2e-exp` — the live-API E2E (74 checks) now starts its own
uvicorn, runs, and tears down in one command; verified green through the
target twice.

Round 33 — defect #39 (host-transaction safety): the six host call sites
(matching engine, workflow runtime ×2, registry search, cohort path,
evaluation rubric) relied on the hooks being TOTAL, but only the facade's
resolve was shielded — an exception in the override's own validation
queries (db.get on configs/offerings/paths) would have aborted the host
transaction: a crashed evaluation run, workflow start, or matching run.
Every override now runs under a @_shield decorator (any exception → log +
default experience), pinned by an exploding-db.get test that proves the
host session survives.

Round 34 — defect #40 (SEVERE, silent data loss): get_db never commits,
and the registry search and cohort-path reads are READ-path hosts — every
sticky assignment and exposure those two hooks wrote through the request
session was DISCARDED at request end. The experiments looked live (same-
transaction reads in tests masked it) while collecting nothing in
production. Both read-path hooks now run their writes in their OWN short
transaction (committed); write-path hooks stay on the host session so a
host rollback still rolls their exposure back (transactional consistency
both ways). The affected tests moved to committed fixtures with explicit
cleanup.

Round 35 — host commit-timing audit (the #40 follow-through), all six
surfaces mapped:

- registry search, cohort path: READ-path hosts → hooks own their committed
  short transaction (fixed in #40).
- matching: the run endpoint commits right after engine.run → exposure
  persists with the MatchRun.
- rubric: the hook runs before evaluation's R94[H5] pre-LLM commit → the
  exposure rides that commit.
- workflow binding: resolve happens before the R13 write-ahead commit that
  precedes every provider call → persisted with the lease state.
- retry policy: inside create_run, persisted by create_run's commit.
  No new defect — the four write-path hooks are transactionally sound, and
  keeping them on the host session is correct (a host rollback reverts their
  exposure, matching the user-visible outcome).

Round 36: the end-to-end NUMBER-CONSERVATION audit — one 60-unit cohort
flows resolve → exposure → funnel diagnostics → snapshot window → analysis
aggregate → guardrail observed, and every stage must agree on the exact
same assigned/exposed counts; any future double-count or lost write in any
stage breaks exactly one labeled equation. This is the invariant the #40
class violates, now held permanently by a single test.

Round 37: rollback safety — the full exp01→exp09 migration chain was
downgraded to its base (eco10) and re-upgraded to head on the dev database;
all nine downgrades execute cleanly (including the two unique-constraint
swaps and the segment-column removal) and the full suite passes on the
rebuilt schema. Also: the #40 class is CLOSED globally — an app-wide sweep
shows the only facade write-path callers are the six hooks and the
self-serve endpoints, all with audited persistence.

Round 234 — warnings join the decision evidence chain: the analysis_look
event now stores the run's warnings, the scorecard and history return
them, and the decision detail page shows the CITED look's warnings as
amber chips next to the hash (matched by result_hash — never another
look's). The decision-maker reads the caveats where they approve.
Web 730; exp 596.

Round 233 — the PR body syncs 229-232 and three stale E2E counts gain
as-of annotations. Certification 151 green (6976).

Round 232 — design/code drift repaid: §4.17 promised the platform-admin
support override on the link endpoint; the implementation had silently
narrowed it to caller-only. The optional user_id now works — naming
another user without platform admin is 403 FORBIDDEN, the admin path
links on behalf (support flows). Wall 134 -> 136 with both checks over
the wire.

Round 231 — hot-path honesty readout after the identity epoch: user
resolves are UNTOUCHED (3.05 ms new / 1.17 ms sticky vs the 2.56/0.89
pre-identity baseline — same order, local-Postgres noise), and the
anonymous namespace costs one link lookup (~0.5 ms: 3.59 new / 1.65
sticky). No regression; the forwarding design keeps the authed product
path query-free.

Round 230 — §18a completeness sweep: every warning the analysis can emit
now has its runbook row (four were missing — the clustered-SE caveat,
the mixed-version provenance, and the two triggered-population mixes;
EXPERIMENT_UNKNOWN_METRICS lives in the error contract, not §18a).

Round 229 — the observational wall goes FULL-FOLD: the manual snapshot
seeds are gone — a real compute_experiment_window produces everything
the section asserts (engine comparisons, ITS, SC, and NOW the auto
selection firing over the wire with its exposed per-covariate evidence).
Two instructive failures en route: mixed windows (one seeded without
covariates) honestly degrade the cross-window fold to AUTO_NONE, and
the as-of pinning law excludes units assigned after window_end (the
roster was EMPTY until the assignments were backdated into the
pre-period) — both already-designed behaviors, each now exercised by the
wall. 134 checks.

Round 228 — wave 42 over the resolved fold gates (64/77 -> confirm in
flight): ten survivors are the standing per-source window-boundary
ledger (template copies of the exposures-pinned half-open contract);
the real ones got killers — an IN-FLIGHT run (finished_at None) pinned
to be skipped by the per-unit latency guard rather than crash it, and a
21-org fixture pinning the org-segment cap at twenty with its
deterministic tie-break; the single-covariate joint-path routing is
ledgered as equivalent (the providers mirror the inline math by
round-117 construction). Confirm: 66/77 — both killers landed.

Round 227 — §7 gains the pre-login surface row and the client-SDK
summary; §4.17's three-step placeholder becomes the shipped record.
Round 226 — the knob seam audit (every spec knob confirmed to have a
through-the-fold path; #77 was the only gap) and wave 42 staged.

Round 225 — defect #77, found auditing the fold path the alarm's
"segment write amplification" angle led into: EVERY covariate gate in
the metrics sweep keyed on the RAW spec list — for an "auto" spec the
literal matched nothing, so the sources never emitted per-unit y, the
assembler never ran, snapshots carried NO covariates and the whole auto
feature silently degraded to plain Welch at fold time (the round-202
tests missed it by seeding snapshots directly). All six gates now
consult resolve_covariates; pinned by a fold-to-analysis END-TO-END auto
test (snapshot covariates carry both resolved candidates, the legacy
cov_* mirror keys on the first resolved name so the PRE_BALANCE guard
works, CUPED_AUTO_SELECTED rides the analysis). Law: a feature tested
only ABOVE a seam (seeded snapshots) is untested BELOW it — every spec
knob needs one end-to-end path through the fold.

Round 224 — wave 41 re-run over the reworked exposure path: 21/26, every
retry-branch mutant killed by the racing-exposure test, the five
defensive-500 ledgers standing. Certification 148 green (6973); PR body
synced through #76.

Round 223 — defect #76, the last identity-seam race: an exposure in
flight when the link's CONFLICT fold deletes its anon assignment row hit
the FK and was absorbed by the fail-safe as a silently LOST exposure.
The insert now runs in a nested savepoint; on IntegrityError it
re-normalizes once under the current link state and retries against the
surviving user assignment — the exposure belongs to the person, not the
row. Kill-proven (the monkeypatch race fails unfixed); the retry row
asserted to land on the survivor exactly once.

Round 222 — exp16: the identity link's user_id gains its CASCADE foreign
key — the anon↔user mapping is privacy-relevant, so user deletion must
never orphan it (the audit found the column shipped as a bare String;
assignments' unit_id is bare BY DESIGN for multi-unit-type, but the link
is user-only). Pinned by a deletion-cascade test; migrations now
exp01–exp16.

Round 221 — §18a gains the experiment_identity_conflict event row (the
new-signal-ships-with-its-row law, applied to events as well as
warnings); certification 147 recorded green (6972).

Round 220 — the claim wires into REGISTRATION too: the anonymous visitor
who signs up is the canonical identity-link case (browse anonymously,
convert, keep the experience) — the register success path now fires
claimAnonymousId fire-and-forget, pinned by a register-page test.
Web 729.

Round 219 — the claim is WIRED: round 217 had shipped claimAnonymousId
exported but uncalled — the login success path now fires it
fire-and-forget (void, fail-safe), so the pre-login carry actually
happens in the product, not just in the SDK. Pinned by a login-page test
(the claim fires exactly once on success). Web 728. PR body synced
through 218.

Round 218 — fuzz totality catches up with the causal-inference epochs:
hypothesis properties over its_estimate (p in [0,1], dof == n-4,
length-honest), km_curve/km_compare (survival in [0,1], self-compare
exactly null), synthetic_control (simplex weights to 1e-6, non-negative
RMSPEs, finite gap, placebo p in (0,1]) and auto_select_covariates
(<= max_k, threshold-honest, finite r) — four cores, zero crashes over
garbage, the refusal-first design holding total. Also audited and
CONFIRMED present this round: cross-experiment interaction sweep,
scoped bandit posteriors, meta-analysis corpus, time post-stratification
— the P1 ledger is fully implemented, not just folded.

Round 217 — the pre-login web SDK: useAnonExperiment mirrors the
self-serve hook over the anon surfaces (device-held 26-char id in
localStorage with try/catch degradation, the #57 identity-stable
exposure callback, the #54 null-safe fail-safe shape) and
claimAnonymousId posts the link after login, failing safe on the
shared-device 422 so login never blocks on experiment plumbing. Web 727.

Round 216 — bookkeeping: §16 item 14 (the identity epoch) and the PR
body sync through wave 41's extension.

Round 215 (closed) — wave 41 extended over the whole identity surface
(21/26; the switchback config lookup gained its missing pin — a flipped
Eq served another variant's payload; five defensive-500 ledgers).
Certifications 145-146 green (6967). The mirror itself:

Round 215 — #73's switchback mirror: the same link/insert race window
existed around the switchback PLACEHOLDER insert (an orphan roster row,
though no variant flip — the day's variant serves either way). The
post-insert re-check now mirrors into _resolve_switchback; kill-proven
with the same monkeypatch race on a switchback spec (fails unmirrored).

Round 214 — defects #74 and #75, both found auditing the identity
epoch's exposure seam: (#74) the link conflict path deleted the anon
assignment row and ondelete=CASCADE silently destroyed its EXPOSURE
audit rows — violating the exposures' append-only contract; fixed by
re-pointing them at the surviving user assignment before the delete
(the exposure happened to this person; the surviving row IS this
person). (#75) record_exposure never learned the anonymous namespace —
every pre-login exposure silently dropped as the fail-safe False and
triggered analyses undercounted linked users; fixed with the same
normalization resolve uses, plus the missing POST
/experiments/anon/exposures surface (rate-limited, strict schema). The
wall grows to 133 with the unauthenticated exposure check; §4.17 now
covers resolve, link and exposure end to end.

Round 213 — defect #73: a link landing BETWEEN resolve's forward-check
and its assignment insert stranded an orphan anon-keyed row — future
resolves forwarded to the user, who drew a FRESH variant: one person,
two experiences, plus a phantom ITT row. Fixed with a post-insert link
re-check that migrates the just-written row immediately (link_identity
is idempotent; the user-row-wins rule applies), plus an entry-time
idempotent re-link that self-heals any pre-fix orphans. Kill-proven with
a monkeypatch race injecting the link inside the window (fails on the
unfixed code); both id forms asserted to serve one variant afterwards.

Round 212 (closed) — wave 41 over the identity surface: 16/18 after the
single-char floor pin and 422 status pins at both validation raise sites
(bare pytest.raises had left the status codes unpinned — the
two-raise-sites-two-pins law); the two survivors are the defensive 500s
behind constraint-guaranteed re-reads, ledgered. Certification 143 green
(6966). Bookkeeping from the first half of the round:

Round 212 — identity epoch bookkeeping: the §16 deferred list drops
anonymous→login resolution (shipped §4.17), the PR body syncs the epoch,
and wave 41 (link_identity + the resolve namespace normalization) is
staged to run after certification 143.

Round 211 — identity step 2: the wire surface — POST
/experiments/anon/resolve (unauthenticated, rate-limited 60/min,
fail-safe like the self-serve surface, strict 26-char no-colon schema)
and POST /experiments/self/identity-link (the caller claims their OWN
pre-login id). The live wall grows 124 -> 132: anonymous assign +
stickiness, link migration, the logged-in user inheriting the anon
variant, the anon id serving the SAME experience post-link, rebinding
422, malformed-id 422 — all over real HTTP; link debris swept by the
cleanup (verified zero).

Round 210 — identity step 1: exp15 (experiment_identity_links),
the ExperimentIdentityLink model, AssignmentService.link_identity
(first-link-wins 422 on rebinding, idempotent re-link, in-place row
migration with assigned_at preserved, user-row-wins conflict handling
with the audit event) and resolve's anonymous-namespace normalization —
REVISING the design at build: anonymous is an id namespace, not a spec
unit type, because eligibility compares against spec.unit_type. Service
tests cover migration, both-id serving, conflict audit, rebinding 422
and malformed-id refusal.

Round 209 — the identity epoch opens (§4.17, step 0): anonymous unit
type, a global first-link-wins identity link (422 on rebinding),
in-place assignment migration preserving ITT timing and exposure FKs,
conflict events as the audit memory, and link-following resolution so
one person gets one experience across login.

Round 208 — runbook completeness: SC_DONOR_POOL_SMALL gets its §18a row
(the round-195 warning had shipped without one — the
new-warning-ships-with-its-row law caught by this audit).

Round 207 — the auto literal over the wire: the live wall grows 122 ->
124 (auto mixed with explicit covariates refused 422 by the validator;
a lone ["auto"] passes the #63 schedule gate because the gate checks
what it RESOLVES to; an aggregate-less observational run warns
CUPED_AUTO_NONE over HTTP).

Round 206 — matrix truth: every "deferred analytics" claim is de-staled
(synthetic control and auto covariate selection both shipped) — the only
open-by-choice item anywhere is write-side org delegation, a product
scope call.

Round 205 — the cuped_auto evidence reaches the console: a teal strip
lists each auto-selected covariate with its pooled r, so the operator
reads the selection's justification where they read the adjustment.
Web 722.

Round 204 — wave 40 over the auto-covariate epoch: first pass left
seven core survivors because the selection's correlation was an
invisible intermediate — the wave-36 dof lesson applied again: r is now
EXPOSED as the per-metric cuped_auto readout (operators see why each
covariate was chosen), pinned exactly in tests, and the wave closes at
18/18 core, 1/1 resolver, 114/124 run() (all ten survivors standing
ledgers). §18a gains the two auto warnings' rows.

Round 203 — §4.6b step 3: the builder's covariates input documents the
"auto" literal (the free-text field already passed it through; the
selected keys surface on the analysis page via the cuped block's
covariates list, which has rendered since round 145). The auto-covariate
epoch ships design-to-console in three rounds; NOTHING remains on the
deliberately-deferred analytics list — write-side org delegation stays a
product-scope decision, not an analytics gap.

Round 202 — §4.6b steps 1-2 land: auto_select_covariates (pooled r from
stored sums alone, |r| >= 0.1, strongest-first with a deterministic key
tie-break, at most 3, degenerate/missing candidates never guessed at),
the "auto" literal through the spec validator (lone-literal only), the
snapshot fold resolving auto to every provider's canonical covariate
(AUTO_COVARIATE_DEFAULTS), the #63 schedule gate checking what auto
RESOLVES to, and the analysis wiring: per-metric selection, chosen keys
riding the cuped block (an auto-selected SINGLETON still takes the joint
estimator — the legacy single path reads columns auto never writes),
CUPED_AUTO_SELECTED / CUPED_AUTO_NONE warnings with the generic
UNAVAILABLE bark suppressed when auto-none already explains itself.
Hand-oracle pure tests + a DB wiring test on seeded aggregates.

Round 201 — the auto-covariate epoch opens (§4.6b, step 0): the last
deferred analytics item in its honest minimal form — "auto" folds every
provider's default covariate into snapshots, analysis selects by pooled
|r| >= 0.1 from the stored sums (deterministic, at most 3), warns
CUPED_AUTO_SELECTED / CUPED_AUTO_NONE so selection is never silent.

Round 200 — residue hygiene for the observational lane: the round-199
section seeded its own tenant/org/project/users/submissions and layer,
none of which the crash-safe cleanup swept (the round-155 residue law) —
now all e2e-obs-% debris is deleted in the finally-wrapper, verified
zero after a full wall run (which also swept round 199's own leftovers).

Round 199 — the observational lane over the wire: the live wall grows
110 -> 122 — a learning-domain observational experiment created,
checklisted (ethics_screened included — the first failing run proved the
ethics gate bites over HTTP too), run to running, its roster and daily
series seeded, and the analysis asserted end to end: causal_claim false,
the ITS block with its caveat, the synthetic-control block with two
donors (placebo honestly None below three), and no km without the knob.

Round 198 — §16 gains item 13 (the causal-inference epochs, defects
#70-#72, waves 36-39, the ~1s observational wall-clock readout measured
on the SC fixture) and the PR body syncs through wave 39.

Round 197 — wave 39 over the SC epoch, and defect #72 IN THE LOOP
ITSELF: a docs commit ran `git add -A` while wave 39 was mid-flight and
shipped a LIVE MUTANT (the simplex boundary flipped to >=) plus the
harness reformat inside d9bd2d26 — caught by the harness's own
dirty-target refusal on the re-run, diagnosed by per-function AST diff
against HEAD, and reverted by restoring the round-195 source verbatim
(AST-verified equal to the harness-restored file). New iron law: NEVER
`git add -A` while a mutation wave is running. Wave 39 first pass: core
26/35, run() re-wave 102/116; killers landed (direct Duchi-projection
hand oracles, the placebo p == 1.0 exact pin on a perfect fit, the
two-donor boundary on the rate branch pinned bit-for-bit, the
constant-matrix refusal asserted block-absent); confirm pass: core
31/35 and run() 106/116 — every remaining survivor a reasoned ledger
entry. The SC epoch is mutation-certified end to end.

Round 196 — SC step 3: the console strip (purple, next to the ITS amber
and KM indigo strips): gap, donor count, RMSPE ratio, placebo p (or
"n/a" when the pool is under three), caveat verbatim. The SC epoch ships
design-to-console in four rounds; deferred shrinks to ML-learned
covariates and write-side org delegation.

Round 195 — SC step 2: observational runs with a donor pool attach
`synthetic_control` on the first primary — donor units = control arm
(sorted, capped SC_MAX_DONORS=20), treated series = other-arm daily
mean, one source call per day via the per-unit variant_units fan-out
(2 x ITS_DAYS calls total, the designed cost envelope). Lone-arm rosters
warn SC_DONOR_POOL_SMALL instead of attaching. The wiring test pins the
attached block BIT-FOR-BIT against the pure core on the
fixture-determined series (the round-185 oracle technique), with the
matched donor absorbing the weight and the gap reading 9/14 - 1 exactly.

Round 194 — SC step 1: the pure core lands — Duchi simplex projection,
projected gradient with the exact Lipschitz step (uniform start, 1000
iterations, zero randomness), post-period gap, post/pre RMSPE honesty
ratio, placebo permutation p (>= 3 donors). Hand oracle: a treated
series that IS 0.5*d0 + 0.5*d1 recovers those weights to 1e-6 with a
perfect pre-fit and gap exactly 1.0; refusal matrix (short pre, lone
donor, all-constant donors, ragged shapes, empty post); byte-identical
determinism pinned.

Round 193 — the synthetic-control epoch opens (§4.16, step 0): design
committed — simplex-constrained donor weights by deterministic projected
gradient, placebo permutation inference, the post/pre RMSPE ratio as the
honesty readout, per-unit daily series from ONE source call per day
(variant_units fan-out, the ITS cost envelope), donor cap 20.

Round 192 — the KM knob over the wire: the live E2E wall grows 106 ->
110 (knob PATCHes onto the talent time_to_event definition and
round-trips; billing time_to_event refused 422 (#70); continuous kind
refused 422; km=False strips). Full wall green against a live server.

Round 191 — segment-slice audit (suspected #71, acquitted): KM, ITS and
DiD all compute from whole-population reads, so a segment-sliced run
carrying them would caption population curves as segment results — but
segment runs return early (informational payload, no look recorded)
before any of the three blocks, so the defect is unreachable. Pinned
with segment-absence asserts on the KM and ITS fixtures so a refactor
that moves the early return re-fails them; no production change.

Round 190 — housekeeping: KM_SOURCE_UNSUPPORTED gets its §18a runbook
row (the new-warning-ships-with-its-row law), and the PR body syncs
through the console-tail fix.

Round 189 — #70's console tail: the Explorer KM toggle (round 186) had
keyed on kind alone, offering retention_rate a checkbox whose save the
API now 422s. The toggle and the PATCH payload both require kind ==
time_to_event AND source == talent_outcomes — the console never offers
what the API refuses.

Round 188 — defect #70: the KM event reader is placement-based, but the
km knob accepted ANY time_to_event definition — enabling it on
retention_rate (billing-sourced) would have attached placement curves to
a billing metric. Fixed at both layers: the analysis gate now requires
source == talent_outcomes (refusing arms with a KM_SOURCE_UNSUPPORTED
warning rather than attaching wrong-source curves), and the PATCH
refuses km=True off talent_outcomes with 422 while still allowing
km=False as the legacy-strip path. §4.15 notes the per-source reader as
the extension point.

Round 187 — the km knob gets its missing service tests + wave 38 over
update_definition (11/11): the knob had shipped tested only via raw spec
writes; the wave then exposed that clear_quantiles could strip the WHOLE
spec unnoticed (a sourceless definition emits no histogram, so the
absence assertion passed vacuously) — now pinned to remove only the
quantiles key. Kind gate asserted in both directions (km=True and
km=False both 422 off time_to_event).

Round 186 — the KM knob reaches the console: the Metric Explorer's
inline editor shows a KM checkbox on time_to_event rows only
(initialized from spec.km, carried on the PATCH; other kinds never send
the field — the kind gate is the API's to enforce and the console's to
respect), and the spec column badges opted-in definitions with "· KM".

Round 185 — wave 37 closure: the ITS service block lands at 88/98 via
exact oracle-via-pure-core pins (the fixture fully determines the daily
series, so the attached block must equal its_estimate() on that series),
a second primary pinning first-primary-only, a rate-kind observational
run covering the numerator/denominator daily branch, and a randomized
run that now carries a sourced primary + roster + started_at so the
observational gate's conjunction is load-bearing. One new ledgered
equivalent (the its-attach And — both operands tautological at the call
site); the KM/ITS epochs are now mutation-certified end to end.

Round 184 — mutation wave 37 over the KM epoch: the pure core lands at
21/23 (two ledgered equivalents: the zero-censor filter and the
greenwood-zero SE gate) after exact boundary pins — n0 == 2 admissible,
total-death days, refusal past an empty risk set, the combined Greenwood
SE pinned to 0.2 exactly. The service re-wave (98 mutants over run())
kills all four KM-wiring survivors by reshaping the DB fixture: a day-0
event exactly at assigned_at, an early censor BEFORE the control event
day, arms with different survival, and a cancelled-only-event arm
pinning block-off over half-attached None. 79/98 — the remainder is the
eight wave-34 ledgered equivalents plus the ten ITS-service-block
mutants, queued as round 185.

Round 183 — the KM strip on the analysis console (the ITS pattern):
an indigo strip under the metric card shows survival per arm, the
horizon diff with p/CI, and the censoring-correct caveat verbatim.
Typed into AnalysisResult.metrics; renders only when the block is
present, so non-opted metrics are untouched.

Round 182 — KM step 2 of 2: a time_to_event primary whose definition
opts in (the km knob, time_to_event-kind-gated on the PATCH) carries a
censoring-correct `km` block — counts computed ON DEMAND per arm (each
unit's event day from its own assigned_at; horizon via the DB clock, the
#68 law), product-limit curves compared at the horizon, the
binary-at-horizon engine read staying authoritative alongside; knob off
means no block. The deferred list shrinks to synthetic control,
ML covariates and write-side org delegation.

Round 181 — the KM epoch opens (§4.15, step 1): the product-limit pure
core lands — km_curve over day-granular event/censor counts (risk set
shrunk by both, Greenwood SE, textbook hand-computed oracle incl. the
censoring-correctness contrast against binary-at-horizon) and km_compare
(horizon survival difference, normal CI, censoring-correct caveat with
the engine read staying authoritative). Step 2 (source counts + exp15 +
analysis block) follows.

Round 180 — the ITS block renders on the analysis page (amber
informational strip: level/trend changes with p-values, days per side,
the association-only caveat verbatim); behavior-pinned.

Round 179 — mutation wave 36 over its_estimate: 13/16 — the n==3 floor
pinned from both sides and the dof EXPOSED as an honest readout (its
arithmetic was unkillable while internal); three equivalents ledgered
(the trend dummy agrees at t == t0, the dof guard is unreachable under
the floors, float residuals never hit exact zero).

Round 178 — ITS step 2 of 2, service wiring: an observational run with a
started_at gets an `its` block on its first primary — the whole ITT
roster read as ITS_DAYS=14 on-demand daily source windows per side,
silent days as ITT zeros, segmented OLS in the pure core,
association-only caveat; randomized runs never carry the block. The last
deliberately-deferred quasi-design is shipped.

Round 177 — the ITS epoch opens (§10 v3, step 1 of 2): the last
deliberately-deferred quasi-experiment design becomes buildable — "no
pre-period exists" only meant no pre-period SNAPSHOTS; the sources accept
arbitrary windows, so daily pre/post means can be computed on demand. The
pure core lands first: `its_estimate` — segmented OLS
(y = b0 + b1·t + b2·post + b3·(t−t0)·post) over daily means via the
existing k-generic Gaussian solver, classical OLS standard errors from
k diagonal solves, level/trend changes with t-tests, refusals under 3
points per side, and the association-only caveat. Oracle: exact recovery
on piecewise-linear data; significance on a deterministic jump; flat
series stays null. Step 2 (service wiring: on-demand daily source reads
for observational runs) follows.

Round 174 — the first BROWSER-level experiments spec
(e2e/experiments-wall.spec.ts, Playwright): a plain user sees no
Experiments sidebar entry and a deep link to the console renders the
error state without crashing the layout — the #59 wall checked in a real
Chromium. (Platform-admin browser flows stay with the live-API E2E, which
can SQL-promote; the browser suite deliberately tests the unprivileged
side.) 2/2 green against live servers.

Round 172 — fuzz extension over the quantile surfaces: histogram_quantile
is total over arbitrary string->int mappings (rotted JSONB included —
None or a finite ordered read), and the quantiles-knob validator is total
over arbitrary garbage (accept or the typed 422, nothing else).

Round 171 — hot-path baseline refresh after the window's feature work
(the #63 schedule gate, the list exposure injection, binary CUPED):
new-assignment resolve 2.56 ms/call and sticky resolve 0.89 ms/call —
both IMPROVED on the round-91 baselines (3.38/1.11); the new gates live
on schedule-time and list-time paths, not the resolve hot path.

Round 170 — mutation wave 35 over the six domain hooks: 13/13 outright.
Every module in the experiments package now carries a dedicated
post-rewrite mutation wave (waves 1-35, ~1100 mutants cumulative).

Round 169 — mutation wave 34, the largest single wave (88 mutants over
AnalysisService.run itself): 79/88 across five strengthening passes — the
error-status AST contract now covers this file, the cross-window
covariates fold and corpus shrink formula are exactly pinned, power and
data-flow boundaries sit exactly ON their edges, and degenerate entries
(one-armed, zero-variance, zero-denominator, insufficient-under-a-prior)
are all guarded-not-crashed. Two in-build discoveries: the corpus prior's
sd is FLOORED above zero (identical-effect corpora still shrink — now
pinned), and two guard pairs are deliberately redundant (the later guard
catches the same state; ledgered as such). 9 equivalents ledgered.

Round 168 — #69 visibility: the Metric Explorer's spec column shows the
guardrail aggregate ("guards sum") so an operator can SEE which semantics
a ceiling enforces. A wire-level seed assertion was deliberately NOT added
to the E2E: the shared test DB's pre-#69 rows persist by design (ON
CONFLICT DO NOTHING), and the honest pin is the seed template one.

Round 167 — the #69 family audit over every seeded definition: ONE
sibling (internal_cost_usd — same total-cost semantics) gained the sum
aggregate; the remaining continuous metrics (latency, ARPU, margin,
revisions, durations) are legitimately per-event/per-unit means. The seed
TEMPLATE is pinned (the shared test DB may hold pre-#69 rows, so the pin
reads the template, not the row).

Round 166 — defect #69 (found chasing a wave-33 survivor): the cost
CEILING guardrail silently evaluated the MEAN cost per task — _observed's
sum branch was unreachable (no seed set guardrail_aggregate and
definition.spec is immutable), so "Cost ceiling (USD)" with threshold 100
paused only when the AVERAGE task cost passed 100. The cost_usd seed now
sets guardrail_aggregate: "sum" (seeds are ON CONFLICT DO NOTHING —
pre-existing deployments keep the old row until re-seeded; operators of
old environments should verify the spec). Pinned by a fixture where the
window TOTAL breaches while the mean sits far under. Wave 33 closed 19/19
(fold antisymmetry, exact-threshold safety under both ops, the 404 pin);
the surviving Add->Sub mutant was the TELL: a negated fold is invisible
to rate/mean reads (signs cancel) and only a SUM guardrail could see it —
no sum guardrail test existed because the sum semantics itself was
unreachable.

Round 165 — mutation wave 32 over the decision registry: 30/31 — the
repeated-identical-look legality is now pinned (the hash probe stays a
limit-1 EXISTS) and the guardrail outcome is scoped to exactly the
experiment's own events; the search default-limit constant ledgered.

Round 164 — mutation wave 31 over the schedule gate: 19/19 after a full
exemption/risk matrix (medium+exempt still refuses; high-risk 403s
non-admins and schedules under an admin — the success arm was untested).

Round 163 — mutation wave 30 over layer allocation: 14/14 killed by the
existing suite outright. The service-core mutation sweep (waves 26-30:
compute, promotion, holdouts, exposure, layers) is complete — every core
now has a dedicated post-rewrite wave on record.

Round 162 — mutation wave 29 over the exposure path: 4/5 after pinning
the stored exposure context verbatim; the unreachable lost-write defense
ledgered.

Round 161 — mutation wave 28 over the holdout lifecycle: 12/12 after
pinning the race branch's 409 (two raise sites need two status pins).

Round 160 — mutation wave 27 over the promotion lifecycle (apply, async
apply, approve/reject): 16/16 killed by the existing suite outright.

Round 159 — mutation wave 26 over the compute loop and snapshot writer:
15/16 — the switchback first-version salt query is now pinned by a
two-version fixture (the day variant keeps the v1 salt bound under both
limit and ordering mutants); the top-20 segment cap ledgered.

Round 158 — §4.6 v3 scope note (a phantom gap closed by analysis, not
code): the cost_ledger and workflow_runs sources keep their
single-covariate in-source mode ONLY, deliberately. Multi-covariate
assembly needs >= 2 non-collinear covariates on the experiment's unit
type; org/tenant units have exactly one metric family (cost — any second
cost key is collinear by construction, and the joint solver rightly
refuses singular designs), and installation units likewise have only the
run-latency family. User units are where multiple independent sources
exist (projects, evaluations), and that is where the provider registry
operates. A future org-unit source family would unlock org-level multi by
adding a provider, not by changing the math.

Round 157 — the wave-24 design note repaid: the multi-covariate per-unit
y path now winsorizes exactly like the single-covariate branch (the
robustness knob cannot depend on how many covariates ride along); the
clamped values flow into the per-unit map the assembler pairs with
covariates, and the _winsorized provenance flag rides. Pinned with an
outlier fixture against the winsorize helper itself. The §4.6 v3 design
note is resolved.

Round 156 — E2E corpse root-cause fixed: the lifecycle script's cleanup
ran AFTER the main body, so any mid-flight crash skipped it entirely —
that is where the round-155 19-corpse residue came from. Cleanup now runs
in a finally over module-level state (ids registered as they are created),
reporting but never masking the run's own error. E2E 106 green under the
new wrapper.

Round 155 — concurrency: two racing PROMOTE decisions leave exactly one
terminal record, one typed DECISION_STATE_INVALID loser and one promoted
status (the terminal unique constraint's 409 mapping, now race-pinned like
apply). The racing test COMMITS, which surfaced the residue class again:
interrupted E2E runs had left 19 experiment corpses in the shared test DB,
and three tests asserting GLOBAL counts (window-sweep zero, digest counts)
broke. Mass cleanup was refused by policy — the CORRECT fix anyway:
those assertions are now residue-robust (differential sweep counts,
owner-scoped digest reads), and the racing test sweeps its own debris in a
finally (committed-session law).

Round 154c — the #68 clock audit swept every remaining app-clock use in
the package: the SRM/interaction/significance dedup windows (hour-coarse —
skew-insensitive), the day-level sweep windows, switchback's bucketing
instant (inherent boundary under any clock), started_at/ends_at record
values and start_at comparisons (user input, not DB-written timestamps).
Conclusion: the holdout report was the ONLY window comparison mixing the
app clock with DB-written row timestamps. Audit rule: any window whose
UPPER bound gates rows written with server_default now() must read the DB
clock.

Round 154b — defect #68 (the clock-skew class strikes the holdout
report): the report's window upper bound used the APP clock while rows
timestamp with the DB's server_default now() — with the DB clock 119ms
ahead (measured; Docker VM drift makes it arbitrary), freshly written rows
fell silently outside the window. This is the SAME lesson the guardrail
evaluator recorded; the report now reads clock_timestamp() from the DB.
Correction to the round-133b triage: that "environment flake" was THIS
defect's early signal — the parallel-uvicorn attribution was wrong; a
boundary failure that recurs deserves a clock audit before an environment
write-off.

Round 154 — calibration part 4: the quantile order-statistic CI's
COVERAGE pinned on skewed lognormal data (300 deterministic reps, p95) —
the bucket-resolution bracket must cover the true quantile at or above the
nominal 95% (coarsening only widens, so coverage can only rise). All four
statistical read surfaces now carry a calibration pin.

Round 153 — the always-valid promise ITSELF pinned: 300 null runs peeked
after every batch (12 looks each) — the mSPRT rejection rate across the
whole monitored run stays within the alpha band while the naive
fixed-horizon peeker inflates several fold alongside (the contrast keeps
the bound non-vacuous). Rounds 151-153 together: null calibration, power
calibration, and sequential validity — the three statistical promises the
platform makes, each now Monte-Carlo-pinned deterministically in the main
suite.

Round 152 — POWER calibration closes the design loop: simulating binary
A/B at EXACTLY required_n_per_arm(10%, 20%) == 3841 must detect at the
promised 0.8 power (Monte-Carlo band) — a drift in either the planner or
the runtime test breaks the pair. Together with round 151's null
calibration, the stats layer is now pinned on BOTH error axes.

Round 151 — A/A CALIBRATION Monte-Carlo (the verification stack's missing
axis: oracles pin point correctness, nothing pinned CALIBRATION): 400
deterministic-seed null replications — the Welch and binary p false-positive
counts must sit in a 3-sigma band around nominal 5%, the always-valid mSPRT
p must be strictly conservative at a single look, and CUPED under the null
with a REAL correlated covariate must not inflate alpha. Fast (<3s) and
deterministic, so it rides the main suite, not a slow lane.

Round 150 — mutation wave 25 over holdouts.report: 28/29 killed by the
EXISTING suite (the wave-12-era strengthenings held through two rewrites);
the 20k sample_capped informational flag ledgered.

Round 149 — integration snippet card on the detail page (SDK developer
experience): the experiment's own key pre-filled into the useExperiment
usage and the raw self-serve resolve/exposure calls — wiring a surface is
one copy-paste. Rounds 148/148b were doc-honesty: §4.13 now describes the
IMPLEMENTED health-signal channels (no dedicated table exists) and §17's
deferred list no longer claims multi-covariate CUPED is deferred.

Round 147 — mutation wave 24 over the project/evaluation sources after
the binary-CUPED branches: 42/43 (every branch's window edges proven by
exactly-on-timestamp rows; an antisymmetric review fixture kills inverted
join/status mutants; xy_sum pins the binary y through the covariate cross
term). Ledgered: the k > 1 gate's >= variant — at k == 1 both branches
produce identical sufficient stats; the single observable divergence is
that the MULTI per-unit y path does not winsorize (design note: §4.6 v3;
the single-covariate branch does — a future winsorize-enabled covariate
metric should unify this).

Round 146 — list-page data-flow badge: the experiments list injects
last_exposure_at (ONE grouped exposure query per page, never per-row) and
the console shows flowing / stale (>48h) / no exposures per running row —
the NO_RECENT_EXPOSURES signal surfaced where operators scan. The #49
model-response drift guard correctly caught the injected field and gained
its first deliberate allowlist entry (it keeps catching any other
non-column field). E2E 106.

Round 145 — the binary-CUPED caveat renders inline on the analysis page
(the honesty string was server-side only); behavior-pinned. The data-path
interaction audit for the new branch came back clean: guardrail and
holdout-report source calls pass no variance_reduction (per-review
semantics preserved), spec immutability prevents mixed per-unit/per-review
snapshot semantics, and unsupported binary sources degrade to the honest
CUPED_COVARIATES_UNAVAILABLE warning.

Round 144 — binary CUPED's second source: the evaluations source under
variance_reduction switches to the same per-unit 0/1 contract (a unit
passes when ANY of its in-window reviews is APPROVED; numerator counts
passing UNITS), feeding the covariate assembler cross-source.

Round 143 — mutation wave 23 (whole _compare after the binary-CUPED
branch): 30/31. The sweep exposed three blind spots OLDER than the new
code — effect values never exactly pinned, the rate-bayesian
p_beat/expected_loss formulas never value-pinned, and se == 0 reachable
(zero-variance arms are sufficient data) so the guards' else branches are
real; the k == 1 strict >1 gates are pinned with a covariates map present.
One mathematical equivalent ledgered.

Round 142 — BINARY CUPED (§4.6 v4, Statsig-parity regression adjustment
on proportions): a 0/1 per-unit outcome has sum == sum_sq == numerator, so
the existing Welch CUPED cores (single AND multi) apply verbatim. The
projects approval_rate source, under variance_reduction, switches to
per-UNIT 0/1 (unit-of-analysis change, the same documented contract as the
revision_count CUPED branch; numerator counts approved UNITS) and emits
_unit_values for the assembler — covariates come from the providers,
cross-source. The binary comparison carries the adjusted estimate as
cuped with an explicit caveat ("linear adjustment on a per-unit 0/1
outcome"); the unadjusted engine result stays authoritative. Bayesian
binary skips adjustment (posterior and linear adjustment don't compose —
documented).

Round 141 — the digest covers the decision queue: analyzed experiments
(waiting on a human decision) now appear as "AWAITING DECISION" lines —
running-only was a blind spot exactly where staleness hurts most (an
analysis nobody acts on). Title says "active" instead of "running".

Round 140 — mutation wave 22 over the new readers (look_history,
list_assignments): 8/10 killed — the OF look-number payload mapping needed
an obrien_fleming run (msprt looks are None there, invisible to the
mutant); the two default-limit constants ledgered (the limit mechanism is
killed by explicit small limits).

Round 139 — digest opt-out parity: the weekly digest (round 135) shipped
suppressible on the backend (prefs key = the type name) but the
notifications settings page had no toggle — the operator could not opt
out from the UI. Added the "Experiment Weekly Digest" toggle, and the
notifications-preferences page gained its FIRST behavior test (the page
predates the every-page-tested campaign, which covered experiments pages
only). Law: a new notification type ships WITH its preference toggle.

Round 138 — look-history console card: the analysis page lists the look
sequence (time, look number when OF, automated badge, truncated result
hash) under the results; behavior-pinned.

Round 137 — look history: GET /analysis/history lists every recorded
look newest first (audit-trail reads only, latest_look's shape per entry,
same delegated scope as the scorecard; segment analyses stay out — they
record no look). E2E 105; the delegated-surface manifest moved with it.

Round 136 — mutation wave 21 over the digest sweep: 13/14 killed (both
7-day >= edges by exactly-on-boundary rows, the day constant by a
7.5-day-old event, EXACT per-line counts against inverted id filters, the
dedup window's own >= edge); the body's lines[:20] display cap ledgered
(a 21-running-experiment fixture for a truncation constant).

Round 135 — weekly owner digest (industry-standard lifecycle email): one
notification per owner summarizing their running experiments' 7-day
exposure volume and guardrail-event counts (experiment_digest type,
Tuesday 08:23 cron off the Monday pileup, 6-day query-side dedup so
restarts are idempotent, per-owner savepoint under the #42 law). Sits
beside the daily significance notification; notification preferences
already gate delivery.

Round 134 — console export buttons: the three CSV surfaces (snapshots,
guardrail events, assignments) were API-only; each page header now carries
a CsvExportButton (authenticated raw-text fetch via a new apiTextWithAuth
that mirrors apiWithAuth's Bearer + 401-refresh, blob download). The
button surfaces failure inline ("Export failed — retry") — the first
draft's unhandled rejection was invisible to the operator and leaked as a
test-level unhandled error, which is what caught it.

Round 133b — hygiene: the holdout report's function-local
`from datetime import ...` (the UnboundLocalError-shadowing law's latent
form) hoisted to module level — removing it exposed that the top import
lacked timedelta, i.e. the local import was MASKING an incomplete module
import. One full-suite flake of test_holdout_report_comparison_edges
(isolated/file-level 5x green, full-suite rerun green) matches the
known parallel-DB-use environment class: a just-killed E2E uvicorn's
connections raced the suite start — wait for server death before starting
the suite.

Round 133 — the export trio completes: raw assignment rows export as CSV
(GET /assignments/export — the audit/compliance read next to snapshots and
guardrail events), stable (assigned_at, id) order so a capped export is a
deterministic prefix, same delegated read scope and uniform 404; E2E 104.
In-build lesson: an E2E insertion anchored on a check() must verify WHOSE
response variable that check reads — landing between an assignment and its
check silently retargets the assertion (caught because the 404 check went
green-to-red, not silently green).

Round 132b — defect #67 (the #66 family applied everywhere): the start
and closure sweeps' docstrings promised "the human simply wins" a racing
manual transition — but when the human won, transition() raised and the
sweep aborted the whole batch. Both sites now skip the racer (logged) and
continue; kill-proven with a monkeypatched race on the start sweep. Audit
rule: every batch loop that writes through a law-enforcing service must
catch that service's refusal per item.

Round 132 — defect #66 (concurrency sweep over the new sweep): between
sweep_ramp_plans' read and its set_ramp write, a manual ramp or a pause
makes set_ramp refuse — the unfixed sweep let that AppError abort the
WHOLE batch, starving every later experiment's scheduled step
(kill-proven via a monkeypatched race). The sweep now skips the racing
experiment (logged) and continues; set_ramp's own law still guards the
write. Same family as the poison-entry guard — a per-item failure must
never become a batch failure.

Round 131 — ramp-plan verification closes: live E2E 103 checks (a
non-increasing plan refused over the wire, the platform wall, null
round-trip) and mutation wave 20 at 23/23 after strengthening (every
refusal's 422 pinned, the 20/21 boundary, ramp_bp 1 and 10000 admissible
on a draft, the audit payload's steps, a step exactly AT the sweep
instant).

Round 130 — ramp-plan console: the detail page lists the standing steps
and takes new ones (one line per step: ISO time + target percent; blank
clears), PATCHing the plural plan; both the parse and the clear are
behavior-pinned. The Experiment web type gained ramp_plan.

Round 129 — scheduled ramp plans (exp14): `ramp_plan` on the experiment —
up to 20 {at, ramp_bp} steps, strictly increasing targets (ITT: a plan
cannot encode a decrease), first live target must exceed the current ramp,
naive datetimes normalize to UTC. A worker sweep (minute 14/44) applies
the HIGHEST due target on running experiments through set_ramp itself (its
monotonicity law still guards every write), records the standard
ramp_changed audit event, skips poison entries, and is idempotent.
Platform-walled PATCH /ramp-plan (the delegated-surface manifest pin moved
with it, deliberately). Guardrail auto-pause naturally halts the plan —
the sweep only touches running experiments.

Round 128 — defect #65 + percentile guardrails: the window fold did
scalar + dict the moment a quantiles-enabled definition served as a
guardrail (the source now emits value_histogram) — a TypeError that killed
the ENTIRE guardrail sweep for that experiment; the repro crashed exactly
there pre-fix. Histograms now fold bucket-wise, and
`guardrail_aggregate: "p95"` guards the percentile itself through
histogram_quantile (no sketch in the window -> not evaluable, skip —
never crash). The p95 breach pins the exact bucket range and the
auto-pause. Law: every consumer of a source's output shape must be swept
when the shape grows a key — the analysis fold got the histogram handling
in round 124, the GUARDRAIL fold did not.

Round 127 — live E2E reaches 100 checks: the quantiles knob PATCHes and
round-trips over the wire, a binary definition refuses it through the HTTP
stack, exp13's value_histogram JSONB serializes back verbatim, and
clear_quantiles strips the knob (leaving the seeded definition clean for
the next run).

Round 126 — mutation wave 19 over the quantile cores: 45/49 killed, 4
ledgered (the rank walk's final return is unreachable — the clamp
guarantees rank <= total and the last bucket closes >= rank; the
zero-count bucket filter has no observable effect). The first run left 23
alive: structural tests don't kill arithmetic mutants — the kills needed
the CI formula spelled out by hand (np ± z·sqrt(np(1-p)) with the z
constant), the exact rank-boundary bucket edge, the zero-mass boundary,
both clamp ends and every validator edge (a set and a string included).

Round 125 — quantile console parity: the analysis comparison renders its
quantile lines (p50: control → treatment (diff), teal, per probability)
and the Metric Explorer's inline edit gains the quantiles knob (comma
list; blank sends clear_quantiles like its siblings), prefilled from the
definition's spec. Found in-build: the Edit button initialized the edit
state via an object literal that dropped the new key — undefined.trim()
threw INSIDE the mutation, so the PATCH never fired and only the
clear-flags test (which skips the fill) caught it. Law: a literal that
RESETS state must be updated with every state key its shape gained.

Round 124 — the QUANTILE epoch lands (§4.14, design-first): p50/p95
reads for continuous metrics, the industry question mean-based sufficient
stats cannot answer. Step 1: definitions take a `quantiles` knob (1-3
probabilities, continuous-kind only, PATCHable — it changes reporting, not
stored semantics). Step 2: snapshots gain value_histogram (exp13) — a
base-2 log sketch with **zero**/**neg** overflow keys, emitted by BOTH
per-event continuous sites (run latency, path time-to-completion) only
when the definition asks; counts fold across windows like the covariates
map. Step 3: pure `histogram_quantile` (cumulative walk, geometric
interpolation) with a distribution-free order-statistic CI, and
`quantile_comparison` whose combined CI subtracts opposite ends
(conservative by construction, caveat attached); the analysis comparison
carries `quantiles: {"0.5": {...}}` — informational, never a decision
basis. Oracle: estimates bracket the true sample quantile's bucket across
scales; exact pins on hand histograms; refusals (negatives, n<2, p
bounds) pinned.

Round 123 — the multi adjustment gains the single path's honesty readout:
variance_reduction_pct (achieved reduction vs the unadjusted Welch) now
rides the multi result too, pinned 1e-9 against the oracle's residuals and
exactly equal to the single path at k == 1; the analysis page's conditional
pct render (round 118) lights up for multi without changes. Also de-staled
the time_to_event caveat ("full KM in exp10" — exp10 shipped as scheduled
start; the caveat now points at the deferred list).

Round 122 — console parity #64: the builder exposed MDE, switchback and
segments but variance_reduction was unconfigurable — CUPED (single or
multi) existed only for operators hand-writing spec JSON. The builder now
takes covariate metrics (comma list, up to 3; 2+ run the joint adjustment)
plus a lookback-days input, emitting the plural covariate_metrics form; a
blank field omits the block entirely (both pinned). Live E2E grows to 96:
the #63 gate proven over the wire (typo'd key versions fine, scheduling
refuses, EXPERIMENT_UNKNOWN_METRICS names it).

Round 121 — defect #63 (write-boundary law applied to specs): a spec
referencing a metric key with NO definition — primary, secondary, guardrail
or covariate — scheduled fine and collected silent zeros forever; the typo
surfaced only as an analysis warning weeks later. The schedule gate
(_check_schedule_preconditions) now resolves every referenced key against
MetricDefinition and refuses with EXPERIMENT_UNKNOWN_METRICS naming the
unknowns. Blast radius handled honestly: the unwired-guardrail pin's
undefined-key arm became a sourceless-definition arm (that state can no
longer reach running via the lifecycle — which is the point), the #62
degrade test's ghost covariate became cost_usd (defined, no provider), and
the error-status contract pin gained the new code.

Round 120 — defect #62: a multi-covariate spec that degrades to the
single-covariate fallback (unprovided source, degenerate joint design) did
so SILENTLY — any_cuped was satisfied by the single shape, so no warning
fired while the operator believed a joint adjustment ran. Analysis now
appends CUPED_MULTI_DEGRADED (kill-proven; the honest multi e2e pins the
warning absent). Mutation wave 18 on the evaluations provider: 7/7 after
breaking the approved/non-approved fixture symmetry the first run exposed.

Round 119 — live E2E grows to 93 checks: a multi-covariate spec accepted
over the wire (spec_hash round-trip), the exactly-one-form validator's 422
proven through the HTTP stack, and the exp12 covariates JSONB (xx included)
read back verbatim through the response model — the #49/#51 serialization
class only a wire read can prove. No pytest-collected code changed this
round (certification 94 covers the tree).

Round 118 — defect #61 (web, found by parity-sweeping the new multi
shape): the analysis page typed cuped's variance_reduction_pct as required
and called .toFixed on it, so a §4.6 v3 multi result (which carries theta,
not a pct) crashed the whole comparisons table — kill-proven (TypeError:
Cannot read properties of undefined). The line now renders "CUPED ×k" for
multi mode and the pct only when present. Law: every NEW backend response
shape must be swept against the pages that render its parent object.

Round 117 — COVARIATE_PROVIDERS gains its second source, evaluations:
pre-period SubmissionReview verdicts per user unit (pass_count default —
APPROVED only; review_count counts every verdict), mirroring the source's
own semantics. The provider test pins both window edges by
exactly-on-timestamp reviews (the proven wave-17 pattern) plus the ITT
zero default. The registry is now demonstrably cross-source: any of the
two sources' metrics can serve as covariates in one joint adjustment.

Round 116c — defect #60 (test nondeterminism, caught by certification 92):
the multi-covariate e2e used real hash bucketing over 8 random-ULID users,
so ~7% of runs land an arm with n <= 1 and both adjustments correctly
refuse — a flake that an isolated rerun hides. Deterministic 4/4
ExperimentAssignment split; law: an e2e about DOWNSTREAM math must not
leave arm membership to the hash.

Round 116 — mutation wave 17 over the §4.6 v3 cores: 40/46 killed (both
window-boundary edges proven by exactly-on-timestamp rows; the xx
upper-triangle structure pinned against slice mutants; whole-covariate
refusal; the n==2 floor), 6 ledgered equivalents (the 1e-12 singularity
float threshold, the n<=1 trio welch already shields, two comparisons the
i==j branch makes unreachable).

Round 115 — multi-covariate CUPED, step 3 of 3 (the epoch closes): the
assembler now also stores the covariate CROSS-products (upper triangle,
keyed on the earlier covariate) — the joint OLS is unsolvable without
them; the pure core gained multi_cuped_adjusted_welch (pooled centered
normal equations, k<=3 Gaussian elimination, Z = Y - theta·(X - x̄),
Welch over Z) verified at 1e-9 against an EXPLICIT per-unit
residualization oracle with correlated covariates, exactly reducing to the
single-covariate implementation at k == 1, and refusing collinear designs
and missing cross terms; the aggregate folds the covariates map across
windows; comparisons carry cuped.mode == "multi" with the full theta map.
End-to-end pinned: a two-covariate spec flows snapshot -> aggregate ->
joint adjustment. The long-deferred item is DONE for every covariate whose
source has a provider (projects ships; the provider registry is the
extension point).

Round 114 — multi-covariate CUPED, step 2 of 3 (data): a covariate
PROVIDER registry computes per-unit pre-period values per source (projects
ships first, measure-aware: revisions vs approvals); in k>1 mode the main
source emits per-unit y only and the assembler builds the exp12 covariates
map for EVERY covariate — cross-source capable by construction, first
covariate mirrored into cov_*, per-unit maps never persisted, covariate
definitions fetched by key when absent from the spec's own metric set.
Pinned end-to-end with exact per-key sums and xy products on a
two-covariate spec. k == 1 keeps the legacy in-source path byte-identical.
Step 3 (analysis-side multivariate adjustment) next.

Round 113 — multi-covariate CUPED, step 1 of 3 (schema): the deferred item
leaves the deferred list under sustained demand. VarianceReductionSpec
gains covariate_metrics (1-3, deduped) with the singular form kept for
back-compat (exactly one form, validator-pinned; covariates() normalizes
both); exp12 adds a JSONB covariates map {key: {sum, sum_sq, xy_sum}} to
snapshots while the cov_* columns stay as the FIRST covariate's mirror so
every pre-exp12 reader keeps working; the three per-source CUPED gates now
test membership in covariates(). Round-trip verified; steps 2 (sources
compute the map) and 3 (analysis-side multivariate adjustment) follow.

Round 111 — the Promotions page polls every 5s while any draft is
'applying' (an async apply resolves out-of-band; the operator now sees it
land without refreshing) and rests otherwise — the interval logic is an
exported pure function, pinned. Web 702/702.

Round 110 — the scorecard's delegation wall verified over the wire: an org
admin reads their own experiment's latest look (null before any run) and
gets the uniform 404 on a platform experiment. E2E 90 checks.

Round 109 — PR #47 refreshed with the rounds 100-108 record (definition
PATCH + Explorer editing, fourteen-vocabulary parity wall, full console-
page test coverage, the API-side necropsy closure, E2E 88, wave 16).

Round 108 — worker necropsy tail: six arms in one batch (the breach-log
handler path, the deleted-approver parked arm, no-cross-layer-pairs zero,
the single-variant df<1 skip, the interaction notify except arm under an
exploding transport, and the dangling-version closure skip). facade.py
reads 100% across the complementary suites.

Round 107 — the dep layer's own arms pinned (check_enum 422, the 403 for
a plain user with no admin memberships, the delegated org-ids list, the
admin unrestricted scope, and the self-serve pass-through). deps.py fully
covered.

Round 106 — hooks necropsy tail: the three write-path control arms
(binding/rubric/retry with a config missing the surface's key — the control
variant's natural shape) pinned in one batch: default served AND a
control-arm exposure recorded. 91% -> 95%; the read-path twins share the
code shape and stay held by their kill-proven fallback pins (committed-
fixture cost not worth re-paying for an identical branch).

Round 105 — the metric enums joined the web parity wall: METRIC_DIRECTIONS
and METRIC_KINDS are now exported constants pinned against the backend sets
(the Explorer's direction dropdown had them hardcoded — correct today,
a drift point tomorrow; fourteen vocabularies now ride the parity test).

Round 104 — wave 16 over update_definition closed 4/4 (the surviving
status-code mutant died once the dynamic assert joined the static AST map),
and the live E2E grew the definition-PATCH pair (edit the cap, clear the
cap): 88 checks.

Round 103 — the Decision registry list and detail pages gained their
missing behavior tests (the FOURTH and FIFTH uncovered console pages):
record listing with verdicts, and the detail's summary plus the full
64-char result hash a promotion must reference. Every console page now has
behavior tests. Web 701/701 across 144 files.

Round 102 — the Metric Explorer gained inline editing of the operational
knobs (winsorize/cap/direction through the round-101 PATCH; blank fields
send the explicit clear flags — pinned both ways). The Explorer also gained
its missing behavior tests — the THIRD uncovered console page the campaign
has found. Web 699/699 across 143 files.

Round 101 — metric definitions gained an operational-knobs PATCH (title,
privacy class, direction, winsorize/cap with explicit clear flags);
kind/source/query_version stay IMMUTABLE — they are analysis semantics
baked into every stored snapshot, and changing them would silently re-mean
history (the schema does not even accept them, pinned). metrics.py manifest
(2,4).

Round 100 — the hundredth adversarial round. Standing totals: 59 numbered
defects/gaps found and fixed (every fix kill-proven or branch-verified),
11 migrations, 512 exp tests, 697 web tests, an 86-check live E2E journey,
15 mutation waves (every survivor killed or ledgered as an analyzed
equivalent), 79 full-suite certifications all green, and a PR description
that tells the whole story. The loop keeps running.

Round 99 — verification battery #2 after the feature run (clone, search,
exports, probe, scorecard, sparkline): live E2E 86/86, hot path 3.38 ms
new / 1.11 ms sticky (within noise of the 3.2/1.0 baseline across 9 new
endpoints), fuzz + pure cores 78/78.

Round 98 — the holdout report's metric input gained datalist suggestions
limited to the reportable-source set (mirroring the service's
REPORT_SOURCES), so operators pick a valid metric instead of guessing at a 422. Web 697/697.

Round 97 — the layer A/A hash-health probe reaches the console: a per-layer
Probe action on the Layers page renders chi-squared, p and the
healthy/SUSPECT verdict inline (the API's own healthy flag at the 0.001
threshold). The Layers page also gained its missing behavior tests (the
second uncovered console page the campaign found). Web 697/697.

Round 96 — guardrail/incident history CSV export (the metrics export's
sibling): GET /{id}/guardrails/events/export under the same delegated read
scope and uniform 404; system-set key columns only, the free-form detail
JSON stays out of the flat file. E2E 86 checks (delegated export verified).

Round 95 — mutation wave 15 over clone/search/scorecard: 12/13 killed
(the second-look test kills the widened-limit mutant via
scalar_one_or_none; the one survivor is the list's default-arg 50, the
ledgered equivalence class).

Round 94 — clone and search verified over the wire (85 E2E checks): the
clone lands as a draft with the source key's copy, text search finds it, a
bare % is a literal, and clone is platform-walled. The new checks also
flushed a cleanup latent: layers can only drop once nothing hangs on them —
a crashed earlier run leaves orphan experiments on historical org layers,
so the E2E cleanup now deletes riders first (and thereby swept the existing
orphans).

Round 93 — console text search: list_experiments gained q (key OR title,
case-insensitive, ILIKE wildcards in user input ESCAPED so a literal
percent matches a percent — pinned: a bare %tag% matches nothing), the
endpoint takes ?q= (capped 120), and the console grew a search box sharing
the URL-state machinery with the status/domain filters (Enter or blur
applies; the q rides the shareable URL). Web 695/695.

Round 92 — experiment CLONE (industry parity: duplicate): POST
/experiments/{id}/clone creates a NEW draft carrying the source's current
spec as its v1 (identical canonical hash, pinned), same
domain/layer/scope/risk/holdout knobs, NO layer allocation (slices are a
scarce mutually-exclusive resource — claiming them stays a deliberate act),
audit-linked via a cloned_from event. Version-less sources refuse typed;
key collisions are the usual 409. Console: a Clone button on the detail
page (platform admin) prompting for the new key and navigating to the copy.
experiments.py manifest (6,3).

Round 91 — PR #47's description refreshed with the rounds 59-90 record
(client-surface defect chain #54/#57/#58, exp10/exp11, automated
monitoring, console parity set, the necropsy campaign, the bounded-batch
class). Totals: migrations exp01-exp11, exp suites 510, web 693, live E2E
81, 74 certifications latest 6890 all-green.

Round 90 — live E2E grew the scorecard check (the latest-look endpoint
mirrors the run's result hash, automated=false for a human run): 81 checks.

Round 89 — metric trend sparklines (industry parity: results pages chart
movement over time): the snapshot page renders a per-variant inline-SVG
trend above each metric's table — rate (numerator/denominator) or mean
(sum/n) per daily window, whole-population rows only (segment slices
excluded from the trend), skipped below two usable points. Zero
dependencies, zero API changes; the page also gained its missing behavior
tests. Web 693/693.

Round 88 — the residue crossed 500 and took out the OTHER three
bounded-batch credits tests the #86 audit had reasoned were fine (they
construct their own stale rows, which now sort behind 501 residue rows and
miss the batch entirely). One-time cleanup released the 501 debris rows,
and all three tests gained the §106.25 guard — including the committed-
session variant, where the push-out persists and doubles as cleanup. The
#86 audit's miss is itself the lesson: reasoning "the test's rows sort
first" only holds for ORDERINGS the test controls; stale-window membership
is global state, and every bounded-batch test needs the guard regardless.

Round 87 — the standing scorecard (industry parity: results persist on the
experiment page, not just in the last response): GET
/experiments/{id}/analysis/latest reads the newest analysis_look from the
audit trail (same delegated read scope, uniform 404; null before any run)
and the detail page renders it — at/sequential/look, per-metric primary
effects with se, the result hash a decision would reference, and an
`automated` badge when the daily sweep produced it. Component hardened
against junk shapes (the #54 lesson applied at the card level — a crashing
card blanked the whole page in tests). analysis.py manifest (3,0).

Round 86 — the #85 class swept across every bounded-batch sweep test:
closures and starts are ordering-safe by construction (the test's rows sort
first — 29-day-old started_at, explicit past start_at); the guardrail
fairness test already carries the §106.25 stamp-residue-checked guard; the
windows cap test pushes residue out via analysis_close_at; the analysis
sweep tests pause residue running experiments. No unguarded bounded-batch
test remains — the credits ladder was the last one standing.

Round 85 — a certification red outside the exp package, diagnosed to the
row: the credits expiry-ladder test raced the sweep's bounded oldest-first
batch (limit 500) against shared-DB residue — at EXACTLY 499 stale held
rows the test's review hold squeaked in as #500 and its running hold was
cut at #501, so the 6h extension never ran. Fixed with the §106.25 pattern
(push residue out of the stale window in-txn; the rollback fixture restores
it), verified 3x green plus the full credits suite. The residue itself is a
by-product of weeks of committed-fixture and live-E2E traffic on the shared
dev DB — the fix makes the test immune to any future accumulation level.

Round 84 — analysis-service spec arms pinned (dangling current_version
and corrupted stored spec are both typed 422s, never raw 500s). Necropsy
triage for the remainder: the corpus-prior and novelty statistical
sub-branches (per-metric event mining, <30-denominator refusals, the
continuous welch arm of the early/late split) are exercised partially by
the dedicated novelty/corpus tests and the pure-core fuzz; forcing the
rest needs multi-experiment effect-history fixtures with marginal value —
ledgered. The service-layer necropsy campaign (rounds 74-84) closes with:
holdouts 99%, decisions/promotion 98%, analysis core 97%, metrics 96%,
assignment/guardrails/worker/experiments 91-95%, every remaining line
individually accounted for as defense-in-depth, race fallback, or
statistical sub-branch.

Round 83 — experiments-service necropsy: the search body (status/domain
filters, delegation scope list, keyset cursor), list_events, uniform 404s,
create validations (unknown domain/risk, missing layer, layer-domain
mismatch), wrong-status guards (create_version after draft/review, ramp in
terminal), schedule-without-version and incomplete-checklist arms — all
triggered dynamically in one batch.

Round 82 — promotion necropsy: the state-guard arms (draft 404,
approve-after-reject, double-reject, apply-from-rejected) triggered
dynamically — 94% -> 98%. The three remaining lines are defense-in-depth
behind earlier gates (the randomized-only check the decision service
already enforces; the already-applied/in-flight 409s the async-apply tests
exercise through their own flow) — ledgered.

Round 81 — decisions necropsy: six cold arms triggered dynamically in one
batch (unknown decision 422, poison stored spec 422, duplicate decision
typed, get 404, search filters, keyset cursor) — 90% -> 98%. The remaining
pair is the IntegrityError mapping behind the state machine: reaching it
needs a concurrent decision racing past the status check, the same
belt-and-braces shape as the holdout 409 — ledgered as the race fallback
the locked transition normally makes unreachable.

Round 80 — necropsy tail on metrics: the cap_value clamp on latency
durations (100/300/10000 capped at 500 -> sum 900), the learning_paths
scope-org JOIN arm (ITT shape preserved: the unit counts with zero scoped
items), and billing's pre-window-churn skip (a tenant cancelled before the
window is never at risk — added as a fourth tenant to the existing billing
matrix, retention unchanged at 1/2 proving the exclusion).

Round 79 — metrics necropsy continues: the cost_ledger CUPED TENANT arm
(org costs rolled up to tenant inside the covariate lookback) and the
snapshot pipeline's poison-spec arm pinned; 95% -> 96%. Triage insight for
the remaining poison arms (variance-reduction / exposed-only / segment
reads at 1173-1248): they parse the SAME stored spec the key-parse arm
already guards, and the key parse short-circuits first — unreachable
duplicates of one defense, ledgered rather than forced.

Round 78 — necropsy sweep over all twelve registered sources in one
parameterized test: every gated source degrades to {n:0} on a unit_type it
does not serve, and every source (exposures aside — it needs a real
experiment and is exercised everywhere) degrades on an empty unit list.
metrics.py coverage 90% -> 95%; the sweep also DOCUMENTED the gate
topology: workflow_runs and cost_ledger carry no type gate by design, and
the sweep pins which sources are gated (a silently dropped gate now fails).

Round 77 — necropsy catches a SECOND right-for-the-wrong-reason test: the
"unwired guardrail source" pin used cost_usd, whose source was wired in
exp07 — the test has been green via normal evaluation ever since, with both
defensive arms (undefined metric, unregistered source) dead. Rewritten
honestly: a guardrail naming a definition-less metric plus a custom
definition whose source isn't in the registry — both arms now
branch-verified. The alert-notify except arm (transport down: finding
survives, no pause) pinned too.

Round 76 — cold-branch necropsy on assignment.py: five honestly-reachable
branches pinned in one batch (org-scope mismatch reason, missing-allocation
reason, unknown-key exposure False, holdout tally in assignment_stats, and
a non-serving switchback status). Two remain as ledgered defense: the
assignment-write-lost 500 (requires the ON CONFLICT insert and the
re-select to BOTH miss — a torn-write race the lock architecture excludes)
and the switchback non-serving elif that _load_or_none's status filter
already short-circuits. The exp suite crossed 500 tests.

Round 75 — necropsy continues on the analysis sweep's defensive arms: a
stored unparseable spec and a crashing analysis (a real statement error on
the shared session) each skip their experiment while the batch continues —
the healthy experiment behind them is still analyzed, the crash stays
inside its savepoint, and both arms are now branch-verified covered.

Round 74 — the coverage audit pays off twice. (1) A right-for-the-wrong-
reason test: the legacy washout-swallow pin passed because its mutated
stored spec now FAILS PARSE post-#44 (poison-spec skip arm, never the
swallow branch) — the branch's honest reachable case is a VALID week-window
spec (10080) with a 1440-minute washout computed over a day window, and the
test now constructs exactly that (branch verified covered). (2) The
facade's record_exposure except arm had never run — now pinned: a raising
service yields False with the session healthy. Coverage-guided review found
what green suites could not: a test can pass while its target branch died.

Round 73 — coverage audit over the whole package (pytest-cov across the 14
unit suites): services at 90-99% (holdouts 99, analysis core 97, promotion
94, assignment/guardrails/metrics/experiments/worker 90-92) with the
uncovered service lines enumerated and accounted for — typed-error raises
already pinned by the AST status-contract tests, CUPED per-source
sub-branches, and poison-spec skip arms. API routers read 50-65% in this
run BY DESIGN: unit suites call services directly, and the thin router
bodies are exercised by the 80-check live E2E plus the manifest/scope pins
(the uncovered router lines are exactly the pass-through bodies). No
untested logic was found hiding behind the numbers; layers.py's 80% is the
validation branches the spec-validation suite drives via service calls.

Round 72 — experiment notifications are user-manageable: the notification
preferences panel gained toggles for experiment_guardrail and
experiment_significance (absent = enabled, the existing default — the
service's prefs check already honors an explicit opt-out). Web 690/690.

Round 71 — mutation wave 14 over the analysis sweep: 14/16 killed, 2
float-exact boundary equivalents ledgered. The instructive survivor: an
Or->And mutant crashed inside the notification SHIELD and the shield
swallowed the crash — a fail-safe wrapper hides mutants just like it hides
bugs, so the significance unpack moved outside it (only the genuinely
additive write stays shielded).

Round 70 — the analyzed-status hint degrades for delegated operators
(decisions are platform calls; the hint now says to hand the analysis
result hash to a platform admin instead of pointing at a tab they cannot
see). Web 690/690.

Round 69 — automated monitoring (industry parity: scheduled analyses):
sweep_experiment_analyses runs a daily analysis over RUNNING mSPRT
experiments — the always-valid engine pays no peeking cost, so automation
is statistically free; O'Brien-Fleming experiments are EXCLUDED by spec
check (a robot must never spend a budgeted look — pinned: the OF
experiment's look count stays 0 through the sweep). On any primary
comparison crossing always_valid_p < 0.05 the owner is notified once per
day (query-side dedup on stored notifications); each experiment runs under
its own savepoint (#41 law) and the notification under another (#42 law).
The system actor's role=None means automated runs never attach the
platform-admin-only corpus prior. Cron: daily 07:13.

Round 68 — defect #59 (delegation had an API but no DOOR): the Experiments
nav link rendered only for platform roles, so org owners/admins — who hold
real delegated access to their own-org experiments (read, transition, ramp,
diagnostics, analysis, guardrail events, CSV export) — had no way into the
console the delegation was built for. The link now also shows for any
owner/admin org membership (shared my-orgs query), the platform-only tabs
(Decisions/Promotions/Layers/Holdouts/Metric Explorer) hide for delegated
operators instead of serving them 403s, and the New-experiment button gates
on platform admin. Pinned by a delegated-view test. Web 690/690.

Round 67 — post-exp10/exp11 verification battery: live E2E 80/80, hot
path re-benchmarked at 2.76 ms new / 0.88 ms sticky (the rescoped dedup
index sits on the write path and cost nothing — slightly faster than the
3.2/1.0 baseline), Hypothesis fuzz twice green. Segment write volume
ledgered while at it: worst case ≈ metrics x variants x (1 + 20 org
slices) x 3 backfill windows of idempotent upserts per experiment-day —
bounded by the top-20 org cap and the deliberate backfill constant; no
growth path exists without a spec change.

Round 66 — the #58 class closed by audit: all five ON CONFLICT sites in
the package were checked against the unique constraint they ride (seed
definitions on key; snapshot upsert on the window+segment constraint;
sticky assignments on the unit constraint twice; the exposure dedup on the
rescoped per-assignment index). A structural pin now asserts the three
load-bearing idempotency scopes by column list — a future scope widening
(the #58 shape) fails the build instead of silently swallowing rows.

Round 65 — the detail page shows a scheduled experiment's Auto-starts time
(or "manual start"). Web 689/689.

Round 64 — defect #58 (SEVERE: shared dedup keys swallowed other units'
exposures): the dedup unique index was (experiment_id, dedup_key) — but
idempotency is a PER-ASSIGNMENT contract. Any two units sharing a natural
key (the dashboard client's per-day key is the same string for every user)
collided, and the targetless ON CONFLICT DO NOTHING silently dropped every
unit after the first each day. The server-side hooks never tripped it only
because their keys happen to embed unit ids. exp11 rescopes the index to
(assignment_id, dedup_key) — strictly narrower, so existing rows always
satisfy it; kill-proven by downgrading the index under the two-units-one-key
test (old: 1 row; fixed: 2). Round 59's client wiring is what exposed the
latent class — the first real consumer is also the first real adversary.

Round 63 — defect #57 (exposure spam per render): useExperiment's
recordExposure depended on the whole useMutation RESULT object — a new
identity every render — so any effect depending on recordExposure re-fired
per render, POSTing one exposure per render (server-side dedup absorbed the
rows; the network amplification was real). It now depends on the
identity-stable `mutate`; pinned by a double-rerender test asserting exactly
one exposure call, kill-proven against the unfixed hook.

Round 62 — defect #56 (scheduling timezone ambiguity): a NAIVE start_at
was accepted and stored as interpreted by the DB session's TimeZone — the
same request could start an experiment hours apart across deployments (the
console always sends Z; direct API callers could not be sure). Naive now
means UTC, deterministically, normalized at the service boundary; pinned by
a naive-scheduled experiment that stores tz-aware and launches on the UTC
clock. (Shadowing lesson recurs: a function-local `from datetime import
UTC` makes UTC local to the WHOLE function — UnboundLocalError at earlier
uses.)

Round 61 — mutation wave 13 over the start sweep: 4/4 killed after
strengthening (a past `now` launches nothing — the passed clock is
authoritative; start_at == now is the exact <= edge; exact launch count
pinned). Live E2E 80 checks with the start_at echo.

Round 60 — scheduled auto-start (exp10, the gap #55 the status name
promised): 'scheduled' used to mean launch-checked-awaiting-a-human.
start_at is an optional column (NULL = the old manual behavior, unchanged);
the transition to scheduled accepts it, the new sweep_experiment_starts
(cron :09/:39, capped, oldest-due first) launches due experiments through
the SAME locked state machine as every other transition — a racing manual
start simply wins — and the launch is audited as a system transition with
the reason recorded. Console: an Auto-start datetime field beside the
launch checklist ("blank = start manually"). Migration round-trip verified;
pins: due starts launch + stamp started_at, future and NULL stay scheduled.

Rounds 58–59 — the runbook (§18a) and the FIRST REAL CLIENT SURFACE.
Round 59 wired useExperiment into a product page at last (the hook had zero
consumers — a client SDK nobody called): the dashboard To-do headline
(`dashboard-todo-nudge`, presentation-only, config.headline capped at 80
chars, default copy on any miss) with a day-deduped exposure fired only
when the section is actually on screen (assignment != exposure). Wiring it
found defect #54: the hook's optional chain stopped one level short —
`resolve.data?.data.variant_key` crashed the HOST page on a `data: null`
response, so the client-side fail-safe was incomplete; now null-safe
end-to-end and pinned over three malformed shapes. Failure-invisibility
test: a rejected resolve renders the default headline.

Round 57 — defect #52 (found by mutation-driven test strengthening): the
holdout report called analyze_binary with DICTS against its positional-float
signature — the comparison crashed on any populated report, and the
original structure-only test never reached that branch (a weak test is a
defect incubator). Wave 12 drove the strengthening: required_n_per_arm
pinned to its exact textbook value (3841 at 10%/20%/0.05/0.8) plus
open-interval boundary refusals; the report pinned on an org-scoped,
fully-controlled universe with bp chosen to sit exactly ON one member's
roll (the strict-< boundary mutant flips a unit and dies), exact per-arm
values from real submissions, window clamps, and typed statuses. Wave 12:
49 mutants, 2 ledgered equivalents, everything else killed.

Round 56 — defect #51 (regression caught by live E2E, introduced in round
48): serializing updated_at broke every return-the-row-after-commit
endpoint — onupdate marks the attribute expired after the UPDATE flush, and
FastAPI's response serialization then triggered a SYNC lazy refresh
(MissingGreenlet -> 500). Unit tests never serialize through FastAPI after
a commit, so only the live E2E saw it — the layered-verification argument
in one incident. Fix: eager_defaults on the Experiment mapper (the UPDATE's
own RETURNING carries the fresh value; nothing expires). The E2E also grew
the three holdout-report checks (79 total).

Round 55 — the holdout report reaches the console: a Report action per
group with a metric picker renders the held-out/general split, per-arm
rates (or n for continuous), the comparison p, and the observational caveat
verbatim. Web 684/684.

Round 54 — global holdout MEASUREMENT lands (§4.12 v2 — the reason the
groups exist, and until now entirely absent): GET
/experiments/holdout-groups/{id}/report?metric_key=&window_days= splits a
capped user universe (20k, org-scoped via OrgMember when the group is) by
the group's OWN membership roll, aggregates the metric per side through the
registered source functions (experiment=None — only learning_paths ever
read the experiment and it already guards), and compares with the same
engine as experiment analyses (two-proportion for binary/rate, Welch for
continuous). The report carries an explicit caveat: membership is
randomized but the "treatment" is every launch since the group started —
no single-feature causal claim. Sources allowed: the user-unit product set
only (projects, cost_ledger, evaluations, learning_paths, client_briefs,
registry); exposures/workflow metrics refuse typed. Platform-admin only;
holdouts manifest pin (0,4).

Round 53 — defect #50 (retention dead end): promoted/rejected were modeled
as fully terminal, but §13's prune runs on ARCHIVED experiments only — so a
promoted experiment's raw exposures could never be deleted and grew forever
(the accumulation-bomb shape wearing a lifecycle costume). The distinction
is decision-terminal vs storage-terminal: promoted/rejected now allow
exactly one exit, archived (the decision itself is immutable; archiving is
a storage action). Web transition table synced (the API↔web parity pin
caught the drift exactly as designed); pinned end-to-end by a
promoted→archived→pruned lifecycle test.

Round 52 — the data-flow signal reaches the console: the diagnostics page
renders "Last exposure: <local time | none recorded>" under the funnel
table (web 683/683). NO_RECENT_EXPOSURES already rendered verbatim through
the warnings list.

Round 51 — data-flow health: funnel diagnostics now carry
last_exposure_at (the console's "is data still flowing?" signal), and a
full analysis of a RUNNING experiment whose newest exposure is older than
48h — or that has none — warns NO_RECENT_EXPOSURES: that state is most
often a broken integration, not a finished experiment, and silence was the
only previous symptom.

Round 50 — builder gains the optional power target (MDE %, defaults alpha
.05 / power .8): filled, the spec carries power.mde and every analysis
reports required-vs-actual; blank, no power block is sent (both paths
pinned). PR #47's body refreshed with the rounds 26–49 record. Web 682/682.

Round 49 — console surfaces guardrail freshness: the detail page shows
last_guardrail_check_at, and a RUNNING experiment that has never been
checked renders an amber "never — sweep pending" flag — the operator-visible
end of the sweep pipeline (an experiment outside the sweep is exactly the
unguarded state §9 forbids). Web types gained the three round-48 fields;
web 680/680.

Round 48 — the #49 class CLOSED by construction: an automated audit of all
11 (model, response-schema) pairs found three more unserialized columns —
Experiment.last_guardrail_check_at (an operator freshness signal: a running
experiment never checked is a red flag), Experiment.updated_at, and
HoldoutGroup.created_by (audit attribution). All three are serialized now,
and a drift-guard test pins every pair: a model column absent from its
response schema fails the build, as does a response field with no column
behind it (allowlist empty). segment went missing for nine rounds because
nothing owned this pairing; now the pairing owns itself.

Round 47 — defect #49 + the results-export surface. #49: MetricSnapshot
stored `segment` since exp08 but MetricSnapshotResponse never serialized it
— the listing made segment rows indistinguishable from whole-population
rows (the web type even declared `segment?` and never received it), so a
consumer summing rows double-counted every sliced metric; one field in the
response schema fixes it, pinned by a serialization test. Export: GET
/experiments/{id}/metrics/export streams the snapshots as CSV (the
industry-standard results hand-off) under the SAME delegated read scope and
uniform-404 wall as the JSON listing; key columns are pattern-validated
lowercase so there is no Excel formula-injection surface, and provenance
stays out of the flat file. metrics.py manifest pin moved to (2,3); live
E2E grew both export checks (76 checks).

Round 46 — mutation wave 11 over the savepoint/lock fixes (12/12 killed, 0
survivors; facade/_shield yielded 0 mutants — try/except/async-with shapes
are outside the harness's operators and are held by the kill-proven defect
pins instead), and the DESIGN-TIME POWER gap closed (industry parity:
Statsig/Eppo both surface required-vs-actual sample size). New pure
`required_n_per_arm(baseline, mde_rel, alpha, power)` — classic
two-proportion normal approximation, pooled under H0 / unpooled under H1,
mde RELATIVE to baseline, degenerate inputs -> None. Full analyses whose
spec declares a power target now attach a `power` block computed from the
OBSERVED control baseline of the first proportion-shaped (binary OR rate)
primary metric: required_n_per_arm vs min arm n, powered flag, and the
SAMPLE_BELOW_POWER_TARGET health warning when short — a "no effect" read
below target is not evidence of absence. Console analysis page renders a
Powered/Underpowered banner. Textbook check pinned: baseline 10%,
relative MDE 20%, alpha .05, power .8 -> ~3.8k units/arm.

Round 45 — defect #48 (look-budget race, alpha overspend): the sequential
look budget was read-count-then-insert with NO lock — two concurrent full
analyses at the last O'Brien-Fleming look both saw used=N, both passed the
max_looks gate and both recorded a look, exceeding the budget by one beyond
the spending plan (a genuine type-I inflation, not just bookkeeping). Full
analyses now take the experiment row lock (the same one the state machine
uses); informational segment slices stay lock-free — they record no look.
Kill-proven with a two-committed-session race at max_looks=1: unfixed, both
returned look 1; fixed, exactly one look lands and the loser gets the typed
EXPERIMENT_LOOKS_EXHAUSTED.

Round 44 — defect #47 (the #41 family, promotion seam): finish_async_apply
converts a typed adapter failure into a state write ON THE KEPT transaction
(draft parked back to 'approved' + apply_error) — so any partial writes the
adapter made before raising would have been committed alongside the parking.
Today's adapters are single-create (audited: matching_config, learning_path,
workflow_binding via its own savepoint, eco_rollout through the eco service's
validate-first create), so the window was latent — but the next adapter
wouldn't promise that. The validate+apply pair now runs under a savepoint;
pinned by a write-then-fail-typed adapter test (kill-proven: the unfixed
branch leaks the partial row). The sync apply path needs nothing — its
AppError propagates and the request transaction rolls back whole.

Round 43 — defect #46 (snapshot sweep had no catch-up): the windows sweep
enqueued ONLY yesterday — a worker outage left that day's snapshots missing
forever, and exposures landing after the sweep (late writers) were never
reflected. The sweep now re-enqueues a rolling SNAPSHOT_BACKFILL_DAYS=3
window fan per live experiment (most recent last): the snapshot upsert is
idempotent, so recomputation backfills outages up to 2 days and continuously
heals late-arriving data. The cap still counts experiments (slots), so the
anti-starvation ordering is unchanged; outbox volume is 3 small messages per
experiment-day. Longer outages still need a manual window recompute — the
bound is deliberate (unbounded backfill is the accumulation-bomb shape).

Round 42 — defects #44 and #45. #44: the spec cross-checks never compared
washout to window — a switchback spec with washout_minutes >= window_minutes
folds EVERY snapshot window to zero (metrics' swallow guard), so the
experiment runs forever collecting nothing, invisible until someone stares
at an empty analysis. Rejected at the spec boundary now (>= is the exact
dangerous edge); the metrics-side swallow stays as defense for legacy rows,
covered by mutating a stored spec directly — the only way such a row can
exist. #45: the layer A/A probe's n parameter was unbounded — the probe is
a synchronous hash loop ON the event loop, so one admin typo (n=1e9) stalls
the entire API process; Query-clamped to [100, 50000] and pinned by a
route-signature test. Savepoint overhead check from rounds 39–41: resolve
re-benchmarked at 2.99 ms new / 1.08 ms sticky — within noise of the
pre-savepoint baseline, no ADR baseline change needed.

Round 41 — defect #43 (the #41 class, third and final site): @_shield
swallowed hook-body exceptions, but the body runs raw reads on the HOST
session outside the facade's savepoints (db.get with spec-config-derived
ids). A statement failure there left the host either in a failed
transaction (its next statement exploding with InFailedSQLTransaction) or
silently rolled back — the host's prior uncommitted business writes lost
while it went on to "commit" nothing. The shield now wraps the whole hook
body in a SAVEPOINT on the host session; read-path hooks that open their
own sessions just open-and-release an empty one. Test lesson worth keeping:
the first proof attempt asserted survival via db.get — which hits the
identity map and masked the rollback entirely; the pin uses a real SELECT.
With #41 (facade), #42 (notifications) and #43 (hooks), every
swallow-and-continue site in the package now confines its failures to a
savepoint — the class is closed.

Round 40 — defect #42 (the #41 class, swept): all three "additive, never
blocking" owner-notification sites (alert-only findings, the auto-pause
notice, the interaction sweep) swallowed exceptions while CONTINUING on the
same session. A notification flush error therefore poisoned the session and
— worst case — sank the very pause it was announcing: the breached
experiment kept running while arq retried into the same wall forever. Each
site now runs its notification under a SAVEPOINT, making the swallow sound.
Pinned by a pause-survives-notification-DB-failure test (a real failing
statement on the same session inside a monkeypatched create), kill-proven
against the unfixed code. The remaining broad swallows in the package were
triaged: every other one wraps pure spec parsing (no DB inside the try) or
re-raises as a typed error — not in the class.

Round 39 — defect #41 (fail-safe facade poisoned the HOST session): the
facade caught exceptions but never rolled back, so a mid-flush DB error
(natural trigger: a unit_id one char over the varchar(26) column) left the
host's session in PendingRollback. On the self-serve surface the very next
commit 500'd; on write-path hooks the damage surfaced LATER at the host's
own business commit — outside every shield — the experiment breaking the
product path it rode along with, the exact thing this ADR forbids. Fix:
both facade entry points run the service call under a SAVEPOINT
(`begin_nested()`): an error rolls back only the experiment writes, the
host's prior uncommitted business writes survive, and the session stays
healthy. Pinned by a poison-isolation test (host write before the
touchpoint, 27-char unit_id as the bomb, post-poison flush + a fresh valid
resolve must both work); the test was proven to KILL the unfixed facade.

Round 38: the exp outbox handlers joined the §96 pin (an unregistered
handler is dead code the sweeps enqueue into forever — all three topics
asserted by name in the live registry), and the hot path got its baseline
numbers: NEW-assignment resolve ≈ 3.2 ms/call, sticky resolve ≈ 1.0 ms/call
on the dev Postgres with the version-keyed spec cache warm — the figures
future latency regressions will be judged against.

ITS was attempted and DELIBERATELY REVERTED in round 10: spec versions can
only be added in draft/review, so any candidate intervention instant
precedes every running-phase window — there is no pre-period snapshot data,
and an ITS block would be dead code. ITS needs pre-period metric backfill
(computing windows over a roster that predates enrollment), which the
ITT/as_of model intentionally forbids. Revisit only with a dedicated
backfill design.

Remaining (explicitly deferred): per-unit repeated-measures for every
source, CUPED covariates beyond projects/revision_count, segment-dimension
breakdowns (needs a snapshot dimension), full KM time-to-event, write-side
org delegation.

v2 batch 2 (round 9, 2026-10-01) — second slice of the §18 backlog:

- **Global holdout groups** (§4.12, migration exp07a00007): an active group
  withholds a deterministic hash band (salt `holdout-group:<key>`, max
  2000bp) from NEW enrollment into every experiment of its domain —
  platform-wide or org-scoped. Membership is computed, never stored
  (release frees units instantly); existing sticky assignments keep serving
  (a holdout never yanks an experience — same rule as pause); preview names
  the excluding group. Admin CRUD + release at
  /experiments/holdout-groups (+ Console Holdouts tab); the hot-path
  domain lookup is 60s-process-cached like the missing-key cache, with
  ends_at re-checked at eval time so expiry needs no status write.
- **Cross-experiment interaction detection** (§4.13, weekly sweep
  `exp_interaction_sweep`): for running experiment pairs in DIFFERENT
  layers, the variant-assignment contingency over shared units is χ²-tested
  for independence (Wilson-Hilferty `chi2_sf` handles arbitrary df; gate
  α=0.001, min 100 shared units, pair-capped). Deterministic hashing makes
  true dependence impossible by construction, so a hit means something is
  broken (salt collision, replayed assignments) — `__interaction__` alert
  on BOTH experiments, 7-day per-pair suppression, alert-only.
- **CUPED covariates computed** (§4.6): when the spec sets
  variance_reduction with covariate_metric == the metric itself, the
  projects/revision_count source switches to per-UNIT aggregation (ITT:
  every assigned unit contributes, zero when silent) and emits
  cov_sum/cov_sum_sq/cov_xy_sum from the pre-window lookback — analysis now
  engages cuped_adjusted_welch end-to-end and the
  CUPED_COVARIATES_UNAVAILABLE honesty warning clears. Provenance stamps
  `aggregation: per_unit` (the n-semantics change is recorded, not silent).
  Other sources still skip covariates (the warning stays truthful there).

v2 batch 1 (round 8, 2026-10-01) — first slice of the §18 backlog:

- **Launch checklist enforced** (§5 v2): review→scheduled requires every
  required item affirmed (hypothesis peer-check, power, metrics review,
  rollback owner; learner/talent domains add the ethics screen) — 422
  EXPERIMENT_CHECKLIST_INCOMPLETE naming the missing items; the affirmation
  is recorded in the transition audit event; Console renders the checklist
  in review status; keys are web-parity-pinned.
- **Exposure-SRM health check** (§4.13, trigger-bias detection): per-variant
  exposed-unit counts are χ²-tested against assignment proportions every
  guardrail sweep — divergence means the exposure decision is treatment-
  affected, poisoning any exposed-only analysis. Alert-only
  (`__exposure_srm__`), min 50 exposed, 24h suppression.
- **Winsorization actually applied** (§4.6): a shared empirical-percentile
  clamp now runs in the latency, revision-count and cost sources; provenance
  carries winsorize_pct ONLY on snapshots whose source applied it (the
  round-4 honesty rule, now with real application).
- **Honesty warnings in analysis**: `TRIGGERED_ANALYSIS_UNAPPLIED` when the
  spec requests exposed-only analysis (denominators are still ITT) and
  `CUPED_COVARIATES_UNAVAILABLE` when variance_reduction is configured but
  no source computed covariate aggregates — accepted-but-ignored knobs are
  no longer silent.

Hardening round 7 — fuzz layer + live-API E2E (2026-10-01):

- **Hypothesis fuzz** (tests/test_exp_fuzz.py): every untrusted-input surface
  is total — spec validation over arbitrary nested garbage yields parsed or a
  typed AppError only; population evaluation returns bool over any op/values/
  context; the canonical hash is stable and order-free on arbitrary JSONables;
  `_observed` is float-or-None and finite; mSPRT p ∈ [0,1]; OF boundaries are
  positive and monotone; BH is monotone (any passing p dominates every
  failing one). Zero raw exceptions found in product code.
- **Live-API E2E** (tests/e2e_experiment_lifecycle.py, uvicorn APP_ENV=test):
  39 checks over the real HTTP stack exercising all six hardening rounds —
  the non-admin 403 wall on every operator surface, the protected-attribute
  422 over the wire, the ramp-decrease and enum-guard contracts,
  deterministic previews, EXPERIMENT_DECISION_REQUIRED on direct promote,
  forged-hash refusal, draft→approve→apply with the 409 idempotency, the
  applied target-domain ref, surface-key reuse after terminal, and the
  decision registry/meta. 39/39 on first run.

Hardening round 6 — service-core mutation campaign (same day):

- AST mutation over the service decision cores (assignment hashing/ramp/
  population, state machine + spec hash, guardrail `_observed` + SRM, all
  seven metric sources, promotion target validation): **95/115 killed**;
  every survivor individually verified and recorded in in-test ledgers
  (unreachable guards, float-exact boundaries, display precision, and the
  per-source half-open window pairs that are template copies of the
  exposures-pinned contract).
- Real gaps the campaign exposed and closed: the workflow_runs
  latency/failure measures had NO db-level coverage; the success-status
  assertion used a symmetric fixture (== vs != collided at 2/2); the
  cost-ledger unit-type guard's OR combination and the telemetry None-rate
  skip path were untested; `_validate_target` asserted error codes but never
  HTTP statuses (every 404/422 constant was mutable) and its generic branch
  (oversize/blank refs, the 64-char boundary) had no tests; hash golden
  vectors now pin the digest-slice/base/salt layout (a silent change would
  re-randomize every live experiment on deploy).
