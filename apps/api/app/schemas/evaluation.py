from datetime import datetime

from pydantic import BaseModel, field_validator


class TriggerEvaluationRequest(BaseModel):
    submission_id: str
    type: str = "submission_review"

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        valid = {"exercise_text", "exercise_code", "submission_review"}
        if v not in valid:
            raise ValueError(f"Type must be one of: {', '.join(valid)}")
        return v


class EvalTaskResponse(BaseModel):
    id: str
    org_id: str
    submission_id: str | None
    attempt_id: str | None
    type: str
    status: str
    priority: int
    config: dict
    result: dict | None
    error: str | None
    llm_provider: str | None
    llm_model: str | None
    input_tokens: int | None
    output_tokens: int | None
    cost_usd: float | None
    duration_ms: int | None
    retries: int
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class EvalUsageResponse(BaseModel):
    total_tasks: int
    total_input_tokens: int
    total_output_tokens: int
    total_cost_usd: float
    month: str
    budget_usd: float | None
    budget_remaining: float | None


class EvalSettingsResponse(BaseModel):
    enabled: bool
    monthly_budget_usd: float | None
    default_model: str
    auto_evaluate: bool
    pass_threshold: float


class UpdateEvalSettingsRequest(BaseModel):
    enabled: bool | None = None
    monthly_budget_usd: float | None = None
    default_model: str | None = None
    auto_evaluate: bool | None = None
    pass_threshold: float | None = None

    @field_validator("monthly_budget_usd")
    @classmethod
    def validate_budget(cls, v: float | None) -> float | None:
        if v is not None and (v < 0 or v > 1_000_000):
            raise ValueError("monthly_budget_usd must be between 0 and 1,000,000")
        return v

    @field_validator("pass_threshold")
    @classmethod
    def validate_threshold(cls, v: float | None) -> float | None:
        if v is not None and (v < 0 or v > 1):
            raise ValueError("pass_threshold must be between 0 and 1")
        return v

    @field_validator("default_model")
    @classmethod
    def validate_model(cls, v: str | None) -> str | None:
        if v is not None and (not v.strip() or len(v) > 100):
            raise ValueError("default_model must be 1-100 characters")
        return v
