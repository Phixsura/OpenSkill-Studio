# ADR-016: AI Ecosystem Intelligence, Benchmark Lab & Component Lifecycle Automation

- **Status**: Accepted
- **Issue**: #35
- **Depends on**: ADR-011 (capability tags / provider offerings), ADR-012 (matching engine),
  ADR-014 (control plane, `ProviderCostRate`, outbox), ADR-015 (talent capability ontology,
  workforce intelligence)

## 1. Problem

The platform can package, run, monetize, teach and match _existing_ AI capabilities, but it
depends on humans to notice that a new model appeared, a price changed, a tool was deprecated,
or a Skill/Workflow Pack now depends on something outdated. We need a continuously updating
intelligence layer with a strict safety posture: **never silently publish unverified external
content, never auto-migrate production workflows, never execute untrusted code.**

Core loop: Discover → Normalize → Verify → Benchmark → Map to Capabilities → Compare → Draft →
Human Review → Publish/Rollout → Observe Production → Deprecate/Replace → Feed back.

## 2. Package layout

Follows the `app/talent/` / `app/controlplane/` vertical-package precedent:

```
apps/api/app/ecosystem/
  __init__.py
  facade.py            # ONLY entry point for product code (registry/matching/workforce)
  security.py          # SSRF guard, bounded JSON parsing, URL validation, injection hygiene
  models/              # sources, observations, catalog, mapping, pricing, benchmark,
                       # graph, impact, replacement, drafts, lifecycle, rollout, watchlist
  schemas/             # Pydantic request/response
  services/            # one service per bounded context
  api/                 # routers aggregated into ecosystem_router
  worker.py            # outbox topic handlers (eco.*)
```

Migrations: `eco01_*` … chained after `talent15a00015`. All tables prefixed `eco_`.

## 3. Data model

All PKs are 26-char ULIDs (`ulid_pk()`); all timestamps `DateTime(timezone=True)`.
String status/type columns are validated at the service layer (extensible, no DB enums —
same rationale as `capability_tags`).

### 3.1 Part A — `eco_sources` (EcosystemSource)

| column                         | type                   | notes                                                                                                                                                |
| ------------------------------ | ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| id                             | str(26) PK             |                                                                                                                                                      |
| name                           | str(200)               | unique                                                                                                                                               |
| source_type                    | str(40)                | `provider_api` \| `model_docs_feed` \| `github_repo` \| `huggingface` \| `comfyui_repo` \| `pricing_feed` \| `internal_research` \| `manual_analyst` |
| trust_level                    | str(20)                | `official` \| `verified_partner` \| `community` \| `unverified` \| `internal`                                                                        |
| base_url                       | str(2000) nullable     | validated by SSRF guard at write time; `manual_analyst` needs none                                                                                   |
| adapter_key                    | str(64)                | parser/adapter implementation key                                                                                                                    |
| parser_version                 | str(20)                | current parser version, stamped onto observations                                                                                                    |
| config                         | JSONB `{}`             | non-sensitive adapter config; credential **field names only**, never values                                                                          |
| sync_interval_minutes          | int, default 1440      |                                                                                                                                                      |
| rate_limit_per_hour            | int, default 60        |                                                                                                                                                      |
| max_response_bytes             | int, default 5_242_880 | hard response-size cap                                                                                                                               |
| timeout_seconds                | int, default 30        |                                                                                                                                                      |
| etag                           | str(500) nullable      | conditional GET state                                                                                                                                |
| last_modified                  | str(100) nullable      | conditional GET state                                                                                                                                |
| status                         | str(20)                | `active` \| `paused` \| `error` \| `archived`                                                                                                        |
| last_sync_at / last_success_at | ts nullable            |                                                                                                                                                      |
| consecutive_failures           | int default 0          | circuit breaker: pause at 5                                                                                                                          |
| robots_compliant               | bool default true      | operator attestation; sync refuses if false                                                                                                          |
| created_by                     | FK users SET NULL      |                                                                                                                                                      |
| created_at / updated_at        | ts                     |                                                                                                                                                      |

Indexes: `ix_eco_sources_status(status)`, `ix_eco_sources_type(source_type)`.

`eco_source_sync_runs` (SourceSyncRun): id, source_id FK CASCADE, started_at, finished_at,
status (`running|success|not_modified|failed|skipped`), http_status int nullable,
bytes_fetched int, observations_created int, changes_detected int, error text nullable,
parser_version. Index `(source_id, started_at)`.

### 3.2 Part B — `eco_observations` (append-only ledger)

| column                    | type                    | notes                                                                                                                                                                                                                                        |
| ------------------------- | ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| id                        | PK                      |                                                                                                                                                                                                                                              |
| source_id                 | FK eco_sources RESTRICT | provenance must survive                                                                                                                                                                                                                      |
| sync_run_id               | FK nullable SET NULL    |                                                                                                                                                                                                                                              |
| event_type                | str(40)                 | `model_released` \| `model_deprecated` \| `price_changed` \| `api_changed` \| `limits_changed` \| `region_changed` \| `license_changed` \| `security_advisory` \| `workflow_dependency_changed` \| `release_published` \| `catalog_snapshot` |
| entity_kind               | str(30) nullable        | hint: `provider                                                                                                                                                                                                                              | tool | model | model_version | workflow | agent | node_package` |
| external_ref              | str(500) nullable       | source-native identifier                                                                                                                                                                                                                     |
| canonical_entity_id       | str(26) nullable        | set after resolution (kind in `canonical_entity_kind`)                                                                                                                                                                                       |
| canonical_entity_kind     | str(30) nullable        |                                                                                                                                                                                                                                              |
| observed_at               | ts                      | when we saw it                                                                                                                                                                                                                               |
| effective_at              | ts nullable             | when the change takes effect (sunsets in the future)                                                                                                                                                                                         |
| raw_hash                  | str(64)                 | SHA-256 of raw payload — idempotency key with source                                                                                                                                                                                         |
| normalized                | JSONB                   | strict-schema extraction output                                                                                                                                                                                                              |
| parser_version            | str(20)                 |                                                                                                                                                                                                                                              |
| confidence                | Numeric(4,3)            | 0..1                                                                                                                                                                                                                                         |
| provenance_url            | str(2000) nullable      |                                                                                                                                                                                                                                              |
| extraction_method         | str(20)                 | `structured` \| `llm` \| `manual` — LLM-extracted facts are flagged                                                                                                                                                                          |
| human_verified            | bool default false      |                                                                                                                                                                                                                                              |
| verified_by / verified_at | nullable                |                                                                                                                                                                                                                                              |
| superseded_by_id          | FK self nullable        | corrections chain — **never UPDATE normalized**                                                                                                                                                                                              |
| created_at                | ts                      |                                                                                                                                                                                                                                              |

Constraint: `uq_eco_obs_idem UNIQUE(source_id, raw_hash, event_type)` — re-ingesting an
unchanged payload is a no-op. Indexes on `(event_type, observed_at)`,
`(canonical_entity_kind, canonical_entity_id)`. **No UPDATE path exists in the service for
`normalized`/`raw_hash`; corrections append a new row with `superseded_by_id` back-link.**

`eco_change_events` (typed change detection, Part B):
id, observation_id FK, change_type (`price|limits|license|api|model_version|lifecycle|region|security`),
field str(100), old_value JSONB nullable, new_value JSONB nullable,
severity (`info|update_available|degraded|breaking|security_critical|sunset_risk`),
entity_kind, canonical_entity_id nullable, detected_at, acknowledged bool default false,
acknowledged_by nullable. Index `(change_type, detected_at)`, `(severity, acknowledged)`.

### 3.3 Part C — canonical catalog

Seven entity tables share a column core (id, canonical_name, slug unique-per-table,
description, lifecycle_status, external_ids JSONB, aliases JSONB list, metadata JSONB,
first_observed_at, created_at, updated_at):

- `eco_ai_providers` — + website, vendor_status (`operational|degraded|outage|unknown`)
- `eco_ai_tools` — + provider_id FK nullable, tool_type (`api|desktop|node|cli|service`)
- `eco_ai_models` — + provider_id FK, modality inputs/outputs JSONB, family str
- `eco_model_versions` — + model_id FK CASCADE, version str(100), released_at,
  deprecated_at, sunset_at, api_identifier str(200), context/limits JSONB,
  license str(100), commercial_use_allowed bool nullable,
  `uq_eco_model_version UNIQUE(model_id, version)`
- `eco_external_workflows` — + source_repo str, workflow_format (`comfyui|other`),
  node_types JSONB list, graph_hash str(64)
- `eco_external_agents` — + agent_framework str
- `eco_node_packages` — + package_name, repo_url, latest_version, security_flags JSONB

`lifecycle_status` (Part L): `discovered | under_review | verified | recommended | watch |
deprecated | blocked | retired`. Transitions validated by `LifecycleService` (§3.9).

`eco_entity_aliases`: id, entity_kind, entity_id, alias str(300), alias_type
(`official_id|slug|name|api_identifier`), source_id FK nullable,
`UNIQUE(entity_kind, alias, alias_type)`.

`eco_resolution_candidates` (entity-resolution queue): id, observation_id FK,
entity_kind, candidate_entity_id nullable (null ⇒ proposes new entity),
match_method (`official_id|alias|similarity|llm_suggested`), confidence Numeric(4,3),
proposed_payload JSONB, status (`pending|auto_merged|confirmed|rejected`),
decided_by/decided_at nullable, created_at.
**Rule: `confidence >= 0.9` AND method in (`official_id`,`alias`) may auto-merge; anything
lower or LLM-suggested requires human confirmation** (`ECO_MERGE_CONFIRMATION_REQUIRED`).

### 3.4 Part D — `eco_capability_mappings`

id, entity_kind, entity_id, capability_key str(64) (loose FK to `capability_tags.key`,
same pattern as `ProviderModelOffering`), evidence_level
(`vendor_claimed | platform_observed | benchmark_verified | production_verified | human_verified`),
io_spec JSONB (`{"inputs":[{"type":"image","formats":["png"],"max_mp":25}],
"outputs":[{"type":"video","max_seconds":10}],"constraints":{...}}`),
confidence, source_observation_id nullable, verified_by/at nullable, created_at, updated_at.
`UNIQUE(entity_kind, entity_id, capability_key)` — evidence level is _upgraded in place_,
history recoverable from observations.
Evidence order is total: vendor_claimed < platform_observed < benchmark_verified <
production_verified < human_verified; downgrades require `force=true` + admin.

### 3.5 Part E — pricing / limits / availability

`eco_price_observations`: id, observation_id FK, entity_kind, entity_id, region str(30)
nullable, unit (`token_input|token_output|image|megapixel|video_second|minute|request|
subscription_month|volume_tier`), price Numeric(14,6), currency str(3) default USD,
tier JSONB nullable, effective_at, observed_at, reconciliation_status
(`unreviewed|under_review|approved|rejected|superseded`), reconciled_by/at nullable,
approved_cost_rate_id str(26) nullable (loose ref to `cp_provider_cost_rates.id`), created_at.
Index `(entity_kind, entity_id, observed_at)`, `(reconciliation_status)`.
**Approving creates a NEW `ProviderCostRate` via the control-plane facade — this service
never mutates billing tables directly and never auto-approves** (`ECO_PRICING_NOT_APPROVED`).

`eco_availability_records`: id, entity_kind, entity_id, region nullable,
record_type (`rate_limit|concurrency|queue|latency|status|deprecation|sunset`),
value JSONB, observed_at, source_observation_id nullable, created_at.

### 3.6 Part F — Benchmark Lab

`eco_benchmark_suites`: id, key str(64) unique, name, description, family
(one of the 10 AI-visual families, e.g. `ecommerce_hero`, `product_consistency`,
`character_consistency`, `chinese_text_render`, `storyboard_adherence`, `i2v_motion`,
`temporal_consistency`, `commercial_ad_15s`, `background_replacement`, `multimodal_qa`),
capability_key, rubric JSONB (dimension list with weights & anchors), human_review_policy
JSONB (`{"required": true, "blind": true, "min_reviewers": 2}`), automated_metrics JSONB
list, budget_usd_cap Numeric(10,2), repeat_count int default 3, status
(`draft|active|archived`), created_by, created_at, updated_at.

`eco_benchmark_cases`: id, suite_id FK CASCADE, name, prompt text, reference_assets JSONB
list (asset refs, not blobs), constraints JSONB, weight Numeric(4,3) default 1, sort_order.

`eco_benchmark_runs`: id, suite_id FK, status (`queued|running|completed|failed|cancelled`),
target JSONB (`{"entity_kind":"model_version","entity_id":...,"offering_id":...,
"provider_key":...}`), environment_snapshot JSONB (adapter versions, config), seed_settings
JSONB, budget_usd_cap, total_cost_usd Numeric(12,6) default 0, started_at, finished_at,
triggered_by, created_at. Index `(suite_id, created_at)`.

`eco_benchmark_results` (one per run×case×repeat): id, run_id FK CASCADE, case_id FK,
repeat_index int, input_snapshot JSONB, output_assets JSONB list, latency_ms int nullable,
usage JSONB, cost_usd Numeric(12,6), retries int default 0, failed bool default false,
error text nullable, automated_scores JSONB (`{"text_accuracy":0.91,...}`), created_at.
`UNIQUE(run_id, case_id, repeat_index)`.

**Dimensional scoring — never collapsed:** run aggregation produces
`dimension_scores JSONB` on the run: `{"quality":..., "brief_adherence":...,
"consistency":..., "text_accuracy":..., "motion_quality":..., "temporal_quality":...,
"speed_p50_ms":..., "cost_per_case_usd":..., "reliability":..., "commercial_readiness":...}`.
There is deliberately **no** `overall_score` column.

Blind review (`eco_benchmark_reviews`): id, review_batch_id, run_id FK, result_id FK,
reviewer_id FK users, **alias_label str(8)** (e.g. "Model A") — reviewer-facing identity;
scores JSONB per rubric dimension, comment, submitted_at nullable, created_at.
`UNIQUE(result_id, reviewer_id)`. The API **never returns provider/model identity for a
review batch until every reviewer in the batch has `submitted_at` set**
(`ECO_BLIND_REVIEW_SEALED`). Alias assignment is a random permutation stored server-side
in `eco_review_batches.alias_map JSONB` and excluded from all reviewer-facing responses.

