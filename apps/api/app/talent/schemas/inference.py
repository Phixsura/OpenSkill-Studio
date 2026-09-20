"""Pydantic schemas for skill inference endpoint."""

from pydantic import BaseModel, Field, field_validator

INFERENCE_SOURCE_TYPES = frozenset(
    {
        "resume",
        "job_description",
        "project_description",
        "free_text",
    }
)


class SkillInferenceRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=50000)
    source_type: str = Field(
        ..., description="One of: resume, job_description, project_description, free_text"
    )
    max_results: int = Field(20, ge=1, le=100)

    @field_validator("source_type")
    @classmethod
    def _validate_source_type(cls, v: str) -> str:
        if v not in INFERENCE_SOURCE_TYPES:
            raise ValueError(
                f"Invalid source_type: {v}. Must be one of {sorted(INFERENCE_SOURCE_TYPES)}"
            )
        return v


class InferredSkillResponse(BaseModel):
    model_config = {"from_attributes": True}
    capability_id: str | None = None
    capability_name: str
    confidence: float
    source_excerpt: str
    match_type: str  # exact, alias, fuzzy, inferred


class SkillInferenceResponse(BaseModel):
    model_config = {"from_attributes": True}
    skills: list[InferredSkillResponse]
    source_type: str
    text_length: int
    processing_time_ms: float
