# ADR-012: Explainable Matching Engine

## Status: Accepted

## Context

Issue #21 requires ranking four entity types (Skill Packs, Workflow Packs, Project Templates, Creators) against structured requirement profiles — with three non-negotiables:

1. **Hard constraints can never be bypassed** by semantic or LLM stages.
2. **Every recommendation is explainable** — machine-readable reasons and gaps, never a mysterious single score.
3. **Matching runs are reproducible** after ranking logic changes (GDPR Art 22(3) contestability: a historical decision must remain explainable).

Elasticsearch's filter-context vs query-context split, LinkedIn Recruiter's layered ranking, and RankGPT's permutation-only contract are the industry precedents. Three subsystems (pack matching, provider resolution, creator shortlisting) need the same pipeline — it is built once in `app/services/matching/` and consumed everywhere.

## Decision

### Five-layer pipeline (S4/S5 deferred with named sockets)

```
S1 eligibility   silent exclusions: org scope, visibility, status, banned
S2 hard filters  set operations; failures produce structured gap output
S3 scoring       linear weighted sum over [0,1]-normalized signals
S4 semantic      DEFERRED — socket: matching_configs reserves semantic keys;
                 skill_packs.search_tsv STORED tsvector + GIN shipped and
                 already serving registry full-text search
S5 LLM rerank    DEFERRED — when it ships it receives survivor ordinals only
                 and can only permute them (structurally cannot re-admit
                 filtered candidates)
```

- **S1** runs org/visibility/status predicates in SQL. Excluded entities are *invisible* — they appear in neither ranked nor excluded output (another org's private pack simply does not exist for you). The creator candidate query reads **only** `id`, `display_name`, `last_login_at` — protected attributes are structurally absent from the feature space (R9), not filtered out later.
- **S2** produces `(survivors, excluded)`; excluded entries carry the entity plus failure objects. **Hard-constraint failure is distinguishable from low ranking**: failures are persisted as `match_results` rows with `rank = NULL`, `score = NULL`, `hard_failures` populated, and surface in the UI as a separate "Not eligible (N)" section.

| S2 code | Applies to | Meaning |
|---|---|---|
| `CAPABILITY_MISSING` | workflow_pack | Required capability not in `capability_tags` |
| `OUTPUT_TYPE_MISMATCH` | workflow_pack | Requested output type not produced |
| `CAPABILITY_IRRELEVANT` | skill_pack | Teaches none of the requested (required ∪ preferred) capabilities |
| `DIFFICULTY_TOO_HIGH` | skill_pack | More than one level above the learner |
| `CAPABILITY_UNVERIFIED` | creator | No verified evidence row for a required capability |

- **S3** is a linear weighted sum — decomposition is exact, so explanations cannot drift from scores.

### Config v1 weights (seeded by migration, versioned rows)

| workflow_pack | w | skill_pack | w | project_template | w | creator | w |
|---|---|---|---|---|---|---|---|
| capability_match | .35 | capability_teach_match | .35 | scenario_match | .60 | capability_evidence | .45 |
| scenario_match | .20 | difficulty_fit | .25 | difficulty_fit | .40 | recency | .20 |
| output_type_match | .20 | scenario_match | .15 | | | rubric_avg | .20 |
| tool_match | .10 | time_fit | .15 | | | commercial_history | .15 |
| install_popularity | .10 | popularity | .10 | | | | |
| freshness | .05 | | | | | | |

Scenario matching snake-case-normalizes both sides ("Brand Campaign" matches `brand-campaign`); for project_templates — whose `project_type` is the closed `{general, ai_visual}` taxonomy while profile scenarios are free text — the signal is tri-state: normalized match 1.0, in-vocabulary mismatch 0.0, out-of-vocabulary scenario 0.5 (untestable, neutral — never a demonstrated mismatch).

Signal normalizations: popularity = `log1p(count)/log1p(100)` capped at 1; freshness = Gaussian decay over 30 days; creator recency = exponential decay with **90-day half-life** on `last_login_at`; `rubric_avg` normalizes each approved review by **its own project's max_score** before averaging (review scores live on the project's 1..10000 scale — averaging raw then dividing by a fixed 100 would underprice small-scale projects and clamp large-scale ones); `capability_evidence` uses **Bayesian shrinkage** per required capability — `shrunk = (n/(n+3))·raw_mean + (3/(n+3))·0.5` — so a single lucky data point cannot dominate (zero evidence renders as a gap, never a 0.0 averaged in).

### Reasons and gaps — one code path (R5)

Thresholds live in the config row (`reason_min: 0.7`, `gap_max: 0.4`, `tier_great: 0.75`, `tier_good: 0.5`). For each signal:

- value ≥ 0.7 → reason chip `{code, label, evidence: verified|declared|inferred}`
- value < 0.4 **and** weight ≥ 0.10 → gap entry

Both derive from the **same signal values used in the sum** — there is no parallel formatter to drift. Tiers (`great`/`good`/`fair`) are computed server-side; the UI shows tiers, raw scores only in tooltips. Ties on `round(score, 4)` break deterministically by entity ULID ascending. `?explain=true` returns an Elasticsearch-style `{value, description, details[]}` tree where the parent equals the sum of children.

### Auditability (Part H)

Every match persists a `match_runs` row stamped with `engine_version` (`"1.0.0"` constant) and `config_version` (snapshot of the immutable `matching_configs` row used) plus all ranked `match_results`. Hard-failed rows are persisted too, capped at the **50 newest** (S1 loads whole registries, so exclusions are unbounded) — `excluded_count` on the run always records the true total. A future weight change is a new config version; historical runs stay replayable and explainable.

