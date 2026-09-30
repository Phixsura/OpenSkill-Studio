# Competitive Analysis: Experimentation & Decision Intelligence (issue #42)

Benchmarked against: **Statsig** (acquired by OpenAI 2025, platform maintained by
Amplitude), **Eppo / Datadog Experiments** (acquired 2025), **GrowthBook** (OSS),
**Optimizely**, **LaunchDarkly**, **Amplitude Experiment**, and published internal
platforms (Microsoft ExP, Netflix XP, Uber/DoorDash switchbacks, Airbnb ERF,
Spotify Confidence). Feeds ADR-017 v2.

## 1. Feature matrix (industry standard vs ADR-017 v1)

| Capability | Statsig | Eppo | GrowthBook | ADR-017 v1 | v2 decision |
|---|---|---|---|---|---|
| Deterministic sticky bucketing | ✓ | ✓ | ✓ | ✓ | keep |
| Mutually exclusive layers | ✓ | ✓ | ✓ (namespaces) | ✓ | keep |
| SRM detection | ✓ | ✓ | ✓ | ✓ | keep |
| Guardrails w/ auto-stop | ✓ | ✓ | ✓ | ✓ (pause-only) | keep (stricter than industry: never auto-promote) |
| **CUPED variance reduction** | ✓ | ✓ CUPED++ | ✓ | ✗ | **close (P0)** — single pre-period covariate |
| **Bayesian engine** (P(beat control), expected loss) | ✓ | ✓ | ✓ (dual engine) | ✗ | **close (P0)** — conjugate posteriors, dual engine |
| **Always-valid sequential (mSPRT)** | ✓ | ✓ hybrid | ✓ | OF alpha-spending only | **close (P0)** — add mSPRT option |
| **Winsorization / capping / percentile metrics** | ✓ | ✓ | ✓ | ✗ | **close (P0)** — per-metric-definition config |
| **Triggered (exposed-only) analysis + dilution correction** | ✓ | ✓ | ✓ | exposure split existed, no analysis mode | **close (P0)** |
| **Health checks: A/A, exposure/assignment mismatch, pre-balance, novelty (days-since-exposure)** | ✓ | ✓ | partial | SRM only | **close (P0)** |
| **Global/team holdouts (cumulative impact)** | ✓ (~6mo holdouts) | ✓ | ✓ | per-experiment holdout_bp only | **close (P1)** — first-class holdout groups |
| **Interaction detection across experiments** | ✓ (layers + checks) | partial | ✗ | ✗ | **close (P1)** — pairwise scan on overlapping non-same-layer pairs |
| **Multi-armed bandit (Autotune-class)** | ✓ | ✗ | ✓ | deferred | **close (P1), scoped** — Thompson sampling, presentation/marketplace domains only |
| **Switchback / cluster designs for interference** | ✗ (cluster only) | partial | ✗ | cluster only | **close (P1)** — switchback design for matching/marketplace (DoorDash/Lyft class problem, directly relevant to our matching domain) |
| Stratified sampling / post-stratification | ✓ | ✓ | ✓ | ✗ | **close (P1)** — post-stratification for small-n cohort/org experiments |
| **Quasi-experiments (DiD, ITS)** | ✗ | ✗ | ✗ | "observational" label only | **close (P1)** — DiD + interrupted time series with causal_claim:false; synthetic control deferred |
| **Meta-analysis / experiment corpus priors** | ✓ Meta Analysis | ✓ | ✗ | decision registry only | **close (P2)** — win-rate + effect distributions from DecisionRecords, optional prior for Bayesian engine |
| Org-level default guardrail policies | ✓ | ✓ | partial | per-experiment | **close (P2)** — platform guardrail policy auto-attach |
| Launch checklist / review workflow | ✓ | ✓ | partial | review status only | **close (P2)** — structured checklist on review→scheduled |
| Near-real-time guardrail lane | ✓ (minutes) | ✓ | partial | daily windows | **close (P2)** — hourly fast-lane for guardrail metrics; daily for analysis |
| Client SDK ergonomics (hooks, exposure batching) | ✓ | ✓ | ✓ | facade only | **close (P2)** — `useExperiment` TS hook + batched exposure endpoint |
| Warehouse-native metric connectors | ✓ | ✓ (core) | ✓ | n/a | **not building** — we ARE the data store; metric_definitions are our semantic layer |
| Feature-flag CDN / edge SDKs / session replay | ✓ | ✗ | ✓ flags | ✗ | **not building** — out of scope for a B2B platform with in-process facade |
| Identity resolution (anon→login graph) | ✓ | ✓ | ✓ | ✗ | **defer** — all our units are authenticated; note for public registry pages |
| CUPED++ multi-covariate / ML covariates | ✗ | ✓ | ✗ | ✗ | **defer** — v1 single covariate, schema reserves list |
| Synthetic control | internal-platform territory | ✗ | ✗ | ✗ | **defer** |

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
