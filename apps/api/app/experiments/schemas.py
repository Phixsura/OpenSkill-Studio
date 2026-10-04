"""Pydantic schemas for the experiments API (ADR-017).

Request models reject unknown fields (extra="forbid" — the R300 posture: a
typo'd field must 422, never silently drop). The full ExperimentSpec is
validated in the SERVICE layer (not as a request body type) so ethics gates
raise typed AppErrors instead of surfacing through request-parsing.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.experiments.security import (
    ANALYSIS_TYPES,
    DESIGNS,
    POPULATION_OPS,
    SEQUENTIAL_METHODS,
    STATS_ENGINES,
    UNIT_TYPES,
)

# ── Base ─────────────────────────────────────────────────────────────


class _StrictReq(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ── Immutable spec (validated server-side in ExperimentService) ──────


class PopulationRule(_StrictReq):
    field: str = Field(min_length=1, max_length=64)
    op: str = Field(max_length=20)
    values: list[str | int | float | bool] = Field(default_factory=list, max_length=200)

    @field_validator("op")
    @classmethod
    def _op_known(cls, v: str) -> str:
        if v not in POPULATION_OPS:
            raise ValueError(f"unknown population op: {v} (allowed: {sorted(POPULATION_OPS)})")
        return v


class PopulationSpec(_StrictReq):
    rules: list[PopulationRule] = Field(default_factory=list, max_length=20)
    exclusions: list[PopulationRule] = Field(default_factory=list, max_length=20)


class VariantSpec(_StrictReq):
    key: str = Field(min_length=1, max_length=40, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    name: str = Field(min_length=1, max_length=200)
    weight_bp: int = Field(ge=1, le=10_000)
    is_control: bool = False
    config: dict[str, Any] = Field(default_factory=dict)


class GuardrailSpec(_StrictReq):
    metric_key: str = Field(min_length=1, max_length=64)
    op: str = Field(max_length=3)
    threshold: float
    window_hours: int = Field(default=24, ge=1, le=720)

    @field_validator("op")
    @classmethod
    def _op_known(cls, v: str) -> str:
        if v not in ("lte", "gte"):
            raise ValueError("guardrail op must be lte or gte")
        return v

    @field_validator("threshold")
    @classmethod
    def _finite(cls, v: float) -> float:
        # Non-finite floats crash JSONB encoding at the DB boundary (R86)
        if v != v or v in (float("inf"), float("-inf")):
            raise ValueError("threshold must be finite")
        return v


class MetricsSpec(_StrictReq):
    primary: list[str] = Field(min_length=1, max_length=5)
    secondary: list[str] = Field(default_factory=list, max_length=20)
    guardrails: list[GuardrailSpec] = Field(default_factory=list, max_length=20)


class PowerSpec(_StrictReq):
    mde: float = Field(gt=0, lt=1)
    alpha: float = Field(default=0.05, gt=0, lt=0.5)
    power: float = Field(default=0.8, gt=0.5, lt=1)
    estimated_n_per_variant: int | None = Field(default=None, ge=1)


class StopPolicySpec(_StrictReq):
    max_days: int = Field(default=28, ge=1, le=365)
    max_looks: int = Field(default=4, ge=1, le=50)


class VarianceReductionSpec(_StrictReq):
    """§4.6 v3 (round 113): multi-covariate CUPED. `covariate_metrics` is
    the list form (1-3, deduped); the singular `covariate_metric` stays for
    back-compat and means a one-element list. Exactly one form is given."""

    method: str = Field(max_length=20)
    covariate_metric: str | None = Field(default=None, min_length=1, max_length=64)
    covariate_metrics: list[str] | None = Field(default=None, min_length=1, max_length=3)
    lookback_days: int = Field(default=28, ge=1, le=365)

    def covariates(self) -> list[str]:
        if self.covariate_metrics:
            return self.covariate_metrics
        return [self.covariate_metric] if self.covariate_metric else []

    @model_validator(mode="after")
    def _exactly_one_form(self) -> "VarianceReductionSpec":
        if bool(self.covariate_metric) == bool(self.covariate_metrics):
            raise ValueError(
                "variance_reduction takes exactly one of covariate_metric "
                "or covariate_metrics"
            )
        if self.covariate_metrics:
            if len(set(self.covariate_metrics)) != len(self.covariate_metrics):
                raise ValueError("covariate_metrics must be unique")
            for key in self.covariate_metrics:
                if not (1 <= len(key) <= 64):
                    raise ValueError("covariate metric keys must be 1-64 chars")
        return self

    @field_validator("method")
    @classmethod
    def _method_known(cls, v: str) -> str:
        if v != "cuped":
            raise ValueError("variance_reduction.method must be 'cuped'")
        return v


class TriggerSpec(_StrictReq):
    analysis_population: str = Field(default="assigned", max_length=10)
    note: str | None = Field(default=None, max_length=500)

    @field_validator("analysis_population")
    @classmethod
    def _pop_known(cls, v: str) -> str:
        if v not in ("assigned", "exposed"):
            raise ValueError("trigger.analysis_population must be assigned or exposed")
        return v


class SwitchbackSpec(_StrictReq):
    switch_unit: str = Field(min_length=1, max_length=40)
    window_minutes: int = Field(default=60, ge=5, le=10_080)
    washout_minutes: int = Field(default=0, ge=0, le=1440)


class ExperimentSpec(_StrictReq):
    """The immutable versioned specification (ADR-017 §4.2)."""

    hypothesis: str = Field(min_length=10, max_length=2000)
    unit_type: str = Field(max_length=24)
    population: PopulationSpec = Field(default_factory=PopulationSpec)
    variants: list[VariantSpec] = Field(min_length=2, max_length=10)
    metrics: MetricsSpec
    power: PowerSpec | None = None
    design: str = Field(default="parallel", max_length=12)
    switchback: SwitchbackSpec | None = None
    allocation_mode: str = Field(default="fixed", max_length=8)
    stats_engine: str = Field(default="frequentist", max_length=12)
    sequential: str = Field(default="msprt", max_length=16)
    variance_reduction: VarianceReductionSpec | None = None
    # §4.8 v2: opt-in snapshot breakdown dimensions ("org" only for now,
    # user units only — the mapping is OrgMember)
    segments: list[str] = Field(default_factory=list, max_length=3)
    trigger: TriggerSpec = Field(default_factory=TriggerSpec)
    stop_policy: StopPolicySpec = Field(default_factory=StopPolicySpec)
    analysis_type: str = Field(default="randomized", max_length=14)

    @field_validator("unit_type")
    @classmethod
    def _unit_known(cls, v: str) -> str:
        if v not in UNIT_TYPES:
            raise ValueError(f"unknown unit_type: {v} (allowed: {sorted(UNIT_TYPES)})")
        return v

    @field_validator("design")
    @classmethod
    def _design_known(cls, v: str) -> str:
        if v not in DESIGNS:
            raise ValueError(f"unknown design: {v} (allowed: {sorted(DESIGNS)})")
        return v

    @field_validator("allocation_mode")
    @classmethod
    def _alloc_known(cls, v: str) -> str:
        if v not in ("fixed", "bandit"):
            raise ValueError("allocation_mode must be fixed or bandit")
        return v

    @field_validator("stats_engine")
    @classmethod
    def _engine_known(cls, v: str) -> str:
        if v not in STATS_ENGINES:
            raise ValueError(f"unknown stats_engine: {v}")
        return v

    @field_validator("sequential")
    @classmethod
    def _seq_known(cls, v: str) -> str:
        if v not in SEQUENTIAL_METHODS:
            raise ValueError(f"unknown sequential method: {v}")
        return v

    @field_validator("analysis_type")
    @classmethod
    def _analysis_known(cls, v: str) -> str:
        if v not in ANALYSIS_TYPES:
            raise ValueError(f"unknown analysis_type: {v}")
        return v

    @model_validator(mode="after")
    def _cross_checks(self) -> "ExperimentSpec":
        weights = sum(v.weight_bp for v in self.variants)
        if weights != 10_000:
            raise ValueError(f"variant weight_bp must sum to 10000 (got {weights})")
        controls = [v for v in self.variants if v.is_control]
        if len(controls) != 1:
            raise ValueError("exactly one variant must be is_control")
        keys = [v.key for v in self.variants]
        if len(set(keys)) != len(keys):
            raise ValueError("variant keys must be unique")
        for dimension in self.segments:
            if dimension != "org":
                raise ValueError(f"unknown segment dimension: {dimension}")
        if self.segments and self.unit_type != "user":
            raise ValueError("segments require user units (org mapping)")
        if self.design == "switchback" and self.switchback is None:
            raise ValueError("switchback design requires a switchback config")
        if (
            self.switchback is not None
            and self.switchback.washout_minutes >= self.switchback.window_minutes
        ):
            # Defect #44: washout >= window makes EVERY window fold to zero —
            # the experiment runs forever collecting nothing, invisibly.
            raise ValueError(
                "washout_minutes must be < window_minutes "
                f"({self.switchback.washout_minutes} >= {self.switchback.window_minutes})"
            )
        if self.design != "switchback" and self.switchback is not None:
            raise ValueError("switchback config only valid for switchback design")
        return self


# ── Requests ─────────────────────────────────────────────────────────


class CreateExperimentRequest(_StrictReq):
    key: str = Field(min_length=3, max_length=64, pattern=r"^[a-z0-9][a-z0-9_-]{2,63}$")
    title: str = Field(min_length=1, max_length=200)
    domain: str = Field(max_length=20)
    layer_key: str = Field(min_length=1, max_length=64)
    scope_org_id: str | None = Field(default=None, min_length=26, max_length=26)
    risk_class: str = Field(default="medium", max_length=8)
    holdout_bp: int = Field(default=0, ge=0, le=1000)


class CloneExperimentRequest(_StrictReq):
    key: str = Field(min_length=3, max_length=64, pattern=r"^[a-z0-9][a-z0-9_-]{2,63}$")


class CreateVersionRequest(_StrictReq):
    # Validated server-side via ExperimentSpec so ethics gates raise typed codes
    spec: dict[str, Any]


class TransitionRequest(_StrictReq):
    to_status: str = Field(max_length=12)
    reason: str | None = Field(default=None, max_length=1000)
    # exp10: optional auto-start time, only meaningful with to_status=scheduled
    start_at: datetime | None = None
    # §5 v2: review→scheduled requires the launch checklist affirmed
    checklist: dict[str, bool] = Field(default_factory=dict)


class RampRequest(_StrictReq):
    ramp_bp: int = Field(ge=0, le=10_000)


class RampPlanStep(_StrictReq):
    at: datetime
    ramp_bp: int = Field(ge=1, le=10_000)


class RampPlanRequest(_StrictReq):
    """Round 129: scheduled ramp steps; null/empty clears the plan."""

    plan: list[RampPlanStep] | None = Field(default=None, max_length=20)


class PreviewAssignmentRequest(_StrictReq):
    unit_type: str = Field(max_length=24)
    unit_id: str = Field(min_length=1, max_length=26)
    context: dict[str, Any] = Field(default_factory=dict)

    @field_validator("unit_type")
    @classmethod
    def _unit_known(cls, v: str) -> str:
        if v not in UNIT_TYPES:
            raise ValueError(f"unknown unit_type: {v} (allowed: {sorted(UNIT_TYPES)})")
        return v


class CreateLayerRequest(_StrictReq):
    key: str = Field(min_length=3, max_length=64, pattern=r"^[a-z0-9][a-z0-9_-]{2,63}$")
    domain: str = Field(max_length=20)


class CreateAllocationRequest(_StrictReq):
    experiment_id: str = Field(min_length=26, max_length=26)
    slice_start: int = Field(ge=0, le=9999)
    slice_end: int = Field(ge=0, le=9999)


class CreateDecisionRequest(_StrictReq):
    decision: str = Field(max_length=14)
    summary: str = Field(min_length=10, max_length=10_000)
    analysis_result_hash: str = Field(min_length=64, max_length=64)
    uncertainty: dict[str, Any] = Field(default_factory=dict)
    segments: dict[str, Any] = Field(default_factory=dict)
    evidence: dict[str, Any] = Field(default_factory=dict)
    extend_days: int = Field(default=30, ge=1, le=365)


class CreatePromotionDraftRequest(_StrictReq):
    target_type: str = Field(max_length=30)
    target_ref: str = Field(min_length=1, max_length=64)
    draft_payload: dict[str, Any] = Field(default_factory=dict)


class IncidentRequest(_StrictReq):
    reason: str | None = Field(default=None, max_length=1000)


class UpdateMetricDefinitionRequest(_StrictReq):
    """Round 101: the EDITABLE subset only — kind/source/query_version are
    analysis semantics and stay immutable (changing them silently re-means
    every stored snapshot); provenance already records query_version."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    privacy_class: str | None = Field(default=None, max_length=16)
    direction: str | None = Field(default=None, max_length=16)
    winsorize_pct: float | None = Field(default=None, gt=0, lt=100)
    cap_value: float | None = None
    # §4.14: quantile reporting (operational — changes what is REPORTED,
    # not what stored sufficient stats mean); continuous-kind only
    quantiles: list[float] | None = Field(default=None, min_length=1, max_length=3)
    # §4.15: Kaplan-Meier opt-in (time_to_event kind only)
    km: bool | None = None
    clear_winsorize: bool = False
    clear_cap: bool = False
    clear_quantiles: bool = False