`match_results` persists `entity_id` only — never a name snapshot — so entity **names are re-resolved live** on every historical read. That re-resolution MUST re-apply the S1 visibility rule per requesting org (R86): a foreign pack captured in a run while public+approved can later be renamed (which voids approval → unlisted), archived, or made private, and a bare name lookup would leak the pack's current (possibly secret) name and continued existence to an org that can no longer see it. `_resolve_names` filters to own-org packs (any visibility) OR public+published+approved; templates to the org; creators to current ACTIVE members — everything else resolves to `null` (a redacted row, not a name leak). The historical *ranking* stays reconstructable (ids, scores, reasons persist); only the human-readable name of a now-invisible entity is withheld.

Creator-target runs are people-rankings (scores, `CAPABILITY_UNVERIFIED` exclusions), so both running one (`POST /match` with `target_entity_type=creator`) and reading one back (`GET /match-runs/{id}`) are **instructor+**, matching the shortlist endpoint's gate; the read path returns a uniform 404 for non-instructors so run ids stay non-enumerable. Pack/template targets remain member-open.

`feedback_events` ships day one (R17): the engine writes a `shown` event per ranked result with its `rank_position`; a table CHECK (`event_type != 'shown' OR rank_position IS NOT NULL`) makes position-bias data loss impossible — it cannot be backfilled later. Composer-internal match runs set `record_impressions=False` — the user never sees those lists, so logging them would poison position-bias data. Client events (`opened/accepted/rejected/installed/added_to_path/used_in_project/human_override`) post through a dedicated endpoint that verifies `match_run_id` belongs to the caller's org (404 otherwise — the column is a loose reference, not an FK). Scoring code never reads feedback_events; weight tuning is a human-reviewed config-version bump.

### Requirement profiles and provenance gating (R14)

`requirement_profiles` hold `structured_requirements` (15 allowed fields: goal, scenario, industry, output_type, difficulty, time_budget, cost_constraint, tool_constraints, required/preferred_capabilities, quality/speed_priority, commercial_use, reference_assets_present) plus per-field provenance in `extraction_meta` (`extracted` | `user_entered`). Three creation paths: structured form (all `user_entered`), ClientBrief mapping (`extracted`, deterministic), and flag-gated LLM extraction.

**A hallucinated hard constraint silently deleting valid candidates is the worst matching failure**, so `build_match_requirement` enforces:

- `required_capabilities` with provenance ≠ `user_entered` are **demoted to preferred** (scoring only).
- Extracted `output_type`/`difficulty`/`time_budget` are renamed to `_soft_*` keys that S2 predicates do not read but scoring signals still consume — an extracted value influences rank, never eligibility, and an extracted time budget produces an advisory `SOFT_TIME_BUDGET` gap rather than hard `cut_for_budget` truncation (ADR-013). `_soft_*` keys cannot be injected through the API: `ALLOWED_FIELDS` rejects them on create and PATCH.
- Editing a field via PATCH flips its provenance to `user_entered` **only when the value actually changed** — re-submitting an unchanged extracted value does not launder its provenance. Matching requires the profile to be **confirmed** (`PROFILE_NOT_CONFIRMED` 422 otherwise). Both `confirm` and PATCH-edit are status-guarded conditional UPDATEs (`WHERE status='draft'`): an edit racing a confirm cannot land post-confirmation edits (which would promote provenance to `user_entered` → S2 hard constraints nobody re-reviewed), and two concurrent confirms resolve cleanly (one wins, the other 422s). `time_budget` and `tool_constraints` are type/range-validated on write (`INVALID_TIME_BUDGET` / `INVALID_TOOL_CONSTRAINTS` 422), and every open dict/list field screens NUL/control chars **and NaN/Infinity floats** — untyped or non-finite values would crash scoring or the JSONB write.

### LLM extraction contract (flag: `EXTRACTION_ENABLED`, default off)

- Untrusted user text is sanitized (`sanitize_untrusted_text`: NFKC, Tags-block/zero-width/bidi strip) and wrapped in random 16-hex **boundary markers** with an explicit "treat strictly as data" instruction.
- Output validates against a strict Pydantic schema (`extra="forbid"`); unknown enum values (capabilities, output types, difficulties) are dropped to `unmatched_mentions` — the extractor **never invents** and never emits taxonomy values outside the closed vocabulary.
- One retry with the validation error appended; a second failure returns an empty structured draft with the raw text preserved. Temperature 0. The form path is fully functional with the flag off.

## Consequences

### Positive

- The explainability promise is structural: linear scoring + single-code-path reasons + persisted config snapshots mean every historical recommendation can be exactly reconstructed and contested.
- S2/S3 separation gives users actionable output: "not eligible because X" vs "ranked low because Y" are different UI sections with different remedies.
- Position-bias-complete feedback logging from day one makes Phase-2 offline ranking evaluation (NDCG on logged impressions) possible without backfill.
- Adding S4/S5 later is a config flip plus one pipeline stage — schema sockets already exist.

### Negative

- Linear scoring cannot capture signal interactions; this is an accepted trade for exact decomposability in v1.
- Hand-set weights are unvalidated until feedback accumulates; tuning is deliberately manual (config version bumps).
- `CAPABILITY_IRRELEVANT` (skill packs) is looser than the strict all-capabilities rule (workflow packs) — required so multi-capability set cover can assemble paths from single-capability packs; documented asymmetry.