### 3.7 Part G — production telemetry evidence

`eco_telemetry_snapshots`: id, entity_kind, entity_id, window_start, window_end,
org_id nullable (**null ⇒ cross-tenant aggregate**), sample_size int,
metrics JSONB (`{"success_rate":..., "retry_rate":..., "latency_p50_ms":...,
"latency_p95_ms":..., "effective_cost_usd_avg":..., "human_approval_rate":...,
"revision_rate":..., "client_acceptance_rate":..., "error_distribution":{...}}`),
created_at. `UNIQUE(entity_kind, entity_id, org_id, window_start, window_end)`.

Privacy rules (hard, service-enforced):

- Cross-tenant rows (`org_id IS NULL`) are only written when `sample_size >= 20` **and**
  at least 3 distinct orgs contributed (`ECO_TELEMETRY_THRESHOLD`).
- Org-scoped rows are only readable by that org's members or platform admin.
- Divergence detection compares benchmark `dimension_scores` vs telemetry metrics and, when
  |z| > 2 on a comparable dimension, creates a `eco_change_events` row with
  `change_type="lifecycle"`, `severity="degraded"`, `field="benchmark_production_divergence"`
  — **it never mutates rankings.**

### 3.8 Part H/I — dependency graph & impact

`eco_dependency_edges`: id, from_kind str(40), from_id str(26), to_kind, to_id,
constraint_type (`requires_model_version|requires_capability|requires_api_version|
requires_node_package|requires_license|requires_runtime_feature|uses`),
constraint_spec JSONB (`{"version_range":">=2.0 <3.0"}`), org_id nullable (private
component edges are org-scoped), created_at.
`UNIQUE(from_kind, from_id, to_kind, to_id, constraint_type)`,
indexes on `(to_kind, to_id)` and `(from_kind, from_id)`.
Node kinds span both worlds: `provider|model|model_version|tool|node_package|
workflow_pack|workflow_pack_release|skill_pack|project_template|learning_path|
assessment|capability|commercial_project|cohort`.

Impact analysis (Part I) is computed, stored:
`eco_impact_analyses`: id, change_event_id FK, root_kind, root_id, classification
(`informational|update_available|degraded|breaking|security_critical|sunset_risk`),
summary JSONB (counts per kind), deadline_at nullable (from sunset), computed_at, status
(`open|acknowledged|resolved`).
`eco_impact_items`: id, analysis_id FK CASCADE, node_kind, node_id, depth int, path JSONB
(list of edge ids), active_usage JSONB (`{"active_cohorts":3,"running_projects":1}`),
recommended_action str(40) (`none|review|update|migrate|block`).
Traversal: BFS from root over reversed edges, `max_depth=6`, visited-set for **cycle
safety**, cap 5 000 nodes (`ECO_IMPACT_TOO_LARGE` past cap — analysis stored truncated
with `summary.truncated=true`).

### 3.9 Part J/L — replacement & lifecycle

`eco_replacement_edges`: id, from_kind, from_id, to_kind, to_id, edge_type
(`supersedes|recommended_replacement|compatible_alternative|migration_required`),
rationale text, created_by, created_at. `UNIQUE(from_kind,from_id,to_kind,to_id,edge_type)`.

`eco_replacement_candidates`: id, deprecated_kind, deprecated_id, candidate_kind,
candidate_id, score Numeric(5,4), hard_compatible bool, hard_failures JSONB list
(each `{"code":"IO_TYPE_MISMATCH","detail":...}`), score_breakdown JSONB (per-factor:
io_compatibility, capability_coverage, benchmark, production_reliability, cost, latency,
license, availability, binding_compat, migration_effort — weights sum to 1.0),
explanation JSONB (human-readable factor lines, mirrors ADR-012 explain contract),
status (`proposed|under_review|approved|rejected`), decided_by/at, created_at.
**Hard rule: `hard_compatible=false` candidates are returned in a separate
`incompatible` list, never interleaved into the ranked list, regardless of score**
(mirrors matching-engine constraint/scoring split).
Scoring reuses `app/services/matching` primitives via its public functions; weights
configurable per request, defaults:
`{"io":0.2,"capability":0.15,"benchmark":0.15,"reliability":0.15,"cost":0.1,
"latency":0.05,"license":0.05,"availability":0.05,"bindings":0.05,"migration":0.05}`.

`eco_lifecycle_transitions`: id, entity_kind, entity_id, from_status, to_status,
reason (`official_sunset|security_advisory|license_incompatibility|benchmark_regression|
production_failure_threshold|manual_decision`), note, actor_id, created_at.
Valid transitions (service-enforced):

```
discovered → under_review | blocked
under_review → verified | blocked | discovered
verified → recommended | watch | deprecated | blocked
recommended → watch | deprecated | blocked
watch → recommended | deprecated | blocked
deprecated → retired | watch
blocked → under_review | retired
retired → (terminal)
```

Deprecation **never deletes** anything; historical evidence rows are untouched.

### 3.10 Part K — component drafts

`eco_component_drafts`: id, draft_type (`workflow_pack|skill_pack_update|project_template|
capability_mapping|provider_offering|benchmark_suite`), title, payload JSONB (the draft
artifact body), source_kind/source_id (provenance entity), source_observation_ids JSONB
list, validation JSONB (`{"valid":true,"errors":[]}`), status
(`draft|in_review|approved|rejected|published`), org_id nullable, created_by,
reviewed_by/at, published_ref str(26) nullable (id of the created product entity),
created_at, updated_at.
**Publishing requires status=approved and an explicit second call by a human with author/
admin rights; the service refuses `draft→published` in one step**
(`ECO_DRAFT_NOT_APPROVED`). Draft generation never downloads or executes external code;
ComfyUI drafts reuse the existing `comfyui_import` parser (declarative parse only).

### 3.11 Part M — controlled rollout

`eco_rollout_plans`: id, replacement_candidate_id FK, scope_type
(`benchmark_only|internal_org|selected_cohort|selected_installation`), scope_ref str(26)
nullable, baseline JSONB (metrics snapshot of incumbent), candidate_metrics JSONB,
comparison JSONB (per-dimension deltas), status
(`draft|running|evaluating|promoted|rejected|aborted`), decided_by/at, note, created_at,
updated_at. Promote/reject are explicit POST actions; **no automatic promotion path
exists.** Promotion writes an `eco_replacement_edges(recommended_replacement)` row and a
lifecycle transition; it never rewrites existing `WorkflowStepBinding`s.

### 3.12 Part P — watchlists

`eco_watchlists`: id, owner_id FK users, org_id nullable, name, created_at.
`eco_watch_items`: id, watchlist_id FK CASCADE, target_kind (`provider|model|tool|
workflow|github_repo|capability|component`), target_id str(26) nullable, target_ref
str(300) nullable (for external refs like repo URLs), created_at.
`UNIQUE(watchlist_id, target_kind, coalesce(target_id,''), coalesce(target_ref,''))`
implemented as a service-level check + partial unique indexes.

## 4. Services & algorithms

| service                   | responsibility                                                                                                                                                                                                      |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `sources.py`              | CRUD, robots/ToS attestation, pause/resume, circuit breaker                                                                                                                                                         |
| `sync.py`                 | orchestrated fetch: SSRF guard → conditional GET (ETag/Last-Modified) → size-capped stream → adapter parse → observations + idempotency; retry w/ exponential backoff (3 tries, 2^n s), per-source rate-limit check |
| `adapters.py`             | pluggable parsers keyed by `adapter_key` (json_catalog, github_releases, huggingface, comfyui_repo, pricing_json, manual). Each returns `list[NormalizedObservation]`; parser_version stamped                       |
| `change_detection.py`     | diff normalized payload vs latest prior observation for the same (source, external_ref, event_type family); emits typed `eco_change_events` for price/limits/license/api/version/lifecycle/region/security          |
| `catalog.py`              | canonical CRUD, alias registry                                                                                                                                                                                      |
| `resolution.py`           | official-id → alias → similarity (trigram over names+aliases) → optional LLM suggestion; auto-merge policy per §3.3                                                                                                 |
| `capability_mapping.py`   | mapping CRUD + evidence-level upgrade rules                                                                                                                                                                         |
| `pricing.py`              | price observations, reconciliation workflow, approval → control-plane facade call                                                                                                                                   |
| `benchmark.py`            | suite/case CRUD, run execution via provider adapters (mock in tests), budget cap enforcement (run aborts at cap with status failed + `ECO_BUDGET_EXCEEDED`), dimension aggregation                                  |
| `blind_review.py`         | batch creation, alias permutation, sealed identity, submit + reveal                                                                                                                                                 |
| `telemetry.py`            | aggregates WorkflowRun/StepRun + evaluation + client delivery into snapshots; privacy thresholds; divergence detection                                                                                              |
| `graph.py`                | dependency edge CRUD + graph queries; syncs edges from workflow pack releases (`requires_capabilities`, offerings)                                                                                                  |
| `impact.py`               | BFS impact computation §3.8                                                                                                                                                                                         |
| `replacement.py`          | candidate generation + scoring §3.9                                                                                                                                                                                 |
| `drafts.py`               | draft generation/validation/review/publish §3.10                                                                                                                                                                    |
| `lifecycle.py`            | transition state machine §3.9                                                                                                                                                                                       |
| `rollout.py`              | plan lifecycle §3.11                                                                                                                                                                                                |
| `watchlists.py`           | watch CRUD + matching changes → notifications                                                                                                                                                                       |
| `dashboard.py`            | workspace aggregates (Part P)                                                                                                                                                                                       |
| `intelligence_signals.py` | Part N/O: approved-signal projection for registry/matching + workforce gap detection                                                                                                                                |

### 4.1 Security (`security.py`, Part Q)

- `validate_external_url(url)`: https/http only; hostname resolves; rejects literal IPs in
  private/reserved ranges (RFC1918, loopback, link-local, ULA, metadata 169.254.169.254),
  rejects userinfo, non-standard ports (allow 80/443/8443), `.internal`/`.local` TLDs.
  Raises `EcoSecurityError("ECO_SSRF_BLOCKED")`.
- `bounded_json_loads(raw, max_bytes=5MB, max_depth=20, max_string=100_000,
max_keys=10_000)`: pre-checks size; custom depth/width walk post-parse; raises
  `ECO_PAYLOAD_TOO_LARGE` / `ECO_PAYLOAD_TOO_DEEP`.
- `sanitize_text(s, max_len)`: strips NUL/control chars (mirrors R87 lesson), enforces len.
- LLM extraction (when enabled) uses a fixed instruction frame; the fetched text is passed
  as fenced _data_; output must validate against a strict Pydantic schema; any tool-call or
  instruction-like output is discarded; result rows always get
  `extraction_method="llm"` + `confidence<=0.7` and require human verification before the
  fact can drive any downstream automation.
- Archive handling (ComfyUI repos): entries validated against path traversal (`..`,
  absolute paths), per-file and total size caps; only `.json` workflow files parsed.
- **No code execution / no dependency installation anywhere in this package.**

### 4.2 Worker topics (outbox reuse, Part R)

`eco.sync_source {source_id}`, `eco.run_benchmark {run_id}`,
`eco.compute_impact {change_event_id}`, `eco.telemetry_window {window_start,window_end}`,
`eco.generate_candidates {entity_kind,entity_id}`. Handlers registered in
`app/ecosystem/worker.py`, consumed by the existing control-plane worker loop pattern
(FOR UPDATE SKIP LOCKED). All handlers idempotent (keyed on natural ids). Tests drive
handlers inline (established pattern).

## 5. APIs (Part R) — all under `/api/v1/ecosystem/*`

Read = authenticated; org-scoped reads gated by membership; **all mutations of platform
intelligence = platform admin** (`UserRole.ADMIN`), analyst mutations noted below. Errors
use the standard envelope with machine codes listed in §7.

```
POST/GET/PATCH        /sources, /sources/{id}         + POST /sources/{id}/sync
GET                   /sources/{id}/sync-runs
GET                   /observations                    (filters: source, event_type, entity)
POST                  /observations                    (manual analyst input; admin)
POST                  /observations/{id}/verify
GET                   /changes                         (+ POST /changes/{id}/acknowledge)
GET/POST/PATCH        /catalog/{kind}, /catalog/{kind}/{id}   kind ∈ providers|tools|models|
                                                        model-versions|workflows|agents|node-packages
GET                   /resolution-candidates  + POST /resolution-candidates/{id}/confirm|reject
GET/POST/PATCH        /capability-mappings
GET                   /pricing/observations   + POST /pricing/observations/{id}/reconcile
GET                   /availability
CRUD                  /benchmark/suites, /benchmark/suites/{id}/cases
POST/GET              /benchmark/runs (+ /runs/{id}, /runs/{id}/results, /runs/compare?ids=)
POST                  /benchmark/review-batches, GET /review-batches/{id}/assignments,
                      POST /reviews/{id}/submit, POST /review-batches/{id}/reveal
GET                   /telemetry/snapshots
GET/POST/DELETE       /graph/edges, GET /graph/node/{kind}/{id}
POST/GET              /impact/analyses (+ /impact/analyses/{id})
POST/GET              /replacements/candidates (+ confirm/reject)
POST                  /lifecycle/{kind}/{id}/transition
CRUD                  /drafts (+ POST /drafts/{id}/submit-review|approve|reject|publish)
CRUD                  /rollouts (+ POST /rollouts/{id}/start|promote|reject|abort)
CRUD                  /watchlists, /watchlists/{id}/items
GET                   /dashboard          (operator workspace aggregate)
GET                   /signals/matching   (approved signals only — Part N)
GET                   /signals/workforce  (emerging/obsolete capability report — Part O)
```

## 6. Integration (facade only)

`app/ecosystem/facade.py` exports:

- `get_registry_badges(db, pack_ids) -> {pack_id: ["benchmark_verified", "sunset_risk", ...]}`
  — derived only from `human_verified` observations / completed benchmark runs / lifecycle.
