# Experiment-platform mutation campaign configs (ADR-017 §18)

Ten waves over the `app/experiments/` decision cores, ~540 mutation sites
total across rounds 10–23. Run any wave with:

```bash
cd apps/api
uv run python tests/tools_ast_mutate.py tests/mutation_configs/<wave>.json
```

Requirements: the target files must be **git-clean** (the harness rewrites
them in place and restores afterwards; it refuses dirty targets), and the
dev Postgres must be migrated (`make db-migrate`) for the db-coupled waves.

| wave | target | result when last run |
|---|---|---|
| 01 | pool_stratified / thompson_weights / chi2_sf / switchback_variant / holdout_group_roll / aa_probe | 33/43 (10 ledgered equivalents) |
| 02 | holdout service + interaction sweep | 45/51 (6 ledgered) |
| 03 | the five new metric sources | 32/55 (window-template + unit-type ledger) |
| 04 | compute_experiment_window / _write_snapshots / _variant_units / exposures source | 24/27 (3 ledgered) |
| 05 | delegation/self-serve deps + scoped list | 12/13 (1 ledgered) |
| 06 | the six surface hooks | 13/13 |
| 07 | decisions + promotion flow | 45/45 |
| 08 | experiments lifecycle (create/validate/ramp/checklist) | 36/36 |
| 09 | layers allocation + worker sweeps | 36/36 |
| 10 | analysis_service internals | 51/108 (or-coalesce templates, unreachable defaults, float/index-exact instants — all classified in-test) |

Survivor policy: every survivor is either killed by a named killer test or
recorded in an in-test ledger with the reason it is equivalent. "Timed out"
counts as killed. See ADR-017 §18 for the campaign narrative.

## wave11_savepoints_locks.json (round 46)

Targets the rounds-39-45 fixes: facade savepoints, the _shield savepoint,
finish_async_apply's savepointed adapter, and the rolling backfill sweep.
Result: 12/12 killed, 0 survivors. facade.py and _shield yielded 0 mutants —
the harness's operators do not mutate try/except/async-with structure; those
shapes are held instead by the kill-proven defect pins (#41/#42/#43: each
test was run against the unfixed HEAD and failed).

## wave12_power_holdout_flow.json (rounds 56-57)

required_n_per_arm, holdout report, exposure_stats. First pass surfaced 31
survivors and — once the report test asserted VALUES — a real defect (#52):
the report called analyze_binary with dicts against its positional-float
signature; the original structure-only test never reached the comparison
branch. Survivors killed by exact-value pins (required_n(0.10, 0.20) == 3841,
open-interval boundary refusals, org-scoped exact split with bp sitting ON a
member's roll, per-arm numerator/denominator from real submissions, window
clamps, typed statuses). Final ledgered equivalents (49 mutants, 45 killed): the lower-bound
Lt->LtE mutants on required_n (0 <= p lets p=0 through but the p1 == p2
guard then refuses — same output), and the report's sample_capped GtE->Gt
(differs only when the sampled universe is EXACTLY the 20k cap). The
boundary-kill menagerie that got here: one-sided reports in BOTH directions
(a second group whose key is searched so both data-bearing users are held),
n exactly 2 on the continuous gate, bp sitting exactly ON a member's roll,
and a time_to_event definition proving unknown kinds compute no comparison.
Deflake lesson: a searched bp must have at least one roll strictly below it
or the held side is empty and carries no numerator key.

## wave13_start_sweep.json (round 61)

sweep_experiment_starts: 4/4 killed after strengthening — a past `now`
launches nothing (the passed clock is authoritative, killing the
`now or datetime.now()` flip), start_at == now is the exact <= edge, and
the return value is pinned to the exact launch count.

## wave14_analysis_sweep.json (round 71)

sweep_experiment_analyses: 14/16 killed. Kills needed the §106.25
pause-the-residue trick for an exact analyzed count, a balanced no-effect
experiment (never notifies), a 24.5h-backdated notification (the dedup
window re-opens), and moving the significance unpack OUT of the notify
shield (an Or->And mutant crashed there and the shield swallowed the crash
— shields hide mutants; keep only the genuinely-additive write inside).
Ledgered equivalents: p < alpha at float-exact p == 0.05, and the dedup
cutoff's >= at a float-exact timestamp — both unconstructible.

## wave15_clone_search_scorecard.json (round 95)

clone + list_experiments(q) + latest_look: 12/13 killed. The second-look
addition killed the limit(1)->limit(2) mutant (scalar_one_or_none explodes
on two rows). Ledgered equivalent: the list default `limit: int = 50` —
the default-arg equivalence class this ledger already carries.

## wave16_update_definition.json (round 104)

update_definition: 4/4 after the status-code pin (422 is contract — the
AST map pins it statically, the dynamic assert makes the mutant die).

## wave17_multi_cuped.json (round 116)

The §4.6 v3 cores: 40/46 killed. Kills needed boundary-timestamp rows (a
submission exactly ON lookback_start counts; exactly ON window_start is out
of the pre query and IN the window — proving both <=/< edges), the
xx upper-triangle STRUCTURE pins (slice mutants on keys[i+1:] flip which
side carries the cross term), whole-covariate-missing refusal, and the
n == 2 admissible floor. Ledgered equivalents: the 1e-12 singularity
threshold (float-exact), the n <= 1 guard trio (welch's own
insufficient-data refusal makes the outcomes identical), and the two i < j
comparisons the i == j branch already shields.

## wave18_cov_evaluations.json (round 120)

The evaluations covariate provider: 7/7 killed. The first run left the
`status != APPROVED` mutant alive because the fixture held exactly one
approved and one non-approved review — symmetric counts. A second approved
review breaks the symmetry; fixture law: when a predicate picks a SUBSET,
make the subset's count differ from its complement's.

## wave19_quantiles.json (round 126)

The §4.14 quantile cores: 45/49 killed. First run left 23 alive — the
round-124 tests were structural; the kills needed HAND-ARITHMETIC pins
(ci = value(np ± z·sqrt(np(1-p))) spelled out with the z constant, the
rank-boundary bucket edge, the exact zero-mass boundary, both histogram
clamp ends, every validator edge incl. a set and a string). Ledgered
equivalents: the walk's final-return line (3 mutants — the clamp makes
rank <= total, and the last bucket always closes >= rank, so the line is
unreachable) and the zero-count bucket filter (a 0-count entry can never
satisfy a new >= crossing, shifts no n, and the final return is already
unreachable — no observable difference).

