# ADR-010: Workflow Packs & Execution Runtime

## Status: Accepted

## Context

ADR-009 established versioned distribution for *teaching* content (Skill Packs). Issue #21 requires the same distribution semantics for *production* content: reusable AI-visual workflows (e.g. "E-commerce Hero Image Production", "Storyboard-to-Video Pipeline") that organizations can install, upgrade, fork, and — unlike Skill Packs — actually **execute**.

Two hard requirements shape the design:

1. **No arbitrary code execution.** Community-workflow ecosystems that allow code in shared units can only mitigate, never prevent, supply-chain attacks (n8n community nodes "can do anything, including malicious actions"; ComfyUI CVE-2024-21575/21576/21577 demonstrated RCE from crafted workflow JSON alone). The no-code-execution guarantee must live in the schema, not in review policy.
2. **Human review must be a first-class workflow step**, not a bolt-on — production pipelines need approval gates that suspend execution durably.

## Decision

### Data Model — the pack trio (mirrors ADR-009)

- **WorkflowPack** — publishable pack with metadata plus a mutable working `definition` JSONB and derived `input_schema`/`output_schema` caches. Owned by an organization. `CHECK octet_length(definition::text) <= 262144`.
- **WorkflowPackRelease** — immutable snapshot: `manifest` JSONB (`{schema_version, version, name, summary, workflow_type, definition, dependencies, provenance}`), `checksum` = sha256 over the canonical (sorted-keys) manifest JSON, `step_count`, structured `deprecated_by`. The `ui` block (editor layout) is **excluded** from the manifest so layout changes never invalidate releases. `dependencies.requires_capabilities` is **derived at publish time** from the definition's `provider_action` steps (capability + required_features, unioned with the caller's declaration) — trusting the client list alone would let a publisher omit a capability and silently bypass the install gate (ADR-011), deferring the failure to a mid-run `NO_ELIGIBLE_PROVIDER`.
- **WorkflowPackInstallation** — org install of a release; `local_definition` holds the forked copy when status = FORKED. Unique per (org, pack); REMOVED rows are reactivated on reinstall.

