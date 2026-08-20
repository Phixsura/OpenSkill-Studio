"""Pydantic schemas for public registry endpoints."""

from pydantic import BaseModel, field_validator


class PreviewExerciseItem(BaseModel):
    title: str


class PreviewSkillItem(BaseModel):
    name: str
    description: str | None
    difficulty: str | None
    exercise_count: int
    exercises: list[PreviewExerciseItem] = []
    prerequisites: list[str]


class PreviewTemplateItem(BaseModel):
    name: str
    description: str | None
    rubric_criteria_count: int


class PreviewCategoryItem(BaseModel):
    name: str


class PackPreviewResponse(BaseModel):
    skills: list[PreviewSkillItem]
    templates: list[PreviewTemplateItem]
    categories: list[PreviewCategoryItem]
    total_skills: int
    total_exercises: int
    total_templates: int


# ── Category Admin ──────────────────────────────────────


class CreateCategoryRequest(BaseModel):
    name: str
    slug: str
    parent_id: str | None = None
    icon: str | None = None
    sort_order: int = 0

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 1 or len(v) > 100:
            raise ValueError("Name must be 1-100 characters")
        return v

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        v = v.strip().lower()
        if len(v) < 1 or len(v) > 100:
            raise ValueError("Slug must be 1-100 characters")
        return v


class UpdateCategoryRequest(BaseModel):
    name: str | None = None
    slug: str | None = None
    parent_id: str | None = None
    icon: str | None = None
    sort_order: int | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if len(v) < 1 or len(v) > 100:
                raise ValueError("Name must be 1-100 characters")
        return v

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip().lower()
            if len(v) < 1 or len(v) > 100:
                raise ValueError("Slug must be 1-100 characters")
        return v


class CategoryResponse(BaseModel):
    id: str
    name: str
    slug: str
    parent_id: str | None
    icon: str | None
    sort_order: int

    model_config = {"from_attributes": True}