## wave20_ramp_plans.json (round 131)

set_ramp_plan + sweep_ramp_plans: 23/23 killed after strengthening — the
first run left 13 alive (status-code 422 pins on every refusal site, the
20/21 step-count boundary, ramp_bp 1 and 10000 both admissible on a draft,
the audit payload carrying the normalized steps, and a sweep step exactly
AT the sweep instant being due).

## wave21_digest.json (round 136)

sweep_weekly_digest: 13/14 killed — both 7-day >= edges (an exposure AND a
guardrail event exactly ON the boundary), the 7-vs-7.5-day constant, the
per-experiment id filters pinned by EXACT per-line counts, and the dedup
window's own >= edge (a rerun at created_at + 6d sends nothing). Ledgered:
the body's lines[:20] cap (killing it needs 21 running experiments under
one owner — a ~21x-lifecycle fixture for a display truncation constant;
verified by inspection).

## wave22_readers.json (round 140)

look_history + list_assignments: 8/10 killed (the OF look-number field
mapping needed an obrien_fleming run — msprt looks are None there and
cannot distinguish the Or->And payload mutant; order, cap mechanism and
shape equality with latest_look pinned). Ledgered: the two DEFAULT limit
constants (50/5000) — killing them needs 51/5001 fixture rows for a
default nobody passes; the limit MECHANISM is killed via explicit
limit=1/limit=2 calls.

## wave23_binary_cuped.json (round 143)

_compare whole-function sweep after the round-142 binary-CUPED branch:
30/31 killed. The sweep exposed three OLD blind spots beyond the new code —
the binary/continuous effect values were never exactly pinned, the
rate-bayesian p_beat/expected_loss formulas were never value-pinned (now
hand-spelled against the frequentist read), and se == 0 is REACHABLE
(0/200 vs 0/200) so the guards' else-branches are real. The k == 1 strict
> 1 gates are pinned WITH a covariates map present (the real compute path
stores one even for a single covariate). Ledgered: the expected_loss
trailing `if se > 0` (with z0 already guarded to 0, the expression is
identically 0 at se == 0 — equivalent to the else branch).

## wave24_binary_sources.json (round 147)

