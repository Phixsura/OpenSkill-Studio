from datetime import datetime

from pydantic import BaseModel, field_validator

# ── Project ───────────────────────────────────────────────


VALID_PROJECT_TYPES = {"general", "ai_visual"}
VALID_DELIVERABLE_TYPES = {
    "file",
    "text",
    "link",
    "markdown",
    "image",
    "video",
    "audio",
    "prompt",
    "reference",
    "final_output",
}


class CreateProjectRequest(BaseModel):
    title: str
    slug: str | None = None
    description: str
    instructions: str
    project_type: str = "general"
    difficulty: str = "intermediate"
    max_score: int = 100
    rubric: list[dict]
    deadline: datetime | None = None
    late_deadline: datetime | None = None
    late_penalty_pct: int = 0
    max_submissions: int = 0
    skill_ids: list[str] | None = None

    @field_validator("project_type")
    @classmethod
    def validate_project_type(cls, v: str) -> str:
        if v not in VALID_PROJECT_TYPES:
            raise ValueError(
                f"Project type must be one of: {', '.join(sorted(VALID_PROJECT_TYPES))}"
            )
        return v

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
    project_type: str
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
    # file_key (raw S3 object key) is intentionally NOT exposed — downloads go
    # through the presigned-URL endpoint. has_file signals a downloadable file.
    has_file: bool = False
    file_name: str | None
    file_size: int | None
    mime_type: str | None
    version: int = 1
    note: str | None = None
    uploaded_by: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):  # type: ignore[override]
        inst = super().model_validate(obj, *args, **kwargs)
        inst.has_file = bool(getattr(obj, "file_key", None))
        return inst


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
    # raw S3 key not exposed — clients use the presigned download endpoint
    file_name: str | None
    file_size: int | None
    mime_type: str | None
    version: int = 1
    # Generation metadata JSON extracted from the file (item.content)
    content: str | None = None

    model_config = {"from_attributes": True}


# ── Project Templates ────────────────────────────────────


def _validate_template_deliverables(v: list) -> list:
    if len(v) > 30:
        raise ValueError("At most 30 deliverables per template")
    for d in v:
        if not isinstance(d, dict):
            raise ValueError("Each deliverable must be an object")
        name = d.get("name")
        if not isinstance(name, str) or not (2 <= len(name.strip()) <= 200):
            raise ValueError("Each deliverable needs a name of 2-200 characters")
        dtype = d.get("type")
        if dtype not in VALID_DELIVERABLE_TYPES:
            raise ValueError(f"Invalid deliverable type: {dtype}")
        config = d.get("config", {})
        if config is not None and not isinstance(config, dict):
            raise ValueError("Deliverable config must be an object")
    return v


def _validate_rubric_items(v: list) -> list:
    """Same per-item rubric rules as project creation — a template's rubric is
    copied verbatim into a project, so it must satisfy project constraints."""
    if not v:
        raise ValueError("Rubric must have at least one criterion")
    if len(v) > 20:
        raise ValueError("Rubric must have at most 20 criteria")
    for item in v:
        if not isinstance(item, dict):
            raise ValueError("Each rubric item must be an object")
        if "criterion" not in item or "max_score" not in item:
            raise ValueError("Each rubric item must have 'criterion' and 'max_score'")
        if not isinstance(item.get("criterion"), str) or len(item["criterion"]) > 200:
            raise ValueError("Criterion name must be a string of 200 chars or less")
        if not isinstance(item.get("max_score"), (int, float)) or item["max_score"] < 0:
            raise ValueError("Criterion max_score must be a non-negative number")
    return v


class CreateTemplateRequest(BaseModel):
    name: str
    description: str
    instructions: str
    project_type: str = "general"
    difficulty: str = "intermediate"
    suggested_minutes: int | None = None
    max_score: int = 100
    rubric: list[dict]
    deliverables: list[dict] = []
    skill_names: list[str] | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 200:
            raise ValueError("Name must be 2-200 characters")
        return v

    @field_validator("project_type")
    @classmethod
    def validate_project_type(cls, v: str) -> str:
        if v not in VALID_PROJECT_TYPES:
            raise ValueError(
                f"Project type must be one of: {', '.join(sorted(VALID_PROJECT_TYPES))}"
            )
        return v

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        allowed = {"beginner", "intermediate", "advanced"}
        if v not in allowed:
            raise ValueError(f"Difficulty must be one of: {', '.join(sorted(allowed))}")
        return v

    @field_validator("rubric")
    @classmethod
    def validate_rubric(cls, v: list) -> list:
        return _validate_rubric_items(v)

    @field_validator("deliverables")
    @classmethod
    def validate_deliverables(cls, v: list) -> list:
        return _validate_template_deliverables(v)

    @field_validator("suggested_minutes")
    @classmethod
    def validate_suggested_minutes(cls, v: int | None) -> int | None:
        if v is not None and (v < 0 or v > 99999):
            raise ValueError("suggested_minutes must be between 0 and 99999")
        return v


class UpdateTemplateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    instructions: str | None = None
    difficulty: str | None = None
    suggested_minutes: int | None = None
    max_score: int | None = None
    rubric: list[dict] | None = None
    deliverables: list[dict] | None = None
    skill_names: list[str] | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if len(v) < 2 or len(v) > 200:
                raise ValueError("Name must be 2-200 characters")
        return v

    @field_validator("deliverables")
    @classmethod
    def validate_deliverables(cls, v: list | None) -> list | None:
        if v is not None:
            return _validate_template_deliverables(v)
        return v

    @field_validator("rubric")
    @classmethod
    def validate_rubric(cls, v: list | None) -> list | None:
        if v is not None:
            return _validate_rubric_items(v)
        return v


class TemplateResponse(BaseModel):
    id: str
    name: str
    description: str
    instructions: str
    project_type: str
    difficulty: str
    suggested_minutes: int | None
    max_score: int
    rubric: list
    deliverables: list
    skill_names: list
    builtin: bool = False
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class CreateFromTemplateRequest(BaseModel):
    template_id: str
    title: str | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if len(v) < 2 or len(v) > 200:
                raise ValueError("Title must be 2-200 characters")
        return v


# ── Project Assets ───────────────────────────────────────


class AssetResponse(BaseModel):
    id: str
    project_id: str
    name: str
    description: str | None
    file_name: str
    file_size: int
    mime_type: str
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Prompt Items ─────────────────────────────────────────


class PromptItemRequest(BaseModel):
    """Prompt deliverable submission.

    Field vocabulary follows the AI-creation industry convention
    (Civitai/A1111/ComfyUI): seed, negative prompt, cfg_scale, steps,
    sampler, and resource references with weights.
    """

    deliverable_id: str
    prompt: str
    negative_prompt: str | None = None
    tool: str | None = None
    model: str | None = None
    seed: int | None = None
    cfg_scale: float | None = None
    steps: int | None = None
    sampler: str | None = None
    resources: list[dict] | None = None
    parameters: dict | None = None
    notes: str | None = None

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Prompt must not be empty")
        if len(v) > 10000:
            raise ValueError("Prompt must be 10,000 characters or less")
        return v

    @field_validator("negative_prompt")
    @classmethod
    def validate_negative_prompt(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 10000:
            raise ValueError("Negative prompt must be 10,000 characters or less")
        return v

    @field_validator("tool", "model", "sampler")
    @classmethod
    def validate_tool_model(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 100:
            raise ValueError("Tool/model/sampler name must be 100 characters or less")
        return v

    @field_validator("seed")
    @classmethod
    def validate_seed(cls, v: int | None) -> int | None:
        # Unsigned 32-bit range — SD/Runway ecosystem convention
        if v is not None and (v < 0 or v > 2**32 - 1):
            raise ValueError("Seed must be in the unsigned 32-bit range")
        return v

    @field_validator("cfg_scale")
    @classmethod
    def validate_cfg_scale(cls, v: float | None) -> float | None:
        if v is not None and (v < 0 or v > 100):
            raise ValueError("CFG scale must be between 0 and 100")
        return v

    @field_validator("steps")
    @classmethod
    def validate_steps(cls, v: int | None) -> int | None:
        if v is not None and (v < 0 or v > 1000):
            raise ValueError("Steps must be between 0 and 1000")
        return v

    @field_validator("resources")
    @classmethod
    def validate_resources(cls, v: list[dict] | None) -> list[dict] | None:
        if v is None:
            return v
        if len(v) > 20:
            raise ValueError("At most 20 resources")
        for r in v:
            if not isinstance(r, dict):
                raise ValueError("Each resource must be an object")
            rtype = r.get("type")
            name = r.get("name")
            if not isinstance(rtype, str) or not rtype or len(rtype) > 50:
                raise ValueError("Resource type must be a string of 1-50 characters")
            if not isinstance(name, str) or not name or len(name) > 200:
                raise ValueError("Resource name must be a string of 1-200 characters")
            weight = r.get("weight")
            if weight is not None and (
                not isinstance(weight, (int, float)) or weight < -10 or weight > 10
            ):
                raise ValueError("Resource weight must be a number between -10 and 10")
            version = r.get("version")
            if version is not None and (not isinstance(version, str) or len(version) > 100):
                raise ValueError("Resource version must be a string of 100 characters or less")
        return v

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 2000:
            raise ValueError("Notes must be 2,000 characters or less")
        return v

    @field_validator("parameters")
    @classmethod
    def validate_parameters(cls, v: dict | None) -> dict | None:
        if v is not None and len(str(v)) > 5000:
            raise ValueError("Parameters object is too large")
        return v
