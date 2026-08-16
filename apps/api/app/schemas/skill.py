from datetime import datetime

from pydantic import BaseModel, field_validator, model_validator

# ── Category ──────────────────────────────────────────────


class CreateCategoryRequest(BaseModel):
    name: str
    slug: str | None = None
    description: str | None = None
    icon: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 100:
            raise ValueError("Name must be 2-100 characters")
        return v

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v):
        if v is not None and isinstance(v, str) and len(v) > 200:
            raise ValueError("slug must not exceed 200 characters")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 2000:
            raise ValueError("Description must not exceed 2000 characters")
        return v

    @field_validator("icon")
    @classmethod
    def validate_icon(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 100:
            raise ValueError("Icon must not exceed 100 characters")
        return v


class UpdateCategoryRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    icon: str | None = None
    sort_order: int | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        # Column is String(100) — the old 200 cap let renames 500 on write.
        if v is not None and len(v) > 100:
            raise ValueError("Name must not exceed 100 characters")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 2000:
            raise ValueError("Description must not exceed 2000 characters")
        return v

    @field_validator("icon")
    @classmethod
    def validate_icon(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 50:
            raise ValueError("Icon must not exceed 50 characters")
        return v

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v):
        if v is not None and isinstance(v, int) and (v < 0 or v > 100000):
            raise ValueError("sort_order must be between 0 and 100000")
        return v


class CategoryResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str | None
    icon: str | None
    sort_order: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Skill ─────────────────────────────────────────────────


class CreateSkillRequest(BaseModel):
    category_id: str
    name: str
    slug: str | None = None
    description: str
    learning_content: str | None = None
    difficulty: str = "beginner"
    estimated_minutes: int | None = None
    tags: list[str] | None = None
    prerequisites: list[str] | None = None

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        if v is not None:
            return [t.strip() for t in v if t.strip()]
        return v

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        allowed = {"beginner", "intermediate", "advanced", "expert"}
        if v not in allowed:
            raise ValueError(f"Difficulty must be one of: {', '.join(sorted(allowed))}")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        if len(v) > 10000:
            raise ValueError("Description must be 10,000 characters or less")
        return v

    @field_validator("learning_content")
    @classmethod
    def validate_learning_content(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 100000:
            raise ValueError("Learning content must be 100,000 characters or less")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 200:
            raise ValueError("Name must be 2-200 characters")
        return v

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v):
        if v is not None and isinstance(v, str) and len(v) > 200:
            raise ValueError("slug must not exceed 200 characters")
        return v

    @field_validator("estimated_minutes")
    @classmethod
    def validate_estimated_minutes(cls, v):
        if v is not None and isinstance(v, int) and (v < 0 or v > 9999):
            raise ValueError("estimated_minutes must be between 0 and 9999")
        return v


class UpdateSkillRequest(BaseModel):
    category_id: str | None = None
    name: str | None = None
    description: str | None = None
    learning_content: str | None = None
    difficulty: str | None = None
    estimated_minutes: int | None = None
    tags: list[str] | None = None

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str | None) -> str | None:
        if v is not None:
            allowed = {"beginner", "intermediate", "advanced", "expert"}
            if v not in allowed:
                raise ValueError(f"Difficulty must be one of: {', '.join(sorted(allowed))}")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        if v is not None:
            return [t.strip() for t in v if t.strip()]
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) < 2 or len(v) > 200:
            raise ValueError("Name must be 2-200 characters")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 10000:
            raise ValueError("Description must be 10,000 characters or less")
        return v

    @field_validator("learning_content")
    @classmethod
    def validate_learning_content(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 100000:
            raise ValueError("Learning content must be 100,000 characters or less")
        return v

    @field_validator("estimated_minutes")
    @classmethod
    def validate_estimated_minutes(cls, v):
        if v is not None and isinstance(v, int) and (v < 0 or v > 9999):
            raise ValueError("estimated_minutes must be between 0 and 9999")
        return v


class SkillResponse(BaseModel):
    id: str
    category_id: str
    name: str
    slug: str
    description: str
    difficulty: str
    estimated_minutes: int | None
    tags: list[str]
    sort_order: int
    status: str
    published_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SkillDetailResponse(SkillResponse):
    learning_content: str | None
    prerequisites: list[SkillResponse] = []

    model_config = {"from_attributes": True}


# ── Exercise ──────────────────────────────────────────────


class CreateExerciseRequest(BaseModel):
    title: str
    description: str
    type: str
    config: dict
    max_score: int = 100

    @field_validator("max_score")
    @classmethod
    def validate_max_score(cls, v: int) -> int:
        if v < 0 or v > 10000:
            raise ValueError("Max score must be between 0 and 10,000")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        allowed = {"multiple_choice", "text_answer", "code_submission"}
        if v not in allowed:
            raise ValueError(f"Exercise type must be one of: {', '.join(sorted(allowed))}")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 200:
            raise ValueError("Title must be 2-200 characters")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        if len(v) > 5000:
            raise ValueError("Description must be 5,000 characters or less")
        return v

    @field_validator("config")
    @classmethod
    def validate_config(cls, v: dict) -> dict:
        # Bound the config JSON so an MCQ options/correct blob can't be used
        # for unbounded storage abuse.
        if len(str(v)) > 20000:
            raise ValueError("config is too large")
        return v

    @model_validator(mode="after")
    def validate_mcq_has_correct(self):
        # An MCQ without a non-empty `correct` list auto-grades every blank
        # answer as full marks ([] == [] in the grader) — completing skills
        # and minting badges for nothing.
        if self.type == "multiple_choice":
            correct = self.config.get("correct")
            if correct is None or correct == [] or correct == "":
                raise ValueError("multiple_choice config must include a non-empty 'correct'")
        return self


class UpdateExerciseRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    config: dict | None = None
    max_score: int | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 200:
            raise ValueError("Title must not exceed 200 characters")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 2000:
            raise ValueError("Description must not exceed 2000 characters")
        return v

    @field_validator("max_score")
    @classmethod
    def validate_max_score(cls, v):
        if v is not None and isinstance(v, int) and (v < 0 or v > 10000):
            raise ValueError("max_score must be between 0 and 10000")
        return v

    @field_validator("config")
    @classmethod
    def validate_config(cls, v: dict | None) -> dict | None:
        # Same bound as create — update must not bypass it.
        if v is not None and len(str(v)) > 20000:
            raise ValueError("config is too large")
        return v


class ExerciseResponse(BaseModel):
    id: str
    skill_id: str
    title: str
    description: str
    type: str
    config: dict
    sort_order: int
    max_score: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Attempt ───────────────────────────────────────────────


class SubmitAttemptRequest(BaseModel):
    answer: dict

    @field_validator("answer")
    @classmethod
    def validate_answer(cls, v: dict) -> dict:
        # Bound the answer JSON — same unbounded-JSONB-storage class as
        # settings/config. 100KB covers any legitimate text/code answer.
        if len(str(v)) > 100_000:
            raise ValueError("answer is too large")
        return v


class AttemptResponse(BaseModel):
    id: str
    exercise_id: str
    user_id: str
    answer: dict
    score: int | None
    is_correct: bool | None
    feedback: str | None
    graded_by: str | None
    graded_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class GradeAttemptRequest(BaseModel):
    score: int
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
        return v


# ── Progress ──────────────────────────────────────────────


class SkillProgressResponse(BaseModel):
    skill_id: str
    skill_name: str = ""
    status: str
    exercises_total: int
    exercises_done: int
    best_score: int | None
    started_at: datetime | None
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class OverallProgressResponse(BaseModel):
    skills_total: int
    skills_completed: int
    skills_in_progress: int
    exercises_total: int
    exercises_completed: int
    completion_percentage: float
    categories: list[dict]


# ── Reorder ───────────────────────────────────────────────


class ReorderItem(BaseModel):
    id: str
    sort_order: int

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v: int) -> int:
        if v < 0 or v > 100000:
            raise ValueError("sort_order must be between 0 and 100000")
        return v


class ReorderRequest(BaseModel):
    items: list[ReorderItem]

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: list) -> list:
        if len(v) > 1000:
            raise ValueError("Too many items to reorder (max 1000)")
        return v
