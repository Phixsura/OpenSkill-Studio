"""Pydantic schemas for cohort/class management."""

from datetime import UTC, datetime

from pydantic import BaseModel, field_validator, model_validator

# ── Cohort CRUD ───────────────────────────────────────────


class CreateCohortRequest(BaseModel):
    name: str
    description: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    max_learners: int | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 200:
            raise ValueError("Name must be 2-200 characters")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 5000:
            raise ValueError("Description must be 5,000 characters or less")
        return v

    @field_validator("max_learners")
    @classmethod
    def validate_max_learners(cls, v: int | None) -> int | None:
        if v is not None and (v < 1 or v > 10000):
            raise ValueError("max_learners must be between 1 and 10,000")
        return v

    @field_validator("starts_at", "ends_at")
    @classmethod
    def normalize_tz(cls, v: datetime | None) -> datetime | None:
        if v is not None and v.tzinfo is None:
            return v.replace(tzinfo=UTC)
        return v

    @model_validator(mode="after")
    def validate_date_ordering(self):
        if self.starts_at and self.ends_at and self.ends_at < self.starts_at:
            raise ValueError("ends_at must be on or after starts_at")
        return self


class UpdateCohortRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    max_learners: int | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if len(v) < 2 or len(v) > 200:
                raise ValueError("Name must be 2-200 characters")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 5000:
            raise ValueError("Description must be 5,000 characters or less")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None:
            valid = {"draft", "active", "completed", "archived"}
            if v not in valid:
                raise ValueError(f"Status must be one of: {', '.join(sorted(valid))}")
        return v

    @field_validator("max_learners")
    @classmethod
    def validate_max_learners(cls, v: int | None) -> int | None:
        if v is not None and (v < 1 or v > 10000):
            raise ValueError("max_learners must be between 1 and 10,000")
        return v

    @field_validator("starts_at", "ends_at")
    @classmethod
    def normalize_tz(cls, v: datetime | None) -> datetime | None:
        if v is not None and v.tzinfo is None:
            return v.replace(tzinfo=UTC)
        return v

    @model_validator(mode="after")
    def validate_date_ordering(self):
        if self.starts_at and self.ends_at and self.ends_at < self.starts_at:
            raise ValueError("ends_at must be on or after starts_at")
        return self


class CohortResponse(BaseModel):
    id: str
    org_id: str
    name: str
    slug: str
    description: str | None
    status: str
    starts_at: datetime | None
    ends_at: datetime | None
    max_learners: int | None
    member_count: int = 0
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Members ──────────────────────────────────────────────


class AddCohortMemberRequest(BaseModel):
    user_id: str
    role: str = "learner"

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        valid = {"learner", "instructor"}
        if v not in valid:
            raise ValueError(f"Role must be one of: {', '.join(sorted(valid))}")
        return v


class BulkEnrollRequest(BaseModel):
    user_ids: list[str]
    role: str = "learner"

    @field_validator("user_ids")
    @classmethod
    def validate_user_ids(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("At least one user_id required")
        if len(v) > 500:
            raise ValueError("Cannot enroll more than 500 users at once")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        valid = {"learner", "instructor"}
        if v not in valid:
            raise ValueError(f"Role must be one of: {', '.join(sorted(valid))}")
        return v


class CohortMemberResponse(BaseModel):
    id: str
    cohort_id: str
    user_id: str
    role: str
    joined_at: datetime
    user_name: str | None = None
    user_email: str | None = None

    model_config = {"from_attributes": True}


# ── Skill Assignment ─────────────────────────────────────


class AssignSkillRequest(BaseModel):
    skill_id: str


class CohortSkillAssignmentResponse(BaseModel):
    cohort_id: str
    skill_id: str
    assigned_at: datetime
    skill_name: str | None = None

    model_config = {"from_attributes": True}


# ── Project Assignment ───────────────────────────────────


class AssignProjectRequest(BaseModel):
    project_id: str
    deadline_override: datetime | None = None
    late_deadline_override: datetime | None = None
    max_submissions_override: int | None = None
    participation_mode: str = "assigned"

    @field_validator("max_submissions_override")
    @classmethod
    def validate_max_submissions(cls, v: int | None) -> int | None:
        if v is not None and (v < 1 or v > 1000):
            raise ValueError("max_submissions_override must be between 1 and 1,000")
        return v

    @field_validator("participation_mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        valid = {"assigned", "application"}
        if v not in valid:
            raise ValueError(f"participation_mode must be one of: {', '.join(sorted(valid))}")
        return v

    @field_validator("deadline_override", "late_deadline_override")
    @classmethod
    def normalize_tz(cls, v: datetime | None) -> datetime | None:
        if v is not None and v.tzinfo is None:
            return v.replace(tzinfo=UTC)
        return v


class CohortProjectAssignmentResponse(BaseModel):
    id: str
    cohort_id: str
    project_id: str
    deadline_override: datetime | None
    late_deadline_override: datetime | None
    max_submissions_override: int | None
    participation_mode: str
    assigned_at: datetime
    project_title: str | None = None

    model_config = {"from_attributes": True}
