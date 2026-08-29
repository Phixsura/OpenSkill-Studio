# ADR-011: Provider Capability Abstraction

## Status: Accepted

## Context

Workflow steps must not hard-code vendors or models: AI tools change faster than curricula, and a workflow pinned to one vendor dies with that vendor's API. Issue #21 requires steps to reference *capabilities* (`image_generation`, `image_to_video`, …) that organizations satisfy with whatever providers they have connected — while guaranteeing that provider credentials never leak into definitions, manifests, exports, or API responses.

Industry precedent (LiteLLM's `mode` field, OpenRouter's model catalog, HuggingFace's `pipeline_tag`, Kubernetes device plugins) converges on the same shape: a closed capability taxonomy as the join key, with a separate adapter/config/offering/credential split.

## Decision

### Capability taxonomy — a reference table, not a Python enum

`capability_tags` is seeded by migration with deterministic ULIDs and extended only through curated migrations (platform) or `x-<org-slug>.`-prefixed org extensions (excluded from global matching):

| key | category | io_signature |
|---|---|---|
| `image_generation` | generation | prompt → image |
| `image_editing` | editing | image+prompt → image |
| `image_to_video` | generation | image+prompt → video |
| `text_to_video` | generation | prompt → video |
| `video_editing` | editing | video → video |
| `voice_generation` | audio | text → audio |
| `multimodal_review` | review | image+prompt → json |
| `upscale` | editing | image → image |
| `background_removal` | editing | image → image |

Each capability carries a `contract_version` (bumped when its feature-key contract changes). Closed ≠ frozen: the vocabulary grows by migration review, never by free-form publisher tags — free tags never reach hard filters.

### Four-entity provider split

```
ProviderAdapter        platform code catalog: key, config_schema,
   │                   credential_fields (NAMES only — never values)
   ▼
ProviderConnection     org-scoped: adapter + non-sensitive config +
   │                   credential_id (reference), status, health fields
   ▼
ProviderModelOffering  the MATCHABLE unit: capability_key + model_name +
   │                   features[] + limits + cost_per_call_usd + quality_tier
   ▼
OrgCredential          Fernet envelope-encrypted {field: value} JSON
```

Rationale: matching operates on *offerings* (capability + features + cost), connections carry org configuration, adapters carry code, and credentials are an isolated write-only store. No entity mixes concerns. Offering create **and update** enforce the same value bounds (cost 0–9999.999999 — the `Numeric(10,6)` column maximum, validated on the ROUNDED value since Postgres rounds to 6 fraction digits at insert; NaN/inf rejected; model name 1–200 chars, ≤20 features of ≤64 chars, limits ≤5 KB) — partial updates cannot bypass validation. Explicit `null` on a nullable field (e.g. `cost_per_call_usd`) CLEARS it; an absent field leaves it unchanged (`exclude_unset` semantics).

### Credential contract (write-only, late decryption)

- Credential values are accepted on connection create/update, encrypted with Fernet (`CREDENTIAL_ENCRYPTION_KEY`, required in production; dev derives from the JWT secret), and **never returned by any endpoint** — responses carry only `credential_id`.
- **Key rotation**: `CREDENTIAL_ENCRYPTION_KEY` accepts comma-separated Fernet keys — the FIRST encrypts, all decrypt (`MultiFernet`); rotate by prepending a new key and re-encrypting lazily. Key format is validated at **boot** (config validator), never silently substituted: a malformed key must fail startup, not brick every stored credential at first use.
- An empty credentials dict (`{}`) is a client mistake, rejected 422 `EMPTY_CREDENTIALS` on create AND update (omit the key entirely to mean "no credentials"). Explicit `"credentials": null` on update detaches and deletes the connection's credential row.
- Field names smuggled into non-sensitive `config` are rejected (`CREDENTIAL_IN_CONFIG` 422); fields the adapter did not declare are rejected (`UNKNOWN_CREDENTIAL_FIELD` 422).
- Decryption happens in exactly one place: inside the workflow executor, immediately before the adapter call. Definitions, manifests, exports, and job rows carry references only.
- Deleting a connection deletes its credential row.
- LLM-backed adapters treat step inputs as **untrusted** (user run inputs, upstream step outputs, public-pack template text): values are sanitized (`sanitize_untrusted_text` — zero-width/bidi/ASCII-smuggling strip) and wrapped in per-call random boundary markers referenced by the system prompt, same discipline as the requirement-extraction prompt builder (D10).

### Binding ladder (auto / preferred / pinned)

Each `provider_action` step in an installation gets a `workflow_step_bindings` row resolving which offering executes it:

1. **pinned** in the step config (`pinned_offering_id`): that offering or nothing — unavailable means hard stop (`allow_fallbacks: false` semantics).
2. **confirmed binding** for the installation+step (human-confirmed, `confirmed_by`): used if still active; a stale *pinned* binding is a hard stop.
3. **auto**: cheapest active offering for the capability whose `features` are a superset of the step's `required_features`.

Bindings are **revalidated at execution time** — a disabled connection or deactivated offering yields `BINDING_STALE` / `NO_ELIGIBLE_PROVIDER` step failure rather than silently switching providers. Execution-time revalidation re-checks the offering serves the step's **current capability**, not just that it is active: because a kept-but-stale pin (below) survives an upgrade that changed the step's capability, the resolver must re-verify `offering.capability_key` or it would run a wrong-capability offering on the credential path (R82). A pinned binding whose offering row was deleted (FK SET NULL) is a **hard stop**, never a silent fallback to auto-selection. The offering actually used is recorded on every step run (`offering_id` = actual_offering_used). On upgrade, a human-confirmed binding is preserved only if it **still passes the full confirm-time check against the NEW step** — same capability, offering active, connection active, and every `required_features` the (possibly-changed) step now declares. A binding that no longer satisfies the upgraded step (e.g. the step added a `required_features` its offering lacks) is dropped and re-suggested — checking capability alone would let a stale binding survive and defer the failure to a mid-run `NO_ELIGIBLE_PROVIDER`, exactly what confirm-time validation exists to prevent. **Exception: a stale confirmed PIN is kept and flagged (`BINDING_STALE` gap), never dropped** — deleting it would replace the row with an unconfirmed auto-mode suggestion and the runtime's auto rung would silently execute on a provider the org never chose, violating pinned's this-offering-or-nothing contract; the run hard-stops until a human re-confirms or re-pins.

### Capability gate on install — never auto-connect

Installing a workflow pack checks the release manifest's `dependencies.requires_capabilities` against the org's *active* offerings (feature-superset match). Unsatisfied requirements fail the install with 422 `CAPABILITY_UNSATISFIED` and a structured gaps list naming each missing capability/feature. The requirement list carries one entry **per distinct (capability, feature-set)**, never a per-capability feature UNION (R83): the runtime resolves each step against its own `required_features` (one offering per step), so unioning two steps' features would demand a single offering superseting both and falsely block a pack the runtime can run from two separate offerings. A provider_action's `capability` is non-empty by construction (`min_length=1`), so an unset capability fails at definition save rather than silently deriving an empty requirement the gate would skip and the runtime could never match.

The platform **never** auto-connects a provider to satisfy a gap: auto-connecting a provider is this platform's equivalent of auto-purchasing, and it is a red line. Upgrades re-run the same gate (and re-check pack visibility/approval — a pack gone private after install cannot be upgraded by non-owners). Concurrent installs of the same pack race safely: the loser gets 409 `ALREADY_INSTALLED` via unique-constraint recovery, never a 500.

### Phase-1 adapters

- `mock` — deterministic echo (same inputs → same output hash), no credentials, no network. Powers tests, demos, and local development.
- `anthropic` — `multimodal_review`; declares `credential_fields: ["api_key"]` and **requires the org's own key** — the adapter constructs its client directly from the decrypted org credential and never falls back to the platform key (the offering's `model_name` is org-controlled, so a platform-key fallback would let any org burn the platform LLM budget with arbitrary models). `model_name` is additionally allowlisted to `claude-*` ids.

Adapters implement one contract: `execute(capability, model_name, inputs, config, credentials, idempotency_key) -> dict`. Retry policy lives in the runtime, not the adapter. Health checks are manual/endpoint-triggered — never in the request path.

## Consequences

### Positive

- Workflows survive vendor churn: swapping providers is an org-level offering change, not a pack edit.
- Credential exposure surface is a single decryption call site; the leak-test sweep (`test_issue21_security.py`) asserts secrets appear in no read endpoint.
- Cost-aware auto-binding gives sensible defaults while pinning preserves author intent with fail-fast semantics.
- The offerings table doubles as the provider-resolution candidate pool for the matching engine (ADR-012) with no extra modeling.

### Negative

- A closed taxonomy requires governance: new capabilities need a migration + review (deliberate friction).
- Feature-superset matching is exact-string; rich constraint matching (resolution ranges, duration limits) is deferred — `limits` JSONB is stored but not yet enforced at binding time.
- Phase 1 has no background health probing; a dead provider surfaces only at execution (mitigated by retry + BINDING_STALE reporting).
