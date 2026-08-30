# PR #22 — Adversarial Review Summary (Issue #21)

**Branch:** `feature/workflow-pack-runtime`
**Scope:** Workflow Pack Runtime, Intelligent Matching Engine, AI Solution Composer
(ADR-010 / 011 / 012 / 013), plus the whole PR's touched surface.
**Status at time of writing:** NOT merged — awaiting explicit approval.
**Regression baseline:** backend `pytest` 1745 passed / 1 skipped / 0 failed;
frontend type-check + Vitest (183) + ESLint all green.

Every defect below was **live-reproduced** (real HTTP against `localhost:8000`
or a real `pytest`) and **guard-proven** (a test that fails when the fix is
reverted, passes when restored) before commit.

---

## 1. How to read this

The review ran as successive adversarial rounds (R34 → R96). Early rounds
(R34–R76) were large multi-dimension sweeps; late rounds (R88c–R96) were
targeted, one-defect-per-commit passes. This document groups the **confirmed,
fixed** defects by **failure class** rather than by round, because the same
class recurred across many subsystems and the class is the reusable lesson.

The last three rounds (R94, R95, R96) found **zero** new defects across 14
distinct attack surfaces — the convergence signal that motivated closing out.

---

## 2. Defect classes (confirmed + fixed)

### 2.1 Untrusted-input 500s (crash → should be 422)

The single largest class. Untrusted values reached the DB or a Pydantic
response model and raised an unhandled 500 with no machine-readable error.

- **Global backstop (R88c):** `dbapi_error_handler` maps input-fault
  SQLSTATEs `22021 / 22P05 / 22P02 / 22001` → 422. This catches the broad
  case, but **asyncpg `DataError` (non-int→INTEGER), `CheckViolationError`
  (jsonb::text width), and Pydantic `ValidationError`/`ResponseValidationError`
  carry no SQLSTATE** and therefore MUST be gated at the schema/import/write
  boundary — they cannot be backstopped.
- **NUL / control chars** in text + JSONB columns: skill/category
  create+update (R88b), certificate path param (R88a), peer-assessment
  feedback + score_breakdown (R87b), portfolio/profile fields (R87c), pack
  reviews / discussion comments / webhook URLs (R88e).
- **NaN / Infinity floats** in every JSONB write field (R73, R78e, R86a/b).
- **bcrypt >72-byte password** on register/login/change/reset (R87a).
- **Deep-nested JSON brick** via provenance / config / limits / import-manifest
  side doors (R51, R53, R54, R56, R66, R92d).
- **Import/install parity:** validate-at-import exactly what would
  crash-at-install — component name/title (R89b), int column bounds
  (R89c/R89f), dangling category refs + non-int max_score/sort_order (R86b),
  non-object manifest → AttributeError (R92e), non-string manifest fields →
  ValidationError in the anon preview (R86e, R87d, R92c).
- **Contract fuzzing:** out-of-range pagination (R25), max-length duplicate
  (R89a), brief-convert rubric max_score int+str / int32 overflow (R92b).

**Lesson:** every field read at a write/serialize boundary must be
type- and range-checked against the *actual column/response constraint*, not
just "looks like JSON". A GREEN browser suite hides these — the API log must
be watched in parallel.

### 2.2 Authorization / tenancy (IDOR, cross-org, existence oracles)

- **Owner-gate on confidential-derived surfaces:** workflow-run inputs/outputs
  leaked to peers (R58), requirement-profile `raw_request` leaked (R58b),
  composer-draft leak (R90a), step-review queue leak (R90d), draft-asset of a
  DRAFT project (R89d), portfolio (R91d), match-run people-rankings reachable
  by students (R50), assignment listing exposed every creator's offers +
  override_reason (R49).
- **Cross-org isolation:** org-scoped idempotency key handed one member's run
  to another (R59); any member could cancel any member's run (R57);
  match-run history name-leak of packs the org can no longer see (R86d);
  `shared-with-me` cross-tenant field leak (R92h).
- **403-vs-404 existence oracle → uniform 404:** match-run / cancel_run /
  portfolio / pack-item (R90e, R91d). Reading *or* writing a foreign id must
  not distinguish "exists but forbidden" from "does not exist".
