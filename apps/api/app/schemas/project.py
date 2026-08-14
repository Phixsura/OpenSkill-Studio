from datetime import datetime

from pydantic import BaseModel, field_validator

# ── Project ───────────────────────────────────────────────


class CreateProjectRequest(BaseModel):
    title: str
    slug: str | None = None
    description: str
    instructions: str
    difficulty: str = "intermediate"
    max_score: int = 100
    rubric: list[dict]
    deadline: datetime | None = None
    late_deadline: datetime | None = None
    late_penalty_pct: int = 0
    max_submissions: int = 0
    skill_ids: list[str] | None = None

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        allowed = {"beginner", "intermediate", "advanced"}
        if v not in allowed:
            raise ValueError(f"Difficulty must be one of: {', '.join(sorted(allowed))}")
        return v

    @field_validator("max_score")
    @classmethod
    def validate_max_score(cls, v: int) -> int:
        if v < 0 or v > 10000:
            raise ValueError("Max score must be between 0 and 10,000")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 200:
            raise ValueError("Title must be 2-200 characters")
        return v

    @field_validator("rubric")
    @classmethod
    def validate_rubric(cls, v: list) -> list:
        if not v:
            raise ValueError("Rubric must have at least one criterion")
        if len(v) > 20:
            raise ValueError("Rubric must have at most 20 criteria")
        for item in v:
            if not isinstance(item, dict):
                raise ValueError("Each rubric item must be an object")
            if "criterion" not in item:
                raise ValueError("Each rubric item must have a 'criterion' key")
            if "max_score" not in item:
                raise ValueError("Each rubric item must have a 'max_score' key")
            if not isinstance(item.get("criterion"), str) or len(item["criterion"]) > 200:
                raise ValueError("Criterion name must be a string of 200 chars or less")
            if not isinstance(item.get("max_score"), (int, float)) or item["max_score"] < 0:
                raise ValueError("Criterion max_score must be a non-negative number")
        return v

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v):
        if v is not None and isinstance(v, str) and len(v) > 200:
            raise ValueError("slug must not exceed 200 characters")
        return v

    @field_validator("late_penalty_pct")
    @classmethod
    def validate_late_penalty_pct(cls, v):
        if v is not None and isinstance(v, int) and (v < 0 or v > 100):
            raise ValueError("late_penalty_pct must be between 0 and 100")
        return v

    @field_validator("max_submissions")
    @classmethod
    def validate_max_submissions(cls, v):
        if v is not None and isinstance(v, int) and (v < 0 or v > 1000):
            raise ValueError("max_submissions must be between 0 and 1000")
        return v


class UpdateProjectRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    instructions: str | None = None
    difficulty: str | None = None
    max_score: int | None = None
    rubric: list[dict] | None = None
    deadline: datetime | None = None
    late_deadline: datetime | None = None
    late_penalty_pct: int | None = None

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str | None) -> str | None:
        if v is not None:
            allowed = {"beginner", "intermediate", "advanced"}
            if v not in allowed:
                raise ValueError(f"Difficulty must be one of: {', '.join(sorted(allowed))}")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) < 2 or len(v) > 200:
            raise ValueError("Title must be 2-200 characters")
        return v

    max_submissions: int | None = None

    @field_validator("rubric")
    @classmethod
    def validate_rubric(cls, v: list[dict] | None) -> list[dict] | None:
        if v is not None and len(v) == 0:
            raise ValueError("Rubric must have at least one criterion")
        return v

    @field_validator("max_score")
    @classmethod
    def validate_max_score(cls, v):
        if v is not None and isinstance(v, int) and (v < 0 or v > 10000):
            raise ValueError("max_score must be between 0 and 10000")
        return v

    @field_validator("late_penalty_pct")
    @classmethod
    def validate_late_penalty_pct(cls, v):
        if v is not None and isinstance(v, int) and (v < 0 or v > 100):
            raise ValueError("late_penalty_pct must be between 0 and 100")
        return v

    @field_validator("max_submissions")
    @classmethod
    def validate_max_submissions(cls, v):
        if v is not None and isinstance(v, int) and (v < 0 or v > 1000):
            raise ValueError("max_submissions must be between 0 and 1000")
        return v


class ProjectResponse(BaseModel):
    id: str
    title: str
    slug: str
    description: str
    difficulty: str
    max_score: int
    deadline: datetime | None
    late_deadline: datetime | None
    late_penalty_pct: int
    max_submissions: int
    status: str
    published_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectDetailResponse(ProjectResponse):
    instructions: str
    rubric: list[dict]
    deliverables: list["DeliverableResponse"] = []
    skill_ids: list[str] = []

    model_config = {"from_attributes": True}


# ── Deliverable ──────────────────────────────────────────


class CreateDeliverableRequest(BaseModel):
    name: str
    description: str | None = None
    type: str
    required: bool = True
    config: dict = {}
    sort_order: int = 0

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 200:
            raise ValueError("Name must be 2-200 characters")
        return v


class UpdateDeliverableRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    required: bool | None = None
    config: dict | None = None
    sort_order: int | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 200:
            raise ValueError("Name must not exceed 200 characters")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 2000:
            raise ValueError("Description must not exceed 2000 characters")
        return v


class DeliverableResponse(BaseModel):
    id: str
    project_id: str
    name: str
    description: str | None
    type: str
    required: bool
    config: dict
    sort_order: int

    model_config = {"from_attributes": True}


# ── Submission ───────────────────────────────────────────


class SubmissionResponse(BaseModel):
    id: str
    project_id: str
    user_id: str
    version: int
    status: str
    submitted_at: datetime | None
    is_late: bool
    final_score: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SubmissionItemResponse(BaseModel):
    id: str
    deliverable_id: str
    type: str
    content: str | None
    file_key: str | None
    file_name: str | None
    file_size: int | None
    mime_type: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewResponse(BaseModel):
    id: str
    submission_id: str
    reviewer_id: str | None
    reviewer_type: str
    status: str
    score: int | None
    score_breakdown: dict | None
    feedback: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SubmissionDetailResponse(SubmissionResponse):
    items: list[SubmissionItemResponse] = []
    reviews: list[ReviewResponse] = []

    model_config = {"from_attributes": True}


# ── Review ───────────────────────────────────────────────


class CreateReviewRequest(BaseModel):
    status: str
    score: int | None = None
    score_breakdown: dict | None = None
    feedback: str | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid = {"approved", "revision_requested", "rejected"}
        if v not in valid:
            raise ValueError(f"Status must be one of: {', '.join(valid)}")
        return v

    # ── Extension ────────────────────────────────────────────
    @field_validator("feedback")
    @classmethod
    def validate_feedback(cls, v):
        if v is not None and isinstance(v, str) and len(v) > 10000:
            raise ValueError("feedback must not exceed 10000 characters")
        return v

    @field_validator("score")
    @classmethod
    def validate_score(cls, v):
        if v is not None and isinstance(v, int) and (v < 0 or v > 10000):
            raise ValueError("score must be between 0 and 10000")
        return v


class GrantExtensionRequest(BaseModel):
    user_id: str
    new_deadline: datetime
    reason: str | None = None


class ExtensionResponse(BaseModel):
    id: str
    project_id: str
    user_id: str
    original_deadline: datetime
    extended_deadline: datetime
    reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── File ─────────────────────────────────────────────────


class FileResponse(BaseModel):
    id: str
    file_key: str | None
    file_name: str | None
    file_size: int | None
    mime_type: str | None

    model_config = {"from_attributes": True}
