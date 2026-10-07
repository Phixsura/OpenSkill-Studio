# Competitive Analysis: Experimentation & Decision Intelligence (issue #42)

Benchmarked against: **Statsig** (acquired by OpenAI 2025, platform maintained by
Amplitude), **Eppo / Datadog Experiments** (acquired 2025), **GrowthBook** (OSS),
**Optimizely**, **LaunchDarkly**, **Amplitude Experiment**, and published internal
platforms (Microsoft ExP, Netflix XP, Uber/DoorDash switchbacks, Airbnb ERF,
Spotify Confidence). Feeds ADR-017 v2.

## 0d. Status update (2026-10-07, round 628): windowed SRM (defect #90)

Cumulative-only SRM was the one diagnostic where we still trailed
Statsig/Eppo: both slice SRM by time because a late randomization break
is diluted by the healthy cumulative mass (our red-first proof: 5000
balanced + 120 all-control in 24h = cumulative chi2 2.81, quiet at
p<0.001; the 24h slice alone is chi2 120). Closed with
`check_srm_window` — same chi-square, last-24h slice, own
`__srm_window__` key, alert-only, no second page when cumulative
already alerted in the same sweep.

Round 630 addendum — webhook delivery reliability (defect #91):
delivery was fire-once best-effort and logged a 500 as "delivered".
Industry (Svix/LaunchDarkly-class) retries transient failures; now
429/5xx/network errors retry on a 1s/5s/25s backoff with per-retry
SSRF re-validation, 4xx never retries. Red-first both ways (5xx
retries to success; 400 stays single-attempt).

Round 640 addendum — defect #92: the windowed-SRM argument applied to
trigger bias. Cumulative exposure-SRM dilutes a late exposure-call-site
regression (red-first proof: 944 balanced historical exposures + 56
all-treatment in 24h = cumulative chi2 3.14 quiet, window chi2 56
flagrant). `check_exposure_srm_window`, own key, alert-only.

Round 643 addendum — defect #93 (console wiring): the assignments-page
SRM banner only matched `__srm__`, so the new windowed/exposure family
alerts were invisible in the UI. The banner now maps the full family
with per-key guidance text. Red-first (vitest).

Round 647 addendum — defect #94: record_exposure accepted exposures for
holdout units (resolve() never serves them) and returned True, writing
garbage rows against the **holdout** assignment and feeding
last_exposure_at with non-serving traffic. Now the same fail-safe as
exposure-without-assignment: False, no row — on the primary path AND
the identity-retry path. Red-first.

## 0c. Status update (2026-10-06, the webhook + identity epochs, rounds 209-296)

Two capability families shipped since 0b that the original matrix never
even listed (found by scanning the staples the matrix omitted):

- **Anonymous -> login identity resolution** (§4.17, exp15/16) — the
  pre-login story every vendor SDK ships: a device-minted anonymous id
  resolves and records exposures through rate-limited public endpoints,
  login/register claim the id, assignments migrate IN PLACE (ITT and
  exposure FKs preserved), first-link-wins with a 422 conflict contract,
  and a transparency listing. Seven defects (#73-#79) found and killed
  red-first during hardening. The register page's CTA is the first real
  pre-login consumer (round 294) — anonymous -> register -> link ->
  attribution runs end-to-end.
- **Outbound webhooks** (§4.18, rounds 284-296) — Statsig/GrowthBook-class
  event delivery: experiment.status_changed / guardrail_breach /
  decision_recorded through the platform's hardened WebhookService
  (HMAC-SHA256, SSRF blocklist incl. CGNAT/NAT64), org-scoped
  containment (platform-wide experiments reach no tenant), and
  commit-safe delivery the vendors don't document: #80 (no delivery
  before the caller's commit), #81 (a rollback cancels — the event never
  rides a later commit), and the savepoint matrix pinned empirically
  (the outbox runner wraps handlers in savepoints; an unrelated
  sibling's rollback must not cancel). Five DB kill-proofs double as the
  SQLAlchemy-drift alarm.

Also closed since 0b: the design-time sample-size planner (rounds
312-313) — the §4.13 power core was look-time-only; now a read-scope
planning endpoint plus a builder-page calculator card, the staple every
vendor console leads with.

Also since 0c: the sweep-fairness audit the vendors never publish —
one invariant ("filter before the cap, or the predicate self-drains")
hunted through all eight background sweeps, five violations found and
fixed red-first (#84 an unstamped skip leaving a running experiment
silently unguarded; #85-#87 post-cap filters starving tails; #88 a
rotation stride covering one pair per week — 381 weeks to full coverage
at 400 pairs, now ceil(P/cap) weeks by a pinned coverage law); the
fixes themselves then put under mutation (wave 49: 45/49, four reasoned
survivors). And a doc-safety correction vendors rarely admit: pause
freezes enrollment but keeps serving existing assignments — the
operator table now says so and names archive as the full kill.

Still open by choice: webhook subscription UI (a platform-wide console
surface shared by pack/talent/eco events), edge SDKs, session replay,
warehouse connectors, org-admin spec authoring (§2 posture).

## 0b. Status update (2026-10-04, v3 rounds 113-176)

The v3 epochs since the note below closed the last deliberate deferrals
and added depth the matrix's vendors do not ship:

- **Multi-covariate CUPED** (§4.6 v3, exp12) — the "defer" row at the
  matrix bottom is CLOSED: a provider registry (projects, evaluations),
  joint OLS over up to 3 covariates verified at 1e-9 against a per-unit
  oracle, cross-window folding, honest CUPED_MULTI_DEGRADED downgrade
  warning. Data-driven covariate selection SHIPPED rounds 201-205
  (§4.6b: the "auto" literal, pooled-|r| selection from stored sums,
  the exposed cuped_auto evidence) — the row is fully closed.
- **Binary CUPED** (§4.6 v4) — regression-adjusted proportions (Eppo
  CUPED++-class on binaries) on a per-unit 0/1 contract across two
  sources, caveat attached.
- **Quantile metrics** (§4.14, exp13) — p50/p95 reads from a mergeable
  log-histogram sketch with distribution-free CIs, PERCENTILE GUARDRAILS
  ("pause when p95 regresses"), console rendering.
- **Scheduled ramp plans** (exp14) — monotone auto-ramp steps applied by a
  crash-tolerant sweep; console editor.
- **Operational surface**: weekly owner digest (+ decision-queue flags),
  look history, the export trio (snapshots/guardrail events/assignments)
  with console downloads, list data-flow badges, integration snippets,
  digest opt-out.
- **Statistical calibration, Monte-Carlo-pinned in the main suite** —
  something none of the compared vendors publish as tests: null alpha
  (Welch/binary/CUPED), power at the planner's exact n, mSPRT
  anytime-validity under continuous peeking, quantile CI coverage.
- Defects #1-#69 each fixed with a kill-proof; mutation waves 1-35
  (~1100 mutants) cover every module; 131 full-suite certifications.

Still open by choice: org-admin SPEC AUTHORING only — org delegation
already ships creation, transitions, incident pause/resume, diagnostics
and CSV exports for org-scoped experiments; spec versions stay
platform-only as the §2 safety posture (analysis semantics are baked
into stored snapshots). Auto covariate selection SHIPPED rounds 201-205
(§4.6b).
(ITS SHIPPED rounds 177-178, full Kaplan-Meier SHIPPED rounds 181-192
(censoring-correct horizon block, source-gated #70), synthetic control
SHIPPED rounds 193-196 — simplex donor weights, placebo inference,
console strip.)

## 0. Status update (2026-10-01, v2 round 10)

Every "close" row below has SHIPPED (ADR-017 §18 rounds 8-10): CUPED (with
computed covariates for projects/revision_count and cost_ledger), dual
engine, mSPRT, winsorization (applied), health checks (SRM, exposure-SRM,
pre-balance, novelty decay, A/A probe, cross-experiment interaction),
global holdout groups, Thompson bandit suggestions (advisory), switchback
design (epoch windows + washout), post-stratification (time-stratified
inverse-variance pooling), meta-analysis corpus priors + shrinkage, launch
checklist, async apply, org-admin read delegation. Closed later the same day (round-10 second half): triggered/exposed-only
denominators (applied, dilution honestly warned), DiD change-score for
observational runs, segment breakdowns (org dimension), the useExperiment
TS hook + self-serve endpoints, and CUPED covariates on three sources
(projects, cost_ledger, workflow_runs). The "hourly guardrail lane" was
already satisfied: guardrail evaluation runs every 10 minutes on live
sliding windows (only ANALYSIS windows are daily). Still open by choice:
org-admin SPEC AUTHORING (the rest of write-side delegation — creation,
transitions, incidents, exports — already ships; ITS, full KM,
multi-covariate CUPED, synthetic control and auto covariate selection
have all since shipped).

## 1. Feature matrix (industry standard vs ADR-017 v1)

| Capability                                                                                       | Statsig                     | Eppo      | GrowthBook      | ADR-017 v1                               | v2 decision                                                                                                                                 |
| ------------------------------------------------------------------------------------------------ | --------------------------- | --------- | --------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Deterministic sticky bucketing                                                                   | ✓                           | ✓         | ✓               | ✓                                        | keep                                                                                                                                        |
| Mutually exclusive layers                                                                        | ✓                           | ✓         | ✓ (namespaces)  | ✓                                        | keep                                                                                                                                        |
| SRM detection                                                                                    | ✓                           | ✓         | ✓               | ✓                                        | keep                                                                                                                                        |
| Guardrails w/ auto-stop                                                                          | ✓                           | ✓         | ✓               | ✓ (pause-only)                           | keep (stricter than industry: never auto-promote)                                                                                           |
| **CUPED variance reduction**                                                                     | ✓                           | ✓ CUPED++ | ✓               | ✗                                        | **close (P0)** — single pre-period covariate                                                                                                |
| **Bayesian engine** (P(beat control), expected loss)                                             | ✓                           | ✓         | ✓ (dual engine) | ✗                                        | **close (P0)** — conjugate posteriors, dual engine                                                                                          |
| **Always-valid sequential (mSPRT)**                                                              | ✓                           | ✓ hybrid  | ✓               | OF alpha-spending only                   | **close (P0)** — add mSPRT option                                                                                                           |
| **Winsorization / capping / percentile metrics**                                                 | ✓                           | ✓         | ✓               | ✗                                        | **close (P0)** — per-metric-definition config                                                                                               |
| **Triggered (exposed-only) analysis + dilution correction**                                      | ✓                           | ✓         | ✓               | exposure split existed, no analysis mode | **close (P0)**                                                                                                                              |
| **Health checks: A/A, exposure/assignment mismatch, pre-balance, novelty (days-since-exposure)** | ✓                           | ✓         | partial         | SRM only                                 | **close (P0)**                                                                                                                              |
| **Global/team holdouts (cumulative impact)**                                                     | ✓ (~6mo holdouts)           | ✓         | ✓               | per-experiment holdout_bp only           | **close (P1)** — first-class holdout groups                                                                                                 |
| **Interaction detection across experiments**                                                     | ✓ (layers + checks)         | partial   | ✗               | ✗                                        | **close (P1)** — pairwise scan on overlapping non-same-layer pairs                                                                          |
| **Multi-armed bandit (Autotune-class)**                                                          | ✓                           | ✗         | ✓               | deferred                                 | **close (P1), scoped** — Thompson sampling, presentation/marketplace domains only                                                           |
| **Switchback / cluster designs for interference**                                                | ✗ (cluster only)            | partial   | ✗               | cluster only                             | **close (P1)** — switchback design for matching/marketplace (DoorDash/Lyft class problem, directly relevant to our matching domain)         |
| Stratified sampling / post-stratification                                                        | ✓                           | ✓         | ✓               | ✗                                        | **close (P1)** — post-stratification for small-n cohort/org experiments                                                                     |
| **Quasi-experiments (DiD, ITS)**                                                                 | ✗                           | ✗         | ✗               | "observational" label only               | **close (P1)** — DiD + interrupted time series with causal_claim:false; **synthetic control SHIPPED rounds 193-196**                        |
| **Meta-analysis / experiment corpus priors**                                                     | ✓ Meta Analysis             | ✓         | ✗               | decision registry only                   | **close (P2)** — win-rate + effect distributions from DecisionRecords, optional prior for Bayesian engine                                   |
| Org-level default guardrail policies                                                             | ✓                           | ✓         | partial         | per-experiment                           | **close (P2)** — platform guardrail policy auto-attach                                                                                      |
| Launch checklist / review workflow                                                               | ✓                           | ✓         | partial         | review status only                       | **close (P2)** — structured checklist on review→scheduled                                                                                   |
| Near-real-time guardrail lane                                                                    | ✓ (minutes)                 | ✓         | partial         | daily windows                            | **close (P2)** — hourly fast-lane for guardrail metrics; daily for analysis                                                                 |
| Client SDK ergonomics (hooks, exposure batching)                                                 | ✓                           | ✓         | ✓               | facade only                              | **close (P2)** — `useExperiment` TS hook + batched exposure endpoint                                                                        |
| Warehouse-native metric connectors                                                               | ✓                           | ✓ (core)  | ✓               | n/a                                      | **not building** — we ARE the data store; metric_definitions are our semantic layer                                                         |
| Feature-flag CDN / edge SDKs / session replay                                                    | ✓                           | ✗         | ✓ flags         | ✗                                        | **not building** — out of scope for a B2B platform with in-process facade                                                                   |
| Identity resolution (anon→login graph)                                                           | ✓                           | ✓         | ✓               | ✗                                        | **defer** — all our units are authenticated; note for public registry pages                                                                 |
| CUPED++ multi-covariate / ML covariates                                                          | ✗                           | ✓         | ✗               | ✗                                        | **SHIPPED v3 rounds 113-115** (multi-covariate joint OLS + binary CUPED round 142); auto covariate selection SHIPPED rounds 201-205 (§4.6b) |
| Synthetic control                                                                                | internal-platform territory | ✗         | ✗               | ✗                                        | **defer**                                                                                                                                   |

## 2. Where we intentionally exceed industry baseline

- **No auto-promote path at all** (industry ships auto-rollback AND auto-ship;
  our domain — education/employment outcomes — forbids the latter).
- **Employment-decision randomization structurally impossible** (no such
  promotion target type; talent_flow restricted to presentation).
- **DecisionRecord registry as organizational memory** with immutable evidence
  links — Statsig/Eppo knowledge bases are lighter-weight.
- **Provenance-versioned metrics** (query_version on every snapshot) — matches
  Eppo's metric-repo rigor.

## 3. Gap-closure priority

- **P0 (statistical credibility — without these the analysis tab is not
  competitive):** CUPED, Bayesian dual engine, mSPRT, winsorization/percentile
  metrics, triggered analysis, health-check suite.
- **P1 (design coverage — without these several of our domains cannot be
  correctly experimented):** switchback (matching/marketplace interference),
  post-stratification (small-n cohorts), global holdouts, interaction
  detection, scoped bandits, DiD/ITS.
- **P2 (operational maturity):** guardrail policies, launch checklist, hourly
  guardrail lane, meta-analysis, client SDK ergonomics.

All P0/P1/P2 items are folded into ADR-017 v2 (§4, §6, §9–§11, §16 phases).

## 4. Sources

- Statsig vs GrowthBook comparisons and stats-engine docs (statsig.com, growthbook.io)
- Eppo/Datadog CUPED++ and sequential/hybrid/Bayesian documentation
- GrowthBook open-source stats engine (dual frequentist/Bayesian, post-stratification)
- DoorDash/Lyft switchback literature; Regular Balanced Switchback Designs (arXiv 2506)
- Microsoft ExP (CUPED origin), Statsig Meta Analysis / Autotune / holdouts docs
- Industry consolidation context: Datadog×Eppo (2025), OpenAI×Statsig (2025)
