"""Pydantic request schemas for gap closure endpoints.

Replaces raw `body: dict` with typed validation on 37 endpoints.
"""

from pydantic import BaseModel, Field

# ---- Intelligence endpoints ----

class ScreeningRulesRequest(BaseModel):
    rules: list[dict] = Field(default_factory=list, max_length=50)
    candidate_data: dict = Field(default_factory=dict)


class BooleanSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)


class MatchFeedbackRequest(BaseModel):
    rating: str = Field(..., min_length=1, max_length=30)
    comment: str | None = Field(None, max_length=2000)


class PipelineValidationRequest(BaseModel):
    stages: list[str] = Field(..., min_length=3, max_length=15)


class PoolRulesEvaluationRequest(BaseModel):
    rules: list[dict] = Field(default_factory=list, max_length=50)
    candidate: dict = Field(default_factory=dict)


class AdverseImpactRequest(BaseModel):
    group_a_selected: int = Field(0, ge=0)
    group_a_total: int = Field(0, ge=0)
    group_b_selected: int = Field(0, ge=0)
    group_b_total: int = Field(0, ge=0)


class RequisitionValidationRequest(BaseModel):
    title: str | None = None
    department: str | None = None
    justification: str | None = Field(None, max_length=5000)
    headcount: int = Field(0, ge=0)


class AvailabilityValidationRequest(BaseModel):
    mode: str | None = None
    hours_per_week: int | None = Field(None, ge=1, le=80)
    notice_period_days: int | None = Field(None, ge=0, le=180)
    remote_preference: str | None = None


class SalaryExpectationRequest(BaseModel):
    min_amount: float | None = Field(None, ge=0)
    max_amount: float | None = Field(None, ge=0)
    currency: str = Field("USD", max_length=5)
    pay_period: str = Field("annual", max_length=20)


class MentorshipMatchRequest(BaseModel):
    mentor: dict = Field(default_factory=dict)
    mentee: dict = Field(default_factory=dict)


class EmailTemplateRenderRequest(BaseModel):
    template_key: str = Field(..., min_length=1, max_length=100)
    context: dict = Field(default_factory=dict)


class BulkMessageValidationRequest(BaseModel):
    recipient_ids: list[str] = Field(default_factory=list, max_length=100)
    content: str = Field("", max_length=5000)


class ReportConfigRequest(BaseModel):
    report_type: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=200)
    format: str = Field("json", max_length=10)
    filters: dict = Field(default_factory=dict)


class BenchmarkCompareRequest(BaseModel):
    metric: str = Field(..., min_length=1, max_length=100)
    value: float = Field(0)
    industry: str = Field("average", max_length=50)


class KPIEvaluateRequest(BaseModel):
    kpi: dict = Field(default_factory=dict)
    current_value: float = Field(0)


class APIKeyGenerateRequest(BaseModel):
    org_id: str = Field(..., min_length=1, max_length=26)
    name: str = Field(..., min_length=1, max_length=200)
    scopes: list[str] = Field(..., min_length=1, max_length=20)


class HRISValidationRequest(BaseModel):
    employee_id: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None


class ATSConfigRequest(BaseModel):
    provider: str = Field(..., min_length=1, max_length=50)
    api_url: str = Field(..., min_length=1, max_length=500)
    sync_direction: str = Field("inbound", max_length=20)
    sync_entities: list[str] = Field(default_factory=list)


class DataClassificationRequest(BaseModel):
    field_name: str = Field(..., min_length=1, max_length=100)


class IPAllowlistRequest(BaseModel):
    ips: list[str] = Field(default_factory=list, max_length=100)


class RoleEscalationRequest(BaseModel):
    current_role: str = Field(..., max_length=30)
    new_role: str = Field(..., max_length=30)
    actor_role: str = Field(..., max_length=30)


class EvidenceSimulationRequest(BaseModel):
    current_evidence: list[dict] = Field(default_factory=list)
    new_evidence: dict = Field(default_factory=dict)
    decay_config: dict | None = None


class CalibrationValidationRequest(BaseModel):
    dimension_weights: dict | None = None
    shrinkage_k: float | None = Field(None, ge=0, le=100)
    shrinkage_prior: float | None = Field(None, ge=0, le=1)


# ---- Other endpoints ----

class SnapshotCompareRequest(BaseModel):
    snapshot_a_id: str = Field(..., min_length=1, max_length=26)
    snapshot_b_id: str = Field(..., min_length=1, max_length=26)


class CustomQuestionsRequest(BaseModel):
    questions: list[dict] = Field(default_factory=list, max_length=20)


class TaxonomyImportRequest(BaseModel):
    format: str = Field("custom_json", max_length=20)
    rows: list[dict] = Field(default_factory=list, max_length=1000)


class OfferCreateRequest(BaseModel):
    role_title: str = Field(..., min_length=1, max_length=200)
    compensation_text: str | None = Field(None, max_length=500)
    conditions: list[str] = Field(default_factory=list, max_length=20)
    custom_sections: list[dict] = Field(default_factory=list, max_length=10)


class OnboardingTemplateCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=5000)
    tasks: list[dict] = Field(default_factory=list, max_length=50)


class MessageSendRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)
    message_type: str = Field("text", max_length=30)


class PortfolioItemCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    item_type: str = Field("project", max_length=30)
    description: str | None = Field(None, max_length=5000)
    url: str | None = Field(None, max_length=500)
    image_url: str | None = Field(None, max_length=500)
    capability_ids: list[str] = Field(default_factory=list)
    visibility: str = Field("private", max_length=20)
    pinned: bool = False
    sort_order: int = Field(0, ge=0)


class WebhookRegisterRequest(BaseModel):
    url: str = Field(..., min_length=10, max_length=500)
    event_types: list[str] = Field(default_factory=list, max_length=30)


class SuccessorNominationRequest(BaseModel):
    candidate_user_id: str = Field(..., min_length=1, max_length=26)
    readiness: str = Field("not_assessed", max_length=30)


class KeyRoleCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=5000)
    required_capabilities: list[dict] = Field(default_factory=list)
    current_holder_id: str | None = None
    criticality: str = Field("medium", max_length=20)