- `get_matching_signals(db, offering_ids) -> {offering_id: {benchmark, reliability,
availability, cost_efficiency, deprecation_risk, license_ok}}` — **only entities in
  lifecycle `verified|recommended` contribute; raw observations never leak** (Part N).
  Matching consumes these as _optional_ soft-scoring inputs behind a request flag.
- `get_workforce_signals(db) -> list[CapabilityGapSignal]` — joins verified emerging
  capabilities with talent facade demand data (Part O); planning output only.
- `record_production_telemetry(...)` — called from workflow runtime hooks (optional).

Product code imports only this module (talent/controlplane precedent).

## 7. Error codes

`ECO_SSRF_BLOCKED` 422 · `ECO_PAYLOAD_TOO_LARGE` 413 · `ECO_PAYLOAD_TOO_DEEP` 422 ·
`ECO_SOURCE_PAUSED` 409 · `ECO_ROBOTS_NOT_ATTESTED` 422 · `ECO_RATE_LIMITED` 429 ·
`ECO_MERGE_CONFIRMATION_REQUIRED` 409 · `ECO_OBSERVATION_IMMUTABLE` 409 ·
`ECO_PRICING_NOT_APPROVED` 409 · `ECO_BUDGET_EXCEEDED` 402 ·
`ECO_BLIND_REVIEW_SEALED` 409 · `ECO_TELEMETRY_THRESHOLD` 422 ·
`ECO_IMPACT_TOO_LARGE` 422 · `ECO_HARD_INCOMPATIBLE` 409 ·
`ECO_DRAFT_NOT_APPROVED` 409 · `ECO_INVALID_TRANSITION` 409 ·
`ECO_ROLLOUT_NOT_EVALUATED` 409 · `NOT_FOUND` 404 (uniform, no existence oracle) ·
`FORBIDDEN` 403.

## 8. Frontend (Part S)

Under `apps/web/src/app/(dashboard)/ecosystem/`:
`sources`, `discoveries`, `catalog`, `changes`, `pricing`, `conflicts`,
`benchmarks` (suites/runs/compare/blind-review), `components` (graph/impact/replacements/
drafts/rollouts), `operator` (watchlists/calendar/approvals/health). Server components +
client interactivity islands, matching existing dashboard patterns.

## 9. Testing (Part T)

Unit + DB-less endpoint tests + property tests over: ingestion idempotency (same raw_hash
no-ops), ETag 304 path, malformed/oversized/deep JSON, timeout/retry/backoff, SSRF matrix
(private IPs, metadata endpoint, userinfo, schemes), parser provenance stamping, alias
conflicts, low-confidence merge blocking, source conflict surfacing (two sources disagree ⇒
both observations retained + conflict flag), deterministic benchmark snapshots, provider
failure capture, cost capture + budget abort, blind-review identity hiding until all
submitted, transitive impact w/ cycles, private-edge org isolation, hard-incompatibility
separation, draft-only generation (publish gate), hostile prompt injection fixtures, nested
JSON bombs, archive traversal names, malicious URLs, cross-tenant telemetry leakage.
Full E2E (`tests/e2e_ecosystem_lifecycle.py` + endpoint-level
`test_eco_e2e_flow.py`): add source → sync discovers new model version → observation +
resolution candidate → human verify → benchmark old vs new → cheaper w/ acceptable quality
→ impact finds affected Workflow Pack → replacement candidate → update draft → rollout →
promote → registry badge reflects verified component.

## 10. Out of scope (enforced, not just documented)

No crawling beyond registered adapters; no auth/paywall/robots bypass (attestation flag);
no auto-publish (draft gate); no auto-migration (rollout gate + no binding rewrites); no
third-party code execution/installation (no such code path exists); no autonomous price
changes (reconciliation gate); no private-user-data scraping; no hiring decisions.

## 11. Amendments from competitive analysis (2026-09-22)

Derived from `competitive-analysis-ecosystem-intelligence.md` (20 world-class products);
each amendment below is normative and implemented.

### 11.1 Curation cost — bulk review operations (Snyk/Advisory lesson)

Trust is bought with analyst hours; the review queue must be cheap to drain.

- `POST /ecosystem/observations/bulk-verify` — body `{ids: [..≤100]}`, marks each
  observation human-verified (idempotent; missing ids reported, not fatal).
- `POST /ecosystem/resolution-candidates/bulk-decide` — body
  `{ids: [..≤100], decision: "confirm"|"reject"}`; per-id outcome list returned
  (confirm uses each candidate's own proposal; failures collected as
  `{id, error_code}` without aborting the batch).
- Dashboard overview adds `observations_unverified` and `injection_flagged_unverified`
  counts so queue rot is visible.

### 11.2 Heuristic findings flag, never block (ComfyUI YARA-FP lesson)

Injection/security heuristics are ADVISORY: they set `normalized.injection_flag`
and surface in UI/filters, but never gate ingestion, resolution or drafts. Only
HARD rules block (SSRF, size/depth bounds, robots attestation, hard I/O
incompatibility, lifecycle blocked/retired). API: `GET /ecosystem/observations`
gains `injection_flagged` filter (JSONB `normalized->>'injection_flag'`).

### 11.3 Catalog presence ≠ availability (OpenRouter lesson)

Availability is probed INDEPENDENTLY of catalog syncs:

- Worker topic `eco.check_availability {entity_kind, entity_id}` runs an injectable
  prober (`app.ecosystem.services.pricing.AVAILABILITY_PROBER`, mock by default,
  provider adapters later) and appends an `eco_availability_records` row with
  `record_type="status"`, `value={"status": "operational|degraded|unreachable",
"probe": {...}}` — even when the catalog entry is unchanged.
- A listed catalog entity with a stale/absent status record is rendered as
  availability-unknown, never assumed reachable.

### 11.4 Rollout guardrails — minimum sample + per-dimension thresholds (LaunchDarkly lesson)

`eco_rollout_plans.guardrails JSONB` (eco02 migration), shape:
`{"min_samples": int>=0, "thresholds": {"<dimension>": max_allowed_regression_float}}`.
Semantics (enforced in `RolloutService`):

- `evaluate` records `comparison.sample_size` = benchmark-result count of the
  candidate's latest completed run, and per-dimension `regression: bool` where a
  guarded dimension worsens beyond its threshold (higher-is-better dims: delta <
  -threshold; lower-is-better dims: delta > +threshold).
- `decide("promote")` is refused with `ECO_ROLLOUT_INSUFFICIENT_SAMPLES` (409)
  when `sample_size < min_samples`, and with `ECO_ROLLOUT_REGRESSION` (409) when
  any guarded dimension regressed. Guardrails are opt-in per plan (default
  `{"min_samples": 0, "thresholds": {}}`) but the operator UI proposes defaults;
  revising thresholds is a human act — there is still NO auto-promotion and,
  by design (stricter than LaunchDarkly), no auto-rollback of anything in
  production because rollouts never mutate production bindings in the first place.

### 11.5 Single-vendor fragility — sources are config, not code (Helicone lesson)

Every external feed stays behind an adapter key resolved at sync time. A dead or
replaced vendor is handled by `PATCH /ecosystem/sources/{id}` updating
`adapter_key` (validated against the registry; `parser_version` re-stamped) and/or
`base_url` — no code change, no data loss (observations keep the old
`parser_version` provenance). Circuit breaker + last-good ETag state already
guarantee a dying source degrades to a paused config row, never a crash.

New error codes: `ECO_ROLLOUT_INSUFFICIENT_SAMPLES` 409 · `ECO_ROLLOUT_REGRESSION` 409.

## 12. World-class-gap closure (2026-09-22, round 2)

Second amendment round: mechanisms upgraded from "works" to the way the
reference products actually do it. All normative and implemented.

| Gap vs. reference                                    | Change                                                                                                                                                                                                                                                                                                                                                  |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Continuous discovery (any aggregator)                | `eco_sync_sweep` cron (…:04/19/34/49) enqueues `eco.sync_source` for every active source whose `sync_interval_minutes` elapsed; sweep is idempotent (sync stamps `last_sync_at`, rate limiter absorbs double-enqueues)                                                                                                                                  |
| Advisory fan-out (Dependabot)                        | `_fanout` in change detection: same-transaction outbox rows — `eco.compute_impact` for breaking/security_critical/sunset_risk on resolved entities, `eco.notify_watchers` for every resolved-entity change. Watcher notifications ride the product notification system, idempotent per (watcher, change_event)                                          |
| Entity resolution (deps.dev/HF)                      | eco03: pg_trgm extension, `alias_normalized` + GIN trigram indexes on aliases and all 7 catalog `canonical_name`s; `normalize_name()` casefold/punctuation-squash key; deterministic lookups hit normalized keys, similarity is an indexed `%`/`similarity()` scan (difflib only as non-PG fallback). Similarity still never auto-merges                |
| Benchmark statistics (HELM/AA)                       | Case weights honored in aggregation; every dimension carries `dimension_stats` = {mean, std, n, ci95} (AA-style uncertainty); `compare_runs` exposes only numeric dimensions                                                                                                                                                                            |
| Human preference rating (LMArena)                    | Blind reveal computes Bradley-Terry MLE Elo (`stats.bradley_terry`, MM iteration + epsilon-prior) from per-(case, reviewer) score-implied pairwise wins (ties = 0.5); written to `dimension_scores.human_pref_elo`                                                                                                                                      |
| Rollout statistics (LaunchDarkly sequential testing) | `evaluate` runs Welch's t (latency, cost) and two-proportion z (reliability) over per-result samples of candidate vs. incumbent runs; `comparison[dim]` carries `p_value`/`significant`; a guarded regression requires BOTH beyond-threshold AND p<0.05 when samples exist — noise cannot block a promote, real regressions always do                   |
| Version-range semantics (Renovate/deps.dev)          | `stats.version_in_range` (>=, <=, >, <, ==, ^, ~, bare); impact BFS prunes first-hop edges whose `constraint_spec.version_range` provably excludes the changed version; unparseable ranges FAIL OPEN (still affected)                                                                                                                                   |
| Typed change magnitude (Dependabot)                  | Price change events embed `magnitude {unit, region, change_pct}`                                                                                                                                                                                                                                                                                        |
| Real measurement (Replicate/AA)                      | `OfferingExecutor`: benchmark runs whose target names an `offering_id` execute through the real provider-adapter chain (connection -> adapter -> late-decrypted credentials, stable idempotency key `bench-{run}-{case}-{repeat}`, runtime-equal timeout); usage events captured per result; provider failures are data (failed results), never crashes |

Out-of-scope for this round (recorded, not hidden): LLM-suggested resolution
adapter, real (non-mock) provider adapters beyond the existing registry,
canonical-entity merge tooling, workforce trend projection.

## 13. Platform-maturity closure (2026-09-22, round 3)

Round 3 targets the _product/platform_ capabilities that make the reference
services world-class, beyond algorithms. All implemented.