class CreateMetricDefinitionRequest(_StrictReq):
    key: str = Field(min_length=3, max_length=64, pattern=r"^[a-z0-9][a-z0-9_]{2,63}$")
    title: str = Field(min_length=1, max_length=200)
    kind: str = Field(max_length=16)
    domain: str = Field(max_length=20)
    source_kind: str = Field(max_length=10)
    query_version: int = Field(default=1, ge=1)
    spec: dict[str, Any] = Field(default_factory=dict)
    privacy_class: str = Field(default="aggregate_only", max_length=16)
    direction: str = Field(default="increase_good", max_length=16)
    winsorize_pct: float | None = Field(default=None, gt=0, lt=100)
    cap_value: float | None = None
    percentile: float | None = Field(default=None, gt=0, lt=100)


# ── Responses ────────────────────────────────────────────────────────


class ExperimentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    key: str
    title: str
    domain: str
    scope_org_id: str | None
    layer_key: str
    status: str
    current_version: int
    owner_user_id: str
    risk_class: str
    ramp_bp: int
    ramp_plan: list | None = None
    # round 146 (list data-flow badge): injected by the list endpoint from
    # one grouped exposure query — not a model column
    last_exposure_at: datetime | None = None
    holdout_bp: int
    start_at: datetime | None
    started_at: datetime | None
    ended_at: datetime | None
    analysis_close_at: datetime | None
    # Round 48 (the #49 drift class, closed by audit): guardrail freshness is
    # an operator signal — a running experiment never checked is a red flag
    last_guardrail_check_at: datetime | None
    created_at: datetime
    updated_at: datetime


class VersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    experiment_id: str
    version: int
    spec: dict
    spec_hash: str
    created_by: str | None
    created_at: datetime


class LayerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    key: str
    domain: str
    total_slices: int
    created_at: datetime


class SelfResolveRequest(_StrictReq):
    experiment_key: str = Field(min_length=1, max_length=64)


class SelfExposureRequest(_StrictReq):
    experiment_key: str = Field(min_length=1, max_length=64)
    # must match the column bound exactly (String(64)) — a wider schema let
    # 65-120 char keys through to a truncation error the fail-safe facade
    # swallowed as a SILENTLY DROPPED exposure (defect #36, R88 write-boundary)
    dedup_key: str | None = Field(default=None, max_length=64)


class CreateHoldoutGroupRequest(_StrictReq):
    key: str = Field(min_length=3, max_length=64, pattern=r"^[a-z0-9][a-z0-9_-]{2,63}$")
    title: str = Field(min_length=1, max_length=200)
    domain: str = Field(max_length=20)
    holdout_bp: int = Field(ge=1, le=2000)
    scope_org_id: str | None = Field(default=None, min_length=26, max_length=26)
    ends_at: datetime | None = None


class HoldoutGroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    key: str
    title: str
    domain: str
    scope_org_id: str | None
    holdout_bp: int
    status: str
    starts_at: datetime
    ends_at: datetime | None
    created_by: str | None
    created_at: datetime


class AllocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    layer_key: str
    experiment_id: str
    slice_start: int
    slice_end: int
    created_at: datetime


class MetricDefinitionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    key: str
    title: str
    kind: str
    domain: str
    source_kind: str
    query_version: int
    spec: dict
    privacy_class: str
    direction: str
    winsorize_pct: float | None
    cap_value: float | None
    percentile: float | None
    created_at: datetime


class MetricSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    experiment_id: str
    metric_key: str
    variant_key: str
    # Defect #49: segment was stored (exp08) but never serialized — segment
    # rows were indistinguishable from whole-population rows in the listing,
    # and a consumer summing rows double-counted every sliced metric.
    segment: str
    window_start: datetime
    window_end: datetime
    n: int
    numerator: float | None
    denominator: float | None
    sum_value: float | None
    sum_sq: float | None
    cov_sum: float | None
    cov_sum_sq: float | None
    cov_xy_sum: float | None
    covariates: dict
    value_histogram: dict = {}
    provenance: dict
    computed_at: datetime


class DecisionRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    experiment_id: str
    experiment_version: int
    decision: str
    summary: str
    domain: str
    analysis_type: str
    analysis_result_hash: str
    uncertainty: dict
    segments: dict
    guardrail_outcome: dict
    evidence: dict
    approver_user_id: str
    created_at: datetime


class PromotionDraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    decision_record_id: str
    target_type: str
    target_ref: str
    draft_payload: dict
    status: str
    approved_by: str | None
    applied_at: datetime | None
    applied_ref: str | None
    apply_error: str | None
    created_at: datetime


class GuardrailEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    experiment_id: str
    guardrail_key: str
    metric_key: str | None
    observed: float | None
    threshold: float | None
    window_start: datetime | None
    window_end: datetime | None
    action: str
    auto: bool
    detail: dict
    created_at: datetime


class ExperimentEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    experiment_id: str
    actor_user_id: str | None
    event_type: str
    payload: dict
    created_at: datetime
