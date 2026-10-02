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