Status/visibility enums are reused from ADR-009 (`pack_status`, `pack_visibility`, `install_status`). Public-registry reads gate PUBLIC packs on `review_status` approved (rejected/pending → 404), and the unauthenticated preview **strips org-internal binding details** (`pinned_offering_id`, `binding_mode`) from step configs. Anonymous registry endpoints serve **public-only response models** — no `review_status`, `rejection_reason` (the moderator's private note), `owner_org_id`, `created_by`, or release `released_by` reaches an unauthenticated caller; the release-list query `defer()`s the manifest column (the response carries no manifest body, and an author can publish unbounded releases). Paginated list/search queries carry a ULID **tiebreak** on their sort key — OFFSET over a non-unique key (and the 5-min ids-only search cache) would otherwise skip/duplicate rows on timestamp ties. Archiving an organization archives its workflow packs — a dead org's public packs do not stay live and installable.

### Definition contract (pure data, closed vocabulary)

```
7 step types:  instruction | prompt_template | asset_input | transform |
               provider_action | review_gate | output
8 I/O types:   text | prompt | image | video | audio | reference_asset |
               json | selection
```

- `steps[]` carry immutable slug ids (`^[a-z][a-z0-9_]{0,63}$`), display names separate, typed input/output ports.
- `edges[]` are first-class objects (`{id, from_step, from_port, to_step, to_port}`) — wiring never keys on display names.
- **Expressions** are a closed moustache grammar: only `{{inputs.KEY}}` and `{{steps.ID.outputs.PORT}}`, fully resolved and checked at validation time. No functions, no eval.
- **Coercion matrix**: automatic type coercion is identity + `prompt↔text` only. Everything else requires an explicit `transform` step (whitelisted operations: `crop`, `resize`, `concat_text`, `select_field`).
- **Size caps**: ≤50 steps, ≤150 edges, ≤20 inputs/outputs, ≤16 KB per step config, ≤256 KB total.
- **Assets by reference only**: `data:` URIs and base64 blobs ≥1 KB are rejected anywhere in the payload.

### Validation — all errors in one pass

Validation accumulates every error (Argo pattern), each with a JSON pointer and machine code:

| Code | Meaning |
|---|---|
| `WF_SCHEMA_INVALID` | Top-level shape fails Pydantic parsing |
| `WF_INVALID_STEP_ID` / `WF_DUPLICATE_STEP_ID` | Slug regex violation / duplicate id |
| `WF_INVALID_PORT` / `WF_DUPLICATE_PORT` | Port name violations |
| `WF_CONFIG_INVALID` | Per-step-type config schema violation (discriminated union) |
| `WF_EDGE_UNKNOWN_STEP` / `WF_EDGE_UNKNOWN_PORT` | Dangling edge references |
| `WF_EDGE_TYPE_MISMATCH` | Port types not coercible (meta carries from/to types) |
| `WF_GRAPH_CYCLE` | Kahn detection over explicit edges + implicit template-ref edges; `meta.cycle_steps` names the participants, `meta.implicit=true` when the cycle closes through a moustache reference |
| `WF_INPUT_UNSATISFIED` | Required input port with no incoming edge |
| `WF_PORT_MULTIPLE_EDGES` | More than one edge into the same input port (pointer names the extra edge) |
| `WF_EXPR_INVALID` | Moustache reference to unknown input/step output |
| `WF_EXPR_SELF_REF` | Step's template references its own output (can never resolve) |
| `WF_DUPLICATE_EDGE_ID` | Duplicate edge id |
| `WF_INVALID_OUTPUT_KEY` / `WF_DUPLICATE_OUTPUT_KEY` | Workflow output key grammar violation / duplicate key |
| `WF_OUTPUT_PORT_MISMATCH` | Output step input/output port counts differ (positional pairing; single input may fan out) — pairwise types must also be coercible (`WF_EDGE_TYPE_MISMATCH`) |
| `WF_INVALID_DEFAULT` | Input default would fail create_run's per-type checks: json default not an object/array, oversize text/asset default, nested past 64 levels, or (after json.loads) materialized control chars or NaN/Infinity floats |
| `WF_SELECTION_BAD_DEFAULT` | Selection input default outside its options |
| `WF_TOO_LARGE` | Any size cap exceeded |
| `WF_DATA_URI_REJECTED` | Inline data URI / base64 blob (media-type parameters and omitted mediatype do not evade the match) |
| `WF_VALIDATION_FAILED` | Envelope code (422) carrying the details array |

An inputless island step is deliberately **valid** — every node of an acyclic graph roots at an entry step, so a dedicated "unreachable step" check can never fire (cyclic graphs are already `WF_GRAPH_CYCLE`, input-starved steps are already `WF_INPUT_UNSATISFIED`).

Run-creation codes: `INSTALLATION_NOT_FOUND` (404, includes REMOVED installs), `MISSING_INPUT` / `UNKNOWN_INPUT` / `INVALID_INPUT_VALUE` / `WF_INPUT_TOO_LARGE` (422), `WF_TOO_MANY_ACTIVE_RUNS` (422 — org-wide cap of `workflow_max_concurrent_runs` PENDING/RUNNING/WAITING_REVIEW runs; every active run can be mid-provider-call spending money, so creation is a spend gate. Soft limit, checked after the idempotency lookup so retries of an existing run still succeed at the cap). Cancellation is scoped: only the run's initiator (`started_by`) or an instructor+ may cancel it (`RUN_CANCEL_FORBIDDEN` 403) — a run mid-provider-call spends money, so a peer must not be able to kill or grief it. Run **reads** are scoped the same way (mirroring project submission visibility): a non-instructor's list returns only their own runs and a peer's run detail 404s — run inputs/outputs carry the initiator's prompts and private asset references. Install codes: `ALREADY_INSTALLED` (409, also the loser of a concurrent-install race), `CAPABILITY_UNSATISFIED` (422, ADR-011).

### Execution runtime

**Run state machine** (`workflow_runs.status`):

```
PENDING ──► RUNNING ◄──────────► WAITING_REVIEW
               │
               ├──► COMPLETED
               ├──► FAILED       (error_code, e.g. WF_STEP_FAILED)
               └──► CANCELLED    (also reachable from PENDING/WAITING_REVIEW)
```

**Step state machine** (`workflow_step_runs.status`, 9 states):

```
PENDING ──► READY ──► RUNNING ──► COMPLETED
   │                    │  │
   │                    │  ├──► WAITING_REVIEW ──► COMPLETED | FAILED
   │                    │  └──► WAITING_RETRY ──► READY (attempt+1)
   │                    └──► FAILED (attempts exhausted / non-retryable)
   └──► SKIPPED (any upstream FAILED/SKIPPED/CANCELLED)
   (any non-terminal state ──► CANCELLED on run cancellation)
```

Concurrency discipline (R11): **every transition is a conditional UPDATE with an expected-status guard**; zero rows updated means a lost race and the loser backs off silently. `definition_snapshot` is frozen at run creation — running workflows never observe definition changes. Run creation supports an idempotency key (partial unique index), rejects REMOVED installations (404), and validates input **values** per declared type — selection values must be in `options`, text/prompt/json capped at 8,000 chars, asset references at 500 chars (`INVALID_INPUT_VALUE` 422) — on top of presence/unknown-key checks (`MISSING_INPUT` / `UNKNOWN_INPUT`) and the 48 KB total input cap.

- **Review gates** suspend as durable `WorkflowStepReview` rows (a decision is persisted state, never an ephemeral event) with a **mandatory `due_at`** (1–30 days, default 7). Decisions are synchronous validate-then-accept under a row lock and **role-gated to OWNER/ADMIN/INSTRUCTOR** — review gates approve real provider spend, so run initiators (students) cannot self-approve. Double-decide returns 409 `WF_REVIEW_ALREADY_DECIDED` (partial unique index on open reviews). Approve passes the subject through; reject fails the step (`WF_REVIEW_REJECTED`).
- **provider_action** steps write `provider_request_id` + `offering_id` + a lease **and commit before the outbound call** (write-ahead idempotency, R13). After that commit the executor re-reads the step status (a concurrent cancel may have flipped it the instant the row lock released) and bails before spending provider money; the read transaction is closed before the outbound call so no connection sits idle-in-transaction for the call's duration. Credentials are decrypted only at this point (ADR-011). Timeout via `workflow_step_timeout_seconds`; failures retry up to `max_attempts` (output cleared on re-claim). Every settlement UPDATE carries the claimed attempt as a **fencing token** — a resurrected executor cannot settle a newer attempt.
- **Outputs are capped at 48 KB** per step (Airflow XCom lesson) and **screened for NUL/control characters AND non-finite floats (NaN/Infinity)** before the JSONB write (`WF_OUTPUT_INVALID` — an unscreened value would crash asyncpg on the JSONB insert, 22P05 for control chars / 22P02 for NaN, and strand the step RUNNING with a live lease); media flows as asset references. The same NUL/control-char + NaN/Infinity screen applies to all JSONB write surfaces — run inputs, requirement profiles, provider config/limits, pack provenance — since stdlib `json.loads` accepts bare `NaN`/`Infinity` tokens that the default serializer re-emits verbatim. An empty-dict output (`{}` — instruction steps, adapters with nothing to say) is a valid output, distinct from "no output yet".
- **Execution model (Phase 1)**: tracked `asyncio` background tasks with their own DB sessions, drained on shutdown (`drain_workflow_tasks`). The advance loop is an in-memory continuation over durable state, so it has a **durable re-dispatch trigger**: reading a non-terminal run re-dispatches its advance loop (conditional claims make this idempotent) — a crash or deploy between commit and dispatch can no longer strand a run. The ARQ worker is the planned Phase-2 flip — zero schema change required.
- **Lazy sweeper** (`sweep_stale`): triggered on run-detail reads (and a platform-wide `POST /admin/workflows/sweep` for the cron/operator path); recovers crashed executors (expired lease → `WAITING_RETRY`, `WF_EXECUTOR_CRASHED`; attempts exhausted → `WF_RETRY_EXHAUSTED` — `max_attempts` holds on the crash path too), expires overdue reviews (`WF_REVIEW_TIMEOUT`) with a guarded UPDATE that can never overwrite a concurrently committed decision, and **recovers stalled runs** — a run left PENDING/RUNNING with no live executor (no step RUNNING under an unexpired lease, e.g. a crash/deploy between `create_run`'s commit and `dispatch_advance`, or a task drained at shutdown). Stalled runs are surfaced past a grace window and re-dispatched; without this they never recover via cron and count toward `workflow_max_concurrent_runs` forever (permanent `WF_TOO_MANY_ACTIVE_RUNS`). The sweep returns every touched `run_id` and callers re-dispatch each one (idempotent — advance uses conditional status-guarded claims) — repairing step state without resuming the loop would strand the run. No resident scheduler process.
- Every lifecycle change appends a `WorkflowRunEvent` row (append-only audit trail).

**Runtime error codes** (step/run `error_code`, distinct from the publish-time
validation table above): `WF_STEP_FAILED` (run-level: some step exhausted its
attempts), `WF_STEP_ERROR` (unexpected executor exception, retryable),
`WF_PROVIDER_ERROR` / `WF_PROVIDER_TIMEOUT` (adapter call failed / exceeded
`workflow_step_timeout_seconds`, retryable), `WF_OUTPUT_TOO_LARGE` (48 KB cap),
`WF_OUTPUT_INVALID` (NUL/control chars in adapter output),
`WF_UNKNOWN_STEP_TYPE` (defensive — validation should make it unreachable),
`WF_EXECUTOR_CRASHED` / `WF_RETRY_EXHAUSTED` (sweeper), `WF_REVIEW_TIMEOUT`
(review overdue), `WF_REVIEW_REJECTED` (reviewer rejected), `WF_CANCELLED`
(run cancelled). Two additional request-level 422 codes:
`WF_INVALID_CHARACTER` (NUL/control chars anywhere in a submitted definition)
and `WF_SELECTION_NO_OPTIONS` (selection input declared without options —
validation-table companion to `WF_SELECTION_BAD_DEFAULT`).

### ComfyUI import — parse-only, never execute

Imports (JSON or PNG with embedded tEXt/iTXt `workflow`/`prompt` chunks, pure-Python chunk walker) are treated strictly as untrusted data:

1. 5 MB pre-parse cap; ≤2000 nodes / ≤10000 links structural cap.
2. Lenient dual-format detection (UI `nodes[]+links[]` / API `{id: {class_type, inputs}}`) — tolerance at ingestion, strictness at publication.
3. Extraction only: custom node class_types (vs a vendored 73-node core snapshot), model file references (`.safetensors/.ckpt/...`) with `whitelist`/`structural` confidence labels, input/output nodes, detected capabilities (14-entry `NODE_CAPABILITY_MAP`).
4. Byte-exact original stored with sha256 in `comfyui_imports` (immutable provenance); node titles pass through `sanitize_untrusted_text`.
5. Optional draft-pack creation maps detected capabilities to `provider_action` steps and quarantines unknown custom nodes into an inert `instruction` step — always landing as a DRAFT requiring human confirmation.
6. The import service performs **zero network I/O** (test-enforced): no execution, no pip, no model downloads, no URL resolution.

## Red Lines

- No arbitrary code execution in workflows — ever. The step vocabulary is closed; adding a step type requires a new ADR.
- Published releases are immutable; edits ship as new releases. Public visibility is only reachable through the review flow — `APPROVAL_REQUIRED` on a direct request for public visibility at **both create and update** (the workflow-pack create schema simply omits `visibility`; the skill-pack twin, which does accept it, rejects `visibility=public` at create as well as PUT — completing the gate on both paths so create-then-publish cannot list an unapproved pack that the registry treats `review_status IS NULL` as grandfathered). Editing an approved-public pack's definition (or any registry-facing card field) resets its approval — and the same reset fires while a pack is **pending review** (R84): a card/definition edit or new release during the review window returns the pack to draft, so a reviewer can never approve content the author swapped in after submitting (a review-window TOCTOU). `approve` also clears any stale `rejection_reason` from a prior reject→resubmit cycle. **Publishing a new release also resets approval** (R83): the anon registry preview serves the *latest* release manifest (skills/exercises for skill packs; definition, dependencies, recommended_packs for workflow packs), so a v2 published on an approved pack would otherwise carry `approved` onto never-reviewed content — a new release must re-enter review before it is publicly discoverable. The card-field set that voids approval must cover **every field the anonymous registry serializes** (`Public*Response`) — a hand-picked subset let `estimated_minutes`/`language`/`learning_outcomes`/`provenance` (skill) and `provenance` (workflow) be swapped past the gate while the pack stayed approved+public (R82); the void set now tracks the public response model. All pack mutations (update / definition / delete / publish / submit / approve / reject) run under a row lock refreshed to committed state, so a concurrent card edit cannot slip past the approval gate.
- Installation never auto-installs dependencies and never auto-connects providers. `upgrade` / `rollback` / `diff` re-check pack access at call time (`_check_pack_access`), and a pack the owner has **archived** (soft-deleted) is 404 even to its own org — consistent with `install` and `get_pack`, so a soft-deleted pack cannot be operated on.
- Imported ComfyUI content is never executed and its dependencies are never fetched.

## Consequences

### Positive

- The RCE class that hit ComfyUI/n8n is structurally impossible: definitions are data validated against a closed vocabulary.
- Reproducible runs: frozen snapshots + append-only events + checksummed releases give a full audit chain from output back to definition version.
- Conditional-UPDATE discipline makes double-execution and double-charge races lose deterministically.
- Editor layout churn never invalidates releases (ui excluded from checksum).

### Negative

- The transform whitelist means real media operations (crop/resize) are pass-through in Phase 1 — actual processing needs adapter/capability work.
- Tracked-task execution ties step execution to API process lifetime; long-running provider calls block graceful shutdown up to the drain timeout (mitigated by the lease + sweeper; resolved by the Phase-2 ARQ flip).
- The lazy sweeper means a crashed executor is only recovered when someone reads the run (acceptable at Phase-1 scale; a cron hitting the sweep endpoint hardens it).
