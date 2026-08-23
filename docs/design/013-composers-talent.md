# ADR-013: Solution Composers & Creator Matching

## Status: Accepted

## Context

The matching engine (ADR-012) ranks components; Issue #21's composers assemble them into *solutions*: a learning path draft from a learning goal, a production solution draft from a client brief, and a creator shortlist for a commercial project. The governing principle is **bounded, explainable, human-controlled**: composers propose, humans dispose. Nothing a composer produces has side effects until a human confirms it, and nothing is ever hidden from the draft — every cut, waiver, and gap is a visible row with a reason code (R8: composer trust collapses on silent behavior).

For talent matching, GDPR Art 22 and EEOC adverse-impact concerns require a human decision-maker with real discretion and a fully reconstructable evidence trail.

## Decision

### Draft/confirm — the single side-effect gate

All three composers write only `solution_drafts` rows (`draft_type: learning_path | production_solution`), stamped with `engine_version`, the profile id, and the `match_run_id` they derived from. State machine: `draft → confirmed | discarded`; double-confirm returns 422 `DRAFT_ALREADY_CONFIRMED`. Confirmation (`confirmed_by` — always a human user) materializes real entities and records `materialized_entity_id`. Composition requires a **confirmed** requirement profile (`PROFILE_NOT_CONFIRMED` 422).

### Learning composer (Part E)

Algorithm, in order:

1. **Set cover** — greedy weighted: each round picks the ranked pack covering the most uncovered required+preferred capabilities per estimated minute. Capabilities no pack covers become gaps: `{code: NO_CONTENT_AVAILABLE, capability}`.
2. **Prerequisite expansion** — recursive over `prerequisite_packs` (depth ≤ 5, visited-set cycle detection → 422 `PREREQ_CYCLE`). Prerequisites the learner already completed (SkillProgress COMPLETED on installed pack content) are included as **`waived`** items with evidence — waived is distinct from omitted.
3. **Ordering** — Kahn topological sort on prerequisite edges (prereqs first, score order within levels).
4. **Budget truncation** — when `time_budget` is set, items beyond the budget become **`cut_for_budget`** rows *kept in the payload* (struck through in the UI, never silently dropped). If even required items don't fit: gap `{code: BUDGET_INFEASIBLE, minimum_minutes}`.

Item statuses: `included | waived | cut_for_budget | removed_by_user` (the last via draft PATCH). Every omission is a first-class row with a reason code.

**Confirm** creates a DRAFT LearningPath: packs the org has installed expand into their org-local SKILL items (via `origin_pack_id`); packs **not** installed become `SECTION` placeholder items titled "Install pack: …" — the composer **never auto-installs** (red line, test-enforced: confirming a draft creates zero `SkillPackInstallation` rows).

### Production composer (Part F)

1. Matching engine ranks workflow packs against the production profile.
2. **Chain assembly** — output-type back-matching: start from the highest-ranked pack producing the goal output type, then walk unresolved required asset inputs (image/video/audio/reference_asset — identity coercion only) backwards, chaining the best-ranked producer for each. Max chain length 4. Unresolvable required inputs become placeholders `{input_key, type, reason: no_producer}`; user-suppliable inputs (text/prompt/selection) become informational `{reason: needs_user_value}` placeholders.
3. **Template match** — top project_template or gap `NO_TEMPLATE_AVAILABLE`.
4. **Capability roll-up** — union of `requires_capabilities` across chained packs' latest release manifests, checked against org offerings (ADR-011); unsatisfied → gaps with `NO_ELIGIBLE_PROVIDER`. Never auto-connects.
5. Recommended skill packs from chained manifests attach as optional items (family `skill_pack`, `required: false`).

**Confirm** requires a template in the draft (`NO_TEMPLATE_IN_DRAFT` 422) and creates a real Project through the existing template service, appending workflow-pack provenance so the delivered project stays traceable to its matched components and versions.

### Creator matching (Part G)

**Evidence, not declarations.** `creator_capability_evidence` is a derived decomposition table rebuilt idempotently (delete + rebuild per user) from six platform-verified sources:

| evidence_type | Source | Score |
|---|---|---|
| `skill_completed` | SkillProgress COMPLETED (skill tags → capability) | best_score/100 |
| `badge` | SkillBadge | — |
| `approved_submission` | SubmissionReview APPROVED | score/100 |
| `commercial_project` | BriefApplication ACCEPTED | — |
| `workflow_run` | WorkflowRun COMPLETED (capabilities from snapshot) | — |
| `eval_result` | EvaluationTask COMPLETED | result score |

All carry weight 1.0 (verified); the schema reserves lower weights for future self-declared signals (0.6, retrieval-hint only). Scoring uses Bayesian shrinkage (k=3, prior 0.5) per capability and 90-day-half-life recency (ADR-012).

**Structural privacy (R9)**: the candidate query reads only `id`, `display_name`, `last_login_at`. Protected attributes are absent from the feature space by construction — there is nothing to filter because nothing else is read. Missing evidence for a required capability is a hard S2 exclusion (`CAPABILITY_UNVERIFIED`) shown in the "Not eligible" section with the specific capability named — a remediable gap, not a hidden veto.

**Shortlist-as-offer.** The shortlist endpoint refreshes org evidence, runs the creator pipeline, and returns ranked candidates with per-capability evidence detail. Assignment is strictly:

1. A human instructor **offers**: `creator_assignments` row with `assigned_by` (human FK, never a service account), optional `match_run_id` + `override_reason` (assigning off-shortlist is allowed and recorded). Duplicate → 409 `ASSIGNMENT_EXISTS`.
2. The **creator responds**: accept/decline, self-only (403 otherwise), single response (409 on repeat).

**No auto-assignment code path exists** — there is no API surface or service method that creates an accepted assignment without both the human offer and the creator's response.

### GDPR Art 22 alignment

The decision (assignment) is made by a human with recorded discretion (`assigned_by`, `override_reason`); the full scoring decomposition is persisted (`match_runs` + `match_results` + evidence rows) to answer access/contestation requests; the candidate feature space structurally excludes protected attributes; and shortlist generation alone triggers no legal or similarly significant effect — the offer/accept flow keeps meaningful human involvement on both sides.

## Consequences

### Positive

- One uniform contract across all three composers: draft rows, visible omissions with reason codes, single human confirm gate — users learn the pattern once.
- The training→talent flywheel is native: capability gaps in a shortlist point at the skill packs that teach them; completed work becomes match evidence automatically.
- Provenance chains end-to-end: a delivered project traces to its draft, match run, config version, workflow packs, and release checksums.
- Legal posture is structural, not procedural: no auto-assignment path to audit, no protected attributes to leak.

### Negative

- Greedy set cover and greedy chain assembly are approximations; optimal composition is deferred (acceptable at Phase-1 catalog sizes, and the draft is human-edited anyway).
- Evidence rebuild on every shortlist is O(org members × sources) — fine now, needs incremental rebuild at scale.
- Uninstalled packs materialize as placeholder sections, adding a manual install step — the deliberate cost of the never-auto-install red line.