| Reference bar                                     | Now shipped                                                                                                                                                                                                                                                                                                                     |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Cacheable API (HF/deps.dev)                       | `ETagRoute` (weak ETags, If-None-Match -> 304) on catalog/observations/dashboard/pricing/benchmarks read surfaces                                                                                                                                                                                                               |
| API protection (talent parity)                    | Whole `/ecosystem` surface behind the shared sliding-window rate limiter with X-RateLimit-* headers                                                                                                                                                                                                                             |
| Cursor pagination (deps.dev/HF)                   | `/observations` + `/changes` paginate by ULID cursor (`meta.has_more`/`next_cursor`); stable under concurrent inserts; offset kept as legacy                                                                                                                                                                                    |
| iCal subscription (endoflife.date)                | `GET /ecosystem/deprecation-calendar.ics` — RFC 5545 VCALENDAR of upcoming sunsets, subscribe from any calendar client                                                                                                                                                                                                          |
| Outbound webhooks (StatusGator/GitHub)            | `ecosystem.change` added to org webhook event types; org-scoped watchlists fan changes out through the existing fail-safe, entitlement-gated, SSRF-guarded delivery path                                                                                                                                                        |
| Registry dedupe (any registry)                    | `POST /catalog/{kind}/{id}/merge-into/{target}`: re-points observations/aliases/mappings/dependency-edges/prices/availability (unique-conflict rows resolved: survivor alias wins, higher evidence wins), merges alias/external-id sets, retires the duplicate via audited lifecycle transition + `supersedes` replacement edge |
| Machine-readable dataset (LiteLLM/deps.dev)       | `GET /ecosystem/export` — one canonical content-hashed JSON document (`openskill.eco.catalog/v1`): entities, capability mappings, APPROVED prices only                                                                                                                                                                          |
| Inter-rater reliability (human-eval table stakes) | Blind reveal reports `reviewer_agreement` {pairs, percent, mean Cohen's kappa} from per-case preference labels — an Elo over disagreeing reviewers is flagged as such                                                                                                                                                           |
| Suite versioning (HELM)                           | Runs snapshot a case-set fingerprint at creation; execute refuses drifted suites (`ECO_SUITE_DRIFT` failed run) so results always correspond to the recorded suite                                                                                                                                                              |
| Source health history (StatusGator)               | `GET /sources/{id}/health` — windowed success/not-modified/failure rates, volumes, last error                                                                                                                                                                                                                                   |

## 14. Real-world depth closure (2026-09-22, round 4)

| Reference bar                                                   | Now shipped                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| --------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Real vendor execution (Replicate/OpenRouter/OpenAI as products) | Three real HTTP adapters in the provider registry: `openrouter` (chat, slug-validated, token usage), `openai_image` (Images API, model allowlist, size allowlist, b64 never inlined), `replicate` (predictions, IMMUTABLE 64-hex version required — never 'latest', Prefer:wait, Idempotency-Key, predict_time metering). Shared discipline: org credential mandatory, fixed vendor endpoints (no org URLs), trust_env=False, bounded timeout, single attempt                                              |
| LLM-assisted curation (Snyk Human+AI)                           | `llm_extraction.py`: fixed instruction frame, untrusted text inside random boundary markers, strict extra=forbid schema (invalid entries DISCARDED, never coerced), injection-shaped outputs rejected, confidence hard-capped at 0.7; `POST /observations/extract-llm` creates unverified llm-method observations; `POST /resolution-candidates/{id}/llm-suggest` proposes matches that can NEVER auto-merge (llm_suggested excluded from AUTO_MERGE_METHODS); clean ECO_LLM_DISABLED when no platform key |
| Curation loop closure (Snyk)                                    | `POST /catalog/{kind}/{id}/resolve-conflict`: per-field curated overlay {value, source, decided_by, decided_at}; conflicting observations stay fully visible with the decision attached                                                                                                                                                                                                                                                                                                                    |
| Early warning (StatusGator)                                     | Availability probe status FLIPS (operational→degraded/unreachable) emit an `availability_changed` observation on the internal probe source + a degraded change event that rides the normal fan-out (watchers, webhooks); unchanged repeats stay silent                                                                                                                                                                                                                                                     |
| Trend projection (Lightcast)                                    | `stats.linear_trend` least-squares; workforce signals carry weekly change counts + slope + projected next window + R²                                                                                                                                                                                                                                                                                                                                                                                      |
| Global search (HF)                                              | `GET /ecosystem/search?q=` — indexed trigram across all seven kinds, similarity-ranked                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Admin audit (enterprise baseline)                               | Six eco actions registered in the immutable commercial audit trail (merge, lifecycle, price reconcile, rollout decision, draft publish, conflict resolution) via fail-safe `eco_audit` — an audit hiccup never blocks the action                                                                                                                                                                                                                                                                           |
| Cross-source corroboration (StatusGator)                        | `GET /catalog/{kind}/{id}/corroboration`: distinct sources, trust-weighted score (official 1.0 … unverified 0.2), human-verified flag                                                                                                                                                                                                                                                                                                                                                                      |

## 15. Product-surface closure (2026-09-22, round 5)

The reference products are DEFINED by their product surfaces; this round wires
four rounds of backend capability into first-class UI + adds the missing
flagship surface.

| Reference bar                                  | Now shipped                                                                                                                                                                                                                                                                                                                |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Leaderboard (LMArena/AA's core product)        | `GET /benchmark/leaderboard`: latest completed run per target across a family, rankable by ANY preserved dimension (lower-is-better handled for cost/latency; entities missing a dimension sort last, never hidden); Benchmark Lab page renders it with per-dimension mean ± 95% CI cells and the Bradley-Terry Elo column |
| Global search entry (HF)                       | Search box in the ecosystem nav → cross-kind trigram results dropdown                                                                                                                                                                                                                                                      |
| Curation UI (Snyk)                             | Catalog inspect panel: per-conflict one-click "adopt this value" arbitration (curated pick highlighted), corroboration line (sources · trust score · human-verified), duplicate→survivor merge input                                                                                                                       |
| Source health panel (StatusGator)              | Per-source expandable 7-day health (runs, success rate, observations, bytes, last error)                                                                                                                                                                                                                                   |
| Reveal analytics (LMArena)                     | Blind Review page: admin Reveal button → alias→identity table sorted by preference Elo, with reviewer percent agreement + Cohen's κ header                                                                                                                                                                                 |
| Statistical transparency (LaunchDarkly)        | Rollout cards show per-dimension p-values with significance markers (* / ns)                                                                                                                                                                                                                                               |
| Dependency navigation (Backstage)              | Components → Graph tab: bidirectional dependency walk (click any edge endpoint to re-center)                                                                                                                                                                                                                               |
| Subscription surfaces (endoflife.date/LiteLLM) | iCal subscribe + catalog-export JSON links on the Watchlists page                                                                                                                                                                                                                                                          |
| HITL entry (Snyk)                              | "LLM suggest" button on unmatched resolution candidates (suggestion only — never auto-merges)                                                                                                                                                                                                                              |

## 16. Distributed correctness & ops hygiene (2026-09-22, round 6)

What keeps the reference services alive in multi-replica production.

| Reference bar                                     | Now shipped                                                                                                                                                                                                                          |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Shared rate-limit state (any multi-replica API)   | `/ecosystem` surface moved off the in-process limiter onto the platform's Redis sliding-window limiter (user-keyed, route-template buckets, test-env bypass)                                                                         |
| Execution fencing (own workflow-runtime standard) | `execute_run` claims via conditional `UPDATE … WHERE status='queued'`; the losing worker gets `ECO_INVALID_TRANSITION` and produces nothing — double-execution/double-billing is structurally impossible                             |
| Sync mutual exclusion                             | `run_sync` takes the source row `FOR UPDATE NOWAIT`; a concurrent worker skips with `ECO_SYNC_IN_PROGRESS` (worker treats it as an expected state); same-transaction re-entry is reentrant                                           |
| Bounded operational history (ops baseline)        | Daily `eco_retention` cron: availability STATUS probes >90d pruned keeping each entity's latest (flips live forever as append-only observations/events); sync-run audit rows pruned at 180d; observation/change ledgers NEVER pruned |
| Dead-feed detection (StatusGator)                 | `sources_stale` on the operator dashboard: active sources overdue by 3× their sync interval (paused sources excluded)                                                                                                                |
| Graph visualization (Backstage)                   | Components → Graph renders an inline SVG: center node, dependency column left, dependents right, connecting edges — alongside the click-to-recenter walk                                                                             |

## 17. Governance & operator completeness (2026-09-22, round 7)

| Reference bar                                   | Now shipped                                                                                                                                                                           |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Four-eyes principle (enterprise review culture) | Draft creator can neither approve nor publish their own draft (`ECO_FOUR_EYES`, checked after transition validity); submit/reject/edit stay self-service                              |
| Run cancellation (any job system)               | `POST /benchmark/runs/{id}/cancel` — fence-aware conditional UPDATE, queued-only; a cancel racing an executor claim has exactly one winner                                            |
| Self-observability (Prometheus/Datadog)         | `GET /ecosystem/ops/metrics` — plaintext gauges: source states, staleness, review debt, queue depths, eco outbox backlog                                                              |
| Delta feeds (deps.dev)                          | `GET /ecosystem/export/changes?since=` — oldest-first typed-change delta with `next_since` cursor                                                                                     |
| In-product audit (enterprise)                   | `GET /ecosystem/audit` — the eco slice of the immutable commercial audit trail, filterable                                                                                            |
| Day-1 experience (every real product)           | `python -m app.cli eco-seed` — curated starter sources (HF t2i/i2v, ComfyUI releases, analyst desk), ALL seeded PAUSED pending explicit operator attestation + activation; idempotent |

## 18. Property-based & adversarial assurance (2026-09-22, round 8)

Hypothesis suites matching the repo's mutation-testing culture:

- Statistics kernel invariants: CI ordering/containment, weighted-mean bounds,
  Welch p ∈ [0,1] + two-sided symmetry, two-proportion p ∈ [0,1],
  Bradley-Terry completeness/finiteness + dominance ordering, pairwise-win
  mass conservation (ties included), flat-series trend projection,
  kappa self-agreement, semver exact/caret/bound algebra.
- Adapter fuzzing: arbitrary bytes AND arbitrary JSON documents against all
  six adapters — the only permitted exception is the bounded EcoSecurityError
  family; every produced candidate carries a 64-hex hash and a NUL-free
  payload (storage-safe by construction).
- sanitize_text idempotence + control-character freedom.

Round 9 (product completeness): change-feed cursor "load more" UI.

## 19. Comparison & cost-estimation surfaces (2026-09-22, round 10)

| Reference bar                    | Now shipped                                                                                                                                                                                                                          |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Artificial Analysis side-by-side | `GET /ecosystem/compare?kind=&ids=` — 2-6 entities: canonical facts, latest per-unit price (approved beats observed), latest availability status, latest benchmark dimension scores; uniform 404 (no existence oracle)               |
| OpenRouter cost calculator       | `POST /ecosystem/pricing/estimate` — workload {unit: quantity} priced per entity from latest approved/observed prices; sorted fully-priced-then-cheapest; unpriced units FLAGGED, never zeroed; advisory only, never a billing quote |
| UI                               | `/dashboard/ecosystem/compare` — comparison matrix + workload estimator with approved/observed provenance badges                                                                                                                     |

Safety notes: estimates never touch `cp_provider_cost_rates`; approved
reconciled prices merely take precedence over raw observations in display.

## 20. Availability SLO summary (2026-09-22, round 11)

StatusGator bar: `GET /ecosystem/pricing/availability/uptime?entity_kind=&entity_id=&days=` —
time-weighted uptime % from our OWN probe history (each probe's status holds
until the next), incident count (flips into degraded/unreachable), per-day
worst status, and an honest `coverage_pct`: before the first probe the answer
is `unknown`/`null`, never assumed-up. days bounded 1-365.

## 21. Frontier & syndication (2026-09-22, round 12)

- **Pareto frontier** (Artificial Analysis quality-vs-cost chart): leaderboard
  rows gain `on_frontier` — true when no other row has strictly better quality
  AND strictly lower cost. Computed only for higher-is-better dimensions with
  usable cost; unpriceable rows stay unflagged, never hidden. Dominated rows
  remain visible (the operator sees WHY they lose).
- **Atom syndication** (endoflife.date / GitHub releases bar):
  `GET /ecosystem/export/changes.atom` — Atom 1.0 feed of typed change events,
  newest-first, all change data XML-escaped (untrusted external content).

## 22. Automatic benchmark regression detection (2026-09-22, round 13)

promptfoo/LangSmith CI bar: when a run completes, it is compared against the
PREVIOUS completed run for the same suite + target. For every dimension with
summary stats on both sides, Welch's t from summary statistics
(`welch_t_from_stats` — no raw-result re-read) decides significance; a
significant worsening (p<0.05, direction-aware: cost/latency reversed) emits a
`benchmark`/`benchmark_regression` change event, severity `degraded`, on the
`internal:benchmark-lab` source, riding the normal fan-out (watchers,
webhooks, Atom, delta export). Detection only — never auto-rollback, never a
lifecycle mutation. New CHANGE_TYPES member: `benchmark`.

## 23. Entity scorecard (2026-09-22, round 14)

Backstage scorecard bar: `GET /ecosystem/catalog/{segment}/{id}/scorecard` —
independent pass/warn/fail checks, each carrying raw evidence: lifecycle,
corroboration (>=2 distinct sources or human verification), freshness
(30/90-day observation age), availability (current probe status + 30d uptime),
benchmark recency (90d), pricing (any approved). Deliberately NOT one magic
number: never-probed/benchmarked/priced surfaces are `n/a` and excluded from
the denominator — honest unknowns, not failures. Grade = healthy | attention |
failing.

## 24. Watchlist noise controls (2026-09-22, round 16)

Renovate/Dependabot noise bar: watchlists gain `min_severity` (default `info`)
and `muted_until`. Push fan-out (`eco.notify_watchers`) skips lists below the
threshold or currently snoozed — a user notifies when ANY of their watching
lists is loud enough and not muted. Pull (`matching_changes`) honors the
LOWEST threshold among the user's lists watching that target (the most
interested list decides); mute affects push only, never hides data on pull.
`PATCH /ecosystem/watchlists/{id}` (owner-gated) sets threshold, mute, unmute.
Migration eco04a00004 (additive, server_default='info').

## 25. Impact SLA escalation (2026-09-22, round 17)

PagerDuty/Jira SLA bar: cron `eco_impact_sla` (twice hourly) sweeps OPEN
impact analyses past `deadline_at` and notifies every platform admin exactly
once (`summary.escalated_at` stamp = idempotence). Escalation never mutates
analysis status — closing an impact stays a human decision.

## 26. Per-case results drill-down (2026-09-22, round 18)

LangSmith trace bar: every run row expands into its per-case results table —
repeat index, latency, cost, retries, ok/failed (error on hover), automated
scores — straight from `GET /benchmark/runs/{id}/results`. Failures are data,
never hidden.

## 27. One-click watch (2026-09-22, round 19)

GitHub watch-button bar: `POST /ecosystem/watchlists/quick-watch` gets or
creates the user's "Default" watchlist and adds the target idempotently
(double-click = same item, no duplicates). 👁 Watch button on every catalog
row. WATCH_TARGET_KINDS extended to all seven catalog kinds.

## 28. Divergence wiring (2026-09-22, round 20)

§3.7 now fires in BOTH directions automatically: a completed benchmark run is
immediately compared against the latest cross-tenant production telemetry
(`_check_production_divergence`), and every fresh cross-tenant telemetry
snapshot is compared against the latest completed benchmark (telemetry-window
handler). Divergence >0.25 absolute (benchmark reliability vs production
success rate) emits ONE `degraded` change event — re-flag only after an
operator acknowledges the open flag (idempotence guard on unacked events).
Per-org snapshots never drive public divergence flags.

## 29. Duplicate detection sweep (2026-09-22, round 21)

Backstage/deps.dev dedup bar: `GET /ecosystem/catalog/{segment}/duplicates`
(platform-admin) — trigram self-join surfacing entity pairs with similar
canonical names (threshold 0.3-1.0, default 0.55), each pair once, retired
excluded. Suggestion only: merging remains the operator's explicit audited
action. pg_trgm unavailable → empty list, never an error.

## 30. Price history & trend (2026-09-22, round 22)

AA price-over-time bar: `GET /ecosystem/pricing/history?entity_kind=&entity_id=&unit=` —
per-unit oldest-first series of non-rejected observations (approved flagged)
plus a per-unit linear trend (slope in price/day, advisory `projected_next` —
never a rate). Catalog Inspect panel shows the per-unit latest price with a
falling/rising/flat arrow and projection.

## 31. Score history (2026-09-22, round 23)

LMArena score-over-time bar: `GET /ecosystem/benchmark/score-history?entity_kind=&entity_id=&dimension=&suite_id=` —
chronological completed-run series for one dimension (points carry suite_id
for faceting) + advisory linear trend. Failed runs and other entities never
appear; unknown dimensions return an empty series, not an error.

## 32. Catalog coverage (2026-09-22, round 24)

Backstage maturity bar: `GET /ecosystem/dashboard/coverage` — per-kind counts
of entities with capability mapping / completed benchmark / any price
observation, surfaced as a completeness table on the Overview. Curation debt
becomes visible per dimension; incomplete entities are never hidden.

## 33. Shareability & trend surfacing (2026-09-22, round 25)

- **Shareable compare URLs**: the comparison lives in the querystring
  (`/compare?kind=&ids=`) — paste a link, get the same view (Suspense-wrapped
  useSearchParams; state syncs on submit).
- **Benchmark trend in catalog Inspect**: latest reliability + improving/
  declining/stable arrow + run count, from `/benchmark/score-history`.

## 34. Trending (2026-09-22, round 26)

HF/Civitai trending bar: `GET /ecosystem/dashboard/trending?days=&limit=` —
entities ranked by observation count in the current window, each row carrying
distinct-source corroboration and `velocity` (current/previous equal-length
window; `null` = newly observed, never infinite). Pure evidence counting — no
engagement scores, no editorial weighting. Surfaced as chips on the Overview.

## 35. Portable suites (2026-09-22, round 27)

HELM open-suite culture: `GET /benchmark/suites/{id}/export` — a versioned,
self-contained JSON document (definition + cases + fingerprint; runs/results
NEVER travel). `POST /benchmark/suites/import` (platform-admin) re-validates
through the same Pydantic schemas as manual creation, caps at 200 cases,
lands in draft status, and rejects key collisions rather than merging.

## 36. Automatic rollout evaluation (2026-09-22, round 28)

LaunchDarkly auto-check bar: cron `eco_rollout_eval` (twice hourly)
re-evaluates every running/evaluating rollout plan so guardrail breaches
surface without an operator clicking Evaluate. Detection only — promote/
rollback stays an explicit human decision (§11.4). A NEW regression set
notifies platform admins once (fingerprint stamp in comparison); the same
regressions never re-alert. One failing plan never blocks the sweep.

## 37. Compliance CSV export (2026-09-22, round 29)

Enterprise export bar: `GET /ecosystem/audit.csv` (platform-admin, up to 10k
rows) — the eco audit slice as CSV with csv-module quoting AND spreadsheet
formula defusal (cells starting with = + - @ get a leading apostrophe), so
untrusted audit content can never execute in Excel/Sheets.

## 38. Security advisory registry (2026-09-22, round 30)

Snyk/Dependabot bar: structured advisories replace loose security events.

- `eco_security_advisories` (migration eco05a00005): advisory_ref (unique),
  severity, affected name + semver range, fixed_in, status
  open|mitigated|dismissed. Registration is a curated platform-admin act.
- Registration emits ONE `security`/`security_advisory` change event
  (critical/high → `security_critical`, else `breaking`) on the
  `internal:security-desk` source — rides the normal fan-out.
- `GET /security/advisories/{id}/affected` resolves affected catalog entities:
  exact-insensitive name/alias match + `version_in_range` with FAIL-OPEN
  semantics — an unparseable version is `unknown_fail_open`, never "safe".
- Never auto-blocks or auto-migrates; lifecycle transitions stay human.
- UI: Security page (register, list, affected resolution, mitigate/dismiss);
  Overview gains `security_advisories_open`.

### §38.1 Watcher fan-out (round 31)

Registration also emits one `security_advisory_affects` change event PER
affected entity (capped at 50), carrying `canonical_entity_id` — so watchers
of a hit entity are notified through the normal watch/webhook/Atom fan-out:
"a model I watch has a CVE" arrives without polling.

## 39. HTTP contract & API-surface stability (2026-09-22, rounds 32-33)

The recurring authz classes are only provable at the HTTP layer — service
tests never exercise dependency wiring. New suite pins:

- anonymous → 401 on every eco surface (reads and writes) with the
  machine-readable error envelope;
- member → 403 on every platform-admin surface (audit, audit.csv, duplicates,
  source create, advisory create, suite create) — never data;
- member reads → 200 with the `{data: ...}` envelope on 11 core surfaces;
- error shapes: unknown catalog kind and nonexistent entity → uniform 404
  (no existence oracle), bad compare input → 422 `VALIDATION_ERROR`;
- API-surface stability: 29 core (method, path) pairs asserted against the
  OpenAPI document — the surface may only GROW; a missing pair fails the
  suite as an undeliberate breaking change.

## 40. Query budgets (2026-09-22, round 34)

Scale-readiness bar: eliminated the two remaining O(n)-query paths —
trending's per-row previous-window count is now ONE grouped query, and
advisory affected-entity resolution prefilters in SQL (name-prefix LIKE +
lowered-alias LIKE; the exact Python recheck is unchanged, so semantics are
identical — the prefilter can only narrow the scan, never the result).
Guard tests count real SQL statements via a cursor-execute listener and fail
on budget breach: trending ≤ 3+rows, overview ≤ 25, coverage ≤ 15 — an
O(rows) loop reintroduced anywhere in these paths fails CI.

## 41. Alert runbook (2026-09-22, round 35)

Ops deliverable: `docs/ops/ecosystem-alerts.md` — ready-to-import Prometheus
alert rules over the `/ops/metrics` gauges (staleness, outbox backlog,
security-critical, curation debt, stuck benchmarks, impact SLA backstop,
injection-flag rot), each with a runbook line mapping to an in-product
surface; no alert requires shell access. Includes the full metric inventory.

## 42. Raw retention & parser replay (2026-09-22, round 36)

deps.dev reprocessing bar: raw payloads are now retained
(`eco_raw_snapshots`, migration eco06a00006 — one row per distinct
source+payload, size bounded by the fetch guard, pruned after 90 days by the
retention cron) and `POST /sources/{id}/replay` (platform-admin) re-runs the
CURRENT adapter over them. Append-only semantics preserved:

- unseen item hash → normal ingest;
- unchanged output → idempotent no-op;
- CHANGED output (parser upgrade) → a NEW observation with a
  version-derived hash, linked from the old row via `superseded_by_id`;
  the old row is never rewritten. Curated canonical resolution is inherited
  (no re-queue); `human_verified` resets to false — new content needs fresh
  review. Re-replaying with the same parser supersedes nothing.

## 43. Accessibility pass (2026-09-22, round 37)

Enterprise a11y bar: every `<select>` across the eleven ecosystem pages now
carries a semantic `aria-label`, icon-only buttons (mute toggle) and bare
checkboxes (run-comparison, robots-compliance) have accessible names. An a11y
smoke suite renders all eight interactive pages and fails on ANY control
without an accessible name — new unlabeled controls can't ship.

## 44. Review integrity (2026-09-22, round 38)

Two governance holes closed:

- **Blind approval**: the Drafts tab now has a "Review payload" expander —
  reviewers see the exact JSON they are approving, in place.
- **TOCTOU swap**: editing a draft while `in_review` drops it back to `draft`
  (GitHub "new commits dismiss review" semantics) — the window between a
  reviewer reading and a second admin approving can no longer be exploited to
  swap content. Approved drafts remain immutable.

## 45. Publish race fencing (2026-09-22, round 39)

Distributed-correctness closure on the last unguarded read-modify-write:
`DraftService.transition` now takes a row lock (`SELECT ... FOR UPDATE` via
refresh) before the state-machine check, so two concurrent publishes
serialize — the loser re-reads `published` and is refused; the
materialization side effect (`_publish` creating a WorkflowPack) can never
run twice. Proven by a two-session `asyncio.gather` race test asserting
exactly one winner, one `ECO_DRAFT_NOT_APPROVED`, and exactly one pack.

## 46. Merge & reconcile fences + advisory audit (2026-09-22, round 40)

Concurrency sweep over the remaining unguarded read-modify-writes:

- **merge_entities**: locks BOTH rows in deterministic id order (no deadly
  embrace with a concurrent opposite-direction merge) and re-checks retired
  status inside the lock — A→B racing B→A now has exactly one winner; both
  entities can never end up retired.
- **reconcile**: row lock before the already-decided check — two concurrent
  approvals serialize and a cost rate is minted exactly once.
- **advisory audit**: status transitions now write `eco.advisory_status` to
  the immutable commercial audit trail.
  Proven by two-session race tests (opposite merges, double approval).

## 47. Rollout decide fence + zombie-run sweep (2026-09-22, round 41)

- **decide race**: RolloutService.decide takes a row lock — concurrent
  promotes serialize; the loser re-reads a terminal status and is refused, so
  the `recommended_replacement` edge is recorded exactly once (two-session
  race test).
- **zombie runs**: cron `eco_stuck_runs` (hourly) closes runs stuck in
  `running` for >4h as failed (`ECO_RUN_STUCK`, safe to re-queue) via a
  conditional UPDATE — a concurrently-completing run is left alone; recent
  runs untouched; idempotent. The claim fence already prevented re-execution;
  this drains the queue metric and gives the operator an actionable state.

## 48. Residual read-modify-write sweep (2026-09-23, round 42)

Final concurrency pass over the remaining unguarded paths:

- **Blind-review reveal**: row lock + explicit refusal on `revealed` — the
  human-score fold-back and preference-Elo computation run exactly once.
- **Lifecycle transition**: entity row lock so the state machine always
  validates against the CURRENT status and the transition log matches the
  entity's actual path.
- **quick_watch get-or-create**: per-user `pg_advisory_xact_lock` — two
  concurrent first clicks can never create two "Default" lists (race-tested).

### §48.1 Retired entities never recommended (round 42 fix)

The residual-sweep race tests exposed a real product defect: the replacement
candidate pool did not exclude RETIRED entities — a retired model version
could rank as a recommended replacement (and crowd live candidates out of the
top-N). Fixed: retired entities appear in NEITHER channel (blocked entities
still surface in the hard-incompatible channel so the operator sees why).
Race tests additionally self-clean their committed fixtures (retire on exit)
so committed test data can never pollute other tests' candidate pools.

## 49. Watchers follow merges (2026-09-23, round 43)

Data-integrity defect: entity merge re-pointed observations, prices,
availability, aliases and edges — but NOT watch items, so a user watching the
duplicate silently stopped receiving every future change event. Fixed:
merge re-points watch items to the survivor; a list already watching the
survivor drops the now-duplicate item (never doubled). Nothing is left
pointing at the retired duplicate (tested for solo- and both-watchers).

## 50. Merge completeness & stale-candidate guard (2026-09-23, round 44)

Systematic audit of every table referencing an entity id against the merge
re-point list closed three gaps:

- **ChangeEvent.canonical_entity_id** now follows the survivor — entity-scoped
  views (UI filters, watcher pull, delta export) keep the full change story
  instead of losing it behind a retired duplicate.
- **Pending ResolutionCandidate** rows proposing the duplicate re-point to
  the survivor (a later confirm can no longer resolve observations onto a
  retired entity); already-decided rows stay untouched as history.
- **Rollout stale-candidate guard**: a ReplacementCandidate generated before
  a lifecycle change can no longer start a rollout onto a retired/blocked
  entity (`ECO_INVALID_TRANSITION` — regenerate candidates).
  Deliberately NOT re-pointed (history stays where it happened): impact
  analyses, benchmark run targets, decided resolutions.

## 51. No silent mutation failures (2026-09-23, round 45)

UX-integrity pass: every mutation across the eleven ecosystem pages now
surfaces failures — 9 previously silent mutations (acknowledge, discovery
verify/bulk/confirm/llm/reject, watchlist create/update/add/remove, run
compare, price extract, source toggle) gained onError handlers rendering the
machine error message in an in-page banner. One-click Watch also gained
success feedback (button flips to "✓ Watching" and disables) — no more
fire-and-wonder actions.

## 52. Operator-surface completion (2026-09-23, rounds 46-49)

Four operator gaps where backend capability existed with no UI:

- **Impact actions** (round 46): Acknowledge/Resolve buttons on impact
  analyses — the SLA loop closes in-product instead of via raw API calls.
- **Source replay** (round 46): Replay button beside Sync now (§42 endpoint).
- **Run failure visibility** (round 46): run rows show the machine error
  class inline (full text on hover) — ECO_BUDGET_EXCEEDED / ECO_SUITE_DRIFT /
  ECO_RUN_STUCK are no longer invisible.
- **Catalog deep links + pagination** (round 47): `?kind=&entity=` restores
  the Inspect panel (shareable), offset-based Load more with an
  N-of-total footer.
- **Compare uptime** (round 48): availability row shows 30d uptime %,
  incident count and probe coverage per compared entity.
- **Sync history** (round 49): per-source History panel — last 20 runs with
  status/HTTP/bytes/observations/changes/error.

## 53. Navigable overview + stats-kernel mutation audit (2026-09-23, rounds 50-52)

- **Clickable stat cards** (round 50): nine Overview counters link straight to
  their work queues (pricing review, discoveries, benchmark queue, impact,
  drafts, rollouts, sources) — the dashboard is a router, not a poster.
- **UI regression tests** (round 51): sync-history panel, impact
  acknowledge POST wiring, stat-card hrefs (3 new tests).
- **Mutation audit** (round 52, R136-250 technique): six targeted operator/
  constant mutations against the statistics kernel. Two SURVIVED — the CI
  z-score (1.96→1.0) and the Welch n<2 boundary were never numerically
  asserted. Both killed with exact-value tests (half-width = 1.96·std/√n;
  single-sample side ⇒ p exactly 1.0); all six mutants now die.

### §53.1 Evidence-first verification (round 53)

Same class as the draft blind-approval fix: observation VERIFY was blind —
the normalized payload was never shown. Each observation row now expands into
its normalized-JSON payload (capped viewport) beside the provenance link, so
human verification is evidence-based in-product.

## 54. Governance-guard mutation audit (2026-09-23, round 54)

Same technique as §53, aimed at the guards themselves: six mutants disabling
or flipping four-eyes, the rollout regression-threshold direction, the
min_samples floor, the reconcile already-decided gate, uptime's unknown
handling, and the stuck-run cutoff. Two SURVIVED, exposing untested guards:

- **min_samples** had NO test — a rollout could have shipped with the sample
  floor silently disabled. Killed: promote with min_samples above the
  collected count must refuse `ECO_ROLLOUT_INSUFFICIENT_SAMPLES`.
- **uptime unknown-as-up** had no case with an unknown interval. Killed: an
  unknown probe interval is neither up nor down — it reduces coverage, never
  inflates uptime_pct.
  All six guard mutants now die.

### §54.1 Unicode-digit parser trap (round 54 fix)

The full-suite Hypothesis fuzz surfaced a live counterexample (`'-¹'`):
superscript digits pass `str.isdigit()` but crash `int()`. Fixed in BOTH
semver parsers (`workflow_pack` prerelease identifiers and the eco
`parse_version`) with `isascii() and isdigit()`; explicit killer test pins
`parse_version("¹.2.3") is None` and the fail-open contract for
`version_in_range` on unparseable input.

## 55. Security-layer mutation audit (2026-09-23, round 55)

Eight mutants against the SSRF/payload guards: scheme allow-list widened,
private-IP check off, loopback check off, localhost literal off, control-char
stripping off, sanitize length cap off, JSON byte cap ×10, JSON depth cap off.
Results:

- **json-bytes-cap** SURVIVED twice before the killer landed — the 5 MiB byte
  cap was masked first by the 100k string cap, then by the 10k item cap. The
  final killer (9000×600 B strings: inside every other bound) proves the byte
  cap itself rejects; a silently raised cap now fails CI.
- **localhost literal** and **loopback** survivors are VERIFIED equivalent
  mutants: defence-in-depth layers (public-FQDN check, is_private covering
  127/8 and ::1) stop the same inputs — verified by executing each mutant
  directly. A localhost-literal pin test was added anyway.
  Six killable mutants die; the two survivors are documented redundancy, not
  gaps.

## 56. Decision-logic mutation audits (2026-09-23, rounds 56-57)

**Resolution policy (round 56)** — four mutants against the auto-merge core
(similarity allowed in, confidence floor 0.9→0.1, inflated confidences,
llm_suggested allowed in): ALL FOUR survived initially. The two-condition
gate (method ∈ set AND confidence ≥ floor) masks single-point drift, and no
test pinned the policy constants. Fixed with (a) a policy-pin test
(AUTO_MERGE_METHODS == {official_id, alias}; floor == 0.9;
LLM_CONFIDENCE_CAP < floor) and (b) behavioural killers: a PERFECT-similarity
identical-name observation must stay pending; curated-alias hits are exactly
0.95 and auto-merge (aliases are human-entered facts); no-match candidates
are exactly 0.0. 4/4 die. (An initial mis-read of the alias branch was
reverted — zero semantic changes shipped, only pins.)

**Change severity (round 57)** — six mutants (security→info, license→info,
sunset→info, price-increase threshold ×1000, AUTO_FANOUT_SEVERITIES emptied,
magnitude sign flip): three survived — sunset-field severity, the automatic
impact fan-out switch, and the price-magnitude sign had NO tests. Killed with
a dedicated suite asserting sunset_risk on sunset_at changes, an
eco.compute_impact outbox row for breaking changes with zero operator
clicks, and +50% (not −50%) on a 0.04→0.06 price move. 6/6 die.

### §56.1 Impact-BFS audit (round 58)

Six mutants against the blast-radius walk (depth cap off/one, node cap tiny,
visited-set off, edge direction flipped, version-constraint fail-open →
fail-closed). One survivor: no test graph was deeper than the cap, so an
unbounded IMPACT_MAX_DEPTH went unnoticed — killed with an 8-hop chain
asserting depth 6 is reached and depth 7+ is pruned. 6/6 die on the combined
suite.

### §56.2 Adapter identity contracts (round 59)

Four mutants against adapter mechanics. Three survived: the idempotency
hash's key-order independence, and the pricing/HF adapters' event types had
no contract tests — an event-type drift would silently route price facts
around the pricing pipeline (or HF models around resolution). Killed with an
adapter-contract suite: same-content different-key-order hashes are equal
(different content differs); pricing_json emits price_changed; huggingface
emits model_released. 4/4 die.

## 57. Pipeline-guard mutation audits (2026-09-23, rounds 60-63)

Continuing the §56 technique across the remaining pipelines:

- **Telemetry privacy (60)**: 5 mutants — the TWO-dimensional privacy floor
  had only its org dimension tested: 19 samples across 5 orgs sailed through
  with the sample floor dropped to 1. Killed (19-sample cross-tenant write
  must refuse ECO_TELEMETRY_THRESHOLD). Percentile, inverted success-rate and
  widened divergence band were already covered. 5/5 die.
- **Benchmark economics (61)**: 5 mutants — the budget boundary (>= vs >) was
  untested: a strict > runs one case PAST the cap. Killed with an exact-stop
  test (3 cases × $1, $2 cap ⇒ exactly 2 results, total exactly $2,
  ECO_BUDGET_EXCEEDED). Weights, failed-as-success, drift gate covered
  (drift tests added to the harness set). 5/5 die.
- **Sync guards (62)**: 5/5 died first pass — rate limit, paused gate,
  bounded retries, failure counter, 304 handling all already pinned.
- **Watchlist noise (63)**: the PUSH path had NO tests — mute-ignored and
  threshold-off both survived (only the pull path was covered). Killed by
  driving handle_notify_watchers directly: loud user notified, over-threshold
  user silent, snoozed user silent. 5/5 die.

### §57.1 Estimate/compare logic audit (round 64)

Five mutants against pricing decision logic. Two survivors exposed real
holes: (a) the approved-beats-observed rule was guarded by a test whose
same-transaction timestamps TIED — ordering (and the assertion) was
nondeterministic; fixed with explicit timestamps. (b) rejected-price
exclusion in latest_prices was masked by the approved-preference rule;
killed with a no-approved-competitor scenario (rejected newest price must
never win). Sorting, missing-unit flagging and uptime incident counting were
already covered. 5/5 die.

## 58. Export-format compliance (2026-09-23, round 65)

Two live spec defects found by direct inspection:

- **ICS newline injection**: sanitize_text deliberately preserves newlines,
  and the calendar escaper handled commas/semicolons/backslashes but NOT
  newlines — a hostile entity name could fold the SUMMARY line and inject
  arbitrary ICS properties (ATTENDEE, ORGANIZER…). Fixed per RFC 5545
  (\r stripped, \n → literal \\n); injection test pins it.
- **Prometheus exposition non-compliance**: `# TYPE eco_gauge gauge` declared
  a metric that never appears, leaving every real metric untyped. Each metric
  now carries its own TYPE line; a compliance test asserts sample↔TYPE
  bijection.

### §58.1 Blind-review integrity audit (round 66)

Five mutants against the double-blind pipeline. Two real authz/integrity
holes: submit-ownership (reviewer A could submit reviewer B's assignment)
and double-submit (scores editable after submission — i.e. near reveal) had
NO tests. Killed: cross-reviewer submit → uniform 404; a submitted review is
frozen (resubmit → ECO_INVALID_TRANSITION). Identity-leak, foreign-reviewer
and score-range mutants were already covered. 5/5 die.

### §58.2 Scorecard & draft-validation audit (round 67)

Five mutants: freshness-never-fails, n/a-in-denominator, grade-always-healthy
and draft-validation-always-valid were already covered; the corroboration
floor was NOT — a single unverified source passing as "corroborated" went
undetected (both existing cases sat on either side of the boundary). Killed
with an exactly-one-source case pinning warn. 5/5 die.

## 59. Delivery-idempotency audit & sweep repair (2026-09-23, rounds 68-69)

- **HTTP matrix extension (68)**: the §39 authz matrix now covers the
  endpoints added since — replay, suite import and advisory status on the
  admin side; pricing history, uptime, score-history and the delta export on
  the member side; the Atom feed asserted by content type.
- **Worker idempotency (69)**: ALL FOUR duplicate-delivery mutants survived —
  the at-least-once outbox had exactly-once consumers with zero tests. Killed:
  double-delivering compute_impact yields ONE analysis; double-delivering
  notify_watchers yields ONE notification; the SLA re-stamp and rollout
  alert fingerprint each fire once.
- **LIVE DEFECT found by the audit**: evaluating→evaluating was not a legal
  rollout transition, so the §36 auto-evaluation sweep silently failed from
  its SECOND pass on (every plan raised, the alert stamp was dead code).
  Fixed: re-evaluation is idempotent, and the sweep captures the alert
  fingerprint BEFORE evaluate (evaluation rebuilds comparison from scratch,
  so reading it afterwards always saw None). Once-per-regression-set alerting
  now actually works and is race-tested.

## 60. Retention & scheduler audits (2026-09-23, rounds 70-71)

- **Retention (70)**: 4 mutants — two real holes: the keep-latest guard
  (an entity last probed before the cutoff would lose its ONLY status row,
  flipping current_status to unknown) and the raw-snapshot 90-day window
  (a zeroed window silently destroys replay) had no tests. Killed. 4/4 die.
- **Scheduler (71)**: ALL FOUR mutants survived — the continuous-discovery
  scheduler (the epic's first word) had NO tests: paused sources enqueued,
  interval ignored, never-synced never due, and the due boundary flipped were
  all invisible. Killed with a four-state semantics test (never-synced due
  now; fresh waits; overdue re-enqueues; paused never). 4/4 die.

## 61. LLM-safety & curation audits (2026-09-23, rounds 72-73)

- **LLM extraction (72)**: 5/5 mutants died first pass — confidence cap,
  boundary markers, extra=forbid schema, injection flagging and
  injection-output rejection are all pinned. No gaps.
- **Capability evidence & curation (73)**: three holes — force WITHOUT admin
  could downgrade evidence (authz), an unknown evidence level raised
  KeyError instead of 422, and curated conflict values skipped sanitization
  (NUL → JSONB 500 class). Killed with a three-part gate/hygiene test. 4/4 die.

## 62. Hard-compatibility gate audit (2026-09-23, round 74)

Five mutants against the replacement hard gate — FOUR survived: missing
capability, the input-direction subset check, the non-commercial license
gate and the license score direction all had no coverage (existing tests hit
only IO-output mismatch and blocked lifecycle). A recommended replacement
lacking a required capability, unable to accept the incumbent's inputs, or
commercially unusable could have shipped as "compatible". Killed with an
all-axes gate test (five candidates, one per axis + control) asserting each
failure code and the score direction. 5/5 die.

## 63. Approved-only signal audit (2026-09-23, round 75)

ALL FOUR mutants survived — the signal surface feeding the matching engine
and workforce intelligence (Part N: "raw observations never leak") had NO
gate tests: widening the lifecycle set, dropping the evidence floor to
vendor_claimed, badging from any evidence level, and removing the lifecycle
check entirely were all invisible. Killed with a three-entity contract test
(approved+verified appears; discovered lifecycle excluded; vendor-claimed
evidence excluded; badges never from vendor claims). 4/4 die.

## 64. Draft-generation safety audit (2026-09-23, round 76)

Three killable mutants — all survived: the generated steps' human
review_gate, the origin provenance (kind/source repo/graph hash) and the
CENTRAL safety promise "publishing the eco draft never publishes the pack"
(materialized WorkflowPack must be a PRIVATE DRAFT) had no tests. Killed:
every generated step carries review_gate=True; origin is fully traceable;
generation never pre-approves; the materialized pack is PackStatus.DRAFT +
PRIVATE. 3/3 die.

## 65. Release-edge sync audit (2026-09-23, round 77)

ALL FOUR mutants survived — and the audit exposed a LIVE broken endpoint:
`POST /graph/sync-release/{id}` read `release.definition`, an attribute the
release model does not have (the definition lives inside `manifest`), so the
endpoint raised AttributeError (HTTP 500) for EVERY real release since it
shipped — zero tests hid it completely. Fixed to read
`manifest["definition"]`; regression + killer test covers capability
dedup (duplicate → one edge), non-string skip, the requires_capability edge
type and the workflow_pack_release from-kind. 4/4 die.

## 66. Deep-link tests & cross-tenant org guards (2026-09-23, rounds 78-79)

- **Frontend regression (78)**: three new interaction tests — catalog Inspect
  restored purely from `?kind=&entity=` (shareable links actually restore),
  the estimator surfaces API errors instead of swallowing them, and failed
  runs show their machine error class inline.
- **CROSS-TENANT LEAKS FIXED (79)**: two org_id query parameters were honored
  without membership checks — any signed-in member could read ANY org's
  PRIVATE dependency edges (`/graph/node/...?org_id=`) and ANY org's
  component drafts including payloads (`/drafts?org_id=`). Both now require
  membership (or platform admin); non-members get 403/404, org-less calls
  keep the public/global scope. HTTP-matrix test pins both.

### §66.1 Remaining org guards (round 80)

The §66 sweep continued across every org_id parameter:

- **Draft single-read leak**: `GET /drafts/{id}` bypassed the org filter the
  LIST endpoint enforces — any signed-in user could read any org's draft
  payload by id. Non-members now get a UNIFORM 404 (no existence oracle);
  platform admins and members read normally.
- **Watchlist org attach**: any user could attach a watchlist to an arbitrary
  org, driving that org's WEBHOOK fan-out with their watch events. Membership
  now required; org-less watchlists unchanged.
  Draft write paths were verified admin-only; telemetry already gated. Both
  guards pinned in the HTTP matrix (member 404/403 + admin 200 + org-less 201).

## 67. Lifecycle-gate & noise-control-UI audits (2026-09-23, rounds 81-82)

- **Compliance/lifecycle gates (81)**: robots attestation was covered, but
  three gates were not — an ARCHIVED source could still sync, a retired suite
  could still run, and the run-target validation could vanish unnoticed.
  Killed with a three-gate test. 4/4 die.
- **Noise-control UI (82)**: the §24 controls had no interaction tests — the
  severity select now provably PATCHes min_severity and the mute button
  PATCHes a future muted_until timestamp (web 567).

## 68. LIKE-wildcard escaping (2026-09-23, round 83)

Four call sites interpolated user/curator text into LIKE/ILIKE patterns
unescaped — a search for "%" scanned everything and "50%_off" could never be
found literally (catalog search, global-search fallback, and the advisory
name/alias prefilters). New `escape_like` helper (backslash-escaped % _ \,
used with escape="\\") applied at all four sites; killers pin that
wildcards are literal (an entity named "50%_off-…" is found by its exact
name, by "%_off-…", never by unrelated text) and the helper's mapping.

## 69. Normalization-key & admin-action audits (2026-09-23, rounds 84-85)

- **normalize_name (84)**: the resolution key's length cap (unbounded keys
  defeat the alias index) and strict non-string rejection (str(dict) garbage
  keys would auto-merge junk) were untested — killed; 4/4 die (casefold and
  punctuation squash were already covered).
- **Admin action wiring (85)**: three UI interactions pinned — advisory
  registration POSTs the full structured payload (ref + range), suite import
  surfaces API rejections, and the duplicates scan renders suspected pairs
  with similarity (web 570).

## 70. Source-update & conflict-surfacing audit (2026-09-23/24, round 86)

ALL FIVE mutants survived initially:

- **base_url SSRF re-check** could be disabled — an admin update could point
  a source at an internal URL unvalidated (the create path was covered, the
  update path was not).
- **Adapter swap** could keep the stale parser_version (§11.5 provenance
  semantics silently broken) — killed with a stale-stamp-then-swap test
  (adapter versions coincide today, making a naive assertion equivalent).
- **Circuit breaker** could survive re-activation.
- **Conflicts** could report agreement as conflict (noise) and could
  represent a source by an OUTDATED observation — killed with a
  self-correcting-source case (both sources now agree ⇒ no conflict).
  5/5 die.

### §70.1 Price-extraction bounds (round 87)

Four extraction bounds were untested — negative prices, absurd prices
(>1e9), unknown units and unbounded currency strings all passed silently
(the unresolved-observation gate was covered). Killed with a mixed-payload
test: one valid entry survives (currency capped to 3 chars, uppercased),
the three bad entries drop. 5/5 die.

### §70.2 Impact-detail confidentiality (round 88)

The impact DETAIL view returns traversal nodes, which can include org-private
dependency-edge endpoints — it was member-readable. Tightened to
platform-admin (the list view's aggregate counts stay member-readable);
pinned in the HTTP authz matrix.

## 71. Untrusted-text sinks (2026-09-24, rounds 89-90)

Sweep of every user-text column assignment: two sinks were unscreened —
the rollout decision NOTE and the blind-review COMMENT both stored raw user
text (a NUL byte 500s at the column, R87 class). Both now pass sanitize_text;
killers pin NUL/control stripping plus rollout terminal-state freezing
(even abort is refused after reject). Lifecycle reasons were already
enum-gated; replacement rationales are internal constants.

### §71.1 PATCH bounds & query-boundary contracts (rounds 91-92)

- **Catalog PATCH** accepted unbounded, unscreened input: 10k-alias lists,
  unbounded external_ids, NUL in names/descriptions. Schema caps (50 aliases,
  50 external-id keys) + service-side sanitize on every field; killer pins
  screening and caps.
- **Query-boundary contract**: malformed `since`, out-of-range `days`,
  over-cap CSV `limit` and a raw-body NaN workload are all clean 4xx with the
  machine envelope — never 500s (HTTP-matrix pinned).

## 72. Create/update symmetry (2026-09-24, rounds 93-94)

Update paths must never be laxer than create paths:

- **update_suite** skipped text screening and numeric re-checks — a PATCH
  could set a NUL name, repeat_count 99 or a negative budget. Now symmetric
  with create_suite (screened text, 1..10 repeats, (0,10k] budget,
  status enum).
- **add_case** stored raw name/prompt and any weight — and the suite-IMPORT
  path (untrusted documents) relies on these service-level guards. Screened
  - weight bounded to (0, 10].
    Killers pin each screen/bound. (Source-update symmetry was closed in §70.)

## 73. Sink & dedupe hardening — rounds 96–98

Three more gaps closed by targeted review of remaining write paths:

1. **`io_spec` JSONB unbounded (capability mapping)** — `upsert()` stored the
   `io_spec` dict verbatim; a single mapping could balloon the row. Now bounded
   to 20 KB of serialized JSON (`VALIDATION_ERROR` 422). Defence in depth: the
   API is admin-only today, but service callers will include import paths.
2. **Watch-item dedupe bypass** — `add_item()` compared the _raw_ `target_ref`
   against stored rows, but persisted the _sanitized_ value. A control-char
   variant of an existing ref (`"vendor/model\x00"`) bypassed the §3.12
   uniqueness probe and inserted a duplicate watch item — doubling every
   notification for that target. The ref is now screened _before_ the probe.
3. **`scope_ref` DB-truncation 500-class** — `RolloutService.create()` stored
   `scope_ref` unscreened into a `varchar(26)` id column; anything longer hit
   an asyncpg `StringDataRightTruncationError` instead of a client error. Now
   sanitized and explicitly rejected over 26 chars with a 422.

Killers: `test_io_spec_size_bounded`, `test_watch_item_dedupe_uses_screened_ref`
(services), `test_rollout_scope_ref_is_screened` (amendments).

## 74. Manual-input & JSONB depth-guard sweep — rounds 102–104

The R96 io_spec finding generalized: every JSONB dict accepted from a request
is now bounded to 20 KB serialized, and the manual-observation endpoint was
brought up to the same hygiene bar as adapter ingestion.

1. **Manual observations (R102)** — `POST /observations` accepted any
   `event_type` string (now validated against `OBSERVATION_EVENT_TYPES`),
   stored `external_ref` unscreened (now `sanitize_text`), accepted an
   unbounded `normalized` payload (now 100 KB), and stored any
   `provenance_url` — which Discoveries renders as an `<a href>`, so a
   `javascript:` URL was a stored link-injection primitive. Now http(s)-only.
2. **Graph `constraint_spec` (R103)** and **benchmark `seed_settings` +
   source `config` (R104)** — all three stored verbatim in JSONB and replayed
   downstream (impact traversals, executor calls, sync fetches); each now
   capped at 20 KB serialized with a 422.

Killers: `test_manual_observation_input_hygiene` (http contract),
`test_constraint_spec_size_bounded`, `test_jsonb_depth_guards_round104`
(services).

### 74.1 Draft payload bound (round 105)

`DraftService.create` stored the draft `payload` dict verbatim after only
structural checks. Payloads embed whole workflow definitions, so the cap is
100 KB serialized (vs 20 KB for the smaller sinks). Killer:
`test_draft_payload_size_bounded`.

## 75. Operator-surface interaction coverage — rounds 95, 99–101, 106–107

Every mutating control on the ecosystem dashboard now has a wiring test that
pins the exact endpoint, method and body it emits (the class of bug these
catch — a button that renders but posts to the wrong path or drops a field —
is invisible to render-only tests):

- **Changes feed**: cursor load-more appends pages / hides at end; acknowledge.
- **Watchlists**: add item (kind+ref body shape), remove item by id.
- **Discoveries**: verify-all sends ONLY unverified ids; confirm/reject/LLM-
  suggest hit the specific candidate; LLM suggest offered only for NEW-entity
  proposals.
- **Blind review**: alias secrecy pre-reveal, score submit body, premature
  reveal surfaces the refusal instead of identities.
- **Pricing**: approve sends decision+provider_key; reject NEVER sends a
  provider key (no accidental billing mint).
- **Sources**: sync-now disabled unless active; pause/resume PATCH bodies;
  replay POST.

- **Catalog**: quick-watch body + Watching flip; lifecycle move carries the
  deprecation reason; merge disabled until a full 26-char survivor id.
- **Benchmarks**: compare disabled under 2 selections; running runs
  unselectable; compare GET carries exactly the selected ids.
- **Security**: mitigate/dismiss POST the transition; non-open advisories
  offer neither.

- **Components**: hard-incompatible candidates never approvable; draft
  approve/publish; rollout promote body; graph inspector typed-path GET with
  both directions rendered and no stray request without an id.
- **Error paths**: a failed mutation surfaces its ApiError message in the
  banner (not just happy paths).

Suites: ecosystem-changes-feed / watch-items / discoveries-actions /
blind-review / pricing-reconcile / source-controls / catalog-actions /
benchmark-compare / security / lifecycle-actions / graph-inspector
(web 597, tsc + eslint clean).

## 76. Advisory matching & semver-range audits — rounds 108–110

Mutation audits of the two subsystems that decide _who gets a security
notification_:

1. **Advisories (6 mutants)** — 4 killed by existing suites; 2 survived and
   got killers: (a) the per-entity watcher PUSH fan-out (`eco.notify_watchers`
   outbox enqueue) was only pull-tested — dropping `_fanout` survived; now the
   outbox row itself is asserted. (b) exact-vs-substring name matching was
   masked by the SQL prefilter; the killer routes a bystander through the
   alias-containment prefilter (alias contains the ref as a substring) and
   asserts it is rejected python-side.
2. **`version_in_range` (live fix + 7 mutants)** — comparison operators with
   an unparseable bound returned **False** ("provably safe") while `^`/`~`/
   bare paths returned None (fail open). A `>=1.0 <2.O` typo in a CVE range
   silently excluded affected entities. Fixed: every unparseable bound now
   fails OPEN. All operator boundaries were untested (7/7 mutants survived);
   an operator-semantics table now pins caret/tilde upper-exclusive lower-
   inclusive, `>=`/`<`/`<=`/`>` equality edges, and zero-padding of short
   versions. 6/7 killed; `matched_any` removal is provably equivalent
   (non-empty strip always yields a token) — documented, not pinned.

Killers: `test_advisory_watcher_push_fanout_enqueued`,
`test_advisory_name_match_is_exact_not_substring`,
`test_version_range_unparseable_bound_fails_open`,
`test_version_range_operator_semantics`.

## 77. Audit-trail completeness sweep — rounds 114–116

Property-based totality (round 114): `parse_version` is total over arbitrary
unicode and `version_in_range` never crashes or escapes {True, False, None}
for ANY range expression (Hypothesis).

Audit gap sweep (rounds 115–116): §14 requires irreversible ecosystem admin
actions in the immutable commercial audit trail, but nine mutating admin
endpoints emitted nothing — and `record_audit` silently swallows unregistered
actions, so a missing registry entry is as bad as a missing call. Now audited
AND registered:

- `eco.advisory_registered` (create was unaudited; only status changes were)
- `eco.edge_added` / `eco.edge_removed` (destructive graph surgery)
- `eco.source_created` / `eco.source_updated` (trust_level drives
  auto-resolution; adapter swaps re-stamp parsing)
- `eco.observation_manual_created`, `eco.observations_bulk_verified`
  (HITL verification gates downstream automation)
- `eco.suite_imported` (untrusted document becomes an executable suite)
- `eco.entity_updated` (canonical PATCH edits names/aliases/external ids)

Killer `test_admin_actions_are_audited_round115` round-trips every new action
through `eco_audit` and asserts the rows land — registration is the behavior
under test.

## 78. Org webhook noise controls + dead-code sweep — rounds 119–120

1. **Org webhook fan-out ignored §24 noise controls** — `handle_notify_watchers`
   filtered USER pushes by min_severity/muted_until but fired the ORG webhook
   for every matching watchlist: a muted or strict-threshold org watchlist
   still got called. Org fan-out now applies the same eligibility rule.
   Killer: `test_muted_org_watchlist_suppresses_webhook` (a muted org list and
   a security_critical-threshold org list both stay silent on a breaking
   change, while the positive-path webhook test still passes).
2. **Dead code removed** — `GraphService.dependents_of` had zero callers
   (impact traversal inlines the same reverse query); deleted rather than
   left as a divergence trap. A public-method↔test cross-reference sweep
   found no other unreferenced service methods.

## 79. Route-level systemic guards — rounds 122–124

Two invariants that previously lived only in review discipline are now
executable, failing at test time for any FUTURE endpoint that violates them:

1. **Every `limit` query parameter under /ecosystem declares a maximum** —
   an unbounded limit is a one-request table dump / OOM lever
   (`test_all_eco_limit_params_are_bounded`, walks the OpenAPI schema).
2. **Every /ecosystem route — reads included — resolves a User dependency**
   (`get_current_user` or `require_platform_admin`); a new route that forgets
   auth fails in CI, not in prod
   (`test_all_mutating_eco_routes_require_a_user`, walks the FastAPI
   dependency graph). A scan confirmed zero anonymous routes today.

## 80. Concurrent-consumer races — rounds 127–129

The §3.12/§13 dedupe guards were SELECT-then-insert: correct for sequential
redelivery (the earlier double-delivery killers), but two CONCURRENT sessions
both pass the probe. Three instances closed:

1. **Watch items (R127)** — no DB constraint backed the service probe; two
   racing `add_item` calls double-inserted (→ doubled notifications). Fix:
   migration `eco07a00007` adds two PARTIAL unique indexes (one per target
   column — NULLs defeat a single composite constraint) after de-duplicating
   existing rows; `add_item` catches `IntegrityError` and returns the winner.
   Race killer: two-session `asyncio.gather` asserts one row and equal ids.
2. **`handle_compute_impact` (R128)** — a unique constraint is wrong here
   (admin recompute legitimately adds fresh analyses), so concurrent workers
   serialize on `pg_advisory_xact_lock('eco-impact:<change>')`. Removing the
   lock is a verified-killed mutant (the race manifests reliably).
3. **`handle_notify_watchers` (R129)** — same pattern,
   `'eco-notify:<change>'`; lock-removal mutant likewise killed.

## 81. Browser E2E verification — round 131

First real-browser verification of the epic: `e2e/sweep-ecosystem.spec.ts`
ran GREEN (3/3) against a live worktree stack (uvicorn :8001 + next start
:3001 with the new server-only `API_PROXY_URL` rewrite override — unlike
`NEXT_PUBLIC_API_URL` it is never inlined into the client bundle, so the
production `connect-src 'self'` CSP still holds):

1. All 12 ecosystem routes render their h1 for a plain member, no crashes.
2. Watchlist lifecycle end-to-end through the real UI: create list → add
   github_repo ref item → mute (badge appears) → remove item.
3. Catalog quick-watch flips to "Watching" (or the empty state shows on a
   fresh stack).

Playwright lessons recorded: React-rerendering rows make `click()` hang on
stability — `dispatchEvent("click")` delivers through React's root listener
reliably; form Enter-submit was flaky vs clicking the submit button.

## 82. Decision-point row locks — rounds 132–133

Continuation of the §80 race sweep into human decision points:

1. **`ResolutionService.confirm` (R132)** — no row lock: two admins racing to
   confirm the same NEW-entity candidate both saw "pending" and each minted
   its own canonical entity (the second alias registration then hit the
   unique constraint as a 500). `confirm` and `reject` now take
   `refresh(with_for_update=True)` before the status check; the two-session
   race killer asserts exactly one entity and one 409 loser. Lock-removal
   mutant verified KILLED.
2. **`DraftService.update_payload` (R133)** — the status check ("editable
   only while draft/in_review") ran without a lock, so an edit racing the
   approve→publish transition could mutate a just-published draft's payload.
   Now locked; the race killer publishes and edits concurrently and asserts
   the published payload is unchanged whenever the edit lost.

## 83. Hot-path indexes, error-contract guard & estimator currency safety — rounds 137–142

1. **Hot-path indexes (R137, migration eco08)** — the notify fan-out probed
   `eco_watch_items` by bare `target_id` (only the watchlist_id prefix was
   indexed) and the watch feed read `eco_change_events` by bare
   `canonical_entity_id` (the existing composite leads with entity_kind):
   both were seq scans ON EVERY CHANGE EVENT at production scale. Verified
   with EXPLAIN before/after (`enable_seqscan=off` on the small dev table);
   the new (canonical_entity_id, detected_at) index also absorbs the
   ORDER BY via a backward index scan. Schema-presence killer added.
2. **AppError code↔status guard (R139)** — an AST walk over the ecosystem
   package asserts every literal `AppError(code, msg, status)` pairs its
   machine code with the matching HTTP status (NOT_FOUND=404 etc.); clients
   switch on the code, so a mismatched pair breaks them silently. Layering
   scan confirmed zero service-layer commits.
3. **Scorecard semantics (R141)** — both check-boundary mutants survived
   (deprecated-passes-lifecycle, single-source-passes-corroboration); a
   semantics killer pins fail/warn boundaries. Both re-verified KILLED.
4. **Estimator currency safety (R142)** — `estimate` summed line totals
   ACROSS CURRENCIES (a USD token price plus a EUR image price produced a
   meaningless `estimated_total`). Mixed-currency entities now get
   `estimated_total: null` + `mixed_currency: true` with lines still
   itemized.

### 83.1 Supply-chain audit & internal-source races (rounds 145–146)

- `pip-audit` over the full backend environment: **no known vulnerabilities**
  (npm audit unavailable through the configured registry mirror — noted, not
  actionable in-repo).
- Two more internal-source get-or-creates raced on their unique names
  (`internal:availability-probes` in the status-flip emitter,
  `internal:benchmark-lab` in the benchmark change emitter) — same class as
  R130; both serialized with per-name advisory locks. Concurrency killer
  drives two simultaneous status-flip emits and asserts one source row and
  no unique-violation 500.

## 84. Quality-engineering ledger (rounds 1–150)

Summary table for reviewers — what was systematically verified and how:

| Technique                    | Coverage                                                                                                                                          | Outcome                                                                                   |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Targeted mutation audits     | ~45 subsystems, ~190 mutants                                                                                                                      | All non-equivalent mutants killed; 3 documented equivalents                               |
| Live defects found by audits | 20+ (semver fail-closed CVE matching, ICS injection, sync-release 500, 4 cross-tenant org leaks, watch dedupe bypass, cross-currency totals, …)   | All fixed with killers                                                                    |
| Concurrency races            | 9 closed (rollout decide, blind reveal, merge, watch add, impact/notify consumers, confirm, payload-vs-publish, 3× internal-source get-or-create) | Row locks / advisory locks / partial unique indexes; lock-removal mutants verified killed |
| Input hygiene                | Every user-text sink sanitized; every request JSONB bounded; create/update symmetric                                                              | HTTP boundary contracts pinned                                                            |
| Authz                        | Uniform-404, org-membership guards, 29-pair OpenAPI surface, all-routes-require-user + bounded-limit AST/route guards                             | Executable invariants                                                                     |
| Audit trail                  | 10 previously-unaudited admin actions registered + emitted                                                                                        | Round-trip killer                                                                         |
| Ops                          | Per-metric typed Prometheus exposition; docs↔metrics parity test; alert runbook; 5 crons off-peak                                                 |                                                                                           |
| Property-based               | Hypothesis totality over stats/version parsing/adapters/sanitizers                                                                                | Found the Unicode-digit crash                                                             |
| Browser E2E                  | 12 routes + watchlist lifecycle + quick-watch, green against a live stack                                                                         | `sweep-ecosystem.spec.ts`                                                                 |
| Performance                  | Hot-path EXPLAIN audit; 2 missing per-event indexes added CONCURRENTLY                                                                            | eco08                                                                                     |
| Supply chain                 | pip-audit clean                                                                                                                                   |                                                                                           |

Test counts at this writing: backend regression 6277, eco subset 485,
web unit 601, browser e2e 3 — all green at every push.

### 84.1 Browser accessibility audit (round 151)

`e2e/a11y-ecosystem.spec.ts` runs axe-core (WCAG 2.0 A/AA) over all 12
ecosystem routes against a live stack and fails on serious/critical
violations. First run found ONE: the workload-estimator textarea on the
compare page had no accessible label — fixed with `aria-label`. Re-run green
across all 12 pages; the functional sweep stays 3/3.

### 84.2 Price-history retention (rounds 152–153)

`prune_ecosystem_history` covered availability probes, sync runs and raw
snapshots but NOT price observations — one row per sync per unit, unbounded.
Unreviewed rows older than 180 days are now pruned (estimates use the latest
row; the trend window is 90 days); DECIDED rows are kept as billing-mint
audit evidence. Killer proves the decided row of the same age survives.
E2E beforeAll timeouts raised to 120s (registration + UI login exceed 60s
under load — observed flake).

## 85. Per-entity Atom feeds — rounds 157–158

GitHub `releases.atom` posture: watching a specific model should mean
subscribing to THAT model's changes, not the firehose.

- `GET /export/changes.atom?entity_id=<26>` narrows the feed to one canonical
  entity (served by the R137 `(canonical_entity_id, detected_at)` index);
  XML escaping unchanged. Killer proves inclusion/exclusion + escaping.
- The catalog Inspect panel now offers a "subscribe (.atom)" link and a
  "view changes" deep link; the changes page reads `?entity=`, narrows the
  query (badged), and threads the filter through cursor pagination. The whole
  loop is browser-verified: `sweep-ecosystem` test 4 clicks Inspect → view
  changes and asserts the filtered feed (e2e 4/4, a11y still green).
- FastAPI lesson: a plain `Query(None, ...)` default leaks the Query object
  into direct (non-HTTP) test calls — `Annotated[str | None, Query(...)] = None`
  keeps the bare default.
- Test-hygiene regression caught in-flight: the R146 killer's committed
  ProbeRace versions accumulated (10 across runs) and CROWDED OUT the
  replacement-candidate top-10 pool, breaking two latency tests. The killer
  now retires its fixtures in `finally`; one-time purge applied. This is the
  second instance of the committed-fixture class — every future race killer
  must self-clean BOTH the version and its parent model.

## 86. Complete catalog export + entity navigation loop — rounds 162–168

1. **Navigation loop completed (162–166)**: every surface that names a
   canonical entity now links into the loop — watched items, advisory
   affected entities, impact roots → entity-filtered change feed; discovery
   merge candidates → catalog Inspect ("view target"). Catalog `?entity=`
   deep links now resolve entities BEYOND the loaded pages via the
   single-entity GET (they were silently dropped before). Browser-verified
   (sweep 4/4 + a11y 12/12 after every UI change).
2. **Catalog export completeness (168)** — `/catalog/export` capped each
   kind at its first 100 rows with NO truncation signal, handing downstream
   consumers (the LiteLLM-manifest posture) a silently incomplete catalog.
   It now pages through everything (500/page, 10k flagged ceiling) and
   stamps `entity_totals` + `truncated` so drift is detectable. Killer
   exports 105 entities and asserts all 105 land. Round 169 applies the same
   flagged-ceiling rule to capability mappings and approved prices (the old
   code silently sliced both at 2000).

### 86.1 Suite size bound (round 171)

Round 172 applies the same rule to watchlists (100 per owner — every list
joins the matching_changes aggregation). `add_case` had no per-suite count cap — every case multiplies run cost
(× repeat_count) and portable-export size. Bounded at 500 with a 422
(`test_suite_case_count_is_bounded`); export/list paths already return all
cases, which stays correct under the cap.

## 87. Search-to-inspect + bulk triage — rounds 173–174

1. **Global search hits were a dead end** (name + score, nothing clickable):
   every hit now deep-links into the catalog Inspect panel via `?entity=`
   (kind-mapped; the R165 deep-page fallback applies), closing the last
   navigation gap: search → inspect → changes → subscribe.
2. **Bulk acknowledge (§11.1 parity)** — the change-triage queue only had
   per-row acknowledge while observations had bulk-verify. New
   `POST /changes/bulk-acknowledge` (≤100 ids, idempotent, missing ids
   reported, audited as `eco.changes_bulk_acknowledged`) with an
   "Acknowledge all shown" button that sends ONLY unacknowledged ids.
   Route ordering pinned by the killer (the literal path must not be
   captured by `/{change_id}/acknowledge`).

### 87.1 Same-page deep-link bugs (round 178)

The browser test for search→inspect caught TWO real bugs unit tests missed:
the catalog deep-link effect only depended on `[pages]`, so a SAME-PAGE
query change (clicking a search hit while already on /catalog) never fired;
and `if (entityId && !selected)` refused to SWITCH the panel when another
entity was already inspected. Both fixed (`[pages, params]` deps;
`entityId !== selected?.id`); e2e 6/6 including the new
search-hit → Inspect flow, a11y still green.

### 87.2 Final browser verification (rounds 179–180)

Inspect panel gained an aria-labeled close button (it could only be
dismissed by switching segments). Final full-stack browser run: functional
sweep 5/5 (pages, watchlist lifecycle, quick-watch, catalog→changes deep
link, search-hit→Inspect) + a11y 12/12 — 6/6 green.

## 88. Org watchlists reach the UI — rounds 181–184

Org-attached watchlists (whose matching changes fan out over the org's
webhooks, §13/§24) existed only at the API — the UI could create personal
lists exclusively, making the whole webhook path unreachable by hand.

- Create form gains an org selector (personal by default); `org_id` is sent
  in the POST body (null for personal) — both killer-tested.
- Rows show an "org" badge with a fan-out tooltip (previously personal and
  org lists were indistinguishable); `WatchlistResponse.org_id` verified
  present.
- Browser-verified end to end: sweep test 6 creates an org via the API
  helper, creates an org-attached list through the real form, and asserts
  the badge (e2e 7/7, a11y 12/12).

### 88.1 Org lists are org assets (round 185)

Management of an org-attached watchlist was creator-only — a departed
creator locked the org's webhook configuration. `get_owned` now grants
management to the org's OWNER/ADMIN as well (uniform 404 preserved for
plain members and outsiders; personal lists stay strictly owner-only).
Killer covers all four personas.

### 88.2 Org lists are a shared radar (round 186)

`matching_changes` (the pull feed) only aggregated lists the user OWNS — an
org watchlist's changes were visible to its creator alone, while the org
webhook fired for everyone. Org members' pull feeds now include their orgs'
attached lists (killer: plain member sees the change, outsider does not).

### 88.3 Regression signal-to-noise: the 8-hex birthday flake (round 188)

Two consecutive full runs each had ONE transient non-eco failure
(`SLUG_ALREADY_EXISTS` on org creation). Root cause measured, not guessed:
the dev database has accumulated **394k organizations** and 61 test files
named orgs with `uuid4().hex[:8]` — at that population every full run has a
~4% birthday-collision chance. All 61 files widened to 16 hex; the two
previously-failing files re-ran 149/149 green.

### 88.4 LLM extraction reaches the UI (round 190)

§14 HITL LLM extraction existed only as an API. The Discoveries page now
offers the flow: pick a manual/internal source (adapter feeds are excluded
from the selector), paste untrusted text, extract — with copy that makes the
posture explicit ("proposals still require human verification below;
nothing auto-merges"). Killer pins the POST body, the double gating
(source + text), and the source-type filtering.

## 89. Delta-feed tie loss — rounds 193–194

Round 193 pinned cursor-pagination completeness on the change feed (walk by
cursor == full set, no repeats). The same property applied to the DELTA
export found a real data-loss bug: the cursor was a bare
`detected_at > since`, and batch-inserted change events share one
server-default timestamp — rows tied with the page boundary were silently
dropped for every delta consumer. The cursor is now lexicographic on
(detected_at, id): responses carry `next_since_id` alongside `next_since`,
the query resumes with an OR-tie clause, and timestamp-only callers keep the
old strictly-greater semantics. Killer: three same-stamp rows, page size 2,
follow the cursor — all three arrive.

## 90. Dead-handler wiring — round 198

A caller-graph sweep found three REGISTERED outbox handlers with zero
production enqueue sites — promised automation that never ran:

1. `eco.telemetry_window` (§28's "fresh telemetry is automatically compared
   against benchmarks") — new hourly cron `eco_telemetry_sweep` (minute 58)
   enqueues the previous complete hour; snapshot uniqueness keeps re-enqueues
   idempotent.
2. `eco.check_availability` (§11.3's "probed independently of syncs") — new
   cron `eco_availability_sweep` (minutes 14/44) enqueues probes for every
   id-backed WATCHED entity (watchers are exactly who status flips matter
   to), capped at 200/round.
3. `eco.generate_candidates` — now event-driven: transitioning an entity to
   `deprecated` enqueues candidate generation in the same transaction.

Killers: outbox-row assertions for all three paths plus source-level cron
pins. Lesson recorded: a registered handler is not a feature — the
caller-graph sweep (enqueue-site count per topic) is now part of the audit
repertoire.

### 90.1 Probe telemetry surfaces (rounds 201–203)

Handler-level killers for the newly-wired sweeps (probe recorded / clean
skip; window aggregation idempotent under double delivery; malformed payload
no-op). With probes now cron-driven, `availability_unreachable` (entities
whose LATEST probe is unreachable, DISTINCT ON per entity) joins the
overview, /ops/metrics (docs↔metrics parity killer auto-covers it), the
alert runbook, and an alerting stat card on the dashboard.

### 90.2 Telemetry-window self-healing (round 208)

The hourly sweep only enqueued the previous hour — a crashed worker's missed
hours were lost forever. It now looks back 6 hours every run; the snapshot
unique constraint makes re-enqueued windows no-ops, so recovery is free and
idempotent.
