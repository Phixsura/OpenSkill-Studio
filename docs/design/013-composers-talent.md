# ADR-013: Solution Composers & Creator Matching

## Status: Accepted

## Context

The matching engine (ADR-012) ranks components; Issue #21's composers assemble them into *solutions*: a learning path draft from a learning goal, a production solution draft from a client brief, and a creator shortlist for a commercial project. The governing principle is **bounded, explainable, human-controlled**: composers propose, humans dispose. Nothing a composer produces has side effects until a human confirms it, and nothing is ever hidden from the draft — every cut, waiver, and gap is a visible row with a reason code (R8: composer trust collapses on silent behavior).

For talent matching, GDPR Art 22 and EEOC adverse-impact concerns require a human decision-maker with real discretion and a fully reconstructable evidence trail.

## Decision

### Draft/confirm — the single side-effect gate

All three composers write only `solution_drafts` rows (`draft_type: learning_path | production_solution`), stamped with `engine_version`, the profile id, and the `match_run_id` they derived from. Composer-internal match runs record **no impression events** (the user never sees those lists — ADR-012). Draft payloads are capped at 256 KB (`DRAFT_TOO_LARGE` 422, mirroring the workflow-definition CHECK). State machine: `draft → confirming → confirmed | draft → discarded` — `confirming` is a TRANSIENT internal claim status (conditional UPDATE, never exposed via the API; reverted to `draft` if materialization fails) that makes concurrent confirms race-safe: exactly one wins, the loser gets 409 `DRAFT_ALREADY_CONFIRMED`. `discard` and `update_draft` use the same conditional-UPDATE pattern (409 on a lost race). Removing an item that a REMAINING item lists as prerequisite is rejected 409 `ITEM_HAS_DEPENDENTS` (guarded by entity id — slugs may collide between an own-org fork and the public original; remove both in one request to proceed). Confirmation (`confirmed_by` — always a human user) materializes real entities and records `materialized_entity_id`. Composition requires a **confirmed** requirement profile (`PROFILE_NOT_CONFIRMED` 422).

### Learning composer (Part E)

Algorithm, in order:

