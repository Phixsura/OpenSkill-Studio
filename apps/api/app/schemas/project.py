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
