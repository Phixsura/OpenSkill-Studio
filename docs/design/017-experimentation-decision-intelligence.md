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

### 4.13 `experiment_health_checks` (v2)

`experiment_id`, `check_key` enum {srm, exposure_srm, aa_probe, pre_balance,
novelty, interaction}, `status` enum {pass, warn, fail}, `detail` JSONB,
`checked_at`. Latest row per check_key surfaces as the health strip on the
experiment overview page.

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

Facade is the only entry point (eco facade discipline). Configs returned to a
domain still pass ALL of that domain's existing validations and approval gates.

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
| **quasi-experiments (v2)**   | DiD (parallel-trends diagnostic plotted) and interrupted time series for `analysis_type=observational`; always `causal_claim:false`; synthetic control deferred                                                                 | effect + caveat                                                          |

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
- Explicitly deferred (documented in the competitive analysis): synthetic
  control, CUPED++ multi-covariate/ML covariates, anonymous→login identity
  resolution, feature-flag CDN/edge SDKs, session replay, warehouse
  connectors (we are the warehouse).
- Base branch: the epic depends on the eco facade, so implementation chains on
  the issue-35 branch (PR #36) until it merges.

## 18. Implementation notes (exp01–exp09, 2026-09-30)

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
