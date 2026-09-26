"""Pydantic request/response schemas for the ecosystem API (ADR-016 Part R)."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ── Requests ────────────────────────────────────────────────────────


class CreateSourceRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    source_type: str = Field(max_length=40)
    trust_level: str = Field(max_length=20)
    adapter_key: str = Field(max_length=64)
    base_url: str | None = Field(default=None, max_length=2000)
    config: dict = Field(default_factory=dict)
    sync_interval_minutes: int = Field(default=1440, ge=5, le=43200)
    rate_limit_per_hour: int = Field(default=60, ge=1, le=3600)
    robots_compliant: bool = True


class UpdateSourceRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    trust_level: str | None = None
    # §11.5: a dead/replaced vendor is a config change — swap the adapter
    adapter_key: str | None = Field(default=None, max_length=64)
    base_url: str | None = Field(default=None, max_length=2000)
    config: dict | None = None
    sync_interval_minutes: int | None = Field(default=None, ge=5, le=43200)
    rate_limit_per_hour: int | None = Field(default=None, ge=1, le=3600)
    max_response_bytes: int | None = Field(default=None, ge=1024, le=52_428_800)
    timeout_seconds: int | None = Field(default=None, ge=1, le=300)
    status: str | None = None
    robots_compliant: bool | None = None


class SyncSourceRequest(BaseModel):
    # Manual/analyst payload (bypasses fetch); bounded upstream by security guard
    payload: dict | list | None = None


class ManualObservationRequest(BaseModel):
    source_id: str = Field(min_length=26, max_length=26)
    event_type: str = Field(max_length=40)
    entity_kind: str | None = Field(default=None, max_length=30)
    external_ref: str | None = Field(default=None, max_length=500)
    normalized: dict = Field(default_factory=dict)
    provenance_url: str | None = Field(default=None, max_length=2000)


class UpdateCatalogEntityRequest(BaseModel):
    canonical_name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    aliases: list[str] | None = Field(default=None, max_length=50)
    external_ids: dict | None = Field(default=None, max_length=50)


class ConfirmResolutionRequest(BaseModel):
    target_entity_id: str | None = Field(default=None, min_length=26, max_length=26)


class BulkIdsRequest(BaseModel):
    """ADR-016 §11.1 bulk review operations (≤100 per call)."""

    ids: list[str] = Field(min_length=1, max_length=100)


class BulkDecideRequest(BaseModel):
    ids: list[str] = Field(min_length=1, max_length=100)
    decision: str = Field(max_length=10)  # confirm | reject


class ResolveConflictRequest(BaseModel):
    """§14 curation: arbitrate one conflicting field with provenance."""

    field: str = Field(max_length=40)
    chosen_value: str = Field(min_length=1, max_length=300)
    winning_source_id: str | None = Field(default=None, min_length=26, max_length=26)


class LLMExtractRequest(BaseModel):
    """§14: LLM-assisted extraction from untrusted free text (HITL — every
    resulting observation still requires human verification)."""

    source_id: str = Field(min_length=26, max_length=26)
    text: str = Field(min_length=1, max_length=20_000)
    entity_kind: str = Field(default="model", max_length=30)


class LifecycleTransitionRequest(BaseModel):
    to_status: str = Field(max_length=20)
    reason: str | None = Field(default=None, max_length=40)
    note: str | None = Field(default=None, max_length=2000)


class UpsertMappingRequest(BaseModel):
    entity_kind: str = Field(max_length=30)
    entity_id: str = Field(min_length=26, max_length=26)
    capability_key: str = Field(max_length=64)
    evidence_level: str = Field(default="vendor_claimed", max_length=30)
    io_spec: dict = Field(default_factory=dict)
    confidence: float = Field(default=0.5, ge=0, le=1)
    source_observation_id: str | None = None
    force: bool = False


class ReconcilePriceRequest(BaseModel):
    decision: str = Field(max_length=20)  # approve | reject | under_review
    provider_key: str | None = Field(default=None, max_length=50)
    model_or_service: str | None = Field(default=None, max_length=200)


class CreateSuiteRequest(BaseModel):
    key: str = Field(min_length=1, max_length=64, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    name: str = Field(min_length=1, max_length=200)
    family: str = Field(max_length=40)
    capability_key: str = Field(max_length=64)
    description: str | None = Field(default=None, max_length=2000)
    rubric: list = Field(default_factory=list)
    human_review_policy: dict | None = None
    automated_metrics: list = Field(default_factory=list)
    budget_usd_cap: float = Field(default=10.0, gt=0, le=10000)
    repeat_count: int = Field(default=3, ge=1, le=10)


class UpdateSuiteRequest(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    rubric: list | None = None
    human_review_policy: dict | None = None
    automated_metrics: list | None = None
    budget_usd_cap: float | None = Field(default=None, gt=0, le=10000)
    repeat_count: int | None = Field(default=None, ge=1, le=10)
    status: str | None = None


class CreateCaseRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    prompt: str = Field(min_length=1, max_length=20000)
    reference_assets: list = Field(default_factory=list)
    constraints: dict = Field(default_factory=dict)
    weight: float = Field(default=1.0, gt=0, le=10)
    sort_order: int = 0


class CreateRunRequest(BaseModel):
    target: dict
    budget_usd_cap: float | None = Field(default=None, gt=0, le=10000)
    seed_settings: dict = Field(default_factory=dict)
    execute_now: bool = False


class CreateReviewBatchRequest(BaseModel):
    suite_id: str = Field(min_length=26, max_length=26)
    run_ids: list[str] = Field(min_length=2, max_length=8)
    reviewer_ids: list[str] = Field(min_length=1, max_length=20)
    blind: bool = True


class SubmitReviewRequest(BaseModel):
    scores: dict[str, float]
    comment: str | None = Field(default=None, max_length=4000)


class AddEdgeRequest(BaseModel):
    from_kind: str = Field(max_length=40)
    from_id: str = Field(min_length=1, max_length=26)
    to_kind: str = Field(max_length=40)
    to_id: str = Field(min_length=1, max_length=26)
    constraint_type: str = Field(default="uses", max_length=40)
    constraint_spec: dict = Field(default_factory=dict)
    org_scoped: bool = False


class ComputeImpactRequest(BaseModel):
    change_event_id: str = Field(min_length=26, max_length=26)


class GenerateCandidatesRequest(BaseModel):
    deprecated_kind: str = Field(max_length=40)
    deprecated_id: str = Field(min_length=26, max_length=26)
    weights: dict[str, float] | None = None
    limit: int = Field(default=10, ge=1, le=50)


class DecisionRequest(BaseModel):
    decision: str = Field(max_length=20)
    note: str | None = Field(default=None, max_length=2000)


class CreateDraftRequest(BaseModel):
    draft_type: str = Field(max_length=40)
    title: str = Field(min_length=1, max_length=300)
    payload: dict
    source_kind: str | None = Field(default=None, max_length=40)
    source_id: str | None = None
    org_id: str | None = None


class UpdateDraftPayloadRequest(BaseModel):
    payload: dict


class GenerateWorkflowDraftRequest(BaseModel):
    external_workflow_id: str = Field(min_length=26, max_length=26)
    org_id: str | None = None


class GenerateSkillUpdateDraftRequest(BaseModel):
    target_pack_id: str = Field(min_length=26, max_length=26)
    deprecated_kind: str = Field(max_length=40)
    deprecated_id: str = Field(min_length=26, max_length=26)
    replacement_id: str | None = None
    affected: list = Field(default_factory=list)


class CreateRolloutRequest(BaseModel):
    replacement_candidate_id: str = Field(min_length=26, max_length=26)
    scope_type: str = Field(max_length=30)
    scope_ref: str | None = None
    # §11.4: {"min_samples": int>=0, "thresholds": {dimension: max_regression}}
    guardrails: dict | None = None


class CreateWatchlistRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    org_id: str | None = None


class AddWatchItemRequest(BaseModel):
    target_kind: str = Field(max_length=30)
    target_id: str | None = Field(default=None, min_length=26, max_length=26)
    target_ref: str | None = Field(default=None, max_length=300)


# ── Responses (from_attributes serializers) ────────────────────────


class _Orm(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class SourceResponse(_Orm):
    id: str
    name: str
    source_type: str
    trust_level: str
    base_url: str | None
    adapter_key: str
    parser_version: str
    config: dict
    sync_interval_minutes: int
    rate_limit_per_hour: int
    status: str
    last_sync_at: datetime | None
    last_success_at: datetime | None
    consecutive_failures: int
    robots_compliant: bool
    created_at: datetime


class SyncRunResponse(_Orm):
    id: str
    source_id: str
    started_at: datetime
    finished_at: datetime | None
    status: str
    http_status: int | None
    bytes_fetched: int
    observations_created: int
    changes_detected: int
    error: str | None
    parser_version: str


class ObservationResponse(_Orm):
    id: str
    source_id: str
    event_type: str
    entity_kind: str | None
    external_ref: str | None
    canonical_entity_id: str | None
    canonical_entity_kind: str | None
    observed_at: datetime
    effective_at: datetime | None
    raw_hash: str
    normalized: dict
    parser_version: str
    confidence: float
    provenance_url: str | None
    extraction_method: str
    human_verified: bool
    superseded_by_id: str | None


class ChangeEventResponse(_Orm):
    id: str
    observation_id: str
    change_type: str
    field: str
    old_value: dict | None
    new_value: dict | None
    severity: str
    entity_kind: str | None
    canonical_entity_id: str | None
    detected_at: datetime
    acknowledged: bool


class CatalogEntityResponse(_Orm):
    id: str
    canonical_name: str
    lifecycle_status: str
    external_ids: dict
    aliases: list
    # R220: curated facts (conflict arbitrations etc.) live in the `extra`
    # attribute (column "metadata") — expose them as `metadata`
    metadata: dict = Field(default_factory=dict, validation_alias="extra")
    # R254: set on single-entity reads when a supersedes edge exists — old
    # deep links land on the retired duplicate and the UI offers the survivor
    merged_into: str | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True, extra="allow")


class ResolutionCandidateResponse(_Orm):
    id: str
    observation_id: str
    entity_kind: str
    candidate_entity_id: str | None
    match_method: str
    confidence: float
    proposed_payload: dict
    status: str
    created_at: datetime


class MappingResponse(_Orm):
    id: str
    entity_kind: str
    entity_id: str
    capability_key: str
    evidence_level: str
    io_spec: dict
    confidence: float
    verified_at: datetime | None


class PriceObservationResponse(_Orm):
    id: str
    observation_id: str
    entity_kind: str
    entity_id: str
    region: str | None
    unit: str
    price: float
    currency: str
    tier: dict | None
    effective_at: datetime | None
    observed_at: datetime
    reconciliation_status: str
    approved_cost_rate_id: str | None


class AvailabilityResponse(_Orm):
    id: str
    entity_kind: str
    entity_id: str
    region: str | None
    record_type: str
    value: dict
    observed_at: datetime


class SuiteResponse(_Orm):
    id: str
    key: str
    name: str
    description: str | None
    family: str
    capability_key: str
    rubric: list
    human_review_policy: dict
    automated_metrics: list
    budget_usd_cap: float
    repeat_count: int
    status: str
    created_at: datetime


class CaseResponse(_Orm):
    id: str
    suite_id: str
    name: str
    prompt: str
    reference_assets: list
    constraints: dict
    weight: float
    sort_order: int


class RunResponse(_Orm):
    id: str
    suite_id: str
    status: str
    target: dict
    budget_usd_cap: float
    total_cost_usd: float
    dimension_scores: dict
    error: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime


class ResultResponse(_Orm):
    id: str
    run_id: str
    case_id: str
    repeat_index: int
    output_assets: list
    latency_ms: int | None
    usage: dict
    cost_usd: float
    retries: int
    failed: bool
    error: str | None
    automated_scores: dict


class TelemetrySnapshotResponse(_Orm):
    id: str
    entity_kind: str
    entity_id: str
    window_start: datetime
    window_end: datetime
    org_id: str | None
    sample_size: int
    metrics: dict


class EdgeResponse(_Orm):
    id: str
    from_kind: str
    from_id: str
    to_kind: str
    to_id: str
    constraint_type: str
    constraint_spec: dict
    org_id: str | None


class ImpactAnalysisResponse(_Orm):
    id: str
    change_event_id: str
    root_kind: str
    root_id: str
    classification: str
    summary: dict
    deadline_at: datetime | None
    computed_at: datetime
    status: str


class ImpactItemResponse(_Orm):
    id: str
    node_kind: str
    node_id: str
    depth: int
    path: list
    active_usage: dict
    recommended_action: str


class ReplacementCandidateResponse(_Orm):
    id: str
    deprecated_kind: str
    deprecated_id: str
    candidate_kind: str
    candidate_id: str
    score: float
    hard_compatible: bool
    hard_failures: list
    score_breakdown: dict
    explanation: list
    status: str
    created_at: datetime


class DraftResponse(_Orm):
    id: str
    draft_type: str
    title: str
    payload: dict
    source_kind: str | None
    source_id: str | None
    validation: dict
    status: str
    org_id: str | None
    published_ref: str | None
    created_at: datetime


class RolloutResponse(_Orm):
    id: str
    replacement_candidate_id: str
    scope_type: str
    scope_ref: str | None
    guardrails: dict
    baseline: dict
    candidate_metrics: dict
    comparison: dict
    status: str
    note: str | None
    created_at: datetime


class WatchlistResponse(_Orm):
    id: str
    owner_id: str
    org_id: str | None
    name: str
    min_severity: str
    muted_until: datetime | None
    created_at: datetime


class WatchItemResponse(_Orm):
    id: str
    watchlist_id: str
    target_kind: str
    target_id: str | None
    target_ref: str | None


class LifecycleTransitionResponse(_Orm):
    id: str
    entity_kind: str
    entity_id: str
    from_status: str
    to_status: str
    reason: str | None
    note: str | None
    created_at: datetime


class GenericData(BaseModel):
    data: Any

class EstimateRequest(BaseModel):
    """Workload cost estimate across entities (advisory, never a quote)."""

    model_config = ConfigDict(extra="forbid")

    entity_kind: str = Field(..., max_length=30)
    entity_ids: list[str] = Field(..., min_length=1, max_length=20)
    # unit -> quantity, e.g. {"token_input": 1000000, "token_output": 200000}
    workload: dict[str, float] = Field(..., min_length=1, max_length=10)


class UpdateWatchlistRequest(BaseModel):
    """Noise controls: severity threshold + snooze (ADR-016 §24)."""

    model_config = ConfigDict(extra="forbid")

    min_severity: str | None = Field(default=None, max_length=30)
    muted_until: datetime | None = None
    clear_mute: bool = False


class QuickWatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_kind: str = Field(max_length=30)
    target_id: str = Field(min_length=26, max_length=26)


class CreateAdvisoryRequest(BaseModel):
    """Structured security advisory registration (ADR-016 §38)."""

    model_config = ConfigDict(extra="forbid")

    advisory_ref: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=300)
    severity: str = Field(max_length=10)
    affected_ref: str = Field(min_length=1, max_length=300)
    affected_kind: str | None = Field(default=None, max_length=30)
    affected_range: str | None = Field(default=None, max_length=100)
    fixed_in: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=5000)
    source_observation_id: str | None = Field(default=None, min_length=26, max_length=26)


class AdvisoryResponse(_Orm):
    id: str
    advisory_ref: str
    title: str
    severity: str
    description: str | None
    affected_kind: str | None
    affected_ref: str
    affected_range: str | None
    fixed_in: str | None
    status: str
    created_at: datetime
