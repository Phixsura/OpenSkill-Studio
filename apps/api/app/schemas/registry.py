"""Pydantic schemas for public registry endpoints."""

from pydantic import BaseModel


class PreviewSkillItem(BaseModel):
    name: str
    description: str | None
    difficulty: str | None
    exercise_count: int
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