_source_projects + _source_evaluations after the binary-CUPED branches:
42/43 killed. Kills needed exactly-on-timestamp rows on EVERY window edge
of every branch (shared per-submission query, single-CUPED pre/cur, multi
per-unit y, binary per-unit, evaluations per-unit and per-review), an
ANTISYMMETRIC review fixture (approvals on users 0 and 2 only, so an
inverted join or status predicate shifts the per-unit map), and an xy_sum
pin that routes the binary y through the covariate cross term. Ledgered:
the multi-branch k > 1 gate's GtE variant — at k == 1 both branches yield
identical sufficient stats (the provider computes the same x as the
in-source path); the only divergence is that the multi branch does NOT
winsorize y, unobservable while revision_count ships without a winsorize
knob. Design note recorded in ADR §4.6 v3: multi-covariate per-unit y is
NOT winsorized (the single-covariate branch is).

## wave25_holdout_report.json (round 150)

holdouts.report (post-round-58 shape): 28/29 killed by the existing suite
— the roll-split, source dispatch, both comparison gates and the caveat
survived nothing. Ledgered: the sample_capped >= flag (killing it needs a
20k-unit fixture for an informational boolean; the cap MECHANISM itself is
the REPORT_SAMPLE_CAP limit on the unit query, exercised by every report).

## wave26_compute_loop.json (round 159)

compute_experiment_window + _write_snapshots: 15/16. The surviving
first-run mutant was the switchback FIRST-VERSION salt query's limit —
killed by giving the switchback test a second version with a different
hash (the day variant must keep the v1 salt bound: pins both the limit
and the ordering). Ledgered: the top-20 segment org cap (a 21-org fixture
for a capacity constant; the cap mechanism is the sort+slice, exercised by
every segmented compute).

## wave27_promotion.json (round 160)

promotion apply/apply_async/finish_async_apply/approve/reject: 16/16
killed by the existing suite outright — the #47-era savepoint tests, the
apply-race pin and the status-gate pins left nothing alive.

## wave28_holdout_lifecycle.json (round 161)

holdouts create/release/active_groups_for_domain: 12/12 after pinning the
RACE branch's 409 status (the pre-check 409 was pinned; the IntegrityError
branch's status was not — two raise sites, two pins).

## wave29_exposure.json (round 162)

record_exposure + resolve: 4/5 after pinning the stored exposure CONTEXT
verbatim (a truthy context was droppable by an or->and mutant). Ledgered:
the pragma-no-cover 500 on a lost assignment write (the unique constraint
guarantees the row — unreachable defense-in-depth, status constant
included).

## wave30_layers.json (round 163)

layers allocate/create: 14/14 killed by the existing suite (the FOR-UPDATE
slice-overlap races and bound checks all pinned). Config note: the layer
tests live in test_exp_assignment_db.py — a wrong test path makes the
baseline RED and the harness refuses to mutate (correct behavior).

## wave31_schedule_gate.json (round 164)

_check_schedule_preconditions (the #63 gate + guardrail exemption +
high-risk clause): 19/19 after a full gate MATRIX — low+exempt schedules,
low+non-exempt refuses, MEDIUM+exempt STILL refuses (the exemption is
risk AND domain), high-risk 403s a non-admin (status pinned) and
schedules under a platform admin. The 422->423 family dies in the
error-status contract pin (the config must list that test FILE too).

## wave32_decisions.json (round 165)

decisions create/search/hash-exists/guardrail-outcome: 30/31. New arms:
the SAME result hash recorded by repeated looks is legal (the probe must
stay a limit-1 EXISTS — the limit mutant explodes a scalar_one_or_none on
the second identical look), and the guardrail outcome is pinned to EXACTLY
the experiment's own events (a neighbor's pause stays out). Ledgered: the
search default limit constant (50).

## wave34_analysis_run.json (round 169)

AnalysisService.run + _aggregate_metric + latest_look (88 mutants, the
largest single wave): 79/88 over five strengthening passes — the AST
error-status contract extended to this file, the cross-window covariates
fold exactly pinned, the default query_version pinned by a legacy-only
row, the corpus shrink formula hand-spelled, power/exposure boundaries
exactly ON their edges, one-armed insufficiency, n==2 pre-balance
admissibility, degenerate corpus/power entries guarded with a STANDING
prior (unreachable guards otherwise), and the k==1 no-degrade pin. The 9
ledgered: two continuous exact-boundary comparisons (p == 0.001, |z| ==
boundary — measure-zero events), the naive-tzinfo driver branch, the
quantile gate's And (unreachable after #63 + the quantiles validator),
two guard redundancies (a later guard catches the same state), the se/sd
floor guards (welch emits no se on zero variance; the corpus sd is
floored above zero — DISCOVERED and pinned here), and the colon-free
variant-key maxsplit.

