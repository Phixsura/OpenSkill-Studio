"""Pydantic schemas for resume parsing (N18)."""

from pydantic import BaseModel, Field


class ParseResumeRequest(BaseModel):
    text: str = Field(..., min_length=50, max_length=100000)
    auto_create_evidence: bool = False


class ParseResumeResponse(BaseModel):
    extracted_skills: list[dict]
    matched_capabilities: list[dict]
    evidence_created: list[dict]
    unmatched_terms: list[str]
    sections_found: list[str]