- **Anon registry info-leak:** `rejection_reason` (moderator's private note),
  `review_status`, `owner_org_id`, `created_by` served to unauthenticated
  callers (R71); `released_by` on anon releases (R72).
- **Privilege escalation:** role-mint gates used `<` instead of `<=`, letting
  an admin re-add a removed student as another admin (R91c); token missing/
  invalid `sub` → 401 not KeyError 500 (R91a).
- **Session revival:** logout / change-password / revoke_session must sweep
  the rotation-predecessor refresh token within the grace window, else a
  revoked session revives (R87e, R91b, R0 logout-mid-rotation).

### 2.3 State machines & integrity

- **Approval-bypass class (the deepest):** publish trusted client-supplied
  `requires_capabilities`, bypassing the install gate (R44); card-void must
  cover *every* anon field + the PENDING review window (R82, R84);
  publish-voids-approval + per-step capability features + non-empty capability
  (R83); credential-in-config `forbid` (R85); create-path approval gate (R79).
- **Points / evidence integrity:** points idempotent per
  `(user, org, reason, reference_id)` — closed leaderboard replay inflation
  (R88d); certificate gate uses exact completion not rounded display pct
  (R88f); no self-grading of exercise attempts + MCQ rejects unusable
  `correct` (R88g/h); no self-review / self-dealing that self-inflates creator
  evidence (R86c); approved-submission evidence dedup per submission, tracks
  final status (R92a, R92f/g); creator `rubric_avg` cross-scale bug (R40).
- **Race conditions with real impact:** unguarded `remove()` double-decrements
  `install_count` (R42); fork-vs-remove resurrects a removed installation
  (R55); confirm_binding-vs-remove orphaned a binding row (R67); stale-read-
  write approval bypass on pack mutation (R70b/c/d).
- **Structurally-dead code paths** silently disabling features:
  evidence sources (R39), template scenario_match (R41), production composer
  output_type filter killing multi-pack chains (R38), learning composer false
  NO_CONTENT gap (R37), WORKFLOW_PACK path items never creatable (R45).

### 2.4 Content-safety & injection

- **Stored-XSS defense:** presigned download forces `attachment` disposition
  for non-safe MIME; upload magic-byte sniff + `dangerous_mimes` blacklist
  (svg/html/js) — verified in R94/R96.
- **LLM prompt injection:** adapter concatenated untrusted step inputs into the
  prompt raw (R48).
- **SSRF:** webhook URL blocked at create *and* re-checked at delivery (DNS
  rebinding), covering private/loopback/link-local/cloud-metadata/IPv4-mapped
  IPv6 — verified R95.
- **ReDoS:** quadratic backtracking in the data-URI regexes (R78d).

### 2.5 Pagination / cache / distribution

- **Unstable OFFSET pagination** on a non-unique ORDER BY reshuffled cached
  id-pages for the whole TTL → skipped/duplicated rows; every sort now chains
  the ULID id as a tiebreak (R75, R75b).
- **Rate-limit bucket sharding:** keying on the concrete path let a
  `{project_id}` mint a fresh bucket per value → no aggregate ceiling on an
  expensive scoring endpoint; now keyed on the route template (R75b).
- **Cache correctness:** canonical-JSON cache keys (no `:`-join collision);
  registry search re-applies access-control filters on cache hit (R36, R71).

---

## 3. Feature completion (in-scope gaps, not bugs)

- **R45:** wired WORKFLOW_PACK path items end to end (enum existed with no
  creation path).
- **R64:** assigner-side withdraw for pending creator offers.
- **R92i:** completed cross-org pack sharing — exposed `sharing_enabled` on the
  write schemas (not a card field, so it never voids approval) and made
  `install_pack` honor a `PackShare` grant for PRIVATE non-owned packs.

---

## 4. Clean rounds (zero confirmed defects)

Explicitly probed and found sound — recorded so future reviewers do not
re-plow them:

- **R94** — pagination/sort/filter injection (whitelisted, no getattr/text
  interpolation); rate-limit bypass (321/321 endpoints limited, route-template
  keyed, not X-Forwarded-For, prod fail-closed); GET side effects (my-progress
  cert/points idempotent via unique constraints); stored-XSS on public
  portfolio (JSON-LD escaped, hrefs filtered, ReactMarkdown has no rehype-raw);
  cross-endpoint enumeration (uniform 404, constant-time login, silent
  forgot-password 204).
- **R95** — S3 presigned URLs (IDOR-gated, attachment disposition, magic-byte
  sniff); webhook SSRF (double-check + rebinding); provider credentials
  (write-only, no read-path echo); provider cross-org offering isolation;
  Alembic (single head, fresh-DB migrate-to-head round-trips).
- **R96** — CORS (fixed allowlist, not wildcard); cache poisoning (filters
  re-applied on hit); log injection (structlog JSON renderer escapes; slug
  regex cleans); timezone/deadline boundaries (all edge datetimes → 422; NUL →
  422; extension is instructor-only and extend-only).

### Known out-of-scope (documented, not fixed in this PR)

- **Schema drift** flagged by `alembic --autogenerate` on baseline tables: 28
  FK `ondelete` mismatches (model `SET NULL` vs DB `NO ACTION`) and 25 NOT NULL
  timestamp drifts. **Unreachable** — there is no user/org hard-delete path
  (org delete is soft ARCHIVED) so `ondelete` never fires, and every drifted
  timestamp has a `server_default=func.now()` so it is never NULL. PR #22's own
  tables are clean (the one exception already has fix-forward migration
  `c1db4f556304`). The team already fixes this class fix-forward
  (`e6f70b112100`, `c1db4f556304`).
- **issue-18 stale-read-write races** (bare check-then-insert under
  concurrency) beyond the concrete money/quota/security overshoots already
  fixed in the R70 class.

---

## 5. Bottom line

- **34 confirmed defects fixed + 3 in-scope feature completions** across the
  late targeted rounds (R37–R93a), on top of the large early sweeps (R34–R36
  and the 60+ findings of R15/R16/R18).
- Every fix is live-reproduced, guard-proven, committed with a
  `Co-Authored-By` trailer, and pushed.
- Three consecutive final rounds over 14 fresh attack surfaces produced no new
  findings — the marginal return on further probing has bottomed out.

**Recommendation:** the PR is in a strong, well-verified state. Remaining
decision is the reviewer's: merge, or run `/metr-finish`.