## wave35_hooks.json (round 170)

The six domain hooks + the dedup key: 13/13 killed by the existing
integration suite outright. With this, every module in app/experiments/
(services, hooks, worker sweeps) has a dedicated post-rewrite wave on
record — waves 1-35, ~1100 mutants cumulative.

## wave36_its.json (round 179)

its_estimate: 13/16 after pinning the n==3 floor (both operator and
constant, each side) and EXPOSING the dof as an honest readout (n - 4,
pinned — the Sub->Add dof mutant was invisible while dof stayed
internal). Ledgered: the trend dummy's >= at t == t0 (the (t - t0) factor
is zero there, so both comparisons agree), the dof <= 0 guard (the < 3
floors force n >= 6, dof >= 2), and the se == 0 branch (float OLS
residuals are ~1e-15, never exactly zero — integer-input defense).

## wave37_km.json (round 184)

km_curve/km_compare: 21/23 after boundary pins (n0 == 2 admissible,
zero-count event filter, total-death day d == at_risk with the Greenwood
term skipped, refusal after the risk set empties, exact combined-SE pin
se == 0.2 / z == -2, zero-SE degenerate compare). Ledgered: the
zero-count CENSOR filter (a kept zero-censor entry changes no risk set
and emits no curve point) and the greenwood > 0 SE gate (both branches
yield 0.0 at equality). AnalysisService.run re-wave: 79/98 — the four
KM-wiring survivors killed by reshaping the DB fixture (day-0 event
exactly at assigned_at; an early censor BEFORE the control event day so
the risk set shape is visible; arms with DIFFERENT survival so comparing
control-to-control cannot pass; a cancelled-only-event arm pinning that
the block stays off rather than half-attaching None). Round 185 closed the
ITS-service-block mutants: 88/98 after (a) EXACT oracle-via-pure-core
pins — the daily series is fully determined by the fixture, so the
attached block must equal its_estimate() on that series bit-for-bit
(kills the window-arithmetic, empty-arm and value-fallback mutants);
(b) a second primary pinning ITS rides the FIRST primary only; (c) a
rate-kind observational run exercising the numerator/denominator daily
branch with its own oracle; (d) the randomized-run scenario upgraded to
carry a sourced primary, roster and started_at so the gate's CONJUNCTION
is what keeps the block off. Ledgered: the 8 wave-34 equivalents at
shifted lines + the its-attach And (its_estimate never returns None on a
fixed 14/14 non-singular design and every spec metric is in metrics_out
by construction — both operands are tautologies at this call site).

## wave38_update_definition.json (round 187)

update_definition (incl. the round-182 km branch): 11/11. First pass 9/11
— the km knob itself had shipped with NO service-level tests (the KM
wiring tests drove spec directly), and the two survivors exposed a
vacuous assertion: the clear_quantiles strip could drop the ENTIRE spec
(source and measure included) and the histogram-absence check still
passed because the sourceless definition emits nothing. Killed by
asserting the cleared definition keeps source/measure and loses only
quantiles, plus the new km-knob suite (kind gate 422 both directions,
set/strip round-trip, spec preservation).

## wave39_sc.json (round 197)

synthetic_control/_sc_fit/_sc_rmspe/_project_simplex: 31/35 after direct
Duchi-projection hand oracles, the placebo p == 1.0 exact pin on a
perfect fit (any worse-counter or p-formula drift breaks equality or
pushes p past 1), the two-donor boundary, and the constant-matrix
refusal. Ledgered 4: the projection's boundary >= (an equality
coordinate gets zero weight and reproduces the same theta), the
lip <= 0 guard (all-zero donors are already refused as all-constant),
the 1000 -> 1001 iteration budget (converged fixed point), and the
placebo tie >= (measure-zero, the p == 0.001 precedent).
AnalysisService.run re-wave: 106/116 — the SC-wiring survivors killed
(two-donor floor both mutants via the boundary fixture; the per-unit
rate fallback via the approval-rate SC fixture; the attach And via the
constant-matrix scenario pinning block-ABSENT over attached-None); the
10 remaining are the standing ledgered equivalents at shifted lines.

ALSO: this wave caught defect #72 in the loop itself — a `git add -A`
docs commit during the wave's first pass shipped a live mutant
(d9bd2d26, reverted in 6a349d60). Law: never stage or commit a wave's
target files while the wave runs; the harness's dirty-target refusal is
the tripwire that catches it.
