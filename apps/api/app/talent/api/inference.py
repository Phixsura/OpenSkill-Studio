"""Skill inference API — extract capabilities from free text."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.schemas.inference import (
    InferredSkillResponse,
    SkillInferenceRequest,
    SkillInferenceResponse,
)

router = APIRouter(prefix="/talent", tags=["Talent — Skill Inference"])


@router.post(
    "/capabilities/infer",
    response_model=DataResponse[SkillInferenceResponse],
    summary="Infer Skills",
)
async def infer_skills(
    body: SkillInferenceRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Extract capabilities from free text.

    Analyzes resume, job description, project description, or free text
    to identify matching capabilities with confidence scores.
    """
    from app.talent.services.skill_inference import infer_skills_from_text

    skills, processing_time = await infer_skills_from_text(
        db,
        body.text,
        body.source_type,
        max_results=body.max_results,
    )

    return DataResponse(
        data=SkillInferenceResponse(
            skills=[
                InferredSkillResponse(
                    capability_id=s.capability_id,
                    capability_name=s.capability_name,
                    confidence=s.confidence,
                    source_excerpt=s.source_excerpt,
                    match_type=s.match_type,
                )
                for s in skills
            ],
            source_type=body.source_type,
            text_length=len(body.text),
            processing_time_ms=processing_time,
        )
    )
