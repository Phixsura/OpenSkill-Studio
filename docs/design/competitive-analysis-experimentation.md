# Competitive Analysis: Experimentation & Decision Intelligence (issue #42)

Benchmarked against: **Statsig** (acquired by OpenAI 2025, platform maintained by
Amplitude), **Eppo / Datadog Experiments** (acquired 2025), **GrowthBook** (OSS),
**Optimizely**, **LaunchDarkly**, **Amplitude Experiment**, and published internal
platforms (Microsoft ExP, Netflix XP, Uber/DoorDash switchbacks, Airbnb ERF,
Spotify Confidence). Feeds ADR-017 v2.

## 0b. Status update (2026-10-04, v3 rounds 113-176)

The v3 epochs since the note below closed the last deliberate deferrals
and added depth the matrix's vendors do not ship:

- **Multi-covariate CUPED** (§4.6 v3, exp12) — the "defer" row at the
  matrix bottom is CLOSED: a provider registry (projects, evaluations),
  joint OLS over up to 3 covariates verified at 1e-9 against a per-unit
  oracle, cross-window folding, honest CUPED_MULTI_DEGRADED downgrade
  warning. ML-learned covariates remain deferred (that half of the row).
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

Still open by choice: ML-learned covariates, write-side org delegation.
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
ML-learned covariates, write-side org delegation (ITS, full KM,
multi-covariate CUPED and synthetic control have all since shipped).

## 1. Feature matrix (industry standard vs ADR-017 v1)

| Capability                                                                                       | Statsig                     | Eppo      | GrowthBook      | ADR-017 v1                               | v2 decision                                                                                                                         |
| ------------------------------------------------------------------------------------------------ | --------------------------- | --------- | --------------- | ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Deterministic sticky bucketing                                                                   | ✓                           | ✓         | ✓               | ✓                                        | keep                                                                                                                                |
| Mutually exclusive layers                                                                        | ✓                           | ✓         | ✓ (namespaces)  | ✓                                        | keep                                                                                                                                |
| SRM detection                                                                                    | ✓                           | ✓         | ✓               | ✓                                        | keep                                                                                                                                |
| Guardrails w/ auto-stop                                                                          | ✓                           | ✓         | ✓               | ✓ (pause-only)                           | keep (stricter than industry: never auto-promote)                                                                                   |
| **CUPED variance reduction**                                                                     | ✓                           | ✓ CUPED++ | ✓               | ✗                                        | **close (P0)** — single pre-period covariate                                                                                        |
| **Bayesian engine** (P(beat control), expected loss)                                             | ✓                           | ✓         | ✓ (dual engine) | ✗                                        | **close (P0)** — conjugate posteriors, dual engine                                                                                  |
| **Always-valid sequential (mSPRT)**                                                              | ✓                           | ✓ hybrid  | ✓               | OF alpha-spending only                   | **close (P0)** — add mSPRT option                                                                                                   |
| **Winsorization / capping / percentile metrics**                                                 | ✓                           | ✓         | ✓               | ✗                                        | **close (P0)** — per-metric-definition config                                                                                       |
| **Triggered (exposed-only) analysis + dilution correction**                                      | ✓                           | ✓         | ✓               | exposure split existed, no analysis mode | **close (P0)**                                                                                                                      |
| **Health checks: A/A, exposure/assignment mismatch, pre-balance, novelty (days-since-exposure)** | ✓                           | ✓         | partial         | SRM only                                 | **close (P0)**                                                                                                                      |
| **Global/team holdouts (cumulative impact)**                                                     | ✓ (~6mo holdouts)           | ✓         | ✓               | per-experiment holdout_bp only           | **close (P1)** — first-class holdout groups                                                                                         |
| **Interaction detection across experiments**                                                     | ✓ (layers + checks)         | partial   | ✗               | ✗                                        | **close (P1)** — pairwise scan on overlapping non-same-layer pairs                                                                  |
| **Multi-armed bandit (Autotune-class)**                                                          | ✓                           | ✗         | ✓               | deferred                                 | **close (P1), scoped** — Thompson sampling, presentation/marketplace domains only                                                   |
| **Switchback / cluster designs for interference**                                                | ✗ (cluster only)            | partial   | ✗               | cluster only                             | **close (P1)** — switchback design for matching/marketplace (DoorDash/Lyft class problem, directly relevant to our matching domain) |
| Stratified sampling / post-stratification                                                        | ✓                           | ✓         | ✓               | ✗                                        | **close (P1)** — post-stratification for small-n cohort/org experiments                                                             |
| **Quasi-experiments (DiD, ITS)**                                                                 | ✗                           | ✗         | ✗               | "observational" label only               | **close (P1)** — DiD + interrupted time series with causal_claim:false; **synthetic control SHIPPED rounds 193-196**                |
| **Meta-analysis / experiment corpus priors**                                                     | ✓ Meta Analysis             | ✓         | ✗               | decision registry only                   | **close (P2)** — win-rate + effect distributions from DecisionRecords, optional prior for Bayesian engine                           |
| Org-level default guardrail policies                                                             | ✓                           | ✓         | partial         | per-experiment                           | **close (P2)** — platform guardrail policy auto-attach                                                                              |
| Launch checklist / review workflow                                                               | ✓                           | ✓         | partial         | review status only                       | **close (P2)** — structured checklist on review→scheduled                                                                           |
| Near-real-time guardrail lane                                                                    | ✓ (minutes)                 | ✓         | partial         | daily windows                            | **close (P2)** — hourly fast-lane for guardrail metrics; daily for analysis                                                         |
| Client SDK ergonomics (hooks, exposure batching)                                                 | ✓                           | ✓         | ✓               | facade only                              | **close (P2)** — `useExperiment` TS hook + batched exposure endpoint                                                                |
| Warehouse-native metric connectors                                                               | ✓                           | ✓ (core)  | ✓               | n/a                                      | **not building** — we ARE the data store; metric_definitions are our semantic layer                                                 |
| Feature-flag CDN / edge SDKs / session replay                                                    | ✓                           | ✗         | ✓ flags         | ✗                                        | **not building** — out of scope for a B2B platform with in-process facade                                                           |
| Identity resolution (anon→login graph)                                                           | ✓                           | ✓         | ✓               | ✗                                        | **defer** — all our units are authenticated; note for public registry pages                                                         |
| CUPED++ multi-covariate / ML covariates                                                          | ✗                           | ✓         | ✗               | ✗                                        | **SHIPPED v3 rounds 113-115** (multi-covariate joint OLS + binary CUPED round 142); ML covariates stay deferred                     |
| Synthetic control                                                                                | internal-platform territory | ✗         | ✗               | ✗                                        | **defer**                                                                                                                           |

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