1. **Set cover** — greedy weighted: each round picks the ranked pack covering the most uncovered required+preferred capabilities per estimated minute. Capabilities no pack covers become gaps: `{code: NO_CONTENT_AVAILABLE, capability}`.
2. **Prerequisite expansion** — recursive over `prerequisite_packs` (depth ≤ 5, visited-set cycle detection → 422 `PREREQ_CYCLE`; slugs resolve deterministically — own-org pack first, then oldest by ULID). A pack is **`waived`** only when the learner completed **all** of its installed skills (SkillProgress COMPLETED counted against the pack's non-archived content) — any-one-skill waiving would silently drop whole packs and their capability coverage. Waived is distinct from omitted.
3. **Ordering** — Kahn topological sort on prerequisite edges (prereqs first, score order within levels). If the sort cannot place every pack, the leftover set is a cycle whose members were all pre-selected (the recursive check never enters already-known packs) — this also fails loudly with `PREREQ_CYCLE` rather than silently dropping the cycle.
4. **Budget truncation** — when a *user-entered* `time_budget` is set, items beyond the budget become **`cut_for_budget`** rows *kept in the payload* (struck through in the UI, never silently dropped), and cuts **propagate to dependents** — a dependent is never materialized without its required prerequisite. An LLM-*extracted* budget is advisory only (`SOFT_TIME_BUDGET` gap, no cuts — ADR-012 R14). If even required items don't fit: gap `{code: BUDGET_INFEASIBLE, minimum_minutes}`.

Item statuses: `included | waived | cut_for_budget | removed_by_user` (the last via draft PATCH). Every omission is a first-class row with a reason code.

**Confirm** creates a DRAFT LearningPath: packs the org has installed expand into their org-local SKILL items (via `origin_pack_id`); packs **not** installed become `SECTION` placeholder items titled "Install pack: …" — the composer **never auto-installs** (red line, test-enforced: confirming a draft creates zero `SkillPackInstallation` rows).

### Production composer (Part F)

1. Matching engine ranks workflow packs against the production profile.
2. **Chain assembly** — output-type back-matching: start from the highest-ranked pack producing the goal output type, then walk unresolved required asset inputs (image/video/audio/reference_asset — identity coercion only) backwards, chaining the best-ranked producer for each. Max chain length 4; inputs still unresolved when the cap is hit surface as `{reason: chain_length_cap}` placeholders — never silently dropped. Unresolvable required inputs become placeholders `{input_key, type, reason: no_producer}`; user-suppliable inputs (text/prompt/selection) become informational `{reason: needs_user_value}` placeholders.
3. **Template match** — top project_template or gap `NO_TEMPLATE_AVAILABLE`.
4. **Capability roll-up** — union of `requires_capabilities` across chained packs' latest release manifests, checked against org offerings (ADR-011); unsatisfied → gaps with `NO_ELIGIBLE_PROVIDER`. Never auto-connects.
5. Recommended skill packs from chained manifests attach as optional items (family `skill_pack`, `required: false`).

**Confirm** requires a template in the draft (`NO_TEMPLATE_IN_DRAFT` 422) and creates a real Project through the existing template service, appending workflow-pack provenance so the delivered project stays traceable to its matched components and versions.

### Creator matching (Part G)

**Evidence, not declarations.** `creator_capability_evidence` is a derived decomposition table rebuilt idempotently (delete + rebuild per user) from six platform-verified sources:

| evidence_type | Source | Capability derivation | Score (stored 0–100) |
|---|---|---|---|
| `skill_completed` | SkillProgress COMPLETED | skill tags → capability (snake-cased exact match) | best_score |
| `badge` | SkillBadge | skill tags → capability | — |
| `approved_submission` | SubmissionReview APPROVED | project resolution (below) | review score |
| `commercial_project` | BriefApplication ACCEPTED | brief.project_type, snake-cased exact match | — |
| `workflow_run` | WorkflowRun COMPLETED | provider_action capabilities from snapshot | — |
| `eval_result` | EvaluationTask COMPLETED | project resolution (below) | result score |

**Project → capability resolution** (sources 3/6): `project.project_type` is a coarse UX taxonomy (`{general, ai_visual}`) that never intersects capability keys, so a submission's capability resolves through, in order: (1) the project's own `project_type` (future-proof), (2) the linked client brief's free-text `project_type` when it snake-cases to an exact capability key, (3) the confirmed production-solution draft that materialized the project (`payload.required_capabilities` — the platform-verified rollup from workflow release manifests). All matching capabilities are attested, deduplicated per project; both lookups are batched.

Scores are stored on a single 0–100 scale and normalized to 0–1 exactly once, at scoring time — a mixed-scale store double-divides and inverts rankings.

All carry weight 1.0 (verified); the schema reserves lower weights for future self-declared signals (0.6, retrieval-hint only). Scoring uses Bayesian shrinkage (k=3, prior 0.5) per capability and 90-day-half-life recency (ADR-012).

**Structural privacy (R9)**: the candidate query reads only `id`, `display_name`, `last_login_at`. Protected attributes are absent from the feature space by construction — there is nothing to filter because nothing else is read. Missing evidence for a required capability is a hard S2 exclusion (`CAPABILITY_UNVERIFIED`) shown in the "Not eligible" section with the specific capability named — a remediable gap, not a hidden veto.

**Shortlist-as-offer.** The shortlist endpoint refreshes org evidence (skipped when refreshed within the last 10 minutes — a staleness gate, not a rebuild-per-GET), runs the creator pipeline, and returns ranked candidates with per-capability evidence detail. Evidence scores are stored on a 0–100 scale end to end. Assignment is strictly:

1. A human instructor **offers**: `creator_assignments` row with `assigned_by` (human FK with SET NULL — the column is nullable so deleting the assigning user preserves the assignment record), optional `match_run_id` + `override_reason` (assigning off-shortlist is allowed and recorded). Duplicate → 409 `ASSIGNMENT_EXISTS`. Offers against archived projects are rejected 409 `PROJECT_NOT_AVAILABLE` (a dead offer could never be accepted, and the unique index would block any future re-offer).
2. The **creator responds**: accept/decline, self-only (403 otherwise). The response is a conditional UPDATE guarded on `status='offered'` — a repeat or concurrent response loses cleanly with 409 `ASSIGNMENT_ALREADY_RESPONDED`; accepting an offer whose project was archived mid-offer is rejected 409 `PROJECT_NOT_AVAILABLE`.
3. The **assigner withdraws** a still-pending offer (instructor+, `POST .../creator-assignments/{id}/withdraw`): a conditional UPDATE guarded on `status='offered'` sets `withdrawn` (loser/already-responded → 409 `ASSIGNMENT_ALREADY_RESPONDED`). Without this, a mis-directed offer was irrevocable — `ASSIGNMENT_EXISTS` blocks any re-offer until the creator happens to decline. `offer_assignment` supersedes a prior `declined`/`withdrawn` row in place, so a withdrawn creator can be re-offered.

Assignment listing is role-scoped: instructors+ see the org's assignments; every other member sees **only their own** — an unscoped list would expose every creator's offer/decline history and the assigner's `override_reason` (recorded discretion) to any student.

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
