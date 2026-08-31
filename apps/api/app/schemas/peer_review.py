from datetime import UTC, datetime

from pydantic import BaseModel, field_validator

from app.schemas.base import reject_ctrl_json, reject_ctrl_str, reject_nonfinite_json


class CreateRoundRequest(BaseModel):
    project_id: str
    name: str
    num_reviews: int = 2
    anonymous: bool = True
    include_self_review: bool = False
    deadline: datetime | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 200:
            raise ValueError("Name must be 2-200 characters")
        return v

    @field_validator("deadline")
    @classmethod
    def normalize_tz(cls, v: datetime | None) -> datetime | None:
        # Naive datetimes are treated as UTC — mixing naive/aware 500s on
        # every later comparison.
        if v is not None and v.tzinfo is None:
            return v.replace(tzinfo=UTC)
        return v

    @field_validator("num_reviews")
    @classmethod
    def validate_num_reviews(cls, v: int) -> int:
        # Teachfloor's proven range: each learner evaluates 2-5 peers
        if v < 1 or v > 10:
            raise ValueError("num_reviews must be between 1 and 10")
        return v


class RoundResponse(BaseModel):
    id: str
    project_id: str
    name: str
    num_reviews: int
    anonymous: bool
    include_self_review: bool
    phase: str
    deadline: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SubmitAssessmentRequest(BaseModel):
    score: int
    score_breakdown: list[dict] | None = None
    feedback: str | None = None

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: int) -> int:
        if v < 0 or v > 10000:
            raise ValueError("Score must be between 0 and 10,000")
        return v

    @field_validator("feedback")
    @classmethod
    def validate_feedback(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 10000:
            raise ValueError("Feedback must be 10,000 characters or less")
        # feedback -> PeerAssessment.feedback (text column). A NUL/control char
        # (a valid-JSON backslash-u0000 escape) crashes the write with asyncpg
        # 22P05 -> 500 (R87). Screen it to a clean 422.
        return reject_ctrl_str(v, "feedback")

    @field_validator("score_breakdown")
    @classmethod
    def validate_breakdown(cls, v: list[dict] | None) -> list[dict] | None:
        if v is None:
            return v
        if len(v) > 20:
            raise ValueError("At most 20 breakdown entries")
        for item in v:
            if not isinstance(item, dict) or "criterion" not in item or "score" not in item:
                raise ValueError("Each breakdown entry needs 'criterion' and 'score'")
            if not isinstance(item.get("score"), (int, float)) or item["score"] < 0:
                raise ValueError("Breakdown scores must be non-negative numbers")
        # score_breakdown → PeerAssessment.score_breakdown (JSONB). NUL/control
        # chars and NaN/Infinity floats both crash the JSONB write (22P05 /
        # 22P02) → 500 (R87) — every other JSONB write surface screens both.
        reject_ctrl_json(v, "score_breakdown")
        reject_nonfinite_json(v, "score_breakdown")
        return v


class AssessmentResponse(BaseModel):
    id: str
    round_id: str
    submission_id: str
    # reviewer_id intentionally omitted from the default response —
    # anonymity is decided at the endpoint layer per round config
    is_self_review: bool
    status: str
    score: int | None
    score_breakdown: list | None
    feedback: str | None
    submitted_at: datetime | None

    model_config = {"from_attributes": True}


class AssessmentWithReviewerResponse(AssessmentResponse):
    reviewer_id: str


class RoundResultEntry(BaseModel):
    submission_id: str
    avg_score: float | None
    review_count: int
