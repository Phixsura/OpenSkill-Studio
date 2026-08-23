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
- **WorkflowPackRelease** — immutable snapshot: `manifest` JSONB (`{schema_version, version, name, summary, workflow_type, definition, dependencies, provenance}`), `checksum` = sha256 over the canonical (sorted-keys) manifest JSON, `step_count`, structured `deprecated_by`. The `ui` block (editor layout) is **excluded** from the manifest so layout changes never invalidate releases.
- **WorkflowPackInstallation** — org install of a release; `local_definition` holds the forked copy when status = FORKED. Unique per (org, pack); REMOVED rows are reactivated on reinstall.

Status/visibility enums are reused from ADR-009 (`pack_status`, `pack_visibility`, `install_status`).

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
| `WF_GRAPH_CYCLE` | Kahn detection; `meta.cycle_steps` names the participants |
| `WF_INPUT_UNSATISFIED` | Required input port with no incoming edge |
| `WF_UNREACHABLE_STEP` | No path from any entry step |
| `WF_EXPR_INVALID` | Moustache reference to unknown input/step output |
| `WF_DUPLICATE_EDGE_ID` | Duplicate edge id |
| `WF_TOO_LARGE` | Any size cap exceeded |
| `WF_DATA_URI_REJECTED` | Inline data URI / base64 blob |
| `WF_VALIDATION_FAILED` | Envelope code (422) carrying the details array |

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

Concurrency discipline (R11): **every transition is a conditional UPDATE with an expected-status guard**; zero rows updated means a lost race and the loser backs off silently. `definition_snapshot` is frozen at run creation — running workflows never observe definition changes. Run creation supports an idempotency key (partial unique index).

- **Review gates** suspend as durable `WorkflowStepReview` rows (a decision is persisted state, never an ephemeral event) with a **mandatory `due_at`** (1–30 days, default 7). Decisions are synchronous validate-then-accept under a row lock; double-decide returns 409 `WF_REVIEW_ALREADY_DECIDED` (partial unique index on open reviews). Approve passes the subject through; reject fails the step (`WF_REVIEW_REJECTED`).
- **provider_action** steps write `provider_request_id` + `offering_id` + a lease **and commit before the outbound call** (write-ahead idempotency, R13). Credentials are decrypted only at this point (ADR-011). Timeout via `workflow_step_timeout_seconds`; failures retry up to `max_attempts` (output cleared on re-claim).
- **Outputs are capped at 48 KB** per step (Airflow XCom lesson); media flows as asset references.
- **Execution model (Phase 1)**: tracked `asyncio` background tasks with their own DB sessions, drained on shutdown (`drain_workflow_tasks`). The ARQ worker is the planned Phase-2 flip — zero schema change required.
- **Lazy sweeper** (`sweep_stale`): triggered on run-detail reads; recovers crashed executors (expired lease → `WAITING_RETRY`, `WF_EXECUTOR_CRASHED`) and expires overdue reviews (`WF_REVIEW_TIMEOUT`). No resident scheduler process.
- Every lifecycle change appends a `WorkflowRunEvent` row (append-only audit trail).

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
- Published releases are immutable; edits ship as new releases.
- Installation never auto-installs dependencies and never auto-connects providers.
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
